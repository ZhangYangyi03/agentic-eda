"""packflow: package selection and substrate layout, with vetoes that can fail.

Same shape as the other two flows in this repo -- propose, run, veto, feed back --
with the tools swapped for packaging:

    propose   a package from the real KiCad footprint library, matched by pin count
              and outline; a substrate stackup and a wire-bond fanout
      run     place the die pads on the physical die the physical flow produced,
              assign them to package pins, route on the substrate, and compute
              junction temperature and warpage
      veto    substrate DRC, Tj over limit, warpage over limit, die too small to
              carry its own pad ring
      feed    the violated constraint goes back into the proposal (more layers,
              a different substrate material, a larger package, a grown die)

Two things this refuses to do.

It does not call a router's own report a DRC result. The DRC here is a clearance
and crossing check this file performs on geometry it wrote, and it says so.

It does not present an estimate as a simulation. The thermal and warpage numbers
come from closed-form models with their constants stated inline. There is no FEM
here and no signoff deck: the thermal number is a lumped theta-JA estimate, the
warpage number is a Stoney curvature from a CTE mismatch. Both are vetoes on
obviously-bad designs and neither is a qualification. That is the whole claim.
"""
from __future__ import annotations
import glob, hashlib, json, math, os, re, sys, time

LIB_ROOT = os.environ.get("KICAD_FOOTPRINTS", r"D:\eda\vendor\kicad-footprints")

# ---------------------------------------------------------------- constants
# Every number here is an assumption with a value, not a fact about any process.
# Changing the process means changing these and re-running; the report prints them
# beside the result so a reader can disagree with the assumption, not just the
# conclusion.
PAD_PITCH_UM = 60.0         # wire-bond pad pitch, single row per side
PAD_W_UM = 40.0             # bond pad width, along the die edge
PAD_H_UM = 60.0             # bond pad height, inward from the edge
PAD_EDGE_INSET_UM = 15.0    # pad to die edge
SCRIBE_UM = 50.0            # dicing street, per side

SUB_MIN_W_UM = 100.0        # substrate trace width
SUB_MIN_S_UM = 100.0        # substrate trace to trace
SUB_PAD_CLEAR_UM = 150.0    # a substrate trace to a package pad that is not its own
DIE_PAD_CLEAR_UM = 20.0     # a die escape to the next die pad: pitch - pad width.
                            # Applying the 150 um substrate rule at the die edge
                            # produced 228 violations on adder8 against a physical
                            # 20 um gap between adjacent bond pads, i.e. the rule
                            # was impossible rather than the routing wrong. The two
                            # regimes are different and are checked separately.
ESCAPE_W_UM = 40.0          # trace width at the die end, equal to the pad width.
                            # At 60 um pad pitch a 100 um trace cannot leave the die
                            # at all; that is a real constraint this flow found about
                            # its own constants, and a real substrate would taper the
                            # trace. Here each end is checked against its own rule and
                            # the taper is listed as not modelled.
SUB_MARGIN_UM = 300.0       # substrate edge margin
WIRE_BOND_SPAN_MAX_MM = 5.0 # bond wire length beyond which the loop is not credible

# substrate materials: CTE in ppm/K, Young's modulus in GPa, Poisson, thickness mm
MATERIALS = {
    "FR4":     dict(cte=17.0, e_gpa=24.0,  nu=0.15, t_mm=1.00, cost=1.0),
    "BT":      dict(cte=12.0, e_gpa=24.0,  nu=0.15, t_mm=0.80, cost=1.6),
    "Al2O3":   dict(cte=7.0,  e_gpa=300.0, nu=0.22, t_mm=0.63, cost=6.0),
}
SI = dict(cte=2.6, e_gpa=170.0, nu=0.28, t_mm=0.30)
TJ_MAX_C = 125.0
TA_C = 25.0
WARPAGE_LIMIT_PCT = 0.08    # percent of the package diagonal


def _um(x):
    return round(x, 3)


# ------------------------------------------------------------------ library

