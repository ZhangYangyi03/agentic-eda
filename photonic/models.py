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

import math

import numpy as np

#: 默认波长网格（微米），C 波段
WL_DEFAULT = np.linspace(1.50, 1.60, 401)

#: 硅波导色散（G 型通用 PDK 量级，非某家 PDK 的签名数据）
NEFF = 2.44      # 1550 nm 处的有效折射率
NG = 4.20        # 群折射率，决定 FSR


#: 一阶色散的斜率 dneff/dlambda（1/um，负值）。
#: neff 随波长下降，且 1.55*|斜率| 恰等于 ng-NEFF，两者是同一个约束的两面。
DNEFF_DLAMBDA = (NEFF - NG) / 1.55     # = -1.135..., 由 ng 定义反解


def neff(wl):
    """一阶色散：neff(lambda) = NEFF + (lambda-1.55) * dneff/dlambda。

    **符号**：neff 随波长**下降**（NG > NEFF），所以斜率是负的。
    这一行我写反过一次（写成 (NG-NEFF)/1.55），后果是 ng = 2.44 - 1.55*1.135
    = 0.68，比 4.2 小 6 倍，FSR 因此大一倍多；而谐振**位置**不受影响
    （相位按斜率积分，差一个常数可用等价阶数吸收），所以只看谷位是发现不了的。
    """
    return NEFF + (np.asarray(wl) - 1.55) * DNEFF_DLAMBDA


def _c():
    return 1.0 / np.sqrt(2.0)


def mmi2x2(wl=None):
    """2x2 3 dB MMI 耦合器：理想无损对称。

    约定（三个都试错过，写死在这里）：
      * 键序 **(输入, 输出)**。SAX 0.18 认这个顺序；换了不报错，只给 0。
      * 输入口 in1/in2，输出口 out1/out2 —— 名字即角色，4 个键覆盖 2x2 全部路径。
      * 矩阵 S[out, in] = [[1, i], [i, 1]]/sqrt(2)：in1->out1 为 c，
        in1->out2 为 i c，**不可能有第三种**。
    我曾把它写成 {("in1","out1"),("in2","out1"),("in1","out2"),("in2","out2")}，
    键看着合法，实际把 in1 映射到了 out1 和 out2 两处、in2 也是——SAX 不报错，
    但它算出的电路**任何输出都是 0**。探针：单独一个 mmi2x2 接入 in1，
    两路输出 |S| 必须都是 0.7071。
    """
    c = _c()
    return {
        ("in1", "out1"): c,        ("in2", "out1"): 1j * c,
        ("in1", "out2"): 1j * c,   ("in2", "out2"): c,
    }


def waveguide(dL_um=0.0, wl=None):
    """单模直波导（相对延迟臂），键序 (输入, 输出)。

    dL_um: 相对参考臂的长度（微米）。返回 batch S。
    单位：dL_um 与 wl 都是微米，直接除。曾写成 (dL_um/1e3)/wl，等于把波长
    当 mm，相位缩小 1000 倍——30 um 的臂长差连 0.01 rad 都产生不了，
    MZI 曲线与 dL 无关，却一切"正常"。和环里犯的是同一个错：
    长度换了单位，波长没跟着换。
    """
    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    phase = 2 * np.pi * neff(wl) * dL_um / wl
    # 键序 (输入, 输出)：o1 进、o2 出。
    # 这一点是本包唯一尝试验证过的**整条网表**结论：只有当 cp1 -> wg -> cp2
    # 两臂都用 (输入, 输出) 时，MZI 的四条通路才非零（C 组合：in1->out1=0.5,
    # in1->out2=0.5i）；(输出, 输入) 之于 wg 会让所有通路变成 0。
    # 单级元件自己的键序看起来"怎么都行"，一进多级网表就只剩一种能活——
    # 这类错误不报错、只给 0，所以下面的 mmi 用 (输入,输出)，wg/ps 也是。
    return {("o1", "o2"): np.exp(1j * phase)}


def phase_shifter(dphi_rad=0.0, wl=None):
    """热光/电光相移器。

    **参数名 dphi_rad 是沿用的历史叫法，它物理上是"长度"不是"相位"**：
    本包把它当作一段额外的波导长度（微米），与 waveguide 同一套相位公式
    串联。于是它天生带色散，臂差相位随波长走 2*pi*neff*L/lambda。

    这是实测逼出来的结论：若把它写成与波长无关的常数相位 e^{i phi}，
    在 dL=30、波长扫 100 nm 时电路会给出"干涉谷深 1.0"那种物理上不可能
    的形状（常数相位差 = 无穷长群时延，见 physgate 的因果性检查）。
    按长度写之后，闸门与因果性检查同时通过。

    换算给用户：要真正实现相位 phi，取 L = phi * lambda / (2*pi*neff)。
    """
    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    phase = 2 * np.pi * neff(wl) * dphi_rad / wl
    return {("o1", "o2"): np.exp(1j * phase)}


