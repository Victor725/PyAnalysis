import networkx as nx
from adalflow.core.types import Document
from api.data_pipeline import read_all_documents
from pathlib import Path
from importlab import environment, graph, fs
import sys
   

def build_graph(root:str, documents:list[Document]):
    
    path = fs.Path([fs.OSFileSystem(root)])
    env = environment.Environment(path, sys.version_info[0:2])
    g = graph.ImportGraph(env)
    
    base = Path(root)
    #g.add_file("./projs/import/mlflow/server/__init__.py")
    for document in documents:
        rel_path = Path(document.meta_data["file_path"])
        abs_path = (base / rel_path).resolve()
        g.add_file(str(abs_path))
    
    # treat strongly connected component as one node, we do not need
    # g.build()
    
    # delete lib nodes
    rm_nodes = []
    for node in g.graph.nodes():
        p = Path(node)
        if not p.is_relative_to(base) or not p.exists():
            rm_nodes.append(node)
    g.graph.remove_nodes_from(rm_nodes)
    return g.graph
    
    

if __name__ == "__main__":
    
    path = str(Path("./projs/import").resolve())
    documents = read_all_documents(path, code_extensions=[".py"])
    
    g = build_graph(path, documents)