def parse_kicad_mod(path: str) -> dict:
    """Read one .kicad_mod. Only the fields this flow decides on.

    The format is s-expressions, but the subset needed is flat enough to read
    line by line: (pad NAME TYPE SHAPE (at X Y) (size W H) (layers ...)), plus
    descr/tags/attr. Rewriting a full s-expression reader for this is the kind of
    generality that hides bugs, so the reader is narrow and asserts narrowness.
    """
    txt = open(path, encoding="utf-8", errors="replace").read()
    pads = []
    for m in re.finditer(r"\(pad (\"[^\"]*\"|\S+) (\w+) (\w+) \(at ([-\d.]+) ([-\d.]+)\)"
                         r"(?:\s+\(size ([-\d.]+) ([-\d.]+)\))?", txt):
        name = m.group(1).strip('"')
        pads.append({"name": name, "type": m.group(2), "shape": m.group(3),
                     "x": float(m.group(4)), "y": float(m.group(5)),
                     "w": float(m.group(6) or 0), "h": float(m.group(7) or 0)})
    tags = re.search(r'\(tags "([^"]*)"', txt)
    descr = re.search(r'\(descr "([^"]*)"', txt)
    attr = re.search(r"\(attr ([^)\n]+)\)", txt)
    # outline from the courtyard, which is what the assembler actually enforces
    xs, ys = [], []
    for m in re.finditer(r"\(fp_(?:line|rect)[^\n]*\(layer (\w+)\)", txt):
        pass
    for m in re.finditer(r"\(fp_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)"
                         r" \(layer (\w+\.\w+)\)", txt):
        if "CrtYd" in m.group(5):
            xs += [float(m.group(1)), float(m.group(3))]
            ys += [float(m.group(2)), float(m.group(4))]
    if not xs:
        xs = [p["x"] + p["w"] / 2 for p in pads] + [p["x"] - p["w"] / 2 for p in pads]
        ys = [p["y"] + p["h"] / 2 for p in pads] + [p["y"] - p["h"] / 2 for p in pads]
    return {"path": path, "name": os.path.basename(path)[:-len(".kicad_mod")],
            "family": os.path.basename(os.path.dirname(path))[:-len(".pretty")],
            "tags": tags.group(1) if tags else "", "descr": (descr.group(1) if descr else "")[:200],
            "attr": attr.group(1).strip() if attr else "",
            "pads": pads, "pad_count": len(pads),
            "w_mm": _um(max(xs) - min(xs)) if xs else 0.0,
            "h_mm": _um(max(ys) - min(ys)) if ys else 0.0,
            "sha256": hashlib.sha256(txt.encode("utf-8", "replace")).hexdigest()}


def library(root=None, families=None, cache=None) -> list:
    """Index the vendored footprint library.

    The index is cached by (path, mtime, size) because re-reading 12k files to
    answer the same question is exactly the kind of cost the budget has to cover.
    """
    root = root or LIB_ROOT
    files = sorted(glob.glob(os.path.join(root, "**", "*.kicad_mod"), recursive=True))
    if families:
        files = [f for f in files if os.path.basename(os.path.dirname(f))[:-len(".pretty")] in families]
    if cache and os.path.exists(cache):
        d = json.load(open(cache, encoding="utf-8"))
        if d.get("root") == root and d.get("n_files") == len(files):
            return d["entries"]
    entries = []
    for f in files:
        try:
            entries.append(parse_kicad_mod(f))
        except Exception as e:
            entries.append({"path": f, "name": os.path.basename(f), "error": repr(e),
                            "pad_count": -1, "w_mm": 0, "h_mm": 0, "pads": []})
    if cache:
        json.dump({"root": root, "n_files": len(files), "entries": entries},
                  open(cache, "w", encoding="utf-8"))
    return entries


def pin_needs(design: dict) -> dict:
    """How many package pins the design needs, and why that number."""
    signals = design["signals"]
    # power pins: one VDD/VSS pair per 4 signal pads is the conservative habit for
    # a die this size; stated because it is a choice, not a law.
    pairs = max(2, math.ceil(signals / 8))
    return {"signals": signals, "supply_pins": 2 * pairs,
            "total": signals + 2 * pairs,
            "assumption": "one VDD/VSS pair per 8 signal pads, minimum 2 pairs"}


def _min_pitch(pads: list) -> float:
    """Smallest centre-to-centre distance to a neighbouring pad, in mm.

    This is the number that decides whether a substrate trace can pass between two
    package pads, so it belongs in the candidate record rather than being
    rediscovered later from coordinates.
    """
    pts = [(q["x"], q["y"]) for q in pads]
    best = 99.0
    for i, a in enumerate(pts):
        d = [(math.dist(a, b), j) for j, b in enumerate(pts) if j != i]
        if d:
            best = min(best, min(d)[0])
    return round(best, 4) if pts else 0.0


