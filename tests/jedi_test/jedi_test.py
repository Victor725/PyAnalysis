import jedi
from pathlib import Path

def main():
    proj = "D:\\Research\\Project\\PyAnalysis\\projs\\import"
    p = str(Path(proj).resolve())
    
    project = jedi.Project(path = p)
    
    script = jedi.Script(path="D:\\Research\\Project\\PyAnalysis\\projs\\import\\mlflow\\server\\__init__.py", project=project)

    line = 21
    col = 50

    definitions = script.infer(line=line, column=col)
    for d in definitions:
        print("定义:", d.name, "文件:", d.module_path, "行号:", d.line)
        


if __name__ == "__main__":
    main()
