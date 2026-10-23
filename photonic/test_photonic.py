"""光芯片模块的回归测试。

这里每一条用例都对应一个真实的失败，不是为覆盖率写的：
  * SAX 0.18 用 instances[].connections 连多级电路会静默返回 0——专测。
  * MZI 与解析解对拍，五组 dL。
  * 闸门必须能拒绝一个坏设计（否则闸门本身不可信）。
"""
import os

import numpy as np
import pytest

from photonic import mzi, analytic_mzi, check_mzi, mmi2x2
from photonic.physgate import check_unitarity


WL = np.linspace(1.50, 1.60, 401)


def test_mmi_unitary():
    v = check_unitarity(mmi2x2(wl=WL), ("in1", "in2"), ("out1", "out2"))
    assert v.ok, v.lines()


@pytest.mark.parametrize("dL", [0.0, 10.0, 20.0, 30.0, 60.0])
def test_mzi_matches_analytic(dL):
    S, wl = mzi(dL_um=dL, wl=WL)
    ref = analytic_mzi(dL, 0.0, wl)
    for k in ref:
        got = np.asarray(S[k])
        exp = np.broadcast_to(np.asarray(ref[k]), (len(wl),))
        assert np.abs(got - exp).max() < 1e-9, (dL, k, np.abs(got - exp).max())


@pytest.mark.parametrize("dL", [0.0, 30.0])
def test_mzi_energy_conserved(dL):
    S, wl = mzi(dL_um=dL, wl=WL)
    P = np.abs(np.asarray(S[("in1", "out1")])) ** 2 + \
        np.abs(np.asarray(S[("in1", "out2")])) ** 2
    assert np.abs(P - 1.0).max() < 1e-12


def test_phase_shifter_sweeps():
    """相移器必须真的改变输出，否则等于没接。

    注意 dphi_rad 在这个包里是"相移器的等效长度（um）"，不是弧度——见
    models.phase_shifter 的注释。所以这里扫长度，并断言单调性：长度越长，
    臂差相位越大，out1 的功率应当单调增（在 0 到 pi 这段里）。
    """
    ws = []
    for L in (0.0, 0.1, 0.2, 0.3):
        S, _ = mzi(dL_um=0.0, dphi_rad=L, wl=WL)
        ws.append(float(np.mean(np.abs(np.asarray(S[("in1", "out1")])) ** 2)))
    assert ws[0] < 1e-12, f"dL=0 且无相移时 out1 应为 0，实测 {ws[0]}"
    assert ws[-1] > 0.2, f"加了 0.3 um 相移臂后 out1 只有 {ws[-1]:.3f}"
    assert all(b > a for a, b in zip(ws, ws[1:])), f"不单调: {ws}"


def test_dphi_subtracts_from_arm_phase():
    """相移器**减**在臂差相位上，且相位公式与长度一致。

    实测：dL=30、dphi_rad=0.3 时电路给 |out2| = 0.1993/0.2418/0.2838。
    这等价于把臂 1 缩短 0.3 um（|cos(p(dL-0.3)/2)| 的同一组值），
    而**不等于** p/2 - 0.3 ——后者会给出 0.9384/0.9224/0.9045。
    差别就在于相移器模型自带 2*pi*neff*L/lambda 的色散。
    这一条我反复过五次，光是量纲就错了两回，所以把两种写法都钉成用例。
    """
    from photonic.models import neff
    S, wl = mzi(dL_um=30.0, dphi_rad=0.3)
    got = np.abs(np.asarray(S[("in1", "out2")])).ravel()
    # 正确：相移器是一段长度，相位按同一条色散公式扣掉
    p_short = 2 * np.pi * neff(wl) * (30.0 - 0.3) / wl
    right = np.abs(np.cos(0.5 * p_short))
    # 错误：把 dphi 直接当弧度从相位里减
    p = 2 * np.pi * neff(wl) * 30.0 / wl
    wrong = np.abs(np.cos(0.5 * (p - 0.3)))
    assert np.abs(got[:20] - right[:20]).max() < 1e-10, "相移器不是按长度算的"
    assert np.abs(got[:20] - wrong[:20]).max() > 0.3, "按弧度量算本应明显不符"


def test_physgate_accepts_good_design():
    v = check_mzi(dL_um=30.0, wl=WL)
    assert v.ok, v.lines()


def test_physgate_rejects_broken_model():
    """把 MMI 换成不平衡的假模型，闸门必须拒绝——闸门本身也要被检验。"""
    import photonic.models as models
    good = models.MZI_MODELS["mmi2x2"]
    def broken(wl=None):
        return {("in1", "out1"): 0.8, ("in1", "out2"): 0.6j,
                ("in2", "out1"): 0.6j, ("in2", "out2"): 0.8}
    models.MZI_MODELS["mmi2x2"] = broken
    try:
        v = check_mzi(dL_um=30.0, wl=WL)
        assert not v.ok, "闸门放过了一个不平衡的耦合器"
        assert any("unitarity" in c[0] for c in v.checks)
    finally:
        models.MZI_MODELS["mmi2x2"] = good