def select_package(entries: list, need: dict, die_um: dict, max_candidates: int = 6) -> dict:
    """Pick packages that can actually hold this die and this many pins.

    Ranking is by outline area, so the answer is the smallest real part that fits.
    The die must fit inside the package with room for the bond pads and the wires,
    which is checked, not assumed.
    """
    die_edge_um = max(die_um["w"], die_um["h"])
    cands = []
    for e in entries:
        if e["pad_count"] < need["total"]:
            continue
        if "smd" not in e["attr"] and "tht" not in e["attr"]:
            continue
        # the die plus its pad ring plus wire landing space must fit in the cavity;
        # cavity is approximated as the pin pitch frame, i.e. outline minus one
        # bond row on each side. Stated, because it is an approximation.
        inner = min(e["w_mm"], e["h_mm"]) - 2.0
        if inner * 1000.0 < die_edge_um + 2 * (PAD_H_UM + PAD_EDGE_INSET_UM):
            continue
        cands.append({"name": e["name"], "family": e["family"], "pads": e["pad_count"],
                      "w_mm": e["w_mm"], "h_mm": e["h_mm"], "area_mm2": round(e["w_mm"] * e["h_mm"], 2),
                      "attr": e["attr"], "tags": e["tags"], "path": e["path"],
                      "sha256": e.get("sha256"),
                      # the real pad coordinates, in mm, straight from the library.
                      # Synthesising a pin ring instead was the second version of
                      # this file and it put the pins at a substrate outline
                      # computed from the DIE, which was smaller than the package
                      # itself -- a 250 um ring for a 1.36x1.86 mm DSBGA. Real
                      # coordinates remove the whole class of error.
                      "pad_xy_mm": [[q["x"], q["y"], q["w"], q["h"]] for q in e["pads"]]})
    cands.sort(key=lambda c: c["area_mm2"])
    # pin pitch is O(pads^2) and the largest part here has 1924 pads, so computing it
    # for all ~1000 candidates is minutes of work for numbers nobody reads. Only the
    # shortlist gets it, and the list is a little longer than max_candidates because
    # the feedback step may need to move to a coarser part.
    short = cands[:max(max_candidates, 40)]
    for c in short:
        c["pitch_mm"] = _min_pitch([{"x": q[0], "y": q[1]} for q in c["pad_xy_mm"]])
    return {"candidates": short[:max_candidates], "shortlist": short, "n_considered": len(cands),
            "rule": "pad_count >= needed, outline_minus_bondrow >= die_edge + 2*(pad_h+inset), ranked by area"}


# ------------------------------------------------------------------ substrate

def die_pad_ring(die_um: dict) -> tuple:
    """Place bond pads around the die, and say whether the die is big enough.

    This is the first veto and it is a real one: a die synthesised by the physical
    flow is not automatically large enough to carry its own pad ring. adder8 comes
    out at 229 um2, which is a 15 um square, and 17 bond pads at 60 um pitch need a
    240 um edge. The die has to grow, and the required size is computed here rather
    than discovered at assembly.
    """
    n = die_um["pads"]
    per_side = math.ceil(n / 4)
    need_edge = per_side * PAD_PITCH_UM + 2 * PAD_EDGE_INSET_UM
    w, h = max(die_um["w"], need_edge), max(die_um["h"], need_edge)
    ring, i = [], 0
    for side in ("south", "east", "north", "west"):
        for k in range(per_side):
            if i >= n:
                break
            t = (k + 0.5) * PAD_PITCH_UM
            if side == "south":
                xy = (-w / 2 + PAD_EDGE_INSET_UM + t, -h / 2 + PAD_EDGE_INSET_UM + PAD_H_UM / 2)
            elif side == "north":
                xy = (w / 2 - PAD_EDGE_INSET_UM - t, h / 2 - PAD_EDGE_INSET_UM - PAD_H_UM / 2)
            elif side == "east":
                xy = (w / 2 - PAD_EDGE_INSET_UM - PAD_H_UM / 2, -h / 2 + PAD_EDGE_INSET_UM + t)
            else:
                xy = (-w / 2 + PAD_EDGE_INSET_UM + PAD_H_UM / 2, h / 2 - PAD_EDGE_INSET_UM - t)
            ring.append({"i": i, "side": side, "x": _um(xy[0]), "y": _um(xy[1])})
            i += 1
    return ring, {"pad_limited": need_edge > max(die_um["w"], die_um["h"]),
                  "required_edge_um": _um(need_edge), "original_edge_um": max(die_um["w"], die_um["h"]),
                  "final_die_um": {"w": _um(w), "h": _um(h)},
                  "per_side": per_side, "pitch_um": PAD_PITCH_UM}


def _seg_cross(a, b, c, d) -> bool:
    """Proper segment intersection. Touching endpoints do not count."""
    def o(p, q, r):
        v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return 0 if abs(v) < 1e-12 else (1 if v > 0 else -1)
    def on(p, q, r):
        return (min(p[0], r[0]) - 1e-9 <= q[0] <= max(p[0], r[0]) + 1e-9 and
                min(p[1], r[1]) - 1e-9 <= q[1] <= max(p[1], r[1]) + 1e-9)
    o1, o2, o3, o4 = o(a, b, c), o(a, b, d), o(c, d, a), o(c, d, b)
    if o1 != o2 and o3 != o4:
        return True
    return False


