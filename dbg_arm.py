
import json, os, sys, traceback
sys.path.insert(0, r"D:\eda\agentic")
import synth_search as SS, bench_gen, evolve_search as EV, llm_agent as LA
from synth_search import best_by_metric
srcs = bench_gen.emit(r"D:\eda\bench\src")
tbl = json.load(open(r"D:\eda\bench\table.json"))
name="prio32"
base = dict(zip(("and","lev"), [p for p in tbl[name]["pareto"] if p[2]=="baseline"][0][:2]))
gold = rf"D:\eda\evolve\{name}\work\elaborate\gold.blif"
model = SS.model_name(gold)
try:
    r = LA.run(name, gold, r"D:\eda\agent\dbg", False, model, base, steps=3, verbose=False)
    print("LLM arm OK:", json.dumps({k:v for k,v in r.items() if k!="transcript"}, ensure_ascii=False)[:400])
    print("best_area:", json.dumps(r.get("best_area"), ensure_ascii=False)[:200])
    print("best_depth:", json.dumps(r.get("best_depth"), ensure_ascii=False)[:200])
    print("mapped:", r.get("mapped_best_area"), r.get("mapped_best_depth"))
    print("units:", r.get("units"))
except Exception:
    traceback.print_exc()
