import logging
from api.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

from pyvuldtc import *


def main():
   
    # path = "./projs/PyWebappTest"
    # path = "./projs/HttpsServer"
    # path = "./projs/mlflow"
    path = "./projs/Archery"
    # path = "./projs/Synthetic_servers"
    
    pyVD = PyVulDetector(path)#, model="gpt-5")
    
    reports = pyVD.findVul()
    
    # save reports
    

if __name__ == "__main__":
    main()