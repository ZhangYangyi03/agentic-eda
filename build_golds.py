
import os, sys, json
sys.path.insert(0, r"D:\eda\agentic")
import synth_search as SS, bench_gen
srcs = bench_gen.emit(r"D:\eda\bench\src")
for name in ["arbiter16", "mult8", "adder32"]:
    root = rf"D:\eda\evolve\{name}"
    gold = os.path.join(root, "work", "elaborate", "gold.blif")
    if os.path.exists(gold):
        print(name, "exists", os.path.getsize(gold)); continue
    f, r = SS.build(srcs[name]["path"], name, root)
    print(name, "built ->", gold, os.path.exists(gold), "ok:", f.results[0].ok if f.results else None,
          "bytes:", os.path.getsize(gold) if os.path.exists(gold) else 0)
