from api.chat import *
import json
import os
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
        potentialVulType_kb = "./PotentialType/knowledge"
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
        self.potentialVulType_kb = potentialVulType_kb
    
    def build_req(self, prompt, **kargs):
        request = {}

        if kargs.get('repo_url', None) != None:
            request['repo_url'] = kargs.get('repo_url')
        else:
            request['repo_url'] = self.path
            
        if kargs.get('db_save_dir', None) != None:
            request['db_save_dir'] = kargs.get('db_save_dir')
                        
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
        
        if kargs.get('include_dirs', None) != None:
            request['included_dirs'] = kargs.get('include_dirs')
        
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
            
            # Filter out non-request-handling funcs.  
            # then summarize
            prompt = f'''You are an expert in security-oriented code analysis.

Given a function/class, first, you need to determine if its behavior or return value is directly influenced by external input (such as request data, command-line arguments, environment variables, files, or other user-provided values).
Only consider whether the function/class itself directly reads, accesses, or processes such input.
Ignore static content such as static HTML code, string literals, or embedded JavaScript code that may reference external input but is not actually executed by the function/class itself.

If it does not, just answer strictly with "!No!". Do not provide any explanation or additional text.


If it does, summarize the following Python function or class at a high level of abstraction.

Guidelines:
Focus only on the overall purpose and behavior of the code.
If the input is a function, provide one concise summary of its overall role.
If the input is a class, provide a separate summary for each method, focusing on what it does.
Avoid mentioning variable names, parameter names, or implementation details.
The goal is to capture what it does, not how it does it.

Here is the code:

{body}

'''

            request = self.build_req(prompt)
            summarization = await AskLLM_raw(request)

            if "!no!" in summarization.lower():
                rm_entries.append(i)
                continue
            
            
            self.entries[i]['summarize'] = summarization
        
        for i in sorted(rm_entries, reverse=True):
            self.entries.pop(i)
    
    async def getEntry(self):
        
        self.documents = read_all_documents(self.path, code_extensions = [".py"])
        
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
        
        await self.gen_sumarize()
        
        return self.entries
    
    def gen_potVulType(self):
        for i, entry in enumerate(self.entries):
            summarize = entry['summarize']
            include_dirs = "knowledge/"
            
            db_save_dir = os.path.join(os.path.dirname(self.potentialVulType_kb), "rag")
            request = self.build_req(summarize, include_dirs=include_dirs, repo_url=self.potentialVulType_kb, db_save_dir=db_save_dir)
            
            docs, scores = asyncio.run(rag_search(request, top_k=8))
            self.entries[i]['potential_vul_types'] = []
            
            print(f"Entry scope: {entry['scope']}")
            for j, doc in enumerate(docs):
                path = doc.meta_data.get('file_path', 'unknown')
                print(f"Retrieved doc for potential type: {path}")
                self.entries[i]['potential_vul_types'].append(f"{os.path.dirname(path)}: {scores[j]}")
            # self.entries[i]['potential_vul_types'] = list(set(self.entries[i]['potential_vul_types']))
            print("-------------------")


    def detect_vul(self):
        
        strategies = self.load_strategies()
        
        for i, entry in enumerate(self.entries):
            potTypes = entry["potential_vul_types"]
            potTypes = [pt.split(":")[0] for pt in potTypes]
            # detect under strategy, output if vulnerable
            for t in potTypes[0:3]:
                # get detect strategy
                strategy = strategies[t]
                # get code
                
                # detect vuln.
                


    def findVul(self):
        # get entries of projs
        entries = asyncio.run(self.getEntry())
        
        entry_file = "./entries.json"
        with open(entry_file, "w") as f:
            json.dump(entries, f, indent=4)
        
        # get vul in entries
        # find potential vul types
        self.gen_potVulType()
        with open(entry_file, "w") as f:
            json.dump(self.entries, f, indent=4)
            
        
        self.detect_vul()        
        
        
        
        
        

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
    
    
    