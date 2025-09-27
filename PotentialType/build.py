import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import json
from pathlib import Path
from api.chat import *
from api.snapshot import *
import asyncio


CASE_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\cases"
SNAPSHOT_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\snapshot.json"
KNOWLEDGE_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\knowledge"


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
        state = Snapshot.snapshot(CASE_PATH)
        # save_snapshot(state, SNAPSHOT_PATH)
        added = set(state.keys())
    else:
        state_to_save = Snapshot.load_snapshot(SNAPSHOT_PATH)
        state = Snapshot.snapshot(CASE_PATH)
        added, deleted, modified = Snapshot.diff_snapshots(state_to_save, state)
        
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
            Snapshot.save_snapshot(state_to_save, SNAPSHOT_PATH)


if __name__ == "__main__":
    main()