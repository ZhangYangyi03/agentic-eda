
"""Three arms, equal budget, and the random arm is NOT handicapped.

The first version of the random arm sampled freely and produced only 1-4 valid
scripts out of 12, because it kept writing fx/mfs/renode after strash, which ABC
rejects. That is a real cost of not knowing the grammar, but it makes the
comparison "knows the grammar" vs "does not", not "chooses well" vs "chooses at
random". So there are two random arms:

  random_free   uniform over the whole syntax
  random_legal  uniform over the LEGAL syntax only, so it also yields ~12 valid
                candidates -- the fair test of whether the model's *choices* are
                better than chance

Both are scored by the same verifier, in the same units.
"""
import json, os, random, sys, time
sys.path.insert(0, r"D:\eda\agentic")
import synth_search as SS, bench_gen, evolve_search as EV, llm_agent as LA
from synth_search import best_by_metric

bench_gen.emit(r"D:\eda\bench\src")
tbl = json.load(open(r"D:\eda\bench\table.json"))
OUT = r"D:\eda\agent\experiment3.json"

def baseline_of(name):
    return dict(zip(("and","lev"), [p for p in tbl[name]["pareto"] if p[2]=="baseline"][0][:2]))

def _sample(rng):
    pre = [(nm, list(rng.choice(opts))) for nm, opts in
           (rng.choice(EV.LATE_PRIMS) for _ in range(rng.randint(0,2)))]
    post = [(nm, list(rng.choice(opts))) for nm, opts in
            (rng.choice(EV.PRIMS) for _ in range(rng.randint(2,5)))]
    return pre + [("strash",[])] + post

def arm_random(gold, wd, seq, model, n=12, seed=0, legal_only=False):
    rng = random.Random(seed); batch = {}
    for i in range(n):
        s, tries = _sample(rng), 0
        while legal_only and not EV._legal(s) and tries < 200:
            s = _sample(rng); tries += 1
        batch[f"r{i:02d}"] = EV.render(s)
    res = EV.evaluate(gold, wd, seq, model, batch, t=900)
    return [dict(v, script=k) for k, v in res.items()]

out = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"designs": {}}
out["note"] = ("canonical units only ('and'/AIG levels); 'aig' rows never ranked against them. "
               "random_legal is the fair arm; random_free measures the cost of not knowing the grammar.")

for name in ["prio32", "arbiter16", "mult8"]:
    gold = rf"D:\eda\evolve\{name}\work\elaborate\gold.blif"
    rc,o,e = SS.sh(f"grep -c '^.latch' {SS.to_wsl(gold)} || true")
    seq = int((o.strip().splitlines() or ["0"])[-1] or 0) > 0
    model = SS.model_name(gold); base = baseline_of(name)
    rec = out["designs"].setdefault(name, {})
    rec.update({"baseline": base, "hand_written": tbl[name]["best_area"], "seeds": rec.get("seeds", [])})
    done = {s["seed"] for s in rec["seeds"] if "random_legal" in s}
    print(f"\n=== {name}  baseline={base}  hand-written best={tbl[name]['best_area']['and']}  prior={sorted({s['seed'] for s in rec['seeds']})}", flush=True)
    for seed in range(3):
        if seed in done: continue
        t0=time.time()
        r = LA.run(name, gold, rf"D:\eda\agent\{name}_s{seed}", seq, model, base, steps=12, verbose=False)
        ba = r.get("best_area") or {}
        llm = {"area": ba.get("and") if ba.get("and") is not None else ba.get("area"),
               "depth": (r.get("best_depth") or {}).get("lev"),
               "ok": r["counts"]["ok"], "rej": r["counts"]["rejected"],
               "inv": r["counts"]["invalid_script"], "unm": r["counts"]["unmeasured"],
               "tok": r["tokens"]["prompt"]+r["tokens"]["completion"], "s": round(time.time()-t0,1),
               "script": ba.get("script"), "mapped_area": (r.get("mapped_best_area") or {}).get("area")}
        row = {"seed": seed, "llm": llm}
        for arm, legal in [("random_free", False), ("random_legal", True)]:
            t0=time.time()
            rows = arm_random(gold, rf"D:\eda\{arm}\{name}_s{seed}", seq, model, 12, seed=seed, legal_only=legal)
            okr=[x for x in rows if x.get("status")=="ok"]
            rb, rd = best_by_metric(okr,"area"), best_by_metric(okr,"lev")
            row[arm] = {"area": (rb["canonical"] or {}).get("and"),
                        "depth": (rd["canonical"] or {}).get("lev"),
                        "ok": len(okr), "inv": sum(1 for x in rows if x.get("status")=="invalid_script"),
                        "script": (rb["canonical"] or {}).get("script"),
                        "s": round(time.time()-t0,1)}
        rec["seeds"].append(row)
        print(f"  s{seed}: llm area={llm['area']:>4} tok={llm['tok']:>6} ok={llm['ok']:>2} inv={llm['inv']:>2} {llm['s']:>5}s  |"
              f"  rnd_free area={row['random_free']['area']} ok={row['random_free']['ok']:>2}  |"
              f"  rnd_legal area={row['random_legal']['area']} ok={row['random_legal']['ok']:>2}  {row['random_legal']['s']}s", flush=True)
        json.dump(out, open(OUT,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
    # seeds from an earlier arm layout have no random_legal; keep the newest row
    # per seed index and require all three arms, so the summary never compares
    # across two different experiment designs
    newest = {}
    for s in rec["seeds"]:
        if "random_legal" in s and "random_free" in s:
            newest[s["seed"]] = s
    rec["seeds"] = [newest[k] for k in sorted(newest)]
    S = rec["seeds"]
    if not S:
        print("  (no complete seeds yet)"); continue
    def med(k, arm="area"):
        v = [s[k][arm] for s in S if s.get(k,{}).get(arm) is not None]
        return sorted(v)[len(v)//2] if v else None
    rec["summary"] = {
        "llm_area_median": med("llm"), "random_free_area_median": med("random_free"),
        "random_legal_area_median": med("random_legal"),
        "llm_vs_legal": {"llm_wins": sum(1 for s in S if s["llm"]["area"] is not None and s["random_legal"]["area"] is not None and s["llm"]["area"] < s["random_legal"]["area"]),
                         "legal_wins": sum(1 for s in S if s["llm"]["area"] is not None and s["random_legal"]["area"] is not None and s["random_legal"]["area"] < s["llm"]["area"]),
                         "ties": sum(1 for s in S if s["llm"]["area"] == s["random_legal"]["area"])},
        "llm_vs_free": {"llm_wins": sum(1 for s in S if s["llm"]["area"] is not None and s["random_free"]["area"] is not None and s["llm"]["area"] < s["random_free"]["area"]),
                        "free_wins": sum(1 for s in S if s["llm"]["area"] is not None and s["random_free"]["area"] is not None and s["random_free"]["area"] < s["llm"]["area"]),
                        "ties": sum(1 for s in S if s["llm"]["area"] == s["random_free"]["area"])},
        "llm_tokens": sum(s["llm"]["tok"] for s in S),
        "llm_seconds": sum(s["llm"]["s"] for s in S),
        "random_seconds": sum(s["random_legal"]["s"] for s in S),
        "beat_hand_written": sum(1 for s in S if s["llm"]["area"] is not None and s["llm"]["area"] < tbl[name]["best_area"]["and"])}
    json.dump(out, open(OUT,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
    print("  summary:", json.dumps(rec["summary"], ensure_ascii=False), flush=True)

print("\nwrote", OUT)