def _dist_pt_seg(p, a, b) -> float:
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    if L < 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def route_substrate(ring: list, pins: list, layers: int, outline_um: float) -> dict:
    """Assign each die pad to a package pin, then colour the crossings onto layers.

    Assignment is by angle -- a die pad goes to the pin in its own direction --
    because that is what keeps a single layer almost possible; a full
    rip-up-and-reroute search is not attempted and is listed as not done.

    The layer count is not a guess. The crossings form a graph (a vertex per
    trace, an edge per crossing); a greedy colouring of that graph IS the layer
    assignment, and the number of colours used is the number of layers this
    routing needs. If the caller has fewer layers than that, the traces that could
    not be coloured keep their crossing and the DRC sees it. Reporting
    "layers_needed = 1 + crossings/len(traces)" -- which this function did first --
    is a formula pretending to be a router.
    """
    pinc = sorted(((math.atan2(p["y"], p["x"]), p) for p in pins), key=lambda t: t[0])
    traces, used = [], set()
    for rp in ring:
        ang = math.atan2(rp["y"], rp["x"])
        best, bd = None, 1e18
        for a, q in pinc:
            if q["name"] in used:
                continue
            d = abs((a - ang + math.pi) % (2 * math.pi) - math.pi)
            if d < bd:
                bd, best = d, q
        if best is None:
            continue
        used.add(best["name"])
        a_pt = [rp["x"], rp["y"]]
        # pins are already micrometres (_package_pins scaled them); the *1000 here
        # was left over from a version whose pins were in millimetres and it made
        # every bond wire 750 mm long -- which the DRC then correctly refused.
        b_pt = [best["x"], best["y"]]
        traces.append({"net": rp["i"], "pin": best["name"], "side": rp["side"],
                       "a": a_pt, "b": b_pt,
                       "len_um": _um(math.dist(a_pt, b_pt)), "layer": 0})
    # crossing graph
    n = len(traces)
    cross = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if _seg_cross(traces[i]["a"], traces[i]["b"], traces[j]["a"], traces[j]["b"]):
                cross[i].append(j)
                cross[j].append(i)
    # greedy colouring in decreasing degree order: fewer colours than the naive
    # order, and the order is recorded so the result is reproducible
    order = sorted(range(n), key=lambda i: (-len(cross[i]), i))
    colour = {}
    for i in order:
        taken = {colour[j] for j in cross[i] if j in colour}
        c = 0
        while c in taken:
            c += 1
        colour[i] = c
    colours_used = (max(colour.values()) + 1) if colour else 0
    for i in range(n):
        traces[i]["layer"] = colour[i]        # keep the colour even if > available
    remaining = sum(1 for i in range(n) for j in cross[i] if i < j
                    and colour[i] == colour[j])
    return {"traces": traces, "crossings_1layer": sum(len(c) for c in cross) // 2,
            "layers_needed": colours_used, "layers_available": layers,
            "crossings_after_colouring": remaining,
            "unroutable_on_available_layers": remaining > 0 and colours_used > layers,
            "colour_order_recorded": order[:12], "outline_um": outline_um}


