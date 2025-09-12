import logging
from api.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

from pyvuldtc import *
from api.chat import *
import asyncio

def main():
   
    # path = "./projs/PyWebappTest"
    # path = "./projs/HttpsServer"
    path = "./projs/mlflow"
    # path = "./projs/Synthetic_servers"
    
    pyVD = PyVulDetector(path)#, model="gpt-5")
    
    prompt = '''Find definition of the request handler in:
    app.add_url_rule(
        rule=CREATE_USER,
        view_func=create_user,
        methods=["POST"],
    )'''
    
    asyncio.run(rag_search(pyVD.build_req(prompt)))
    

if __name__ == "__main__":
    main()