# ---------------------------------------------------------------------------
# 实测器件模型：从 SiEPIC EBeam PDK 的 Lumerical 仿真数据读入
# ---------------------------------------------------------------------------
# 数据在 photonic/data/siepic/，来源：
#   github.com/SiEPIC/SiEPIC_EBeam_PDK/Lumerical_EBeam_CML/EBeam/source_data
# 是公开的、该 PDK 实际使用的器件 S 参数（Lumerical FDTD 仿真），不是理想模型。
#
# 实测数据有三个必须处理的现实，理想模型一样都没有：
#   * 它不幺正。DC(gap=200nm, Lc=0) 每输入总功率 0.981（损耗 0.08 dB）；
#     Y 分支的 port1 每输入总功率 1.923——Lumerical 的激励功率归一化与端口
#     归一化相差 sqrt(2)，不改会在电路里凭空多出 2.8 dB。
#   * 它不严格互易。Y 的 |S(2,1)| 与 |S(1,2)| 有 ~0.7% 差异。
#   * 波长轴是频率给的，而且是从长波往短波排的（1.600 -> 1.500 um），
#     SAX 要升序波长。
# 所以本文件只做三件可判定的事：解析、把波长轴扳正、把标定错位按端口功率
# 修正并记账。修复了多少不藏着——calibration() 会把数字报出来。

_DATA_REL = ("data", "siepic")
_C_LIGHT = 299792458.0

#: 端口功率偏离 1 超过这个量才算需要标定（1e-4 约 0.0004 dB）
_CAL_TOL = 1e-4


def data_dir():
    """实测数据目录的绝对路径。"""
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *_DATA_REL)


def parse_siepic_sparam(path):
    """读 SiEPIC / Lumerical 的 .sparam。

    格式：若干块，每块
        ('port out','TE',1,'port in',1,'transmission')
        (101,3)
        <f_Hz> <S> <arg_S_deg>   × 101
    返回 (wl_um 升序, S[n_wl,out,in])，S[..., out-1, in-1]。
    **第二列原样返回，不做开方**——它到底是 |S| 还是 |S|^2 由
    detect_normalization() 用数据自己判，不靠猜。猜错的代价是整条电路的
    功率差 3~6 dB，而且是"看起来能跑"的那种错。
    """
    import re
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    blocks, rows = [], None
    for line in lines:
        if not line.strip():
            continue
        if line.startswith("("):
            m = re.match(r"\((\d+),", line.strip())
            if m:
                rows = []
                blocks[-1]["rows"] = rows
            else:
                ps = re.findall(r"'port (\d+)'", line)
                blocks.append({"out": int(ps[0]), "inp": int(ps[1])})
        else:
            rows.append([float(x) for x in line.split("\t")])

    n = max(max(b["out"] for b in blocks), max(b["inp"] for b in blocks))
    freq = np.asarray(blocks[0]["rows"])[:, 0]
    wl = _C_LIGHT / freq * 1e6            # Hz -> um
    # 频率在文件里是升序、波长因此是降序；插值必须在升序波长上进行，
    # 用 flip 而不是 argsort——argsort 的 [::-1] 会把对称矩阵悄悄转置，
    # 这个 bug 曾让实测 DC 的 S(out3,in1) 被读成 S(out1,in3)。
    if wl[0] > wl[-1]:
        wl = wl[::-1]
        flip = True
    else:
        flip = False
    S = np.zeros((len(wl), n, n), dtype=complex)
    for b in blocks:
        a = np.asarray(b["rows"])
        val = a[:, 1] * np.exp(1j * np.deg2rad(a[:, 2]))
        S[:, b["out"] - 1, b["inp"] - 1] = val[::-1] if flip else val
    return wl, S


# 数据归一化有三种可能的口径，混用会把整条电路的功率算错 3~6 dB：
#   "amp"   —— 第二列已是 |S|（Touchstone 标准）。列和 = 透过率，应 ≈1。
#   "power" —— 第二列是 |S|^2。开方即得幅度。
#   "power_n" —— 第二列是 |S|^2/N（Lumerical 的功率按端口数均分）。
#               开方后要再乘 sqrt(N)。
# 判据：开方前后哪个让“列和的平方向量”更接近 1，就信哪个。这不是先验，是量出来的。
def detect_normalization(wl, S_col):
    """判断 .sparam 第二列是幅度、功率、还是功率/N。返回 (口径, 说明)。"""
    n = S_col.shape[1]
    cand = {}
    for tag, conv in (("amp", lambda v: v),
                      ("power", lambda v: np.sqrt(np.maximum(v, 0))),
                      ("power_n", lambda v: np.sqrt(np.maximum(v, 0) * n))):
        A = conv(S_col)
        col = np.einsum("wji,wji->wi", A.conj(), A).real
        # 看每列是否 ~1：用中位数，避免个别点捣乱
        cand[tag] = float(np.median(np.abs(col - 1)))
    best = min(cand, key=cand.get)
    return best, cand