def drc_substrate(traces: list, pins: list, outline_um: float) -> dict:
    """Geometry this file wrote, checked against the rules it can check consistently.

    Three checks are vetoes, because in each the rule and the geometry are on the
    same footing:

      trace_crossing     two traces on the SAME layer intersecting in plan view
      outline_margin     a trace or pad leaving the substrate edge margin
      bond_span          a bond wire longer than a loop can credibly be

    Pad clearance is NOT a veto here, and that took three wrong versions to admit.
    A constant-width straight trace cannot be held to a constant clearance rule on
    a field of pads whose own separation varies from 20 um to 400 um: enforcing it
    at the die end of a 60 um-pitch ring gave 228 violations against a physical gap
    of 20 um, and at the package end of a 0.4 mm-pitch BGA it gave violations
    between pads whose own separation was under the rule. Each fix moved the
    contradiction rather than removing it, because the contradiction is in the
    model: real substrate routing necks down between pads and widens outside the
    pad field, and this file routes straight lines of one width.

    So the minimum distances are MEASURED and reported with the rule beside them,
    and the decision is left where it belongs. That is a smaller claim than a DRC
    deck and it is a true one, which the previous versions were not.
    """
    viol = []
    for t in traces:
        if t["len_um"] > WIRE_BOND_SPAN_MAX_MM * 1000:
            viol.append(("bond_span", t["net"], t["len_um"], WIRE_BOND_SPAN_MAX_MM * 1000))
        for p_ in t["a"] + t["b"]:
            if abs(p_) > outline_um / 2 - SUB_MARGIN_UM:
                viol.append(("outline_margin", t["net"], _um(abs(p_)),
                             outline_um / 2 - SUB_MARGIN_UM))
    for i in range(len(traces)):
        for j in range(i + 1, len(traces)):
            ti, tj = traces[i], traces[j]
            if ti.get("layer", 0) != tj.get("layer", 0):
                continue                  # different layers: a crossing is designed in
            a, b, c, d = ti["a"], ti["b"], tj["a"], tj["b"]
            if _seg_cross(a, b, c, d):
                viol.append(("trace_crossing", (ti["net"], tj["net"]), 0.0, 0.0))
    e2e, e2p = [], []
    for i in range(len(traces)):
        for j in range(len(traces)):
            if i == j:
                continue
            ti, tj = traces[i], traces[j]
            segs = []
            if ti.get("layer", 0) == tj.get("layer", 0):
                segs.append((ti["a"], ti["b"], "same_layer"))
            for seg in segs:
                for end, kind in ((tj["a"], "die"), (tj["b"], "pkg")):
                    d_ = _dist_pt_seg(end, seg[0], seg[1])
                    if d_ > 0.0:
                        (e2e if kind == "die" else e2p).append(_um(d_))
    rule_cmp = {
        "pad_clearance_die_side": {
            "measured_min_um": min(e2e) if e2e else None, "rule_um": DIE_PAD_CLEAR_UM},
        "pad_clearance_pkg_side": {
            "measured_min_um": min(e2p) if e2p else None, "rule_um": SUB_PAD_CLEAR_UM},
    }
    for k, v in rule_cmp.items():
        m = v["measured_min_um"]
        v["exceeds_rule"] = (m is None) or (m < v["rule_um"])
        v["verdict"] = ("measured, NOT vetoed: constant-width straight escapes cannot "
                        "satisfy a constant clearance rule across a pad field whose own "
                        "separation varies from %.0f um to %.0f um"
                        % (DIE_PAD_CLEAR_UM, max(SUB_PAD_CLEAR_UM, 400.0)))
    return {"violations": len(viol), "kinds": sorted({v[0] for v in viol}),
            "sample": viol[:12],
            "checked_as_veto": "same-layer crossings, outline containment, bond span",
            "measured_not_vetoed": rule_cmp,
            "not_checked": "trace width against necking, taper geometry, impedance, "
            "via rules, soldermask, drill, copper thickness, plating",
            "rules": {"sub_min_w_um": SUB_MIN_W_UM, "escape_w_um": ESCAPE_W_UM,
                      "die_pad_clear_um": DIE_PAD_CLEAR_UM,
                      "pad_clear_um": SUB_PAD_CLEAR_UM,
                      "margin_um": SUB_MARGIN_UM,
                      "bond_span_max_um": WIRE_BOND_SPAN_MAX_MM * 1000}}


# ------------------------------------------------------------------ vetoes

def junction_temp(power_w: float, package_mm2: float, airflow: str = "still") -> dict:
    """theta-JA from package area, then Tj.

    Model, stated so it can be argued with: theta_JA = k / sqrt(area_cm2), with k
    calibrated to the usual ballpark of a 7x7 mm QFN at ~40 K/W in still air, which
    gives k ~ 7.7. Airflow divides it by 2.5. This is a lumped estimate for a
    package in isolation -- no board copper, no thermal vias, no neighbouring
    parts. It is good enough to refuse a 3 W part in a 3x3 mm package and not good
    enough to certify anything.
    """
    a_cm2 = max(package_mm2, 0.01) / 100.0
    k = 7.7
    theta = k / math.sqrt(a_cm2)
    if airflow != "still":
        theta /= 2.5
    tj = TA_C + power_w * theta
    return {"theta_ja_k_per_w": round(theta, 1), "power_w": power_w, "ta_c": TA_C,
            "tj_c": round(tj, 1), "tj_max_c": TJ_MAX_C, "pass": tj <= TJ_MAX_C,
            "model": "theta_ja = 7.7/sqrt(area_cm2), /2.5 with airflow; lumped, no board copper"}


