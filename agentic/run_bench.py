
"""Run the agentic-EDA flow over the generated benchmark set.

The point of the set is shape coverage, not size: a strategy win on an 8x8
multiplier is not evidence of a win on a barrel shifter or an LFSR. Three of the
eleven are sequential, which matters because the verifier itself changes there --
ABC cec does not apply to a sequential netlist, so those runs go through yosys
equiv_induct and the self-test exercises that path instead.
"""
import json, os, sys, time
sys.path.insert(0, r"D:\eda\agentic")
import bench_gen
from spine import verify_manifest
import synth_search as SS

ROOT = r"D:\eda\bench\run"
SRC = r"D:\eda\bench\src"

def main():
    srcs = bench_gen.emit(SRC)
    table = {}
    for name, meta in srcs.items():
        t0 = time.time()
        root = os.path.join(ROOT, name)
        f, r = SS.build(meta["path"], name, root)
        mp = f.save()
        ok, probs = verify_manifest(mp)
        rec = {"kind": meta["kind"], "stages": [(x.stage, x.ok) for x in f.results],
               "manifest_ok": ok, "manifest_problems": probs}
        srep = os.path.join(root, "work", "search", "search.json")
        if os.path.exists(srep):
            rep = json.load(open(srep))
            rec.update({"proved": rep["proved"], "tried": rep["tried"],
                        "counts": rep["counts"], "verifier": rep["verifier"],
                        "gate_selftest": rep["gate_selftest"],
                        "best_area": rep["best_area"], "best_depth": rep["best_depth"],
                        "area_spread_pct": rep["area_spread_pct"],
                        "depth_spread_pct": rep["depth_spread_pct"],
                        "pareto": rep["pareto"]})
            print(f"{name:10s} {meta['kind']:10s} proved={rep['proved']:>2d}/{rep['tried']:<2d} "
                  f"area={rep['best_area']['and']:>5d}(-{rep['area_spread_pct']:>4.1f}%) "
                  f"lev={rep['best_depth']['lev']:>3d}(-{rep['depth_spread_pct']:>4.1f}%) "
                  f"[{rep['verifier']:18s}] gate={'rejected' in rep['gate_selftest']} "
                  f"manifest={ok} {time.time()-t0:>5.0f}s", flush=True)
        else:
            rec["error"] = r.error if r else "no stage result"
            print(f"{name:10s} {meta['kind']:10s} FAILED: {rec['error'][:100]}", flush=True)
        table[name] = rec
    json.dump(table, open(r"D:\eda\bench\table.json", "w"), indent=2)
    print("\nwrote D:\\eda\\bench\\table.json")

if __name__ == "__main__":
    main()
