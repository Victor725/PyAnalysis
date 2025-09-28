import pandas as pd
import os
import zipfile
from pathlib import Path
import time
import ast

CASE_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\cases"
CASE_CSV_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\cases.csv"
CVE_COLLECTION_PATH = r"\\?\G:\\SASTcomparison\\CVECollection"


def Log(message:str):
    current_time = time.asctime(time.localtime(time.time()))
    
    message = current_time + " " + message
    
    print(message)


def un_zip(file_name:str):
    #file_name: absolute path of zip
    dir_name = file_name.split(".zip")[0]
    parent_dir = os.path.abspath(os.path.join(dir_name, "../"))
    if os.path.isdir(dir_name):
        #print(file_name)
        Log(file_name + " Already unzipped")
        return dir_name
    
    zip_file = zipfile.ZipFile(file_name)
    ori_name = zip_file.namelist()[0]
    zip_file.extractall(os.path.abspath(os.path.join(dir_name,"../")))
    os.rename(os.path.abspath(os.path.join(parent_dir, ori_name)), dir_name)
    zip_file.close()
    
    Log(file_name + " Unzipped")
    return dir_name


def get_function_content(file_path:Path, scope:str):
    
    file_content = file_path.read_text(encoding="utf-8")
    
    file_lines = file_content.splitlines()
    
    tree = ast.parse(file_content)
    
    scope = scope.split(".")
    
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef) or isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef):
            if n.name == scope[0]:
                if len(scope) == 1:
                    start = n.lineno
                    end = n.end_lineno
                    if n.decorator_list:
                        start = min([n.lineno] + [d.lineno for d in n.decorator_list])
                    code_snippet = "\n".join(file_lines[start-1:end])
                    return code_snippet
                else:
                    scope.pop(0)

    Log(f"Warning: cannot find function {'.'.join(scope)} in {file_path}")
    return None


def get_vul_type(vul_type:str):
    Type = ""
    
    if vul_type == "code injection":
        Type = "CodeInjection"
    elif vul_type == "OS Command Injection":
        Type = "CommandInjection"
    elif vul_type == "Deserialization":
        Type = "Deserialization"
    elif vul_type == "path traversal":
        Type = "PathTraversal"
    elif vul_type == "sql injection":
        Type = "SQLInjection"
    elif vul_type == "cross-site scripting":
        Type = "XSS"
    
    return Type

    
def main():
    case_df = pd.read_csv(CASE_CSV_PATH)
    for index, row in case_df.iterrows():
        cvelnk = row["CVE"]
        cve = cvelnk[cvelnk.find("CVE-"):]
        cve_dir = Path(CVE_COLLECTION_PATH) / cve
        
        # unzip
        files = os.listdir(cve_dir)  # file name, not abs path
        dir_name = None
        for file in files:
            if file.endswith("-vul.zip"):
                file_name = os.path.join(cve_dir, file)
                dir_name = un_zip(file_name)  # unzipped dir
                break
        
        item_root = cve_dir / dir_name
        rel_locations = row["EntryPoint"].split("; ")
        for i, rel_location in enumerate(rel_locations):
            rel_path = rel_location.split(":")[0]
            scope = rel_location.split(":")[1]
            
            abs_path = item_root / rel_path
            
            func_content = get_function_content(abs_path, scope)
            
            if func_content is not None:
                # get vul type
                vul_type = row["Type"]
                Type = get_vul_type(vul_type)
                
                case_name = ""
                if len(rel_locations) > 1:
                    case_name = cve + f"_{i}.py"
                else:
                    case_name = cve + ".py"
                target_path: Path = Path(CASE_PATH) / Type / case_name
                if not target_path.exists():
                    target_path.write_text(func_content, encoding="utf-8")
                
                

if __name__ == "__main__":
    main()