from .pyvuldtc import *


def main():
    path = ""
    
    pyVD = PyVulDetector(path)
    
    reports = pyVD.findVul()
    
    # save reports
    

if __name__ == "__main__":
    main()