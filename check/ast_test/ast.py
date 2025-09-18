import ast

path = "D:\\Research\\Project\\PyAnalysis\\tests\\ast_test\\tornado.py"

code = ""
with open(path, encoding='utf-8') as f:
    code = f.read()
    
tree = ast.parse(code)

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "Application" and \
                isinstance(node.func.value, ast.Attribute) and \
                node.func.value.attr == "web" and \
                isinstance(node.func.value.value, ast.Name) and \
                node.func.value.value.id == "tornado":
                    
                if node.args and isinstance(node.args[0], ast.List):
                    for elt in node.args[0].elts:
                        if isinstance(elt, ast.Tuple) and len(elt.elts) >= 2:
                            handler = elt.elts[1]
                            pass