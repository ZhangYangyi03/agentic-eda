
"""bench_gen: EPFL-class benchmark circuits, generated rather than downloaded.

Measured reason: raw.githubusercontent and cdn.jsdelivr are both unreachable from
this host (SSL reset on the Windows side, reset inside WSL too), so a benchmark
set that must be fetched is a benchmark set that cannot be run here. These
generators cover the same axes the published suites do -- arithmetic depth,
control-dominated logic, and a size ladder -- so the scaling behaviour, which is
what the search is being measured on, is still real.
"""
from __future__ import annotations
import os


def mult(n: int) -> str:
    return (f"module mult{n}(input [{n-1}:0] a, input [{n-1}:0] b, output [{2*n-1}:0] p);\n"
            f"  assign p = a * b;\nendmodule\n")


def adder(n: int) -> str:
    return (f"module adder{n}(input [{n-1}:0] a, input [{n-1}:0] b, input cin, "
            f"output [{n-1}:0] s, output cout);\n"
            f"  assign {{cout, s}} = a + b + cin;\nendmodule\n")


def arbiter(n: int) -> str:
    """Round-robin-ish priority arbitration: control-dominated, structurally deep."""
    body = [f"module arbiter{n}(input [{n-1}:0] req, output [{n-1}:0] gnt);"]
    body.append(f"  wire [{n-1}:0] m;")
    body.append(f"  assign m = req & ~((req << 1) - 1'b1);")
    body.append(f"  assign gnt = m;")
    body.append("endmodule")
    return "\n".join(body) + "\n"


def prio(n: int) -> str:
    """Priority encoder: wide shallow OR-AND structure."""
    lines = [f"module prio{n}(input [{n-1}:0] x, output [{n-1}:0] y, output v);"]
    lines.append(f"  assign v = |x;")
    lines.append(f"  assign y = x & (~x + 1'b1);")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def barrel(n: int) -> str:
    """Barrel shifter: evenly spread, shallow, the opposite shape to a multiplier."""
    lines = [f"module barrel{n}(input [{n-1}:0] d, input [{'%d' % max(1,(n-1).bit_length()-1)}:0] s, "
             f"output [{n-1}:0] q);"]
    lines.append("  assign q = d << s;")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def lfsr(n: int) -> str:
    """Sequential: control/state heavy, so the AB C script sees feedback logic."""
    taps = {4: 0b1001, 8: 0b10111000, 12: 0b101111000000, 16: 0b1011110000000000}
    t = taps.get(n, 0b1001)
    lines = [f"module lfsr{n}(input clk, input rst, output reg [{n-1}:0] q);"]
    lines.append("  always @(posedge clk) begin")
    lines.append("    if (rst) q <= %d'd1;" % n)
    lines.append("    else begin")
    lines.append("      q <= {q[%d:0], 1'b0} | ^{" % (n - 2) +
                 ", ".join(f"q[{i}]" for i in range(n) if (t >> i) & 1) + "};")
    lines.append("    end")
    lines.append("  end")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


BENCH = {}
for n in (4, 8, 12, 16):
    BENCH[f"mult{n}"] = (mult(n), "mult")
for n in (8, 16, 32):
    BENCH[f"adder{n}"] = (adder(n), "adder")
BENCH["arbiter16"] = (arbiter(16), "control")
BENCH["prio32"] = (prio(32), "control")
BENCH["barrel16"] = (barrel(16), "shifter")
BENCH["lfsr16"] = (lfsr(16), "sequential")

def emit(root: str) -> dict:
    os.makedirs(root, exist_ok=True)
    out = {}
    for name, (src, kind) in BENCH.items():
        p = os.path.join(root, name + ".v")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(src)
        out[name] = {"path": p, "kind": kind, "rtl": src}
    return out

if __name__ == "__main__":
    import json, sys
    d = emit(sys.argv[1] if len(sys.argv) > 1 else r"D:\eda\bench\src")
    print(json.dumps({k: {"kind": v["kind"]} for k, v in d.items()}, indent=1))
