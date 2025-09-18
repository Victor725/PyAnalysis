from importlab import environment, graph, fs
import sys

path = fs.Path([fs.OSFileSystem("./projs/import")])
env = environment.Environment(path, sys.version_info[0:2])
g = graph.ImportGraph(env)
g.add_file("./projs/import/mlflow/server/__init__.py")
g.build()
g