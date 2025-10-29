import time
import docker
import os
import subprocess


class SASTWithDocker():
    def __init__(self):
        pass
    
    def put(self, container_id, source_path, target_path):    
        subprocess.run(['docker', 'cp', source_path, '%s:%s'%(container_id, target_path)])
    
    def get(self, container_id, source_path, target_path):
        subprocess.run(['docker', 'cp', '%s:%s'%(container_id, source_path), target_path])


class Codeql(SASTWithDocker):
    def __init__(self):
        super().__init__()
        client = docker.from_env()
        self.container = client.containers.run(
            detach=True,
            tty=True,
            mem_limit="60g",
            image="codeql:latest"
        )
    
    def __del__(self):
        self.container.stop()
        
    # target: abs_path to target
    # ql: str -- codeql rule
    def __call__(self, target, ql, out, db=None):
        
        if os.path.isfile(target):
            return self.ql_file(target, ql, out, db)
        elif os.path.isdir(target):
            return self.ql_dir(target, ql, out, db)


    def ql_file(self, target, ql, out, db=None):
        
        # create target folder
        self.container.exec_run(
                workdir="/",
                cmd='''/bin/bash -c "mkdir /target"''',
                tty=True
            )
        
        # copy target file
        self.put(self.container.id, target, "/target/")
        
        with open("./tmp.ql", "w") as f:
            f.write(ql)
        
        # copy ql file
        self.put(self.container.id, "./tmp.ql", "/findpath.ql")
        self.put(self.container.id, "./qlpack.yml", "/qlpack.yml")
        
        start_time = time.time()
        
        # create database   source_dir: /target   db_dir: /db
        self.container.exec_run(
            cmd='''/bin/bash -c "codeql database create --threads=0 -l python -s /target -- /db"''',
            tty=True
        )
        
        # perform test   result: /out.bqrs
        self.container.exec_run(
            cmd='''/bin/bash -c "codeql query run /findpath.ql --threads=0 --additional-packs=/codeql --output /out.bqrs --database /db"''',
            tty=True
        )
        
        # resolve result   result: /out.csv
        self.container.exec_run(
            cmd='''/bin/bash -c "codeql bqrs decode /out.bqrs --format=csv --output=/out.csv"''',
            tty=True
        )
        
        end_time = time.time()
        
        # download result and db from docker container
        self.get(self.container.id, "/out.csv", out)        
        
        if db:
            self.get(self.container.id, "/db", db)
        
        # remove /target, /findpath.ql, /out.csv, /out.bqrs, /db
        self.container.exec_run(
            cmd='''/bin/bash -c "rm -rf /target /findpath.ql /out.bqrs /out.csv /db"''',
            tty=True
        )
        os.remove("./tmp.ql")
        
        return end_time - start_time