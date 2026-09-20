
import sys, json, os, subprocess
sys.path.insert(0, r"D:\eda\agentic")
from spine import verify_manifest

mp = r"D:\eda\run1\manifest.json"
before = verify_manifest(mp)
print("1) fresh manifest      :", before)

# 篡改一个真实产物
rep = json.load(open(mp))
victim_path = None
for s in rep["stages"]:
    for r, v in s["hashes"].items():
        if isinstance(v, dict) and v.get("path","").endswith(".blif"):
            victim_path = v["path"]
if victim_path:
    with open(victim_path, "a") as f: f.write("# tampered\n")
    print("2) after touching", os.path.basename(victim_path), ":", verify_manifest(mp))
else:
    print("2) no blif artifact found in manifest")

# 篡改记录本身
m2 = json.load(open(mp))
m2["stages"][0]["ok"] = not m2["stages"][0]["ok"]
json.dump(m2, open(r"D:\eda\tampered.json","w"), indent=2)
print("3) after editing record:", verify_manifest(r"D:\eda\tampered.json", check_files=False))

# 截断尾巴
m3 = json.load(open(mp)); m3["stages"] = m3["stages"][:-1]
json.dump(m3, open(r"D:\eda\truncated.json","w"), indent=2)
print("4) after truncating    :", verify_manifest(r"D:\eda\truncated.json", check_files=False))
