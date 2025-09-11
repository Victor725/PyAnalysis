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
import ast


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


# format scope using line number in source code
def getFunc(code, line_num):
    Ast = None
    try:
        Ast = ast.parse(code)  # Ast is a instance of ast.Module
    except:
        # Ast = ast.parse(code, feature_version=(2,5))
        return ""
    
    current = Ast
    scope = []
    
    def find_body(node):
        try:
            body = node.body
        except:
            return None
        
        # handle 'except'
        if isinstance(node, ast.Try) == True:
            body += node.handlers
            body += node.orelse
            body += node.finalbody
        
        for n in body:
            if line_num >= n.lineno and line_num <= n.end_lineno: # line_num lie in the node
                if isinstance(n, ast.ClassDef) or isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef):
                    # fine body that contains line_num
                    scope.append(n.name)
                return n
        return None
    
    while(True):
        current = find_body(current)
        if current == None:
            return ".".join(scope)


def find_by_decorator(regx:re.Pattern, code):
    
    scopes = []
    
    # find line number of the decorated function
    targeted_locations = []
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            for deco in node.decorator_list:
                decorator = '@' + ast.get_source_segment(code, deco)
                if regx.search(decorator):
                    targeted_locations.append(node.lineno)
    
    # get scope information using getFunc()
    for location in targeted_locations:
        scopes.append(getFunc(code, location))
    
    return scopes
    


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

 
        self.entries = []    # {file_path, scope}
        for framework in frameworks.keys():
            regxs = frameworks[framework]['regx']
            # regxs[0]: register using decorator
            # regxs[1]: register with func call
            for i, regx_str in enumerate(regxs):
                regx = re.compile(regx_str)
                for document in self.documents:
                    document:Document                    
                    # before matching, delete all comments and strings in the code
                    content = remove_comments_and_docstrings(document.text)
                    
                    if regx.search(content):
                        # rel_path = document.meta_data["file_path"]
                        # self.entry_files.append(rel_path)
                        if i == 0: # handle decorator register
                            # funcs: list of function scopes
                            funcs = find_by_decorator(regx, document.text)
                            for func in funcs:
                                entry = {
                                    'file_path': document.meta_data['file_path'],
                                    'scope': func
                                }
                                self.entries.append(entry)
                        elif i == 1:
                            pass
        
        # deduplication
        self.dedup_entries()
        
        return self.entries



    def findVul(self):
        
        # get entries of projs
        entries = asyncio.run(self.getEntry())
        print(entries)
        # get vul in entries
        
        
        

if __name__ == "__main__":
    regx_str = r'''@(\w)*\.(get|post|put|delete|patch|options|head|api_route|route|websocket)\s*\('''
    regx = re.compile(regx_str)
    
    code = '''class SearchRoutesResponse(BaseModel):
    routes: list[Route]
    next_page_token: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "endpoints": [
                    {
                        "name": "openai-chat",
                        "route_type": "llm/v1/chat",
                        "model": {
                            "name": "gpt-4o-mini",
                            "provider": "openai",
                        },
                    },
                    {
                        "name": "anthropic-completions",
                        "route_type": "llm/v1/completions",
                        "model": {
                            "name": "claude-instant-100k",
                            "provider": "anthropic",
                        },
                    },
                    {
                        "name": "cohere-embeddings",
                        "route_type": "llm/v1/embeddings",
                        "model": {
                            "name": "embed-english-v2.0",
                            "provider": "cohere",
                        },
                    },
                ],
                "next_page_token": "eyJpbmRleCI6IDExfQ==",
            }
        }


def create_app_from_config(config: GatewayConfig) -> GatewayAPI:
    """
    Create the GatewayAPI app from the gateway configuration.
    """
    limiter = Limiter(
        key_func=get_remote_address, storage_uri=MLFLOW_GATEWAY_RATE_LIMITS_STORAGE_URI.get()
    )
    app = GatewayAPI(
        config=config,
        limiter=limiter,
        title="MLflow AI Gateway",
        description="The core deployments API for reverse proxy interface using remote inference "
        "endpoints within MLflow",
        version=VERSION,
        docs_url=None,
    )

    @app.get("/", include_in_schema=False)
    async def index():
        return RedirectResponse(url="/docs")

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        for directory in ["build", "public"]:
            favicon_file = Path(__file__).parent.parent.joinpath(
                "server", "js", directory, "favicon.ico"
            )
            if favicon_file.exists():
                return FileResponse(favicon_file)
        raise HTTPException(status_code=404, detail="favicon.ico not found")'''
    
    print(find_by_decorator(regx, code))
    
    
    