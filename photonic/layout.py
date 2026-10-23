"""版图侧：把同一个设计变成 GDS。

电路级（models.py）给出频谱，版图级（这里）给出可流片的几何。
二者共用同一份参数（dL 等），参数对不上就是设计漂移——由 co_design 检查。
"""
from __future__ import annotations

import os

import numpy as np


def _gf():
    """延迟导入并激活 generic PDK。

    gdsfactory 在 Windows 上还需要 USERNAME（它内部调 getpass.getuser()，
    而 getpass 在 Python 3.11 的嵌入式环境下会去 import pwd，Windows 上没有）。
    """
    os.environ.setdefault("USERNAME", os.environ.get("USERNAME") or "china")
    import gdsfactory as gf
    try:
        gf.get_active_pdk()
    except Exception:
        gf.gpdk.PDK.activate()
    return gf


def mmi(**kw):
    gf = _gf()
    return gf.components.mmi2x2(**kw)


def mzi_layout(dL_um=30.0, **kw):
    """gdsfactory 的 MZI 单元（有源版图，仅作几何参考）。"""
    gf = _gf()
    return gf.components.mzi2x2_2x2(delta_length=float(dL_um), **kw)


def write_gds(component, path):
    """写出 GDS，返回 (path, 字节数)。"""
    component.write_gds(path)
    return path, os.path.getsize(path)


def ports_table(component):
    """端口表：(name, x, y, angle, width)。co_design 用它核对几何与电路端口是否一一对应。"""
    rows = []
    # gdsfactory 9 的 component.ports 是可迭代的 DPorts，不是 dict；宽/角要用 .width/.angle
    for port in component.ports:
        rows.append((port.name, float(port.center[0]), float(port.center[1]),
                     float(port.angle), float(port.width)))
    return rows
