import jedi
from pathlib import Path

def main():
    # proj = "D:\\Research\\Project\\PyAnalysis\\projs\\import"
    # proj = "D:\\Research\\Project\\PyAnalysis\\tests\\jedi_test\\test_wsgi.py"
    # p = str(Path(proj).resolve())
    # proj = "D:\\Research\\Project\\PyAnalysis\\tests\\jedi_test\\test_http_server.py"
    proj = "D:\\Research\\Project\\PyAnalysis\\tests\\jedi_test\\falcon.py"
    # project = jedi.Project(path = p)
    
    # script = jedi.Script(path="D:\\Research\\Project\\PyAnalysis\\projs\\import\\mlflow\\server\\__init__.py", project=project)

    script = jedi.Script(path=proj)
    
    line = 30
    col = 30

    definitions = script.goto(line=line, column=col)
    for d in definitions:
        print("定义:", d.name, "文件:", d.module_path, "行号:", d.line)
        


if __name__ == "__main__":
    main()
