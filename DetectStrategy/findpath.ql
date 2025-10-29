/**
 * @name Find entry-to-sink paths
 * @description Finds possible call paths between entry and sink functions.
 * @kind diagnostic
 * @id python/findpath
 * @tags experimental
 */

import python


predicate isEntry(Function f) {
  f.getName() = "resolve_glyphs" and
  f.getLocation().getFile().getRelativePath() = "src/calibre/utils/fonts/sfnt/subset.py"
}


predicate isSink(Function f) {
  f.getName() = "itervalues" and
  f.getLocation().getFile().getRelativePath() = "src/polyglot/builtins.py"
}


predicate calls(Function caller, Function callee) {
    caller.getFunctionObject().getACallee() = callee.getFunctionObject()
}


private string callPath(Function src, Function dst, int depth) {
  // Base case：src 直接调用 dst
  //result = src.getName() + " → " + dst.getName()
  // <rel_path>:start-end -> <rel_path>:start-end
  result = src.getLocation().getFile().getRelativePath() + ":" + 
          src.getLocation().getStartLine() + " -> " +
          dst.getLocation().getFile().getRelativePath() + ":" + 
          dst.getLocation().getStartLine()
  and calls(src, dst) and depth = 1
  or
  // Recursive case：src 调用中间函数 mid，mid 最终能到达 dst
  exists(Function mid, int d |
    calls(src, mid) and
    result = src.getLocation().getFile().getRelativePath() + ":" + 
          src.getLocation().getStartLine() + " -> " + callPath(mid, dst, d) and depth = d+1 and depth < 10
  )
}


from Function entry, Function sink, string path, int d
where 
    isEntry(entry) and 
    isSink(sink) and 
    path = callPath(entry, sink, d)
select entry.getName(), sink.getName(), path


// from Function entry, Function sink, string path, int d
// where 
//     entry.getName() = "resolve_glyphs" and
//     entry.getLocation().getFile().getRelativePath() = "src/calibre/utils/fonts/sfnt/subset.py" and
//     sink.getName() = "itervalues" and
//     sink.getLocation().getFile().getRelativePath() = "src/polyglot/builtins.py" and
//     path = callPath(entry, sink, d)
// select entry, sink, path


// from Function f
// where 
//     f.getName().charAt(0) != "_" and
//     f.getLocation().getFile().getRelativePath() = "src/calibre/utils/fonts/sfnt/subset.py"
// select 
//     f, 
//     f.getName(), 
//     f.getLocation().getFile().getRelativePath()


// from Call c
// where 
//     c.getLocation().getFile().getRelativePath() = "src/calibre/utils/fonts/sfnt/subset.py"
// select 
//     c,
//     c.getFunc(),
//     c.getScope()


// from Function f, Call c, Function callee
// where 
//     c.getScope() = f and
//     c.getFunc()

//     f.getName().charAt(0) != "_" and
//     f.getLocation().getFile().getRelativePath() = "src/calibre/utils/fonts/sfnt/subset.py"
// select 
//     f, 
//     f.getFunctionObject().getACallee(),
//     f.getFunctionObject().getACallee().getFunction()
    // f.getName(), 
    // f.getLocation().getFile().getRelativePath()