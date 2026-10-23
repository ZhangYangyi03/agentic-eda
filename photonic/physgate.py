"""物理闸门（phys-gate）：与电子侧等价性证明同一个角色。

判据只有一条硬规则：**一个设计在没通过独立参考之前，不算设计**。
每一条都是可判定的（有具体数值、有容差），不接受"看起来对"。

四条检查，任何一条不过 => rejected，且给出是哪条、差多少：
  1. 幺正性 —— 无源无损网络的 S 矩阵必须满足 S^H S = I（能量守恒）。
  2. 参考对拍 —— 与解析解在同一波长网格上逐点比，误差有上限。
  3. 因果性 —— 相位对波长求导必须为负（群延迟 dphi/domega > 0）。
  4. 端口完备 —— 每条外部端口都要有非零能量通路，没有悬空口。

用法：
    from photonic import check_mzi
    v = check_mzi(dL_um=30.0)
    print(v.ok, v.lines())
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

TOL_UNITARY = 1e-6      # S^H S 与 I 的最大偏差
TOL_REFERENCE = 1e-6    # 与解析解的最大复振幅偏差
TOL_ENERGY = 1e-6       # 单端口注入时 total power 与 1 的偏差
TOL_PHASE = 1e-9        # 群延迟符号的判定余量


@dataclass
class Verdict:
    ok: bool
    checks: list = field(default_factory=list)   # [(name, passed, detail)]

    def lines(self):
        out = ["VERDICT: " + ("ACCEPTED" if self.ok else "REJECTED")]
        for name, passed, detail in self.checks:
            out.append(f"  [{'ok' if passed else 'FAIL'}] {name}: {detail}")
        return "\n".join(out)


def _as_matrix(S, ports_in, ports_out):
    """把 SAX 的 SDict 折成 (N, n_out, n_in) 的复数矩阵。"""
    n_in, n_out = len(ports_in), len(ports_out)
    n_wl = None
    for pi in ports_in:
        for po in ports_out:
            v = np.asarray(S[(pi, po)])
            if v.ndim >= 1:
                n_wl = v.shape[0]
                break
        if n_wl is not None:
            break
    if n_wl is None:
        n_wl = 1
    M = np.zeros((n_wl, n_out, n_in), dtype=complex)
    for i, pi in enumerate(ports_in):
        for j, po in enumerate(ports_out):
            v = np.asarray(S[(pi, po)])
            M[:, j, i] = np.broadcast_to(v, (n_wl,)) if v.ndim == 0 else v.reshape(n_wl)
    return M


def check_mzi(dL_um=30.0, dphi_rad=0.0, wl=None, tol_unitary=TOL_UNITARY,
              tol_reference=TOL_REFERENCE):
    """对一条 MZI 跑完整物理闸门，返回 Verdict。"""
    from .models import mzi, analytic_mzi, WL_DEFAULT

    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    S, wl = mzi(dL_um=dL_um, dphi_rad=dphi_rad, wl=wl)
    ins, outs = ("in1", "in2"), ("out1", "out2")
    M = _as_matrix(S, ins, outs)
    checks = []

    # 1. 幺正性
    err_u = 0.0
    for k in range(M.shape[0]):
        G = M[k].conj().T @ M[k]
        err_u = max(err_u, float(np.abs(G - np.eye(len(ins))).max()))
    checks.append(("unitarity S^H S = I", err_u <= tol_unitary,
                   f"max|S^H S - I| = {err_u:.3e} (tol {tol_unitary:.0e})"))

    # 2. 与解析解对拍
    A = analytic_mzi(dL_um, dphi_rad, wl)
    errs = {}
    for pi in ins:
        for po in outs:
            ref = np.broadcast_to(np.asarray(A[(pi, po)]), (M.shape[0],))
            got = np.asarray(S[(pi, po)])
            got = np.broadcast_to(got, (M.shape[0],)) if got.ndim == 0 else got.reshape(-1)
            errs[f"{pi}->{po}"] = float(np.abs(got - ref).max())
    worst = max(errs.values())
    checks.append(("reference (analytic)", worst <= tol_reference,
                   f"max|S - S_ref| = {worst:.3e} over {len(errs)} paths (tol {tol_reference:.0e})"))

    # 3. 因果性：相位对 1/wl 求导的符号（群延迟必须为正）
    P = np.abs(M[:, 1, 0]) ** 2       # i1 -> o1 的功率，相位在极小值处不可靠，改用 out2
    Q = np.abs(M[:, 0, 0]) ** 2
    phi = np.unwrap(np.angle(M[:, 1, 0]))
    dphi_dwl = np.gradient(phi, wl)
    bad_causal = int(np.sum(dphi_dwl > TOL_PHASE))
    checks.append(("causality dphi/dlambda <= 0", bad_causal == 0,
                   f"{bad_causal}/{len(wl)} points with positive group delay"))
    del P, Q

    # 4. 端口完备：每个输入口都要有能量出去
    dead = []
    for i, pi in enumerate(ins):
        tot = np.sum(np.abs(M[:, :, i]) ** 2, axis=1)
        if float(tot.min()) < 1.0 - TOL_ENERGY:
            dead.append(f"{pi} min total power {tot.min():.6f}")
    checks.append(("ports complete (no dangling)", not dead,
                   "all inputs carry power" if not dead else "; ".join(dead)))

    ok = all(c[1] for c in checks)
    return Verdict(ok=ok, checks=checks)


def check_unitarity(S, ins, outs, tol=TOL_UNITARY):
    """对任意 SAX 结果跑幺正性检查——器件库新加单元时的第一道关。"""
    M = _as_matrix(S, ins, outs)
    err = 0.0
    for k in range(M.shape[0]):
        err = max(err, float(np.abs(M[k].conj().T @ M[k] - np.eye(len(ins))).max()))
    v = Verdict(ok=err <= tol, checks=[("unitarity S^H S = I", err <= tol,
                                        f"max|S^H S - I| = {err:.3e} (tol {tol:.0e})")])
    return v