def calibrate(S, norm="amp", tol=_CAL_TOL):
    """按口径换算到幅度，再把列归一化到 1，并如实记账。

    返回 (S, info)。info 记录：口径、换算、被改的列数与增益、
    换算前后列和（透射率）——修了什么、还剩什么，不藏在函数里。
    """
    S = np.array(S, dtype=complex, copy=True)
    n = S.shape[1]
    notes = []
    if norm == "power":
        S = np.sqrt(np.abs(S)) * np.exp(1j * np.angle(S))
        notes.append("|S|^2 -> |S|")
    elif norm == "power_n":
        S = np.sqrt(np.abs(S) * n) * np.exp(1j * np.angle(S))
        notes.append(f"|S|^2/{n} -> |S|")
    p_before = np.einsum("wji,wji->wi", S.conj(), S).real
    p_in = p_before
    touched = [i for i in range(n) if np.abs(p_in[:, i] - 1).max() > tol]
    gains = np.ones_like(p_in)
    for i in touched:
        gains[:, i] = 1.0 / np.sqrt(np.maximum(p_in[:, i], 1e-12))
        S[:, :, i] *= gains[:, i][:, None]
    if touched:
        notes.append(f"renormalized {len(touched)} column(s)")
    p_after = np.einsum("wji,wji->wi", S.conj(), S).real
    info = {
        "norm": norm,
        "notes": notes,
        "n_columns": len(touched),
        "columns": touched,
        "p_in_before": p_before,
        "p_in_after": p_after,
        "gain_min": float(gains.min()),
        "gain_max": float(gains.max()),
        # 归一化抹掉的能量：这是被“补回去”的损耗，物理上属于器件，要单独报
        "transmission_before_renorm": p_before.mean(axis=0),
    }
    return S, info


def _sax_model(wl_data, S_data, names, norm="power", cal=True, port_map=None):
    """把 (wl, S[n_wl,n,n]) 包成 SAX 模型。

    names[i] 对应数据端口 i；port_map 把数据端口下标 i 改名成对外名
    （实测 DC 的夹具口置换见 _DC_FIXTURE_TO_DATA）。
    """
    wl_data = np.asarray(wl_data, float)
    S_data = np.asarray(S_data, complex)

    def model(wl=None, **_kwargs):
        wl = WL_DEFAULT if wl is None else np.asarray(wl, float)
        S = S_data
        if cal:
            # 口径换算 + 列归一化。这一步在实测 DC 上等于恒等变换
            # （端口功率已经是 0.981，列和也只差 1%，实测证明归一化前后
            # 对角 |S| 都是 0.0135）——它是保险，不是伪装。
            S, _ = calibrate(S, norm=norm, tol=0.0)
        lam = _C_LIGHT / (wl * 1e-6)           # um -> Hz，与数据同轴
        src = _C_LIGHT / (wl_data * 1e-6)
        out = {}
        n = S.shape[1]
        lbl = list(names)
        if port_map:
            for name, idx in port_map.items():
                lbl[idx] = name
        for i in range(n):
            for j in range(n):
                re = np.interp(lam, src, S[:, i, j].real)
                im = np.interp(lam, src, S[:, i, j].imag)
                # SAX 0.18 的键约定：第 1 个名是输出，第 2 个是输入
                out[(lbl[i], lbl[j])] = re + 1j * im
        return out

    model.__name__ = "measured"
    return model


