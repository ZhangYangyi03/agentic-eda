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
    """相移器要真的改变输出，否则等于没接。"""
    S0, _ = mzi(dL_um=0.0, dphi_rad=0.0, wl=WL)
    Spi, _ = mzi(dL_um=0.0, dphi_rad=np.pi, wl=WL)
    p0 = float(np.mean(np.abs(np.asarray(S0[("in1", "out1")])) ** 2))
    ppi = float(np.mean(np.abs(np.asarray(Spi[("in1", "out1")])) ** 2))
    assert abs(p0 - ppi) > 0.5, (p0, ppi)


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
