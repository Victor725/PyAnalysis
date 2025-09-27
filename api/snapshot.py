import json
from pathlib import Path
import os


class Snapshot:
    
    def snapshot(dir_path):
        state = {}
        target_path = Path(dir_path)
        
        for f in target_path.rglob("*"):
            if f.is_dir():
                continue
            stat = f.stat()
            state[str(f.relative_to(target_path))] = stat.st_mtime
            
        return state

    def save_snapshot(state, filename="./snapshot.json"):
        with open(filename, "w") as f:
            json.dump(state, f)

    def load_snapshot(filename="./snapshot.json"):
        if not os.path.exists(filename):
            return {}
        with open(filename) as f:
            return json.load(f)

    def diff_snapshots(old, new):
        old_files = set(old.keys())
        new_files = set(new.keys())

        added = new_files - old_files
        deleted = old_files - new_files
        modified = {f for f in old_files & new_files if old[f] != new[f]}

        return added, deleted, modified
    
    
    
class RAGSnapshot(Snapshot):
    
    def snapshot(dir_path):
        state = {}
        target_path = Path(dir_path)
        
        for f in target_path.rglob("*"):
            if f.is_dir():
                continue
            stat = f.stat()
            state[str(f.relative_to(target_path))] = {"mtime": stat.st_mtime}
        return state
    

    def diff_snapshots(old, new):
        old_files = set(old.keys())
        new_files = set(new.keys())

        added = new_files - old_files
        deleted = old_files - new_files
        modified = {f for f in old_files & new_files if old[f]['mtime'] != new[f]['mtime']}

        return added, deleted, modified