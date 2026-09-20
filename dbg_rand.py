
import json, os, sys, traceback, random
sys.path.insert(0, r"D:\eda\agentic")
import synth_search as SS, bench_gen, evolve_search as EV
from synth_search import best_by_metric
gold = r"D:\eda\evolve\prio32\work\elaborate\gold.blif"
model = SS.model_name(gold)
rng = random.Random(0)
batch = {}
for i in range(12):
    pre = [(nm, list(rng.choice(opts))) for nm, opts in
           (rng.choice(EV.LATE_PRIMS) for _ in range(rng.randint(0,2)))]
    post = [(nm, list(rng.choice(opts))) for nm, opts in
            (rng.choice(EV.PRIMS) for _ in range(rng.randint(2,5)))]
    steps = pre + [("strash",[])] + post
    batch[f"r{i:02d}"] = EV.render(steps)
print("sample scripts:")
for k,v in list(batch.items())[:4]: print("  ", k, v)
try:
    res = EV.evaluate(gold, r"D:\eda\random\dbg", False, model, batch, t=900)
    rows=[dict(v,script=k) for k,v in res.items()]
    from collections import Counter
    print("status:", Counter(x.get("status") for x in rows))
    ok=[x for x in rows if x.get("status")=="ok"]
    print("best_by_metric area:", json.dumps(best_by_metric(ok,"area").get("canonical"), ensure_ascii=False)[:200])
    print("best_by_metric lev :", json.dumps(best_by_metric(ok,"lev").get("canonical"), ensure_ascii=False)[:200])
except Exception:
    traceback.print_exc()
