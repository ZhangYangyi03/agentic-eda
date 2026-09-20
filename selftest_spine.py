
import sys, os, subprocess, json
sys.path.insert(0, r"D:\eda\agentic")
from spine import Flow, Stage, verify_manifest

def s_write(inp, wd):
    p = os.path.join(wd, "counter.v")
    open(p,"w").write("""module counter(input clk, input rst, output reg [7:0] q);
  always @(posedge clk) if (rst) q <= 0; else q <= q + 1;
endmodule
""")
    return {"rtl": p}

def s_hashish(inp, wd):
    # 用系统可用工具做一次真变换, 证明 stage 契约成立
    out = os.path.join(wd, "copy.v")
    with open(inp["rtl"], encoding="utf-8") as f, open(out,"w",encoding="utf-8") as g:
        g.write(f.read())
    return {"rtl_copy": out}

def s_linecount(inp, wd):
    n = sum(1 for _ in open(inp["rtl_copy"], encoding="utf-8"))
    p = os.path.join(wd, "count.json")
    json.dump({"lines": n}, open(p,"w"))
    return {"stats": p}

f = Flow(r"D:\eda\selftest")
f.note_env("python", sys.version.split()[0])
r1 = f.run(Stage("emit_rtl", s_write, (), ("rtl",), tool="python"))
r2 = f.run(Stage("copy", s_hashish, ("rtl",), ("rtl_copy",), tool="python"))
r3 = f.run(Stage("stats", s_linecount, ("rtl_copy",), ("stats",), tool="python"))
for r in (r1,r2,r3):
    print(f"{r.stage:10s} ok={r.ok} {r.seconds}s {list(r.hashes)} {r.error}")
mp = f.save()
ok, probs = verify_manifest(mp)
print("manifest verifies:", ok, probs)

# 负面用例1: 声明了输出却不产出 -> 必须被拒
def s_lying(inp, wd):
    return {"rtl": inp["rtl"]}
bad = f.run(Stage("lying", s_lying, ("rtl",), ("nonexistent","gds"), tool="python"))
print("lying stage rejected:", not bad.ok, "|", bad.error)

# 负面用例2: 产出未声明的输出 -> 必须被拒
def s_extra(inp, wd):
    p = os.path.join(wd,"secret.txt"); open(p,"w").write("x")
    return {"rtl": inp["rtl"], "secret": p}
bad2 = f.run(Stage("extra", s_extra, ("rtl",), ("rtl",), tool="python"))
print("undeclared output rejected:", not bad2.ok, "|", bad2.error)

# 负面用例3: 篡改产物字节 -> verify 必须发现
m = json.load(open(mp))
tgt = r"D:\eda\selftest\work\copy\copy.v"
open(tgt,"a").write("// tampered\n")
m2 = json.load(open(mp))
print("manifest fields:", list(m2.keys()), "| head:", m2["head"][:16])
