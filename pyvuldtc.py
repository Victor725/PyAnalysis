from api.chat import *
import json
import asyncio

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
        
    
    
    def getEntry(self):
        # Whether it is a web app?
        webapp_promptContent = '''Your task is to determine whether this project is a web application.
        Your answer should be only 'Yes' or 'No'
        '''
        
        request = self.build_req(webapp_promptContent)
        
        response_webapp = asyncio.run(AskLLM(request))
        
        if "No" in response_webapp:
            print("Not web app, skip")
            return []
        
        # find out the entries        
        entry_promptContent = '''Your task is to find all entries exposed to users in this web application.

Your answer should only contain a list, the items of which is a dict, containing the following attributes: method, name, parameters, file_path.
"parameters" is a str list, if there's no parameters, return an empty list: [].
"file_path" is path of file that contains definition of the entry

IMPORTANT: Generate all the content in English.

You will be given content of related source files.

Remember to ground every claim in the provided source files.'''

        request = self.build_req(entry_promptContent)
        
        response_entry = asyncio.run(AskLLM(request))
        
        entry_json = json.loads(response_entry)
        
        if len(entry_json) == 0:
            print("No entries found")
        
        return entry_json

       

    def findVul(self):
        
        # get entries of projs
        entries = self.getEntry()
        
        # get vul in entries
        