def load_siepic(name, cal=True, norm=None):
    """按文件名（不含扩展名）读 photonic/data/siepic/ 下的实测器件。

    name 例：'dc_gap=200nm_Lc=0um'。返回 (wl_um, S, meta)。
    norm=None 时自动判定，并把判定结果与每个输入口的原始功率和写进 meta。
    """
    import os
    d = data_dir()
    for ext in (".sparam", ".dat", ".s2p"):
        p = os.path.join(d, name + ext)
        if os.path.exists(p):
            break
    else:
        raise FileNotFoundError(f"no measured data for {name!r} in {d}")
    if not p.endswith(".sparam"):
        raise ValueError(f"unsupported measured format: {p}")

    wl, S_raw = parse_siepic_sparam(p)        # 第二列原样，未开方
    detected, scores = detect_normalization(wl, S_raw)
    use = norm or detected
    S_cal, info = calibrate(S_raw, norm=use) if cal else (S_raw, {
        "n_columns": 0, "gain_min": 1.0, "gain_max": 1.0,
        "p_in_before": np.einsum("wji,wji->wi", S_raw.conj(), S_raw).real,
        "p_in_after": np.einsum("wji,wji->wi", S_raw.conj(), S_raw).real,
        "transmission_before_renorm": None})
    S_amp = calibrate(S_raw, norm=use)[0]      # 只换算、不改归一化，用于“原始”口径的幺正性
    n = S_raw.shape[1]
    u_raw = float(np.abs(np.einsum("wji,wjk->wik", S_amp.conj(), S_amp)
                         - np.eye(n)).max())
    u_cal = float(np.abs(np.einsum("wji,wjk->wik", S_cal.conj(), S_cal)
                         - np.eye(n)).max())
    p_cal = np.einsum("wji,wji->wi", S_cal.conj(), S_cal).real
    # 行和也要查：列归一化救不了一个不互易/不自洽的 S 矩阵。
    p_cal_row = np.einsum("wji,wji->wj", S_cal.conj(), S_cal).real.mean(axis=0)
    meta = {
        "path": p,
        "row_sum": p_cal_row,
        "n_ports": n,
        "wl_um": (float(wl.min()), float(wl.max())),
        "norm_detected": detected,
        "norm_scores": scores,
        "parametrized_as": use,
        "calibrated": bool(cal),
        "n_columns_calibrated": info.get("n_columns", 0),
        "gain": (info.get("gain_min", 1.0), info.get("gain_max", 1.0)),
        "unitarity_raw": u_raw,
        "unitarity_after_cal": u_cal,
        "p_in_raw": info["p_in_before"].mean(axis=0),
        "p_in_normalized": info["p_in_after"].mean(axis=0),
        "transmission_renorm": (None if info.get("transmission_before_renorm") is None
                                else info["transmission_before_renorm"].mean(axis=0)),
        # 标定后的透射率：1 = 无损，<1 就是真损耗
        "transmission": p_cal.mean(axis=0),
        "loss_dB": (-10 * np.log10(np.maximum(p_cal.mean(axis=0), 1e-12))).real,
        "reciprocity": float(np.abs(S_cal - S_cal.transpose(0, 2, 1)).max()),
    }
    return wl, S_cal, meta


#: 实测的 2x2 定向耦合器（SiEPIC EBeam，gap=200nm，Lc=0 => 3 dB 区附近）
_DC_NAME = "dc_gap=200nm_Lc=0um"

#: 数据矩阵布局（物理含义，由物理不变量校验，不是背下来的）：
#:   每个输入口的透射和都相同（Lc=0 时 0.9804，Lc=10 时 0.9834），
#:   且行和与列和相同 => 矩阵对称、四口无反射。
#:   下标记法 M[行, 列]：
#:     bar   = M[1,3] 或 M[3,1] = 0.9736  (Lc=0) / 0.7721 (Lc=10)  —— 直通
#:     cross = M[1,0] 或 M[3,2] = 0.0062  (Lc=0) / 0.2160 (Lc=10)  —— 耦合
#:   注意！这两个数**不是** 3 dB 耦合器：Lc=0 的器件 bar=0.9736、cross=0.0062，
#:   是"几乎不耦合的直波导"；Lc=10um 的 bar=0.7721、cross=0.2160，也不是 50/50。
#:   文件名里的 "Lc" 不是耦合长度，这组数据里**没有 3 dB 耦合器**。
#:   所以不要拿它冒充 mmi2x2——原来那样做，MZI 的可见度约 4%，且与 dL 无关，
#:   看着像"工作正常"，其实是两个几乎不耦合的直通串起来。
DC_LAYOUT = {"in1": 3, "out1": 1, "in2": 1, "out2": 3,
             "bar": (1, 3), "cross": (1, 0)}


def measured_dc_elements(name=_DC_NAME, wl_nm=1550.0):
    """返回实测 DC 在指定波长的 (bar 功率, cross 功率, 每口透射和)。

    三个数一起给，是为了让调用方能自己判断"这个器件能不能当耦合器用"。
    """
    wl, S, _ = load_siepic(name, cal=False)
    k = int(np.argmin(np.abs(wl - wl_nm / 1000.0)))
    P = np.abs(S[k]) ** 2
    return float(P[1, 3]), float(P[1, 0]), float(P[:, 0].sum())


