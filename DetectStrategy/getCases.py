import pandas as pd
import json
from pathlib import Path
from Codeql import Codeql

CASE_CSV_PATH = "D:\\Research\\Project\\PyAnalysis\\DetectStrategy\\cases.csv"
Synthetic_Dataset = "G:\\SASTcomparison\\SyntheticDataset"
codeql = None

ql_template = '''/**
 * @name Find entry-to-sink paths
 * @description Finds possible call paths between entry and sink functions.
 * @kind diagnostic
 * @id python/findpath
 * @tags experimental
 */

import python


predicate isEntry(Function f) {{
  f.getName() = "{entry_func}" and
  f.getLocation().getFile().getRelativePath() = "{entry_relpath}"
}}


predicate isSink(Function f) {{
  f.getName() = "{vul_func}" and
  f.getLocation().getFile().getRelativePath() = "{vul_relpath}"
}}


predicate calls(Function caller, Function callee) {{
    caller.getFunctionObject().getACallee() = callee.getFunctionObject()
}}


private string callPath(Function src, Function dst, int depth) {{
  // Base case: src calls dst
  // <rel_path>:start-end -> <rel_path>:start-end
  result = src.getLocation().getFile().getRelativePath() + ":" + 
          src.getLocation().getStartLine() + " -> " +
          dst.getLocation().getFile().getRelativePath() + ":" + 
          dst.getLocation().getStartLine()
  and calls(src, dst) and depth = 1
  or
  // Recursive case: src calls mid, mid reaches dst
  exists(Function mid, int d |
    calls(src, mid) and
    result = src.getLocation().getFile().getRelativePath() + ":" + 
          src.getLocation().getStartLine() + " -> " + callPath(mid, dst, d) and depth = d+1 and depth < 10
  )
}}


from Function entry, Function sink, string path, int d
where 
    isEntry(entry) and 
    isSink(sink) and 
    path = callPath(entry, sink, d)
select entry.getName(), sink.getName(), path'''


def parse_path(result_csv):
    path = ""
    
    result = pd.read_csv(result_csv, names = ['1', '2', '3'])
    
    for index, row in result.iterrows():
        path = row['3']
        break
    
    
    return path


# return path
# <rel_path>:startLine -> ... -> <rel_path>:startLine
def get_from_synthetic(case_name, entry, vul_loc):
    item_root = Path(Synthetic_Dataset)
    
    cwe = case_name[:case_name.find("_DS")]
    suffix = "_vul.py"
    abs_path = item_root / cwe / (case_name+suffix)
    
    ql = ql_template.format(
        entry_func = entry,
        entry_relpath = case_name+suffix,
        vul_func = vul_loc,
        vul_relpath = case_name+suffix
    )
    
    out = "./out.csv"
    codeql(abs_path, ql, out)
    
    return parse_path(out)


def main():
    # get EntryPoint, TrigerLocation from cases.csv
    case_df = pd.read_csv(CASE_CSV_PATH)
    
    global codeql
    codeql = Codeql()
    
    for index, row in case_df.iterrows():
        cvelnk = row["Vul"]
        
        # test path extraction
        if cvelnk != "94_DS-3":
            continue

        entry = row["EntryPoint"]
        vul_loc = row["VulLocation"]
        
        call_path = get_from_synthetic(cvelnk, entry, vul_loc)
        print(call_path)


if __name__ == "__main__":
    main()