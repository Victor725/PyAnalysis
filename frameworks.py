frameworks = {
    'django':{
        'regx': [
            r'''@action\s*\(''',
            r'''(django(.|\n)*(?<!\.)(\bpath\s*\(|\bre_path\s*\())|(\.register\s*\()|(\.as_asgi\s*\()'''
        ],
        'examples': ''''''
    },
    "fastapi":{
        'regx': [
            r'''@(\w)*\.(get|post|put|delete|trace|patch|options|head|api_route|route|websocket)\s*\(''',
            r'''(add_api_route|add_api_websocket_route|add_websocket_route|add_route)\s*\('''
        ],
        'examples': ''''''
    },
    'flask':{
        'regx': [
            r'''(@(\w)*\.(route|get|post|put|delete|patch)\s*\()|(@expose\s*\()''',
            r'''(\.add_url_rule\s*\()|(\.add_resource\s*\()'''
        ],
        'examples': ''''''
    }
    # 'bottle':{
    #     'regx': r'''(@\s*(route|get|post|put|delete|patch|error)\s*\()|(\broute\s*\()|(\b\w+\.route\s*\()|(\b\w+\.add_route\s*\()''',
    #     'examples': ''''''
    # },
    # 'web2py':{
    #     'regx': r'''(?:\bpath\s*\(|\bre_path\s*\(|\binclude\s*\(|\.as_view\s*\(|router\.register\s*\(|@action\s*\(|consumers\..*\.as_asgi\s*\(|admin\.site\.urls)''',
    #     'examples': ''''''
    # }
}

from pathlib import Path
import ast
import jedi
import re


def get_def_at_line(file_path, target_line):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    
    tree = ast.parse(source)
    lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = 0
            try:
                if node.decorator_list:
                    start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                else:
                    start = node.lineno
            except:
                start = node.lineno
                
            end = getattr(node, "end_lineno", start)
            if node.lineno == target_line:
                if "def " in lines[node.lineno-1] or "class " in lines[node.lineno-1]:
                    code_snippet = "\n".join(lines[start-1:end])
                    return code_snippet
                else:
                    return None
            
# format scope using line number in source code
def getFunc(code, line_num):
    Ast = None
    try:
        Ast = ast.parse(code)  # Ast is a instance of ast.Module
    except:
        # Ast = ast.parse(code, feature_version=(2,5))
        return ""
    
    current = Ast
    scope = []
    
    def find_body(node):
        try:
            body = node.body
        except:
            return None
        
        # handle 'except'
        if isinstance(node, ast.Try) == True:
            body += node.handlers
            body += node.orelse
            body += node.finalbody
        
        for n in body:
            if line_num >= n.lineno and line_num <= n.end_lineno: # line_num lie in the node
                if isinstance(n, ast.ClassDef) or isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef):
                    # fine body that contains line_num
                    scope.append(n.name)
                return n
        return None
    
    while(True):
        current = find_body(current)
        if current == None:
            return ".".join(scope)

def jedi_resolve(project_path, file_path, line, col):
    # if "mlflow\\server\\auth\\__init__.py" in str(file_path):
    #     pass
    project = jedi.Project(path = project_path)    
    script = jedi.Script(path=file_path, project=project)
    definitions = script.goto(line=line, column=col, follow_imports=True)
    for d in definitions:
        try:
            module_path = Path(d.module_path)
            rel_path = str(module_path.relative_to(Path(project_path)))
            d_line = d.line
            
            code = ""
            with open(module_path, encoding="utf-8") as f:
                code = f.read()
            scope = getFunc(code, d_line)
            if scope == "":
                continue
            entry = {
                'file_path': rel_path,
                'scope': scope,
                'lineno': d_line
            }
            return entry
        except:
            continue
        
        
    return None

def find_by_decorator(regx:re.Pattern, code):
    
    scope_and_lineno = []    #{scope, lineno}
    
    # find line number of the decorated function
    targeted_locations = []
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            for deco in node.decorator_list:
                decorator = '@' + ast.get_source_segment(code, deco)
                if regx.search(decorator):
                    targeted_locations.append(node.lineno)
    
    # get scope information using getFunc()
    for location in targeted_locations:
        
        scope_and_lineno.append(
            {
                "lineno": location,
                'scope': getFunc(code, location)
            }
        )
    
    return scope_and_lineno



