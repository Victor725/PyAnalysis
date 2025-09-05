import logging
from api.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

from pyvuldtc import *


def main():
   
    path = "./projs/PyWebappTest"
    # path = "./projs/HttpsServer"
    # path = "./projs/mlflow"
    
    pyVD = PyVulDetector(path)
    
    reports = pyVD.findVul()
    
    # save reports
    

if __name__ == "__main__":
    main()