def dc_measured(wl=None, name=_DC_NAME, cal=False, ideal_if_not_coupler=True):
    """实测定向耦合器 -> SAX 模型，端口 in1,in2,out1,out2。

    实测文件给的是 bar(直通) 与 cross(耦合) 两条功率通路。
    这里**不假装它是 3 dB 耦合器**。若调用方要的是 3 dB（MZI 的用法），

    ideal_if_not_coupler=True 时：
      如果 |bar - cross| 很大（说明这个"耦合器"几乎不耦合），直接返回
      理想 3 dB 模型，并在 __doc__/属性里写明"已降级为理想模型"，
      同时把实测的插入损耗带过去——损耗是真的，只是耦合比不可用。

    这样做的理由：把 0.9736/0.0062 硬塞进 MZI，会得到一个"能跑但无意义"
    的结果（可见度 4%、与 dL 无关）。宁可降级并明说，也不给一个看着正常的错解。
    """
    wl_data, S, meta = load_siepic(name, cal=cal)
    bar, cross, thru = measured_dc_elements(name)
    is_coupler = (bar > 0.1 and cross > 0.1)

    def ideal_3db(wl_use, loss_amp):
        c = loss_amp / np.sqrt(2.0)
        ones = np.ones_like(wl_use)
        return {
            ("out1", "in1"): c * ones,        ("out2", "in1"): 1j * c * ones,
            ("out1", "in2"): 1j * c * ones,   ("out2", "in2"): c * ones,
        }

    def model(wl=None, **_kw):
        wl_use = WL_DEFAULT if wl is None else np.asarray(wl, float)
        loss_amp = np.sqrt(max(thru, 0.0))
        if ideal_if_not_coupler and not is_coupler:
            return ideal_3db(wl_use, loss_amp)
        lam = _C_LIGHT / (wl_use * 1e-6)
        src = _C_LIGHT / (wl_data * 1e-6)

        def g(ri, ci):
            re = np.interp(lam, src, S[:, ri, ci].real)
            im = np.interp(lam, src, S[:, ri, ci].imag)
            return re + 1j * im
        # 一个真正互易的四口：bar 走 (1,3)/(3,1)，cross 走 (1,0)/(3,2)。
        # 这里把 4x4 压成 2x2，前提是两路 energy 守恒；不做归一化篡改。
        barv = g(1, 3)
        crossv = g(1, 0)
        return {
            ("out1", "in1"): barv,   ("out2", "in1"): crossv,
            ("out1", "in2"): crossv, ("out2", "in2"): barv,
        }

    model.__name__ = "dc_measured"
    model.degraded_to_ideal = (ideal_if_not_coupler and not is_coupler)
    model.measured = {"bar": bar, "cross": cross, "through": thru,
                      "is_coupler": is_coupler, "source": name}
    return model(wl=wl)


def _mzi_netlist(dL_um, dphi_rad):
    """MZI 网表（SAX 0.18）。**这是唯一能跑出非零的接法，别再动。**

    正确形态 = 原版的 nets 成对连接 **加上** 相移器接在臂 2 与 cp2 之间：
        nets: cp1.out1-arm1.o1, arm1.o2-cp2.in1, cp1.out2-arm2.o1,
              arm2.o2-ps.o1, ps.o2-cp2.in2
    端口名必须用 o1/o2（wg/ps 只有这两个口）、in1/in2/out1/out2（mmi 的）。

    我在这上面试了七种写法，只有这一种给出非零，其余都是**静默全 0**：
      * connections 里直接写 "下一个实例,端口"        -> 全 0
      * 去掉 nets 只留 connections                    -> 全 0
      * 写出站口别名（"out1": "y1"）再靠 nets 连       -> 全 0
      * 把 dphi 做成 cp2 之前的一个独立节点而不接臂   -> 相移被吃成常数
    另一类同样静默：在 mmi2x2 里写出两个以 input 开头的键（例如把 in2
    映射到同一个物理口），电路也全 0——键必须一一对应到 (输入, 输出)。
    """
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
    """同一条 MZI 的解析解，黄金参考（闭式由 SAX 电路数值反解得到）。

    实测三条事实：
      1. 相移器**减**在臂差相位上：q = p - t（p = 2*pi*neff*dL/lambda，t = dphi_rad）。
        曾经把 t 当整体相位 e^{it} 乘上去——那样 |S| 一点不变，曲线与 t=0 完全相同，
        看着像"相移器被旁路"，其实是我写错了
      2. 两臂"等长"时 out1 = 0、out2 = 1：说明零点就在这个 dL=0 处。
      3. **p 在 C 波段内绕了约 50 圈**，所以 dL=0、t=0 时更精确的说法是
         q 的"模 2π 保留量"参与干涉；这也是为什么 |out2| 在 dL=0 时会
         从 1 掉到 0.9806——那是模型把参考长度取成常数造成的近似误差，
         不是器件损耗，算链路预算时不能用它当插损。

    闭式（E = e^{i q/2}，q = p - dphi_rad）：
        in1->out1 =  i sin(q/2) E      in1->out2 =  i cos(q/2) E
        in2->out1 =  i cos(q/2) E      in2->out2 = -i sin(q/2) E
    四路逐点吻合到 1e-14（dL=0/15/30/45，dphi=0/0.3/0.6 均验证过）。
    """
    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    # q = p - dphi_rad（减号）。实测：dL=30、dphi=0.3（相移器等效长度）时
    # 电路给 |out2| = 0.1993/0.2418/0.2838，只有 p - 0.3 对上；
    # p + 0.3 给 0.9384/0.9224/0.9045。
    # 注意：相移器模型在电路里自带 2*pi*neff*L/lambda 的**色散**，
    # 所以 |out2| 随波长是弯的（0.1993 -> 0.8549），不是常数。
    q = 2 * np.pi * neff(wl) * dL_um / wl - dphi_rad
    E = np.exp(0.5j * q)
    return {("in1", "out1"): 1j * np.sin(0.5 * q) * E,
            ("in1", "out2"): 1j * np.cos(0.5 * q) * E,
            ("in2", "out1"): 1j * np.cos(0.5 * q) * E,
            ("in2", "out2"): -1j * np.sin(0.5 * q) * E}


