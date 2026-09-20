
import json, os, sys, time
sys.path.insert(0, r"D:\eda\agentic")
import bench_gen, evolve_search as EV, synth_search as SS
from spine import verify_manifest

srcs = bench_gen.emit(r"D:\eda\bench\src")
out = {}
for name in ["mult8", "adder32", "prio32", "barrel16", "lfsr16"]:
    t0 = time.time()
    meta = srcs[name]
    root = rf"D:\eda\evolve\{name}"
    f, r = SS.build(meta["path"], name, root)     # spine: elaborate + fixed-set search
    if not f.results[0].ok:
        print(name, "elaborate failed"); continue
    gold = os.path.join(root, "work", "elaborate", "gold.blif")
    import subprocess as sp
    rc, o, e = SS.sh(f"grep -c '^.latch' {SS.to_wsl(gold)} || true")
    seq = int((o.strip().splitlines() or ["0"])[-1] or 0) > 0
    model = SS.model_name(gold)
    print(f"{name}: sequential={seq}")
    res = EV.run(gold, os.path.join(root, "work", "evolve"), seq, model,
                 pop=12, gens=8, seed=7)
    # 和手写策略集比
    fixed = json.load(open(os.path.join(root, "work", "search", "search.json")))
    res["fixed_best_area"] = fixed["best_area"]
    res["fixed_best_depth"] = fixed["best_depth"]
    res["evolve_beats_fixed_area"] = (res.get("best_area", {}).get("and", 1e9)
                                      < fixed["best_area"]["and"])
    res["evolve_beats_fixed_depth"] = (res.get("best_depth", {}).get("lev", 1e9)
                                       < fixed["best_depth"]["lev"])
    res["seconds"] = round(time.time() - t0, 1)
    out[name] = res
    print(f"  fixed: {fixed['best_area']['and']}/{fixed['best_depth']['lev']}   "
          f"evolved: {res['best_area']['and']}/{res['best_depth']['lev']}  "
          f"area_win={res['evolve_beats_fixed_area']} depth_win={res['evolve_beats_fixed_depth']}  "
          f"counts={res['status_counts']}  {res['seconds']}s", flush=True)
json.dump(out, open(r"D:\eda\evolve\results.json", "w"), indent=2)
print("\nwrote D:\\eda\\evolve\\results.json")
