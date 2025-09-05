from .pyvuldtc import *


def main():
   
    # path = "./projs/PyWebappTest"
    #path = "./projs/HttpsServer"
    path = "./projs/mlflow"
    
    pyVD = PyVulDetector(path)
    
    reports = pyVD.findVul()
    
    # save reports
    

if __name__ == "__main__":
    main()