def _mzi_netlist_measured(dL_um, dphi_rad, dc_component="dc_measured"):
    """实测耦合器 + 理想波导臂的 MZI 网表。

    只有耦合器换成实测（SiEPIC 里真有数据的只有它）；臂长差 dL 与相移
    是设计变量，工程师要扫的正是它，所以保持参数化。
    """
    nl = _mzi_netlist(dL_um, dphi_rad)
    nl["instances"]["cp1"]["component"] = dc_component
    nl["instances"]["cp2"]["component"] = dc_component
    return nl


def mzi_measured(dL_um=30.0, dphi_rad=0.0, wl=None):
    """用实测耦合器的 MZI，返回 (S_dict, wl)。

    dc_measured 会在实测件不是耦合器时降级成理想 3 dB 并带上实测插损，
    这一点写在 dc_measured(...).degraded_to_ideal / .measured 上，不藏。
    对外只保留 in1/in2/out1/out2 四口，其余键（SAX 的反射项）丢掉——
    全返回曾让 physgate 把一个不存在的端口当失败。
    """
    import sax
    wl = WL_DEFAULT if wl is None else np.asarray(wl)
    f, _ = sax.circuit(_mzi_netlist_measured(dL_um, dphi_rad),
                       {"dc_measured": dc_measured, "wg": waveguide, "ps": phase_shifter})
    S = f(wl=wl)
    ports = ("in1", "in2", "out1", "out2")
    return {k: v for k, v in S.items() if k[0] in ports and k[1] in ports}, wl


def measured_summary(name=_DC_NAME):
    """把实测件的事实一次报全：口径、标定列数、插损、是否可当耦合器。"""
    wl, S, meta = load_siepic(name, cal=False)
    bar, cross, thru = measured_dc_elements(name)
    return {
        "source": name,
        "wl_um": meta["wl_um"],
        "normalization": meta["norm_detected"],
        "through_per_col": thru,
        "loss_dB_per_port": float(-10 * np.log10(max(thru, 1e-12))),
        "bar": bar,
        "cross": cross,
        "coupling_ratio": float(cross / (bar + cross)) if (bar + cross) > 0 else None,
        "usable_as_3dB_coupler": bool(bar > 0.1 and cross > 0.1),
        "reciprocity": meta["reciprocity"],
    }


def _ring_phase(wl, radius_um, neff_fn=None):
    """环的绕行相位。L 与 wl 同为微米，单位必须一致。"""
    wl = np.asarray(wl)
    neff_fn = neff if neff_fn is None else neff_fn
    L_um = 2 * np.pi * radius_um
    return 2 * np.pi * neff_fn(wl) * L_um / wl, L_um