def test_sax_connections_bug_is_real():
    """SAX 0.18 的已知行为：instances[].connections 连多级电路静默返回 0。

    这条用例锁住的是上游的坑。如果哪天上游修好了，它会失败，那时本包
    models.py 里的 nets 写法仍然是对的，删掉用例即可。
    """
    import sax
    from photonic.models import mmi2x2, waveguide

    def build(use_nets):
        nl = {"instances": {
            "cp1": {"component": "M", "settings": {},
                    "connections": {"in1": "i1", "in2": "i2", "out1": "x1", "out2": "x2"}},
            "arm1": {"component": "W", "settings": {}, "connections": {"o1": "x1", "o2": "y1"}},
            "arm2": {"component": "W", "settings": {}, "connections": {"o1": "x2", "o2": "y2"}},
            "cp2": {"component": "M", "settings": {},
                    "connections": {"in1": "y1", "in2": "y2", "out1": "o1", "out2": "o2"}}},
            "ports": {"i1": "cp1,in1", "i2": "cp1,in2", "o1": "cp2,out1", "o2": "cp2,out2"}}
        if use_nets:
            nl["nets"] = [{"p1": "cp1,out1", "p2": "arm1,o1"},
                          {"p1": "arm1,o2", "p2": "cp2,in1"},
                          {"p1": "cp1,out2", "p2": "arm2,o1"},
                          {"p1": "arm2,o2", "p2": "cp2,in2"}]
        return nl

    def wg():
        return {("o1", "o2"): 1.0}
    models = {"M": mmi2x2, "W": wg}
    f_conns, _ = sax.circuit(build(False), models)
    f_nets, _ = sax.circuit(build(True), models)
    # 端口名取 i1/o1：这一对在本电路里由 cp1.in1 -> (cp1.out2, arm2) -> cp2.in2 一路连通。
    # 注意 "i1"->"o1"（cp1.out1 经 arm1 那条）在本网表里恰是干涉相消的暗口，恒为 0，
    # 不能拿它当判据——这正是"看起来对"会骗人的地方。
    p_conns = float(np.abs(np.asarray(f_conns(wl=WL)[("i1", "o2")])).max() ** 2)
    p_nets = float(np.abs(np.asarray(f_nets(wl=WL)[("i1", "o2")])).max() ** 2)
    assert p_nets > 0.9, f"nets 写法应当给出 ~1，实际 {p_nets}"
    assert p_conns < 1e-6, f"上游行为变了：connections 写法现在给出 {p_conns}，可删本条"


#: 协同设计要同时载入 jax + klayout + gdsfactory，单个进程约需 1.5 GB；
#: 在内存紧张的机器上（本机 13.7 GB、常驻 WSL 1.6 GB）不能和上面的电路用例
#: 挤在同一个 pytest 进程里，否则会在 70 KB 的分配上 OOM。所以单独起进程跑。
_LOW_MEM = os.environ.get("PHOTONIC_SKIP_CODESIGN") == "1"


def test_co_design_matches(tmp_path):
    """电路参数与版图参数必须一致，且 GDS 真的写出来。"""
    if _LOW_MEM:
        pytest.skip("PHOTONIC_SKIP_CODESIGN=1：内存不足，另起进程跑 test_codesign.py")
    from photonic import co_design
    r = co_design(dL_um=30.0, out_dir=str(tmp_path))
    assert r.ok, r.lines()
    assert r.layout["gds_bytes"] > 100
    assert abs(r.layout["dL_um"] - 30.0) < 1e-9
    assert r.circuit["n_points"] == 401


def test_co_design_catches_drift(tmp_path, monkeypatch):
    """版图参数被偷偷改掉时，协同检查必须报 DRIFT——否则它等于没检查。"""
    if _LOW_MEM:
        pytest.skip("PHOTONIC_SKIP_CODESIGN=1")
    import photonic.layout as lay
    from photonic import co_design
    real = lay.mzi_layout
    def drifted(dL_um=30.0, **kw):
        return real(dL_um=dL_um + 5.0, **kw)   # 版图比电路长 5um
    monkeypatch.setattr(lay, "mzi_layout", drifted)
    r = co_design(dL_um=30.0, out_dir=str(tmp_path))
    assert not r.ok
    assert any("drift" in p for p in r.problems), r.problems


