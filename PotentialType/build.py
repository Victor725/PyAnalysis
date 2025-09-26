import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import json
from pathlib import Path
from api.chat import *
import asyncio


CASE_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\cases"
SNAPSHOT_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\snapshot.json"
KNOWLEDGE_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\knowledge"


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


def ask_LLM_summary(case_file: Path, model = "gpt-4o", provider = "openai"):
    
    prompt = f"""You are an expert security-oriented code analyst.
Given the following Python function/class definition, analyze and summarize its behavior.

Your summary must include:
User Input Sources: Does the function take any input that could originate from the user (e.g., HTTP request parameters, command-line arguments, environment variables, file contents)? If yes, specify how.
Main Functionality: Provide a concise but clear description of the function's core purpose and logic.
Outputs / Return Values: What kind of data does it return or produce (e.g., HTML page, JSON object, file, plain text, system command output)?

Format your answer in a structured way, like:
User Input Sources: …
Main Functionality: …
Outputs / Return Values: …

If given a class, you can return multi groups of User Input Sources, Main Functionality, and Outputs / Return Values for every methods

CRITICAL:
You NEVER start responses with markdown headers or code fences.
IMPORTANT: Generate all the content in English.

Here is the function/class:

{case_file.read_text(encoding="utf-8")}

"""
    
    request_data = {
        "provider": provider,
        "model": model,
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ]
    }

    return asyncio.run(AskLLM_raw(request_data))


def main():
    # check snapshot
    added = set()
    deleted = set()
    modified = set()
    state = {}
    state_to_save = {}
    if not os.path.exists(SNAPSHOT_PATH):
        state = snapshot(CASE_PATH)
        # TODO: save when finished writing knowledge
        # save_snapshot(state, SNAPSHOT_PATH)
        added = set(state.keys())
    else:
        state_to_save = load_snapshot(SNAPSHOT_PATH)
        state = snapshot(CASE_PATH)
        added, deleted, modified = diff_snapshots(state_to_save, state)
        
    if len(deleted) > 0:
        for d in deleted:
            knowledge_file: Path = Path(KNOWLEDGE_PATH) / d
            knowledge_file.unlink()
            
    workset = set()
    if len(added) > 0 or len(modified) > 0:
        workset = added | modified

    for i, work in enumerate(workset):
        # ask LLM to genrate summary for case
        case_file: Path = Path(CASE_PATH) / work
        summary = None
        while True:
            try:
                summary = ask_LLM_summary(case_file)
                if summary != None:
                    break
            except:
                continue
        # put the summary to knowledge
        case_name = work.split(".")[0] + ".txt"
        knowledge_file: Path = Path(KNOWLEDGE_PATH) / case_name
        knowledge_file.write_text(summary, encoding="utf-8")

        state_to_save[work] = state[work]
        
        if i != 0 and i % 20 == 0:
            save_snapshot(state_to_save, SNAPSHOT_PATH)


if __name__ == "__main__":
    main()