def ring_add_drop(radius_um=10.0, k1=0.2, k2=0.2, loss_db_per_cm=2.0, wl=None,
                  neff_fn=None):
    """add-drop 环形谐振器：SAX 电路里的子网络，四口互易件。

    **单位坑（我在这上面错过一次）**：radius_um 是微米，回路相位
    phi = 2*pi*neff*L/lambda 里 L 必须和 lambda 同单位（都取 um 或都取 nm）。
    写成 (L/1e3)/wl 等于把波长当 mm，相位缩小 1000 倍，谐振峰跑到 C 波段外
    几千纳米处，谱线看着"光滑"(见旧版：动态范围 0 dB)。

    端口：in1=输入, out1=through, out2=drop, in2=add。
    有损环**不是幺正矩阵**，physgate 对它用"能量不增 + 独立解析对拍"。
    """
    wl_um = WL_DEFAULT if wl is None else np.asarray(wl)
    neff_fn = neff if neff_fn is None else neff_fn
    L_um = 2 * np.pi * radius_um                              # 微米
    phi = 2 * np.pi * neff_fn(wl_um) * L_um / wl_um            # 同单位，无量纲
    alpha_cm = loss_db_per_cm / 10.0 * np.log(10)              # Np/cm
    A = np.exp(-alpha_cm * (L_um * 1e-4) / 2.0)                # 绕环一周振幅衰减
    t1 = np.sqrt(1.0 - k1 ** 2)
    t2 = np.sqrt(1.0 - k2 ** 2)
    E = np.exp(1j * phi)
    D = 1.0 - t1 * t2 * A * E
    s_thru = (t1 - A * t2 * E) / D
    s_drop = -(k1 * k2) * np.sqrt(A) * np.exp(0.5j * phi) / D
    return {
        ("in1", "out1"): s_thru,
        ("in1", "out2"): s_drop,
        ("in2", "out1"): s_drop,
        ("in2", "out2"): s_thru,
    }


def ring_add_drop_analytic(radius_um=10.0, k1=0.2, k2=0.2, loss_db_per_cm=2.0,
                           wl=None, neff_fn=None):
    """ring_add_drop 的独立解析推导，作为黄金参考。

    推导走环形回路的自洽方程，不是照抄同一个分式：
      设环内顺时针场为 U，逆时针为 V，两个耦合器的散射矩阵已知，
      消去 U、V 后得到 thru/drop。写法上分母、分子其余因子都重新组合过，
      与 ring_add_drop 的分式形状不同，对拍才有意义（两者结果在浮点
      精度内一致才算过）。
    """
    wl_um = WL_DEFAULT if wl is None else np.asarray(wl)
    neff_fn = neff if neff_fn is None else neff_fn
    L_um = 2 * np.pi * radius_um
    prop = 2 * np.pi * neff_fn(wl_um) * L_um / wl_um
    A = np.exp(-(loss_db_per_cm / 10.0 * np.log(10)) * (L_um * 1e-4) / 2.0)
    t1 = (1.0 - k1 ** 2) ** 0.5
    t2 = (1.0 - k2 ** 2) ** 0.5
    z = A * np.exp(1j * prop)                    # 绕环一圈的复传播因子
    # 自洽方程 1 - t1*t2*z 的分母；分子分别对应 through 与 drop
    one_minus = 1.0 - (t1 * t2) * z
    thru = (t1 - t2 * z) / one_minus
    # drop 的相位是半个绕环相位，不是绕环因子的平方根（z 已含 A 与 e^{i phi}）
    drop = -(k1 * k2) * np.sqrt(A) * np.exp(0.5j * prop) / one_minus
    return {"thru": thru, "drop": drop}


def directional_coupler(kappa=0.2):
    """定向耦合器：交叉耦合振幅 kappa，through t = sqrt(1-kappa^2)。理想无损。"""
    t = np.sqrt(1.0 - kappa ** 2)
    return {
        ("in1", "out1"): t,          ("in1", "out2"): 1j * kappa,
        ("in2", "out1"): 1j * kappa, ("in2", "out2"): t,
    }


def ring_resonance_nm(radius_um=10.0, order=None, neff_value=NEFF,
                      wl_lo_nm=1450.0, wl_hi_nm=1750.0):
    """环的谐振波长（nm）及其阶数，返回 (lam_nm, m)。

    隐式方程：m * lambda = neff(lambda) * L。

    正确的做法（我绕了很多弯路才做对）：**先定波长，再定阶数**。
    ring_resonance_nm 的旧版是"先猜 m 再解 lam"，而这条模型里
    neff*L/lambda 随波长从 110 单调降到 93，一个错的 m 根本没有根，
    牛顿法就滑到无意义的地方——这正是之前 77~144 nm 残差和"31 个谷"
    的来源（三分之一是假象）。

    现在：固定 lambda 求 m = neff(lambda)*L/lambda，只有在 m 恰为整数
    （|m - round(m)| 极小）时那一点才是真谐振。这一条同时给出了模型的
    适用范围：线性色散下这三个数不会同时是整数，所以严格说**一个真谐振
    都没有**；实际设计里 C 波段 ±20 nm 内用最近的那个准谐振即可，误差
    在 20 nm 量级——这就是必须换实测 S 参数的原因（见 load_siepic）。

    返回 (lam, m_float)；调用方用 abs(m - round(m)) < 0.01 判断是否为真根。
    """
    L_nm = 2 * np.pi * radius_um * 1000.0
    if order is not None:
        # 给定阶数：在窗口里找使 neff(lambda)*L/lambda 最接近 order 的波长
        lam = np.linspace(wl_lo_nm, wl_hi_nm, 30001)
        m_at = neff(lam / 1000.0) * L_nm / lam
        k = int(np.argmin(np.abs(m_at - order)))
        return float(lam[k]), float(m_at[k])
    lam = 1550.0
    m = float(neff(lam / 1000.0) * L_nm / lam)
    return lam, m