def django_find_by_call(root, rel_path):
    
    proj_root = Path(root)
    rel_path = Path(rel_path)
    file_path = proj_root / rel_path
    
    file_path_str = str(file_path.resolve())
    code = ""
    with open(file_path_str, encoding='utf-8') as f:
        code = f.read()
    
    entries = []    # {file_path(rel), scope(not ''!!!), lineno}
    tree = ast.parse(code)
    
    r'''(django(.|\n)*(?<!\.)(\bpath\s*\(|\bre_path\s*\())|(\.register\s*\()|(\.as_asgi\s*\()'''
    # return ast.dump(tree, indent=4)
    for node in ast.walk(tree):
        value_node = None
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "register":
                    if len(node.args) > 1:
                        value_node = node.args[1]
                elif node.func.attr == "as_asgi":
                    value_node = node.func.value
            elif isinstance(node.func, ast.Name):
                if node.func.id == "path" or node.func.id == 're_path':
                    if len(node.args) > 1:
                        value_node = node.args[1]
                                
        if value_node:
            if isinstance(value_node, ast.Attribute): # name in other file or under class def
                col = value_node.value.end_col_offset + 2  # get attr
                lineno = value_node.value.lineno
                entry = jedi_resolve(root, file_path_str, lineno, col)
                if entry:
                    entries.append(entry)                            
            elif isinstance(value_node, ast.Name): # plain function name
                col = value_node.end_col_offset
                lineno = value_node.lineno
                entry = jedi_resolve(root, file_path_str, lineno, col)
                if entry:
                    entries.append(entry)
            elif isinstance(value_node, ast.Call): # .as_view()
                # as_view
                if isinstance(value_node.func, ast.Attribute) and value_node.func.attr == "as_view":
                    # take content before .as_view as target
                    col = value_node.func.value.end_col_offset
                    lineno = value_node.func.value.lineno
                    entry = jedi_resolve(root, file_path_str, lineno, col)
                    if entry:
                        entries.append(entry)
                # elif isinstance(value_node.func, ast.Name) and value_node.func.id == "include":
                #     continue
                        
    return entries

def fastapi_find_by_call(root, rel_path):
    proj_root = Path(root)
    rel_path = Path(rel_path)
    file_path = proj_root / rel_path
    
    file_path_str = str(file_path.resolve())
    code = ""
    with open(file_path_str, encoding='utf-8') as f:
        code = f.read()
    
    entries = []    # {file_path(rel), scope(not ''!!!), lineno}
    tree = ast.parse(code)
    # return ast.dump(tree, indent=4)
    r'''(add_api_route|add_api_websocket_route|add_websocket_route|add_route)\s*\('''
    for node in ast.walk(tree):
        value_node = None
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "add_api_route" or node.func.id == 'add_api_websocket_route':
                    if len(node.args) > 1:
                        value_node = node.args[1]
                    else:
                        for kw in node.keywords:
                            if kw.arg == "endpoint":
                                value_node = kw.value
                elif node.func.id == "add_websocket_route" or node.func.id == 'add_route':
                    if len(node.args) > 1:
                        value_node = node.args[1]
                    else:
                        for kw in node.keywords:
                            if kw.arg == "route":
                                value_node = kw.value             

        if value_node:
            if isinstance(value_node, ast.Attribute): # name in other file or under class def
                col = value_node.value.end_col_offset + 2  # get attr
                lineno = value_node.value.lineno
                entry = jedi_resolve(root, file_path_str, lineno, col)
                if entry:
                    entries.append(entry)                            
            elif isinstance(value_node, ast.Name): # plain function name
                col = value_node.end_col_offset
                lineno = value_node.lineno
                entry = jedi_resolve(root, file_path_str, lineno, col)
                if entry:
                    entries.append(entry)
                    
    return entries

def flask_find_by_call(root, rel_path):
    
    proj_root = Path(root)
    rel_path = Path(rel_path)
    file_path = proj_root / rel_path
    
    file_path_str = str(file_path.resolve())
    code = ""
    with open(file_path_str, encoding='utf-8') as f:
        code = f.read()
    
    entries = []    # {file_path(rel), scope(not ''!!!), lineno}
    tree = ast.parse(code)
    # return ast.dump(tree, indent=4)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # is this .add_url_rule?
            # is this .add_resource?
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "add_url_rule":
                    value_node = None
                    if len(node.args) > 2:
                        value_node = node.args[2]
                    else:
                        for kw in node.keywords:
                            if kw.arg == "view_func":
                                value_node = kw.value
                    if value_node:
                        if isinstance(value_node, ast.Attribute): # name in other file or under class def
                            col = value_node.value.end_col_offset + 2  # e.g., views.get
                            lineno = value_node.value.lineno
                            entry = jedi_resolve(root, file_path_str, lineno, col)
                            if entry:
                                entries.append(entry)                            
                        elif isinstance(value_node, ast.Name): # plain function name
                            col = value_node.end_col_offset
                            lineno = value_node.lineno
                            entry = jedi_resolve(root, file_path_str, lineno, col)
                            if entry:
                                entries.append(entry)
                        elif isinstance(value_node, ast.Call): # .as_view()
                            # as_view
                            if isinstance(value_node.func, ast.Attribute) and value_node.func.attr == "as_view":
                                # take content before .as_view as target
                                col = value_node.func.value.end_col_offset
                                lineno = value_node.func.value.lineno
                                entry = jedi_resolve(root, file_path_str, lineno, col)
                                if entry:
                                    entries.append(entry)
                                
                elif node.func.attr == "add_resource":
                    value_node = None
                    if len(node.args) > 0:
                        value_node = node.args[0]
                    if value_node:
                        if isinstance(value_node, ast.Attribute): # name in other file or under class def
                            col = value_node.value.end_col_offset + 2 # get attr
                            lineno = value_node.value.lineno
                            entry = jedi_resolve(root, file_path_str, lineno, col)
                            if entry:
                                entries.append(entry)                            
                        elif isinstance(value_node, ast.Name): # plain function name
                            col = value_node.end_col_offset
                            lineno = value_node.lineno
                            entry = jedi_resolve(root, file_path_str, lineno, col)
                            if entry:
                                entries.append(entry)
                        
    return entries
