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

    # 3. 色散一致性：相位对波长的导数必须与材料色散对得上。
    #
    # 这条我改了四次，全记下来：
    #   a) 最初用 |S| 干涉极小处的相位 —— 零点附近相位跳 180°，梯度爆到 1000+，
    #      "10/401 点违例"全是那些点。零点处相位本来就不可信，判据不能取在那里。
    #   b) 改成"相位随波长单调增 = 因果"——方向反了：纯延迟 e^{-iωt} 的相位随
    #      波长增大而**减小**。按错误方向判，模型唯一健康的性质被判成失败。
    #   c) 换成"dphi/dlambda <= 0"也只是同义反复，任何延迟都满足，抓不到错。
    #   d) 有效判据是**量级**：dphi/dlambda 必须等于 -pi*ng*L/lambda^2。
    #      实测中位 -164.4 rad/um，理论 -164.8 rad/um，差 0.3%。
    # 这条能抓到的东西很具体：如果 dL 的单位写错（多除 1000），斜率就小 1000 倍，
    # 而 |S| 曲线仍然"看着像干涉"，任何只看形状的检查都发现不了。
    mag = np.abs(M[:, 0, 1])
    phi = np.unwrap(np.angle(M[:, 0, 1]))
    good = mag > 1e-2                            # 只在信噪比够的地方看相位
    dphi_dwl = np.gradient(phi, wl)[good]
    from .models import group_index
    ng = group_index(float(np.median(wl)))
    expected = -np.pi * ng * abs(dL_um) / (np.median(wl) ** 2)
    med = float(np.median(dphi_dwl)) if dphi_dwl.size else 0.0
    # 零臂长时没有净延迟，判据退化为"斜率为 0"
    if abs(dL_um) < 1e-9:
        ok_disp = abs(med) < 1e-6
        detail = f"dL=0: dphi/dlambda median {med:.3e} (should be 0)"
    else:
        ratio = med / expected if expected != 0 else float("inf")
        ok_disp = 0.98 <= ratio <= 1.02
        detail = (f"dphi/dlambda median {med:.2f} rad/um vs theory "
                  f"-pi*ng*L/lambda^2 = {expected:.2f} (ratio {ratio:.4f}, "
                  f"accepted 0.98-1.02; sign included — a flipped sign is a real failure)")
    checks.append(("dispersion: dphi/dlambda matches -pi*ng*L/lambda^2", ok_disp, detail))

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


# ---------------------------------------------------------------------------
# 环形谐振器的闸门
# ---------------------------------------------------------------------------
# 环有损耗，S 不幺正，所以幺正性这条不适用。换成三条对环真正有意义的：
#   1. 能量不增 —— 无源器件任意波长下 |thru|^2 + |drop|^2 <= 1
#   2. 独立解析对拍 —— 与 ring_add_drop_analytic（另一条推导）逐点比
#   3. 互易对称 —— 无源无损无磁 ⇒ S 是对称矩阵
#   4. 谐振位置 —— 实测谷位必须与隐式色散方程的解对上（这是环最硬的一条）

TOL_ENERGY_RING = 1e-6
TOL_RECIPROCITY = 1e-12
TOL_RESONANCE_NM = 0.05


def check_ring(radius_um=10.0, k1=0.2, k2=0.2, loss_db_per_cm=2.0, wl=None,
               tol_energy=TOL_ENERGY_RING, tol_reference=TOL_REFERENCE,
               tol_reciprocity=TOL_RECIPROCITY):
    """对 add-drop 环跑物理闸门。"""
    from .models import ring_add_drop, ring_add_drop_analytic, WL_DEFAULT

    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    S = ring_add_drop(radius_um, k1, k2, loss_db_per_cm, wl=wl)
    A = ring_add_drop_analytic(radius_um, k1, k2, loss_db_per_cm, wl=wl)
    thru = np.asarray(S[("in1", "out1")])
    drop = np.asarray(S[("in1", "out2")])
    checks = []

    # 1. 能量不增
    p_tot = np.abs(thru) ** 2 + np.abs(drop) ** 2
    excess = float(p_tot.max() - 1.0)
    checks.append(("passive (|thru|^2+|drop|^2 <= 1)", excess <= tol_energy,
                   f"max total power = {p_tot.max():.9f} (excess {excess:+.2e})"))

    # 2. 独立解析对拍
    e1 = float(np.abs(thru - A["thru"]).max())
    e2 = float(np.abs(drop - A["drop"]).max())
    worst = max(e1, e2)
    checks.append(("reference (independent derivation)", worst <= tol_reference,
                   f"max|dthru|={e1:.2e} max|ddrop|={e2:.2e} (tol {tol_reference:.0e})"))

    # 3. 互易对称
    e_rec = float(np.abs(np.asarray(S[("in2", "out1")]) - drop).max())
    e_rec = max(e_rec, float(np.abs(np.asarray(S[("in2", "out2")]) - thru).max()))
    checks.append(("reciprocity S12 == S21", e_rec <= tol_reciprocity,
                   f"max|S12-S21| = {e_rec:.2e}"))

    ok = all(c[1] for c in checks)
    return Verdict(ok=ok, checks=checks)


def check_ring_resonances(radius_um=10.0, k1=0.2, k2=0.2, loss_db_per_cm=2.0,
                          tol_nm=0.05):
    """谐振位置对拍：谱线寻极小值  vs  整数阶方程 m*lambda = neff(lambda)*L。

    这是两种完全不同的算法（数值极小 vs 方程求根），所以它能抓到"公式里
    单位/符号错了但谱线看着还光滑"这一整类问题——我在环上就是这样连栽
    三次（相位 L 单位、ng 符号、m 猜错），每一次都是这条才把问题钉住。

    实测：R=10 有 31 个谷、R=20 有 63 个谷，与整数阶根一一对应，
    最大偏差 0.0005 nm。
    """
    from .models import ring_add_drop, ring_resonances_nm

    wl = np.linspace(1.45, 1.75, 300001)          # 0.1 pm 网格
    thru = np.abs(np.asarray(ring_add_drop(radius_um, k1, k2, loss_db_per_cm,
                                           wl=wl)[("in1", "out1")]))
    idx = [i for i in range(1, len(thru) - 1)
           if thru[i] < thru[i - 1] and thru[i] < thru[i + 1]]
    meas = np.array([wl[i] * 1000.0 for i in idx])
    pred = np.array(ring_resonances_nm(radius_um, wl_min_nm=1450.0, wl_max_nm=1750.0))

    if len(meas) < 2:
        return Verdict(ok=False, checks=[("resonances found", False,
                                          f"only {len(meas)} dip(s) in 1450-1750 nm — ring is not resonating")])
    if len(pred) == 0:
        return Verdict(ok=False, checks=[("resonances predicted", False,
                                          "no integer-order root in window")])
    errs = np.array([np.min(np.abs(pred - m)) for m in meas])
    worst = float(errs.max())
    unmatched = int((errs > tol_nm).sum())
    checks = [
        ("dip count == integer-order roots", len(meas) == len(pred),
         f"{len(meas)} dips measured, {len(pred)} roots"),
        ("dip positions", worst <= tol_nm,
         f"max |dip - root| = {worst:.5f} nm over {len(meas)} dips ({unmatched} unmatched, tol {tol_nm} nm)"),
    ]
    return Verdict(ok=all(c[1] for c in checks), checks=checks)
