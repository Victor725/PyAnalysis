import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pathlib import Path
from api.chat import *
from api.snapshot import *
import asyncio
import argparse


CASE_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\cases"
SNAPSHOT_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\snapshot.json"
KNOWLEDGE_PATH = "D:\\Research\\Project\\PyAnalysis\\PotentialType\\knowledge"


def ask_LLM_summary(case_file: Path, model = "gpt-4o", provider = "openai"):
    
    prompt = f"""You are an expert in security-oriented code analysis.
Summarize the following Python function or class at a high level of abstraction.

Guidelines:
Focus only on the overall purpose and behavior of the code.
If the input is a function, provide one concise summary of its overall role.
If the input is a class, provide a separate summary for each method, focusing on what it does.
Avoid mentioning variable names, parameter names, or implementation details.
The goal is to capture what it does, not how it does it.

Here is the code:

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

    parser = argparse.ArgumentParser(description="Build knowledge for potential type detection.")
    parser.add_argument("--rebuild", action="store_true", help="Whether to rebuild the knowledge base. Default is False.")
    args = parser.parse_args()

    if args.rebuild:
        if os.path.exists(SNAPSHOT_PATH):
            os.remove(SNAPSHOT_PATH)
    
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
        print(f"Processing {i+1}/{len(workset)}: {work} ...")
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