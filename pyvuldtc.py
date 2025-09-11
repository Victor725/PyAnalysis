from api.chat import *
import json
import asyncio
from frameworks import *
import re
from api.data_pipeline import read_all_documents
from adalflow.core.types import Document
from import_graph import build_graph
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
        
    
    def dedup(self):
        seen = set()
        unique_entries = []
        
        for entry in self.entries:
            key = json.dumps(entry, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique_entries.append(entry)
                
        self.entries = unique_entries
    
    
    async def getEntry(self):
        # Whether it is a web app?
        # webapp_promptContent = '''Your task is to determine whether this project is a web application.
        # Your answer should be only 'Yes' or 'No'
        # '''
        
        # request = self.build_req(webapp_promptContent)
        
        # response_webapp = await AskLLM(request)
        
        # if "No" in response_webapp:
        #     print("Not web app, skip")
        #     return []
        
        self.documents = read_all_documents(self.path)
        
        # build import graph
        import_graph = build_graph(self.path, self.documents)

        self.entry_files = []
        # find files containing entries
        for framework in frameworks.keys():
            regx = re.compile(frameworks[framework]['regx'])
            for document in self.documents:
                document:Document
                content = document.text
                
                # before matching, delete all comments and strings in the code
                content = remove_comments_and_docstrings(content)
                
                if regx.search(content):
                    rel_path = document.meta_data["file_path"]
                    self.entry_files.append(rel_path)
        
        
        self.entries = []     
        # for each file, find 'related' files, send to LLM to determine entries defined
        # self.entry_files: rel_paths
        for entry_file in self.entry_files:
            
            print("Processing entry file: %s"%entry_file)
            
            rel_path = Path(entry_file)
            abs_path = str((Path(self.path) / rel_path).resolve())
            
            target_file_content = ""
            with open(abs_path, encoding="utf-8") as f:
                target_file_content = f.read()
            
            # get related files, depth = 1
            predecessors = list(import_graph.predecessors(abs_path))
            successors = list(import_graph.successors(abs_path))
            related_files = list(set(predecessors + successors))
            
            context_parts = []
            for related_file in related_files:
                header = f"## File Path: {entry_file}\n\n"
                content = ""
                with open(related_file, encoding='utf-8') as f:
                    content = f.read()
                context_parts.append(f"{header}{content}")
            
            context_text = "\n\n" + "-" * 10 + "\n\n".join(context_parts)

            # do not need parameter
            entry_promptContent = f'''You are an expert code analyst. 
Your task is to identify all entry points exposed in the following source code (e.g., HTTP endpoints such as routes, views, url, or API methods).
You provide direct, concise, and accurate information about source code.

CRITICAL:
You NEVER start responses with markdown headers or code fences.

IMPORTANT: Generate all the content in English.

Remember to ground every claim in the provided source files.

Requirements:
- Your output should not contain any other content, except for a JSON-compatible list, where each item is a dict with the following keys:
  - "method": the HTTP method (e.g., GET, POST, PUT, DELETE).
  - "name": the route or entry path exposed to the user.
  - "file_path": file path where the entry is defined.

Here is content of the file:

## File Path: {entry_file}

{target_file_content}

Here are other files you can refer to:

{context_text}
'''
            
            request = self.build_req(entry_promptContent)
            
            response_entry = await AskLLM_raw(request)

            # print(response_entry)
            
            json_response = json.loads(response_entry)
            self.entries.extend(json_response)
        
        # deduplication
        self.dedup()
        
        return self.entries



    def findVul(self):
        
        # get entries of projs
        entries = asyncio.run(self.getEntry())
        print(entries)
        # get vul in entries
        