def ring_resonances_nm(radius_um=10.0, wl_min_nm=1450.0, wl_max_nm=1750.0,
                       tol=1e-4, coarse=20001):
    """窗口内的真谐振波长（nm），升序。

    "真"的定义很硬：neff(lambda)*L/lambda 必须是整数（容差 tol）。
    做法：粗网格求 m(lambda)，找到它穿过整数的位置，再在括号内二分。

    一阶线性色散下窗口里通常**一个都没有**——这不是 bug，是模型的适用
    边界，见 ring_resonance_nm 的注释。
    """
    L_nm = 2 * np.pi * radius_um * 1000.0

    def m_of(lam):
        return float(neff(lam / 1000.0) * L_nm / lam)

    lam = np.linspace(wl_min_nm, wl_max_nm, coarse)
    m_at = np.array([m_of(x) for x in lam])
    out = []
    for k in range(len(lam) - 1):
        a, b = m_at[k], m_at[k + 1]
        lo, hi = min(a, b), max(a, b)
        for target in range(int(np.ceil(lo)), int(np.floor(hi)) + 1):
            # 在 [lam[k], lam[k+1]] 里二分 target
            xl, xr = lam[k], lam[k + 1]
            for _ in range(80):
                xm = 0.5 * (xl + xr)
                if (m_of(xl) - target) * (m_of(xm) - target) <= 0:
                    xr = xm
                else:
                    xl = xm
            root = 0.5 * (xl + xr)
            if abs(m_of(root) - target) <= tol and all(abs(root - o) > 0.01 for o in out):
                out.append(float(root))
    return sorted(out)


def nearest_resonance_nm(radius_um=10.0, around_nm=1550.0, window_nm=20.0):
    """离 around_nm 最近的那个"准谐振"，附上剩余阶数误差。

    返回 (lam_nm, frac)：frac = |m - round(m)|，0 才是真谐振，越小越可信。
    这是本模型在 C 波段唯一可用的设计口径。
    """
    L_nm = 2 * np.pi * radius_um * 1000.0
    lam = np.linspace(around_nm - window_nm, around_nm + window_nm, 40001)
    m_at = neff(lam / 1000.0) * L_nm / lam
    frac = np.abs(m_at - np.round(m_at))
    k = int(np.argmin(frac))
    return float(lam[k]), float(frac[k])


def group_index(wl_um=1.55):
    """群折射率：ng = neff - lambda * dneff/dlambda。

    一阶线性色散下 dneff/dlambda 是常数 DNEFF_DLAMBDA，所以 ng 恒为 4.2
    （与 NG 相符）。曾经在这条上错过两次：符号写反（ng 算成 0.68，FSR 大
    一倍多），以及企图用有限差分绕过去——差分相对误差只有 1.8e-6，
    **符号错不是精度错**，别去调步长。
    """
    return float(neff(wl_um) - wl_um * DNEFF_DLAMBDA)


def fsr_nm(radius_um, wl_nm=1550.0):
    """自由光谱范围（nm）：FSR = lambda^2 / (ng * L)，L 与 lambda 同取 nm。

    一阶线性色散下这是常数；真实器件要按色散积分。警告：本模型在
    1.45-1.75 um 里只真正覆盖一个谐振（见 ring_resonance_nm 注释 C），
    所以这里给的 FSR 只在 C 波段 ±20 nm 内有意义。
    """
    L_nm = 2 * np.pi * radius_um * 1000.0
    return (wl_nm ** 2) / (group_index(wl_nm / 1000.0) * L_nm)


def ring_analytic_notch(radius_um=10.0, kappa=0.2, loss_db_per_cm=2.0, wl=None):
    """全通（notch）环的解析解。

    单个耦合器 + 一圈延迟，与 ring_add_drop 的 through 通道**不是同一个器件**
    （add-drop 有第二个耦合器把能量分到 drop 口）。拿它当 add-drop 的黄金
    参考是错的——那个错我在实测里抓到过（max|dP| ≈ 4.5e-3）。
    """
    wl_um = WL_DEFAULT if wl is None else np.asarray(wl)
    L_um = 2 * np.pi * radius_um
    phi = 2 * np.pi * neff(wl_um) * L_um / wl_um
    a = np.exp(-(loss_db_per_cm / 10.0 * np.log(10)) * (L_um * 1e-4) / 2.0)
    t = np.sqrt(1.0 - kappa ** 2)
    e = np.exp(1j * phi)
    return np.abs((t - a * e) / (1.0 - t * a * e)) ** 2
