"""光芯片链路演示：一条命令跑完 电路 -> 物理闸门 -> 版图。

    .venv-photonic\Scripts\python photonics_demo.py --dL 30

输出既是给人看的，也是给 CI 判的：任何一步不过，进程退出码非 0。
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dL", type=float, default=30.0, help="臂长差 (um)")
    ap.add_argument("--out", default=os.path.join("build", "photonic"), help="GDS 输出目录")
    ap.add_argument("--skip-layout", action="store_true", help="只跑电路级与闸门")
    a = ap.parse_args(argv)

    from photonic import mzi, check_mzi, co_design

    S, wl = mzi(dL_um=a.dL)
    o1 = np.abs(np.asarray(S[("in1", "out1")])) ** 2
    o2 = np.abs(np.asarray(S[("in1", "out2")])) ** 2
    print(f"MZI dL={a.dL}um  ({len(wl)} 点, {wl.min()*1000:.0f}-{wl.max()*1000:.0f} nm)")
    print(f"  out1 功率 均值 {o1.mean():.4f}  区间 [{o1.min():.4f}, {o1.max():.4f}]")
    print(f"  out2 功率 均值 {o2.mean():.4f}  区间 [{o2.min():.4f}, {o2.max():.4f}]")
    print(f"  能量守恒 max|P1+P2-1| = {np.abs(o1+o2-1).max():.2e}")
    print()

    v = check_mzi(dL_um=a.dL)
    print(v.lines())
    if not v.ok:
        return 1

    if a.skip_layout:
        return 0

    os.makedirs(a.out, exist_ok=True)
    r = co_design(dL_um=a.dL, out_dir=a.out)
    print()
    print(r.lines())
    return 0 if r.ok else 1


if __name__ == "__main__":
    sys.exit(main())