# ---------------------------------------------------------------------------
# 环形谐振器
# ---------------------------------------------------------------------------
# 每条用例都对应一次真实的失败，不是为覆盖率写的：
#   * 相位单位写错 (L/1e3)/wl -> 谱线全平，不报错
#   * ng 符号写反 -> ng=0.68, FSR 大一倍多
#   * 猜 order 再解 lambda -> 牛顿法滑到无意义处，谷数虚增到 31 个假象
from photonic import (ring_add_drop, ring_add_drop_analytic, fsr_nm,   # noqa: E402
                     group_index, ring_resonances_nm, check_ring,
                     check_ring_resonances, neff)


def test_neff_decreases_with_wavelength():
    """neff 必须随波长下降。写成上升会让 ng=0.68，而谐振位置看不出问题。"""
    assert neff(1.45) > neff(1.55) > neff(1.75)


def test_group_index_equals_NG():
    """一阶线性色散下 ng 必须等于 NG=4.2。这条是符号错的直接探针。"""
    ng = group_index(1.55)
    assert abs(ng - 4.2) < 1e-9, f"ng = {ng}，正确值 4.2（差这么多通常是 dneff/dlambda 符号反了）"


def test_ring_units_are_sane():
    """回路相位必须真的在 C 波段里绕，否则谱线是平的且不报错。"""
    S = ring_add_drop(10.0, 0.2, 0.2, 2.0)
    th = np.abs(np.asarray(S[("in1", "out1")]))
    dr = np.abs(np.asarray(S[("in1", "out2")]))
    dyn_db = -20 * np.log10(th.min() / th.max())
    assert dyn_db > 10.0, f"through 动态范围只有 {dyn_db:.2f} dB（检查相位单位）"
    assert dr.max() > 0.9


@pytest.mark.parametrize("R,k,loss", [(10.0, 0.2, 2.0), (20.0, 0.2, 2.0), (10.0, 0.5, 2.0)])
def test_ring_matches_independent_derivation(R, k, loss):
    S = ring_add_drop(R, k, k, loss)
    A = ring_add_drop_analytic(R, k, k, loss)
    assert np.abs(np.asarray(S[("in1", "out1")]) - A["thru"]).max() < 1e-12
    assert np.abs(np.asarray(S[("in1", "out2")]) - A["drop"]).max() < 1e-12


@pytest.mark.parametrize("R,k", [(10.0, 0.2), (20.0, 0.2), (10.0, 0.5)])
def test_ring_physgate(R, k):
    v = check_ring(radius_um=R, k1=k, k2=k)
    assert v.ok, v.lines()


def test_ring_physgate_rejects_amplifying_ring():
    """|thru|^2+|drop|^2 > 1 的"环"违反无源性，必须被拒。"""
    import photonic.models as models
    good = models.ring_add_drop
    def amplifying(*a, **kw):
        return {k: v * 1.2 for k, v in good(*a, **kw).items()}
    models.ring_add_drop = amplifying
    try:
        v = check_ring(radius_um=10.0)
        assert not v.ok, "闸门放过了一个有增益的环"
        assert any("passive" in c[0] for c in v.checks)
    finally:
        models.ring_add_drop = good


@pytest.mark.parametrize("R", [10.0, 20.0])
def test_ring_resonances_match_equation_roots(R):
    """谱线谷位 与 m*lambda = neff*L 的整数阶根必须一一对上。

    实测：R=10 有 31 个谷、R=20 有 63 个谷，最大偏差 0.0005 nm。
    """
    v = check_ring_resonances(radius_um=R)
    assert v.ok, v.lines()


def test_resonance_solver_is_stable():
    """求根器必须对相邻阶给出稳定解（步长 ~FSR），不是乱跳。"""
    roots = np.array(ring_resonances_nm(20.0, wl_min_nm=1540.0, wl_max_nm=1560.0))
    assert len(roots) >= 4
    gaps = np.diff(roots)
    assert gaps.min() > 3.0 and gaps.max() < 6.0, f"相邻阶间隔 {gaps}"
    assert np.all(np.diff(roots) > 0)


def test_fsr_matches_measured_gap():
    """FSR 公式 与 谱线相邻谷间隔 必须在 10% 内对上。"""
    R = 20.0
    wl = np.linspace(1.525, 1.565, 40001)
    th = np.abs(np.asarray(ring_add_drop(R, 0.2, 0.2, 2.0, wl=wl)[("in1", "out1")]))
    idx = [i for i in range(1, len(th) - 1) if th[i] < th[i-1] and th[i] < th[i+1]]
    assert len(idx) >= 3
    measured = float(np.mean(np.diff(wl[idx])) * 1000)
    predicted = fsr_nm(R, wl_nm=float(wl[idx[0]]) * 1000)
    assert abs(measured - predicted) / measured < 0.1, \
        f"实测 {measured:.3f} nm vs 公式 {predicted:.3f} nm"


def test_directional_coupler_unitary():
    from photonic import directional_coupler
    from photonic.physgate import check_unitarity
    v = check_unitarity(directional_coupler(0.3), ("in1", "in2"), ("out1", "out2"))
    assert v.ok, v.lines()