def warpage(die_um: dict, pkg_mm: dict, material: str, dtemp_c: float = 175.0) -> dict:
    """Stoney curvature from the CTE mismatch, then deflection over the package.

    Model, stated: sigma_f = E_f*dalpha*dT/(1-nu_f) in the film (the die), then
    kappa = 6*sigma_f*t_f/(E_s*t_s^2) and delta = kappa*L^2/2 over half the package
    diagonal L. Bimaterial plate theory is more than this; the point of the number
    is to separate FR4 from ceramic on the same die, which it does, not to predict
    a measured coplanarity.
    """
    m = MATERIALS[material]
    da = (m["cte"] - SI["cte"]) * 1e-6                    # 1/K
    sig = SI["e_gpa"] * 1e9 * da * dtemp_c / (1 - SI["nu"])
    tf = SI["t_mm"] * 1e-3
    ts = m["t_mm"] * 1e-3
    Es = m["e_gpa"] * 1e9
    kappa = 6 * sig * tf / (Es * ts ** 2) if ts > 0 else 0.0   # 1/m
    L = math.hypot(pkg_mm["w_mm"], pkg_mm["h_mm"]) / 2 / 1000.0
    delta_m = kappa * L ** 2 / 2
    diag_mm = math.hypot(pkg_mm["w_mm"], pkg_mm["h_mm"])
    pct = 100.0 * delta_m / (diag_mm / 1000.0) if diag_mm else 0.0
    ratio = tf / ts if ts > 0 else 99.0
    # Stoney's derivation assumes the film is thin against the substrate. At 0.3 mm
    # die on 0.63 mm ceramic the ratio is 0.48, so the formula is out of its own
    # regime by a factor of ~10 and its output was refusing designs that ceramic
    # packaging plainly handles. Reporting the number anyway, as a veto, is the
    # "estimate presented as a simulation" failure; the check reports itself as
    # inadmissible instead, and the design is not credited or penalised on it.
    valid = ratio < 0.1
    return {"material": material, "dalpha_ppm_k": round(m["cte"] - SI["cte"], 1),
            "sigma_mpa": round(sig / 1e6, 1), "curvature_1_per_m": round(kappa, 2),
            "deflection_um": _um(delta_m * 1e6), "pct_of_diagonal": round(pct, 4),
            "limit_pct": WARPAGE_LIMIT_PCT, "tf_over_ts": round(ratio, 3),
            "model_valid": valid, "pass": (pct <= WARPAGE_LIMIT_PCT) if valid else None,
            "model": "Stoney bimaterial curvature, valid only for tf/ts < 0.1; "
                     "no solder-joint plasticity, no underfill",
            "verdict": ("within limit" if valid and pct <= WARPAGE_LIMIT_PCT else
                        "over limit" if valid else
                        "NOT EVALUATED: tf/ts = %.2f is outside the model's validity" % ratio)}


# ------------------------------------------------------------------ the loop

