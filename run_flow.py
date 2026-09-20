
import sys, json
sys.path.insert(0, r"D:\eda\agentic")
from synth_search import build
f, r = build(r"D:\eda\flow\mult8.v", "mult8", r"D:\eda\run1")
print("stage:", r.stage, "ok:", r.ok, r.error[:200] if r.error else "")
if r.ok:
    rep = json.load(open(r"D:\eda\run1\\work\\search\\search.json"))
    print(f"proved {rep['proved']}/{rep['tried']}  area spread {rep['area_spread_pct']}%")
    print("best area :", rep["best_area"])
    print("best depth:", rep["best_depth"])
mp = f.save()
print("manifest:", mp)
from spine import verify_manifest
print("verifies:", verify_manifest(mp))
