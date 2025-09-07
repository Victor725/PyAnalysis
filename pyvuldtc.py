from api.chat import *
import json
import asyncio
from frameworks import *
import re
from api.data_pipeline import read_all_documents
from adalflow.core.types import Document

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
        self.path = path
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

        
        self.entry_files = []  # items: {path: str, import:[]}
        # find files containing entries
        for framework in frameworks.keys():
            regx = re.compile(frameworks[framework]['regx'])
            for document in self.documents:
                document:Document
                content = document.text
                if regx.search(content):
                    entry_file = {
                        'path': document.meta_data["file_path"]
                    }
                    self.entry_files.append(entry_file)
        
        
        # return self.entry_files
        # build import graph
        
        
            
        # for each file, find 'related' files, send to LLM to determine entries defined
                
        entry_promptContent = '''Your task is to identify all entry points exposed in this web application 
# (e.g., HTTP endpoints such as routes, views, url, or API methods).

# Requirements:
# - Your output must be a JSON-compatible list, where each item is a dict with the following keys:
#   - "method": the HTTP method (e.g., GET, POST, PUT, DELETE).
#   - "name": the route or entry path exposed to the user.
#   - "parameters": a list of parameter names (strings). If there are no parameters, return [].
#   - "file_path": the path of the source file where the entry is defined.

# Here are some common examples:

# Flask:
#     @app.route("/login", methods=["GET", "POST"])
#     def login():
#         ...

#     app.add_url_rule("/logout", "logout", logout_handler)

# IMPORTANT: Generate all the content in English.

# You will be given content of related source files.

# Remember to ground every claim in the provided source files.
# '''
            
        
        request = self.build_req(entry_promptContent)
        
        response_entry = await AskLLM(request)
        
        entry_json = response_entry
        # entry_json = json.loads(response_entry)
        
        # if len(entry_json) == 0:
        #     print("No entries found")
        
        return entry_json

       

    def findVul(self):
        
        # get entries of projs
        entries = asyncio.run(self.getEntry())
        print(entries)
        # get vul in entries
        