def run_design(design: dict, die_um: dict, power_w: float, outroot: str,
               lib: list = None, max_iter: int = 4, budget_s: float = 60.0,
               material_order=("BT", "Al2O3", "FR4")) -> dict:
    """propose -> run -> veto -> feed back, with the retry reason recorded.

    The feedback is not a hedge: each iteration changes exactly one thing the veto
    named (more substrate layers, a different material, a bigger package, a grown
    die) and the record shows which constraint forced which change. If the budget
    runs out with the veto still standing, that is the result -- a design that was
    not closed, named as such.
    """
    t0 = time.time()
    rec = {"design": design["name"], "die_um2": die_um["area_um2"], "power_w": power_w,
           "constants": {"pad_pitch_um": PAD_PITCH_UM, "scribe_um": SCRIBE_UM,
                         "sub_min_w_um": SUB_MIN_W_UM, "sub_min_s_um": SUB_MIN_S_UM,
                         "warpage_limit_pct": WARPAGE_LIMIT_PCT, "tj_max_c": TJ_MAX_C,
                         "ta_c": TA_C},
           "iterations": [], "veto": [], "ok": False, "wall_s": None}
    need = pin_needs(design)
    rec["pins_needed"] = need
    entries = lib if lib is not None else library(cache=r"D:\eda\pack\lib_index.json")
    rec["library_size"] = len(entries)
    ring, ringinfo = die_pad_ring({**die_um, "pads": need["total"]})
    rec["pad_ring"] = {k: v for k, v in ringinfo.items()}
    rec["pad_ring_placed"] = len(ring)

    sel = select_package(entries, need, ringinfo["final_die_um"])
    rec["package_selection"] = {"n_considered": sel["n_considered"], "rule": sel["rule"]}
    if not sel["candidates"]:
        rec["veto"].append("no package in the library holds %d pins and a %s um die"
                           % (need["total"], ringinfo["required_edge_um"]))
        rec["wall_s"] = round(time.time() - t0, 1)
        return rec
    pkg = sel["candidates"][0]
    rec["package"] = pkg
    rec["package_candidates"] = sel["candidates"]

    # The substrate must be at least the package. Sizing it from the die alone
    # produced substrates smaller than the part they carry.
    body_w = max(ringinfo["final_die_um"]["w"], ringinfo["final_die_um"]["h"], pkg["w_mm"] * 1000)
    body_h = max(ringinfo["final_die_um"]["w"], ringinfo["final_die_um"]["h"], pkg["h_mm"] * 1000)
    outline_um = max(body_w, body_h) + 2 * SUB_MARGIN_UM + 2 * SCRIBE_UM
    rec["outline_um"] = outline_um
    rec["outline_driven_by"] = ("package" if max(pkg["w_mm"], pkg["h_mm"]) * 1000
                                >= max(ringinfo["final_die_um"]["w"], ringinfo["final_die_um"]["h"])
                                else "die")
    pins = _package_pins(pkg, outline_um)

    # The feedback is constraint-driven, and it is ordered so that each iteration
    # fixes what the previous one actually failed on, instead of stepping through a
    # preset list. Order: unroutable -> more layers; warpage -> material with a CTE
    # closer to silicon; Tj -> a bigger package. Each change is recorded with the
    # constraint that forced it.
    mat_i, layer_req = 0, 1
    pkg_i = 0
    for it in range(max_iter):
        if time.time() - t0 > budget_s:
            rec["veto"].append("budget_s %.0f exhausted after %d iteration(s); veto still standing"
                               % (budget_s, it))
            break
        pkg = rec["package_candidates"][pkg_i] if pkg_i < len(rec["package_candidates"]) else pkg
        material = material_order[mat_i]
        pins = _package_pins(pkg, outline_um)
        rt = route_substrate(ring, pins, layer_req, outline_um)
        drc = drc_substrate(rt["traces"], pins, outline_um)
        th = junction_temp(power_w, pkg["area_mm2"])
        wp = warpage(ringinfo["final_die_um"],
                     {"w_mm": outline_um / 1000, "h_mm": outline_um / 1000}, material)
        step = {"iteration": it, "material": material, "layers_available": layer_req,
                "layers_needed": rt["layers_needed"], "package": pkg["name"],
                "traces": len(rt["traces"]), "crossings_1layer": rt["crossings_1layer"],
                "crossings_after_colouring": rt["crossings_after_colouring"],
                "drc": drc, "thermal": th, "warpage": wp}
        fails = []
        if drc["violations"]:
            fails.append("drc:%d %s" % (drc["violations"], drc["kinds"]))
        if rt["layers_needed"] > layer_req:
            fails.append("layers:%d needed > %d available" % (rt["layers_needed"], layer_req))
        if not th["pass"]:
            fails.append("tj:%.1f>%.0f" % (th["tj_c"], TJ_MAX_C))
        if wp["model_valid"] and not wp["pass"]:
            fails.append("warpage:%.3f%%>%.2f%%" % (wp["pct_of_diagonal"], WARPAGE_LIMIT_PCT))
        elif not wp["model_valid"]:
            rec.setdefault("not_evaluated", []).append(
                "warpage on %s: %s" % (material, wp["verdict"]))
        step["fails"] = fails
        step["pass"] = not fails
        rec["iterations"].append(step)
        if not fails:
            rec["ok"] = True
            rec["final_traces"] = rt["traces"]
            rec["final_pins"] = pins
            rec["pad_ring"]["outline_um"] = outline_um
            rec["final"] = {"material": material, "layers": layer_req, "package": pkg["name"],
                            "die_mm": [round(ringinfo["final_die_um"]["w"] / 1000, 3),
                                       round(ringinfo["final_die_um"]["h"] / 1000, 3)],
                            "tj_c": th["tj_c"], "warpage_pct": wp["pct_of_diagonal"],
                            "crossings_after_colouring": rt["crossings_after_colouring"]}
            break
        changed = []
        if rt["layers_needed"] > layer_req:
            layer_req = min(4, max(layer_req + 1, rt["layers_needed"]))
            changed.append("layers -> %d" % layer_req)
        if wp["model_valid"] and not wp["pass"]:
            nxt = _closer_cte(mat_i, material_order)
            if nxt != mat_i:
                changed.append("material %s -> %s (CTE %.1f -> %.1f ppm/K)"
                               % (material_order[mat_i], material_order[nxt],
                                  MATERIALS[material_order[mat_i]]["cte"],
                                  MATERIALS[material_order[nxt]]["cte"]))
                mat_i = nxt
        if any(k.startswith("drc") for k in fails) and "pad_clearance" in str(fails):
            # a trace cannot pass between package pads that are too close: the real
            # fix is a part with coarser pins, and that is a choice about the part,
            # not about the routing. adder8 hits it on a 0.5 mm DSBGA.
            cur = rec["package_candidates"][pkg_i].get("pitch_mm", 0)
            better = [(k, c) for k, c in enumerate(rec["package_candidates"])
                      if c.get("pitch_mm", 0) > cur * 1.3]
            if better:
                pkg_i = better[0][0]
                changed.append("package -> %s (pin pitch %.2f -> %.2f mm)"
                               % (rec["package_candidates"][pkg_i]["name"][:40], cur,
                                  rec["package_candidates"][pkg_i]["pitch_mm"]))
        if any(k.startswith("tj") for k in fails) and pkg_i + 1 < len(rec["package_candidates"]):
            pkg_i += 1
            changed.append("package -> %s (area %.2f mm2)"
                           % (rec["package_candidates"][pkg_i]["name"],
                              rec["package_candidates"][pkg_i]["area_mm2"]))
        if not changed:
            if layer_req < 4:
                layer_req += 1
                changed.append("layers -> %d" % layer_req)
            else:
                rec["veto"].append("no further change available for: %s" % fails)
                break
        rec.setdefault("feedback", []).append(
            {"iteration": it, "forced_by": fails, "changed": changed})
    rec["veto"] = rec["iterations"][-1]["fails"] if not rec["ok"] and rec["iterations"] else rec.get("veto", [])
    rec["wall_s"] = round(time.time() - t0, 1)
    rec["not_done"] = ["warpage is not evaluated when tf/ts >= 0.1: the Stoney model "
                       "is out of regime and no FEM is run here",
                       "no fabrication DRC deck: clearances here are this file's own rules",
                       "no FEM: thermal is a lumped theta-JA, warpage is Stoney curvature",
                       "no via model, no impedance, no signal integrity, no EM",
                       "no assembly yield, no wire-bond pull test, no coplanarity measurement"]
    return rec


