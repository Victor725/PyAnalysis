from api.chat import *
import json
import asyncio
from frameworks import *
import re
from api.data_pipeline import read_all_documents
from adalflow.core.types import Document
from pathlib import Path

import io
import tokenize



def remove_comments_and_docstrings(source: str) -> str:
    io_obj = io.StringIO(source)
    out_tokens = []
    
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type, token_string, start, end, line = tok
        
        if token_type == tokenize.COMMENT:
            continue
        
        # 跳过三引号字符串（多行的 STRING，且出现在定义外部时多半是注释用途）
        if token_type == tokenize.STRING:
            if token_string.startswith('"""') or \
                token_string.startswith("'''") or \
                token_string.startswith('"') or \
                token_string.startswith("'"):
                continue
        
        out_tokens.append(token_string)
    
    return "".join(out_tokens)


'''
class ChatCompletionRequest(BaseModel):
    """
    Model for requesting a chat completion.
    """
    repo_url: str = Field(..., description="URL of the repository to query")
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    filePath: Optional[str] = Field(None, description="Optional path to a file in the repository to include in the prompt")
    token: Optional[str] = Field(None, description="Personal access token for private repositories")
    type: Optional[str] = Field("github", description="Type of repository (e.g., 'github', 'gitlab', 'bitbucket')")

    # model parameters
    provider: str = Field("google", description="Model provider (google, openai, openrouter, ollama, azure)")
    model: Optional[str] = Field(None, description="Model name for the specified provider")

    language: Optional[str] = Field("en", description="Language for content generation (e.g., 'en', 'ja', 'zh', 'es', 'kr', 'vi')")
    excluded_dirs: Optional[str] = Field(None, description="Comma-separated list of directories to exclude from processing")
    excluded_files: Optional[str] = Field(None, description="Comma-separated list of file patterns to exclude from processing")
    included_dirs: Optional[str] = Field(None, description="Comma-separated list of directories to include exclusively")
    included_files: Optional[str] = Field(None, description="Comma-separated list of file patterns to include exclusively")
'''
class PyVulDetector:
    
    # provider: ('google', 'openai', 'openrouter', 'ollama', 'bedrock')
    def __init__(
        self, path, provider="openai", model = "gpt-4o",
        language = "en", #(e.g., 'en', 'ja', 'zh', 'es', 'kr', 'vi')
        ):
        self.path = str(Path(path).resolve())
        self.provider = provider
        self.type = (
            "bitbucket" if "bitbucket.org" in path else
            "gitlab"    if "gitlab.com" in path else
            "github"    if "github.com" in path else
            ""
        )
        self.model = model
        self.language = language
    
    def build_req(self, prompt):
        request = {}
        
        request['repo_url'] = self.path
        request['messages'] = [{
            'role': 'user',
            'content': prompt
        }]
        request['type'] = self.type
        request['provider'] = self.provider
        request['model'] = self.model
        request['language'] = self.language
        
        request['excluded_dirs'] = ""
        request['excluded_files'] = ""
        request['included_dirs'] = ""
        request['included_files'] = ""
        
        return request        
            
    def dedup_entries(self):
        seen = set()
        unique_entries = []
        
        for entry in self.entries:
            key = json.dumps(entry, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique_entries.append(entry)
                
        self.entries = unique_entries
    
    async def gen_sumarize(self):
        # for each entry
        # get body, using line number
        # give LLM the body, generate summarize
        root = Path(self.path)
        rm_entries = []
        for i, entry in enumerate(self.entries):
            lineno = entry['lineno']
            rel_path = Path(entry['file_path'])
            file_path = str((root / rel_path).resolve())
            body = get_def_at_line(file_path, lineno)
            if body == None:
                rm_entries.append(i)
                continue
                
            prompt = f'''You are an expert security-oriented code analyst.
Given the following Python function/class definition, analyze and summarize its behavior.

Your summary must include:
User Input Sources: Does the function take any input that could originate from the user (e.g., HTTP request parameters, command-line arguments, environment variables, file contents)? If yes, specify how.
Main Functionality: Provide a concise but clear description of the function's core purpose and logic.
Outputs / Return Values: What kind of data does it return or produce (e.g., HTML page, JSON object, file, plain text, system command output)?

Format your answer in a structured way, like:
User Input Sources: …
Main Functionality: …
Outputs / Return Values: …

If given a class, you can return multi groups of User Input Sources, Main Functionality, and Outputs / Return Values for every methods

CRITICAL:
You NEVER start responses with markdown headers or code fences.
IMPORTANT: Generate all the content in English.

Here is the function/class:

{body}'''

            request = self.build_req(prompt)
            summarization = await AskLLM_raw(request)
            
            self.entries[i]['summarize'] = summarization
        
        for i in sorted(rm_entries, reverse=True):
            self.entries.pop(i)
            
    
    async def getEntry(self):
        
        self.documents = read_all_documents(self.path)
        
        compiled_frameworks = {}
        for framework in frameworks.keys():
            regxs = frameworks[framework]['regx']
            for i, regx_str in enumerate(regxs):
                if i == 0:
                    compiled_frameworks[framework] = {}
                    compiled_frameworks[framework]['regx'] = []
                if regx_str == None:
                    compiled_frameworks[framework]['regx'].append(None)
                else:
                    compiled_frameworks[framework]['regx'].append(re.compile(regx_str))


        self.entries = []    # {file_path, scope, lineno}        
        for document in self.documents:
            for framework in compiled_frameworks.keys():
                regxs = compiled_frameworks[framework]['regx']
                for i, regx in enumerate(regxs):
                    
                    if regx == None:
                        continue
                    
                    document:Document                    
                    # before matching, delete all comments and strings in the code
                    content = remove_comments_and_docstrings(document.text)
                    
                    # if document.meta_data['file_path'] == 'sql\\urls.py':
                    #     pass
                    
                    if regx.search(content):
                        # rel_path = document.meta_data["file_path"]
                        # self.entry_files.append(rel_path)
                        if i == 0: # handle decorator register
                            # funcs: list of function scopes
                            locations = find_by_decorator(regx, document.text)
                            for item in locations:
                                entry = {
                                    'file_path': document.meta_data['file_path'],
                                    'scope': item['scope'],
                                    'lineno': item['lineno'],
                                    'args': item['args']
                                }
                                self.entries.append(entry)
                        elif i == 1:
                            entries = []
                            if framework == 'fastapi':
                                entries = fastapi_find_by_call(self.path, document.meta_data['file_path'])
                            elif framework == 'django':
                                entries = django_find_by_call(self.path, document.meta_data['file_path'])
                            elif framework == 'flask':
                                entries = flask_find_by_call(self.path, document.meta_data['file_path'])
                            elif framework == 'pyramid':
                                entries = pyramid_find_by_call(self.path, document.meta_data['file_path'])
                            elif framework == 'bottle':
                                entries = bottle_find_by_call(self.path, document.meta_data['file_path'])
                            elif framework == 'tornado':
                                entries = tornado_find_by_call(self.path, document.meta_data['file_path'])
                            elif framework == 'websockets':
                                entries = websockets_find_by_call(self.path, document.meta_data['file_path'])    
                            elif framework == 'aiohttp':
                                entries = aiohttp_find_by_call(self.path, document.meta_data['file_path'])
                            elif framework == 'sanic':
                                entries = sanic_find_by_call(self.path, document.meta_data['file_path'])
                            elif framework == 'falcon':
                                entries = falcon_find_by_call(self.path, document.meta_data['file_path'])
                            
                            
                            self.entries.extend(entries)
        
        # deduplication
        self.dedup_entries()
        
        
        if len(self.entries) == 0:
            return []
        
        # await self.gen_sumarize()
        
        return self.entries



    def findVul(self):
        
        # get entries of projs
        entries = asyncio.run(self.getEntry())
        
        entry_file = "./entries.json"
        with open(entry_file, "w") as f:
            json.dump(entries, f)
        # get vul in entries
        
        
        

if __name__ == "__main__":
    regx_str = r'''\.add_url_rule\s*\('''
    regx = re.compile(regx_str)
    
    code = '''def create_app(app: Flask = app):
    app.add_url_rule(
        SIGNUP,
        'dsaf',
        view_func=signup.views.as_view(),
        methods=["GET"],
    )'''
    
    print(flask_find_by_call(regx, code))
    
    
    