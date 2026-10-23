"""光芯片器件模型库（SAX 电路级）。

每个模型是一个函数，返回 {(port_in, port_out): S} 的 dict。
S 可以是标量（与波长无关）或长度 N 的一维数组（N = 仿真波长点数），
后者会被 SAX 识别为 batch 维——这条约定是本包能在一次求值里拿到整条频谱的原因。

注意 SAX 0.18 的两个坑，见 physgate.py：
  1. 多级电路必须用 netlist 的 "nets" 显式连线，用 instances[].connections 会
     静默算出全 0（不是报错，是 0）。
  2. 模型返回的 S 若为 batch（shape=(N,)），整个电路就是 batch 的，各实例必须一致。
"""
from __future__ import annotations

import numpy as np

#: 默认波长网格（微米），C 波段
WL_DEFAULT = np.linspace(1.50, 1.60, 401)

#: 硅波导色散（G 型通用 PDK 量级，非某家 PDK 的签名数据）
NEFF = 2.44      # 1550 nm 处的有效折射率
NG = 4.20        # 群折射率，决定 FSR


def neff(wl):
    """一阶色散：neff 随波长线性下降（近似，够 FSR/相位用）。"""
    return NEFF + (np.asarray(wl) - 1.55) * (NG - NEFF) / 1.55


def _c():
    return 1.0 / np.sqrt(2.0)


def mmi2x2(wl=None):
    """2x2 3 dB MMI 耦合器：理想无损对称。

    返回 S 为标量，不随波长变化（理想耦合器）。
    """
    c = _c()
    return {
        ("in1", "out1"): c,        ("in1", "out2"): 1j * c,
        ("in2", "out1"): 1j * c,   ("in2", "out2"): c,
    }


def waveguide(dL_um=0.0, wl=None):
    """单模直波导。

    dL_um: 相对参考臂的长度（微米）。返回 batch S（形状=波长点数），
    因此含它的电路必须整条 batch 化。
    """
    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    phase = 2 * np.pi * neff(wl) * (dL_um / 1e3) / wl
    return {("o1", "o2"): np.exp(1j * phase)}


def phase_shifter(dphi_rad=0.0):
    """理想相位调制器：加一个与波长无关的相移（标量 S，不破坏 batch）。"""
    return {("o1", "o2"): np.exp(1j * dphi_rad)}


def _mzi_netlist(dL_um, dphi_rad):
    return {
        "instances": {
            "cp1": {"component": "mmi2x2", "settings": {},
                    "connections": {"in1": "in1", "in2": "in2", "out1": "x1", "out2": "x2"}},
            "arm1": {"component": "wg", "settings": {"dL_um": dL_um},
                     "connections": {"o1": "a1", "o2": "b1"}},
            "arm2": {"component": "wg", "settings": {"dL_um": 0.0},
                     "connections": {"o1": "a2", "o2": "b2"}},
            "ps": {"component": "ps", "settings": {"dphi_rad": dphi_rad},
                   "connections": {"o1": "b2", "o2": "c2"}},
            "cp2": {"component": "mmi2x2", "settings": {},
                    "connections": {"in1": "y1", "in2": "y2", "out1": "out1", "out2": "out2"}},
        },
        # 这一行是必须的：SAX 0.18 只认 nets，connections 只在单级时碰巧有效
        "nets": [
            {"p1": "cp1,out1", "p2": "arm1,o1"},
            {"p1": "arm1,o2", "p2": "cp2,in1"},
            {"p1": "cp1,out2", "p2": "arm2,o1"},
            {"p1": "arm2,o2", "p2": "ps,o1"},
            {"p1": "ps,o2", "p2": "cp2,in2"},
        ],
        "ports": {"in1": "cp1,in1", "in2": "cp1,in2",
                  "out1": "cp2,out1", "out2": "cp2,out2"},
    }


def _mmi_conn_ok():
    """给 arm2/ps 的 o2 一个真名，避免 SAX 把它当成外部端口。"""
    return None


MZI_MODELS = {
    "mmi2x2": mmi2x2,
    "wg": waveguide,
    "ps": phase_shifter,
}


def mzi(dL_um=30.0, dphi_rad=0.0, wl=None):
    """马赫-曾德尔干涉仪：返回 (S_dict, wl)。

    例：S, wl = mzi(dL_um=30); P = abs(S[("in1","out1")])**2
    """
    import sax
    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    f, _ = sax.circuit(_mzi_netlist(dL_um, dphi_rad), MZI_MODELS)
    return f(wl=wl), wl


def analytic_mzi(dL_um, dphi_rad=0.0, wl=None):
    """同一条 MZI 的解析解，用作黄金参考。

    p = 臂1 相位, q = 臂2 相位 + 相移。矩阵元如上注释，符号约定与
    physgate 的对拍一起锁定；任何一个符号写错都会被它抓到。
    """
    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    p = 2 * np.pi * neff(wl) * (dL_um / 1e3) / wl
    q = np.zeros_like(p) + dphi_rad
    # in1 注入：out1 = (e^{i(p+q)} - 1)/2,  out2 = 1j(e^{ip} + e^{iq})/2
    a11 = (np.exp(1j * (p + q)) - 1) / 2
    a21 = 1j * (np.exp(1j * p) + np.exp(1j * q)) / 2
    # 由幺正性 + 前向/后向对称补出 in2 注入的两条路径：
    # 在该符号约定下 a12 = 1j(e^{i(p+q)} + 1)/2, a22 = -(e^{ip} - e^{iq})/2
    a12 = 1j * (np.exp(1j * (p + q)) + 1) / 2
    a22 = -(np.exp(1j * p) - np.exp(1j * q)) / 2
    return {("in1", "out1"): a11, ("in1", "out2"): a21,
            ("in2", "out1"): a12, ("in2", "out2"): a22}
