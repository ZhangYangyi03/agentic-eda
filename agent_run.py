
import json, os, sys, time
sys.path.insert(0, r"D:\eda\agentic")
import synth_search as SS, bench_gen, llm_agent as LA
srcs = bench_gen.emit(r"D:\eda\bench\src")
name = "prio32"
meta = srcs[name]
root = rf"D:\eda\evolve\{name}"
gold = os.path.join(root, "work", "elaborate", "gold.blif")
print("gold exists:", os.path.exists(gold))
rc,o,e = SS.sh(f"grep -c '^.latch' {SS.to_wsl(gold)} || true")
seq = int((o.strip().splitlines() or ["0"])[-1] or 0) > 0
model = SS.model_name(gold)
tbl = json.load(open(r"D:\eda\bench\table.json"))[name]
base = dict(zip(("and","lev"), [p for p in tbl["pareto"] if p[2]=="baseline"][0][:2]))
print("baseline:", base)
res = LA.run(name, gold, rf"D:\eda\agent\{name}", seq, model, base, steps=10)
print("\n--- 结果 ---")
print("attempts:", res["attempts"], "ok:", res["counts"], "tokens:", res["tokens"], f"{res['seconds']}s")
print("baseline:", base, "-> best_area:", res.get("best_area",{}).get("area"),
      "best_depth:", res.get("best_depth",{}).get("lev"))
print("beats baseline: area", res.get("beats_baseline_area"), "depth", res.get("beats_baseline_depth"))