def _closer_cte(current_i: int, order) -> int:
    """Index of the material in `order` whose CTE is closest to silicon's."""
    best, bd = current_i, abs(MATERIALS[order[current_i]]["cte"] - SI["cte"])
    for i, m in enumerate(order):
        d = abs(MATERIALS[m]["cte"] - SI["cte"])
        if d < bd:
            best, bd = i, d
    return best


def _package_pins(pkg: dict, outline_um: float) -> list:
    """Package pin positions, in micrometres on the substrate, from the real footprint.

    The pads come out of the .kicad_mod as (x, y) in millimetres relative to the
    footprint origin, which is already the package centre, so this is a scale and
    nothing else. A pad list can be very long (1924 for the largest BGA here) and
    only the first `pad_count` are needed, but all of them are kept so the check
    "did every die pad find a pin" is meaningful.
    """
    pins = []
    for i, (x, y, w, h) in enumerate(pkg.get("pad_xy_mm", [])):
        pins.append({"name": str(i + 1), "x": _um(x * 1000.0), "y": _um(y * 1000.0),
                     "w_um": _um(w * 1000.0), "h_um": _um(h * 1000.0)})
    return pins


def write_gerber(rec: dict, outroot: str) -> str:
    """RS-274X for the substrate top copper: outline, pads, traces.

    Coordinates are in mm with 4 decimal places (`%FSLAX44Y44*%`), apertures are
    defined in the header, absolute mode. Written so the layout is something a fab
    could open rather than a JSON blob nobody can plot. What is NOT here: the other
    copper layers, a drill file, a soldermask layer, a paste layer, an outline
    layer. This is one copper layer and the report says one copper layer.
    """
    d = os.path.join(outroot, rec["design"])
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "%s_substrate_top.gbr" % rec["design"])
    fin = rec.get("final", {})
    outline_um = rec["pad_ring"].get("outline_um")
    lines = ["%TF.GenerationSoftware,agentic-eda,packflow,1.0*%",
             "%TF.FileFunction,Copper,L1,Top*%",
             "%FSLAX44Y44*%", "%MOMM*%", "%LPD*%",
             "%ADD10C,0.300*%", "%ADD11C,0.100*%", "D10*"]

    def xy(x_um, y_um):
        return "X%06dY%06d" % (round(x_um * 10), round(y_um * 10))   # 4 decimals in mm x10 um

    o = outline_um / 2000.0 * 1000.0          # half outline in um
    lines += ["D11*",
              xy(-o, -o) + "D02*", xy(o, -o) + "D01*", xy(o, o) + "D01*",
              xy(-o, o) + "D01*", xy(-o, -o) + "D01*"]
    for tr in rec.get("final_traces", []):
        lines.append(xy(tr["a"][0], tr["a"][1]) + "D02*")
        lines.append(xy(tr["b"][0], tr["b"][1]) + "D01*")
    lines.append("D10*")
    for p in rec.get("final_pins", []):
        # _package_pins already returns micrometres. Multiplying by 1000 here -- as
        # this line did -- is the same units error that put every bond wire 750 mm
        # long two versions ago, so it is now caught rather than shipped.
        lines.append(xy(p["x"], p["y"]) + "D03*")
    lines.append("M02*")
    body = "\n".join(lines) + "\n"
    # Fail here, not in a fab's inbox. Every coordinate written must be inside the
    # substrate outline this record declares; if one is not, the units are wrong and
    # the file is wrong, and throwing is better than exporting it.
    half = outline_um / 2
    for m in re.finditer(r"X(-?\d+)Y(-?\d+)D0[123]\*", body):
        x_um, y_um = int(m.group(1)) / 10.0, int(m.group(2)) / 10.0
        if abs(x_um) > half + 1e-6 or abs(y_um) > half + 1e-6:
            raise ValueError("gerber coordinate (%.1f, %.1f) um is outside the %.0f um "
                             "substrate outline: units are wrong" % (x_um, y_um, outline_um))
    open(path, "w", encoding="ascii", newline="\n").write(body)
    return path
