"""协同设计：电路级与版图级必须共用同一份参数。

这是"AI 辅助 EDA"里 AI 最容易出错的地方——它可以同时生成两套自洽但彼此
不一致的描述。co_design 把这种漂移变成一条可判定的失败，而不是靠人盯。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

import numpy as np


@dataclass
class CoDesignResult:
    ok: bool
    circuit: dict
    layout: dict
    problems: list = field(default_factory=list)

    def lines(self):
        out = ["CO-DESIGN: " + ("CONSISTENT" if self.ok else "DRIFT")]
        out.append(f"  circuit: dL={self.circuit.get('dL_um')}um ports={self.circuit.get('ports')}")
        out.append(f"  layout : dL={self.layout.get('dL_um')}um ports={self.layout.get('ports')} gds={self.layout.get('gds_bytes')}B")
        for p in self.problems:
            out.append("  FAIL " + p)
        return "\n".join(out)


def co_design(dL_um=30.0, wl=None, out_dir=".", write=True):
    """跑电路级 + 版图级，并检查二者参数与端口一致。"""
    from .models import mzi, WL_DEFAULT
    from . import layout as lay

    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    S, wl = mzi(dL_um=dL_um, wl=wl)
    circ = {
        "dL_um": float(dL_um),
        "ports": sorted({p for k in S for p in k}),
        "wl_nm": [float(wl.min() * 1000), float(wl.max() * 1000)],
        "n_points": int(len(wl)),
    }

    comp = lay.mzi_layout(dL_um=dL_um)
    ports = lay.ports_table(comp)
    gds_bytes = 0
    gds_path = None
    if write:
        gds_path = os.path.join(out_dir, f"mzi_dL{int(dL_um)}.gds")
        _, gds_bytes = lay.write_gds(comp, gds_path)
    # gdsfactory 的 mzi2x2_2x2 端口名是 o1..o4；不带 . 的名字是结构和标签，
    # 真正的光口是 o 开头的这四个（带 . 的是金属/焊盘图层）。
    opt = [p[0] for p in ports if p[0].startswith("o") and not p[0].startswith("o.")]
    layr = {"dL_um": float(dL_um), "ports": sorted(opt),
            "gds_bytes": gds_bytes, "gds_path": gds_path,
            "n_optical_ports": len(opt)}

    problems = []
    # 1. 参数一致：版图里的 delta_length 必须就是电路里的 dL
    got_dl = None
    try:
        got_dl = float(comp.settings.delta_length)
    except Exception:
        try:
            got_dl = float(comp.settings["delta_length"])
        except Exception:
            got_dl = None
    if got_dl is None:
        problems.append("layout component does not expose delta_length; cannot verify")
    elif abs(got_dl - float(dL_um)) > 1e-9:
        problems.append(f"delta_length drift: layout={got_dl} circuit={dL_um}")
    # 2. 端口数一致：电路 4 口，版图光口也必须 4 个
    if len(circ["ports"]) != 4:
        problems.append(f"circuit exposes {len(circ['ports'])} ports, expected 4")
    if len(opt) != 4:
        problems.append(f"layout exposes {len(opt)} optical ports, expected 4")
    # 3. GDS 真的落盘了
    if write and gds_bytes < 100:
        problems.append(f"GDS too small ({gds_bytes} B) — layout did not really write")

    return CoDesignResult(ok=not problems, circuit=circ, layout=layr, problems=problems)
