
import json, os, sys
sys.path.insert(0, r"D:\eda\agentic")
import bench_gen, synth_search as SS
from spine import verify_manifest

srcs = bench_gen.emit(r"D:\eda\bench\src")
out = {}
for name in ["mult8", "adder16", "lfsr16"]:
    meta = srcs[name]
    for run in ("A", "B"):
        root = rf"D:\eda\determinism\{run}\{name}"
        f, r = SS.build(meta["path"], name, root)
        mp = f.save()
        ok, probs = verify_manifest(mp)
        out.setdefault(name, {})[run] = {
            "manifest": json.load(open(mp)),
            "netlist_hash": next((s["hashes"].get("netlist") for s in json.load(open(mp))["stages"]
                                  if "netlist" in s["hashes"]), None),
            "report_hash": next((s["hashes"].get("search_report") for s in json.load(open(mp))["stages"]
                                 if "search_report" in s["hashes"]), None),
            "manifest_ok": ok, "problems": probs, "stage_ok": [x.ok for x in f.results],
        }
for name, d in out.items():
    A, B = d["A"], d["B"]
    same_net = A["netlist_hash"] == B["netlist_hash"]
    repA = json.load(open(os.path.join(rf"D:\eda\determinism\A\{name}\work\search\search.json")))
    repB = json.load(open(os.path.join(rf"D:\eda\determinism\B\{name}\work\search\search.json")))
    same_area = [ (r["name"], r.get("and"), r.get("lev")) for r in repA["all"] ] == \
                [ (r["name"], r.get("and"), r.get("lev")) for r in repB["all"] ]
    print(f"{name:9s} stages={A['stage_ok']} manifestA={A['manifest_ok']} manifestB={B['manifest_ok']} "
          f"weights_identical={same_area} netlist_bytes_identical={same_net}")
    if not same_net:
        print("   A netlist:", A["netlist_hash"])
        print("   B netlist:", B["netlist_hash"])
    print("   best:", repA["best_area"], "| verifier:", repA["verifier"], "| gate:", repA["gate_selftest"][:52])
