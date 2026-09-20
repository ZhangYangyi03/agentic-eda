
"""synth_search: synthesis-script search with a verifier that must prove itself.

Why the verifier selection is not a detail: ABC's cec only applies to an AIG, so
on a sequential netlist it errors out and proves nothing. A harness that reported
its silence as success would badge every sequential result as 'equivalent' while
checking nothing. So the design's own shape picks the verifier:

    latches == 0  ->  abc  'cec <reference>'          (SAT/structural, gives a counterexample)
    latches  > 0  ->  yosys equiv_simple + equiv_induct -seq N, require 0 unproven

and either way `gate_selftest` runs first on a netlist corrupted on purpose: if
the verifier accepts that, the run aborts instead of reporting numbers.

Toolchain, measured on this host:
    apt yosys 0.9   -> elaborator only; its bundled ABC produces no output.blif
    yowasp-yosys    -> ABC pass never returns (even for one gate); unusable here
    berkeley-abc    -> the actual optimiser, with cec
    yosys -noabc    -> enough to emit a gate-level BLIF worth optimising
"""
from __future__ import annotations
import json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spine import Flow, Stage, sha256

WSL = ["wsl", "-d", "Ubuntu-22.04", "-e", "bash", "-lc"]
PRELUDE = "export LANG=C LC_ALL=C; "

def sh(cmd, t=300, merge=True):
    """Run in WSL; stdout and stderr kept apart.

    Both details are load-bearing. ABC localises its messages, so LANG must be C.
    WSL writes a localhost-proxy warning to stderr, and when that was merged into
    stdout it pushed the ABC statistics line out of a `tail -4` window -- four
    candidates that had compiled and proved were scored as failures.
    """
    r = subprocess.run(WSL + [PRELUDE + cmd], capture_output=True, text=True, timeout=t,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or ""), (r.stderr or "")

def to_wsl(p: str) -> str:
    p = os.path.abspath(p)
    return "/mnt/" + p[0].lower() + p[2:].replace("\\", "/")

# Stats are read field by field rather than by one regex over the whole line.
# Measured reasons, both of which silently discarded legal candidates:
#   - `and = 473 (choice = 22)  lev = 35` -- an optional " (choice = N)" infix
#     sits between the two fields and a `\s+lev` pattern never matches it
#   - after `if`, ABC reports a mapped network as `aig = 1157 lev = 5`, with no
#     `and` field at all, so an area regex finds nothing
# A candidate whose metric is missing has not failed; it was measured in a
# different unit, and that distinction is now kept.
_FIELD = re.compile(r"\b(and|aig|lev|lat|nd|edge)\s*=\s*(\d+)")

def parse_stats(body: str):
    """Read the last ABC statistics line in a body. Returns None if there is none."""
    # The line is recognised by pattern, not by the substring "and =" -- ABC
    # pads its fields, so the real line reads `aig  =   218` with two spaces,
    # and a substring test for "aig =" missed it. That silently dropped every
    # candidate whose script contained `if` into "unmeasured", which is the same
    # mistake this project already made once with a different regex.
    line, _stats_re = None, re.compile(r"\b(and|aig|nd)\s*=\s*\d+.*\blev\s*=\s*\d+")
    for l in body.splitlines():
        if _stats_re.search(l):
            line = l
    if line is None:
        return None
    f = {k: int(v) for k, v in _FIELD.findall(line)}
    if "lev" not in f:
        return None
    # preference order matters: 'and' is the gate count, 'aig' is what ABC
    # reports instead once the network has been mapped by `if` (not comparable
    # with 'and', and flagged as such by `metric`), and 'nd' is the node count
    # for a sequential network, where neither of the first two is emitted.
    area, metric = None, None
    for key in ("and", "aig", "nd"):
        if key in f:
            area, metric = f[key], key
            break
    if area is None:
        return None
    return {"area": area, "metric": metric, "lev": f["lev"], "lat": f.get("lat", 0),
            "lev_unit": "lut" if metric == "aig" else "aig",
            "nd": f.get("nd"), "edge": f.get("edge"), "raw": line.strip()[:120]}

# Every entry below was executed against this berkeley-abc and produced a
# statistics line. Two families do not work here and are deliberately absent:
#   compress2rs / resyn / resyn2rs  -- "unknown command" in this build
#   fx / mfs after strash, and &-commands without &put  -- these orderings error
#     out, because fx and mfs need the logic network, not the AIG.
# An invalid script is reported as invalid_script, never as a failed measurement:
# conflating "the tool refused the request" with "the request produced nothing"
# is how a search silently scores an illegal candidate as a bad one.
STRATEGIES = {
    "baseline": "balance; rewrite; balance; rewrite",
    "drw":      "balance; rewrite; drw -l; balance",
    "resub6":   "balance; rewrite; resub -K 6; balance",
    "resub8":   "balance; rewrite; resub -K 8 -N 2; balance",
    "dc2":      "balance; rewrite; dc2; balance",
    "dch":      "balance; rewrite; dch; balance",
    "dc2dch":   "balance; rewrite; dc2; dch; balance",
    "if6":      "balance; rewrite; if -K 6; balance",
    "if8":      "balance; rewrite; if -K 8; balance",
    "fx":       "fx; strash; rewrite; balance",
    "mfs":      "mfs; strash; rewrite; balance",
    "mix":      "balance; rewrite -l; resub -K 8; dc2; dch; balance",
    "mix2":     "fx; mfs; strash; rewrite -l; resub -K 8; dc2; if -K 6; balance",
}

def canonical(netlist: str) -> bytes:
    """The bytes that define the circuit, with the tool's timestamp removed.

    ABC stamps `# Benchmark "x" written by ABC on <date>` as line 1. That single
    line made two runs of an identical netlist hash differently, which would have
    looked like non-determinism in the optimiser when it is only a clock in a
    comment. Everything else is kept verbatim.
    """
    txt = open(netlist, encoding="utf-8", errors="replace").read()
    lines = [l for l in txt.splitlines() if not l.startswith("# Benchmark")]
    return ("\n".join(lines) + "\n").encode("utf-8")


def best_by_metric(rows, key):
    """Pick the best row **within one metric**, never across two.

    Why this is not defensive coding but a correctness requirement: after `if`,
    ABC reports `aig = 254 ... lev = 2`, where aig is a post-mapping LUT count
    and lev is a LUT level count. Before `if` it reports `and = N lev = M`,
    where M is an AIG level count. Those two `lev` numbers are different units,
    and comparing them produced a phantom "depth 8 -> 2" win for prio32 (a
    32-input priority encoder, which cannot be two levels deep). The rule is
    simple and enforced here: a `aig` row is reported separately and marked
    non-comparable, never merged into the ranking.
    """
    # field naming is not uniform across callers: the ABC parser emits `and`,
    # while the agent transcript emits `area`. Reading r[key] directly meant that
    # asking for "area" silently matched nothing and returned no best row at all
    # -- which reads exactly like "nothing succeeded".
    def value(r):
        if key == "lev":
            return r.get("lev")
        v = r.get("area")
        return r.get("and") if v is None else v

    ok = [r for r in rows if r.get("status") == "ok" and value(r) is not None]
    canon = [r for r in ok if r.get("metric", "and") == "and"]
    mapped = [r for r in ok if r.get("metric") == "aig"]
    other = [r for r in ok if r.get("metric") not in ("and", "aig")]
    pick = lambda xs: min(xs, key=value) if xs else None
    return {"canonical": pick(canon), "mapped": pick(mapped), "other": pick(other),
            "n_canonical": len(canon), "n_mapped": len(mapped),
            "mixed": bool(canon and mapped)}


def model_name(blif: str) -> str:
    for l in open(blif, encoding="utf-8", errors="replace"):
        if l.startswith(".model"):
            return l.split()[1]
    raise RuntimeError(f"no .model in {blif}")

def _verifier(gold: str, impl: str, seq: bool, model: str) -> str:
    g, i = to_wsl(gold), to_wsl(impl)
    if not seq:
        return f'timeout 240 yosys-abc -c "read_blif {i}; cec {g}" 2>/dev/null'
    return ("timeout 300 yosys -p "
            f"'read_blif {g}; rename {model} gold; read_blif {i}; rename {model} impl; "
            "equiv_make gold impl equiv; hierarchy -top equiv; "
            "equiv_simple -seq 5; equiv_induct -seq 5; equiv_status' 2>/dev/null")

def _verdict(out: str, seq: bool) -> tuple[bool, str]:
    """Read a verdict, requiring positive proof and rejecting any counterexample."""
    if seq:
        m = re.search(r"(\d+) are proven and (\d+) are unproven", out)
        if not m:
            return False, "no equiv_status line"
        proven, unproven = int(m.group(1)), int(m.group(2))
        if unproven:
            return False, f"{unproven}/{proven+unproven} unproven"
        return True, f"equiv_induct proved {proven} outputs, 0 unproven"
    cex = next((l.strip() for l in out.splitlines() if l.startswith("Input pattern")), "")
    if "Verification failed" in out or cex:
        return False, f"counterexample {cex}"
    if "Networks are equivalent" in out:
        return True, "abc cec: equivalent"
    return False, "no cec verdict"

def _batch_script(gold, wd, strategies, seq, model):
    """One bash script for the whole candidate set, in one WSL call.

    Deliberately not one call per candidate: wsl.exe intermittently returns an
    empty stdout when several instances start concurrently from threads, and that
    is indistinguishable from 'this strategy produced nothing' -- it silently
    dropped four candidates that had in fact compiled and proved.
    """
    lines = ["set -u"]
    for name, script in strategies.items():
        cd = os.path.join(wd, name)
        lines.append(f'mkdir -p "{to_wsl(cd)}"')
        lines.append(f'echo "--BEGIN {name}"')
        lines.append(f'cd "{to_wsl(cd)}" && timeout 240 yosys-abc -c '
                     f'"read_blif {to_wsl(gold)}; strash; {script}; print_stats; '
                     f'write_blif {to_wsl(cd)}/mapped.blif" 2>/dev/null')
        lines.append(f'echo "--OPT {name} rc=$?"')
        lines.append(f'if [ -f "{to_wsl(cd)}/mapped.blif" ]; then')
        lines.append("  " + _verifier(gold, os.path.join(cd, "mapped.blif"), seq, model))
        lines.append('fi')
        lines.append(f'echo "--END {name}"')
    return "\n".join(lines)

def _parse(blob, strategies, wd, seq):
    rows = []
    for name in strategies:
        m = re.search(rf"--BEGIN {re.escape(name)}(.*?)--END {re.escape(name)}", blob, re.S)
        body = m.group(1) if m else ""
        rc_m = re.search(rf"--OPT {re.escape(name)} rc=(\d+)", blob)
        st = parse_stats(body)
        mapped = os.path.join(wd, name, "mapped.blif")
        errs = [l.strip()[:90] for l in body.splitlines()
                if "cmd error" in l or l.strip().startswith("Error")
                or l.strip().startswith("** cmd")]
        if errs:
            rows.append({"name": name, "status": "invalid_script",
                         "error": errs[0], "error_all": errs})
            continue
        if st is None or not os.path.exists(mapped):
            rows.append({"name": name, "status": "unmeasured",
                         "error": f"no statistics line (abc rc={rc_m.group(1) if rc_m else '?'})"})
            continue
        equiv, why = _verdict(body, seq)
        rows.append({"name": name, "status": "ok" if equiv else "rejected",
                     "ok": True, "and": st["area"], "metric": st["metric"],
                     "lev": st["lev"], "lat": st["lat"],
                     "equiv": equiv, "verify": why, "blif": mapped})
    return rows

def gate_selftest(gold: str, mapped: str, wd: str, seq: bool, model: str) -> tuple[bool, str]:
    """Corrupt a real netlist and require the verifier to reject it.

    Run before any result is believed, because a harness bug that makes the check
    vacuous (a missing filename argument, a swallowed error) turns every 'proved'
    into a rubber stamp and nothing downstream can tell. This is not hypothetical:
    a bare `cec` with no reference file passed an AND network against an OR one.
    """
    bad = os.path.join(wd, "_selftest_broken.blif")
    lines = open(mapped, encoding="utf-8", errors="replace").read().splitlines()
    flipped = False
    for i, l in enumerate(lines):
        if l.strip() == "11 1":
            lines[i], flipped = "10 1", True
            break
    if not flipped:
        return False, "self-test could not find a cube to corrupt"
    with open(bad, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    rc, out, err = sh(_verifier(gold, bad, seq, model))
    ok, why = _verdict(out, seq)
    if ok:
        return False, f"verifier ACCEPTED a corrupted netlist -- gate is vacuous ({why})"
    return True, f"verifier rejected the corrupted netlist ({why})"

def s_search(inp, wd):
    gold, top = inp["blif"], inp["top"]
    os.makedirs(wd, exist_ok=True)
    rc, out, err = sh(f"grep -c '^.latch' {to_wsl(gold)} || true")
    seq = int((out.strip().splitlines() or ["0"])[-1] or 0) > 0
    model = model_name(gold)
    sp = os.path.join(wd, "search.sh")
    open(sp, "w", encoding="utf-8", newline="\n").write(
        _batch_script(gold, wd, STRATEGIES, seq, model))
    rc, out, err = sh(f"bash {to_wsl(sp)}", t=1800)
    rows = _parse(out, STRATEGIES, wd, seq)
    proved = [r for r in rows if r.get("equiv")]
    if not proved:
        raise RuntimeError(f"no strategy survived verification (rc={rc}); "
                           f"modes={[(r.get('status'), r.get('error') or r.get('verify')) for r in rows][:4]}")
    gate_ok, gate_msg = gate_selftest(gold, proved[0]["blif"], wd, seq, model)
    if not gate_ok:
        raise RuntimeError("self-test failed: " + gate_msg)
    ba = min(proved, key=lambda r: r["and"])
    bd = min(proved, key=lambda r: r["lev"])
    worst = max(r["and"] for r in proved)
    worstd = max(r["lev"] for r in proved)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    report = {"all": rows, "proved": len(proved), "tried": len(rows), "counts": counts,
              "sequential": seq, "verifier": "yosys equiv_induct" if seq else "abc cec",
              "gate_selftest": gate_msg,
              "best_area": {k: ba[k] for k in ("name", "and", "lev")},
              "best_depth": {k: bd[k] for k in ("name", "and", "lev")},
              "area_spread_pct": round((1 - ba["and"] / worst) * 100, 1),
              "depth_spread_pct": round((1 - bd["lev"] / worstd) * 100, 1),
              "pareto": sorted({(r["and"], r["lev"], r["name"]) for r in proved})}
    rp = os.path.join(wd, "search.json")
    json.dump(report, open(rp, "w"), indent=2)
    canon = os.path.join(wd, "best_netlist.blif")
    open(canon, "wb").write(canonical(ba["blif"]))
    return {"search_report": rp, "netlist": canon}

def s_elaborate(inp, wd):
    """RTL -> gate-level BLIF.

    `synth -noabc` and nothing less: without it the BLIF still contains coarse
    cells like $mul and ABC has nothing to map, which is how the first benchmark
    run produced 'no candidate survived' on every circuit.
    """
    rtl, top = inp["rtl"], inp["top"]
    os.makedirs(wd, exist_ok=True)
    blif = os.path.join(wd, "gold.blif")
    rc, out, err = sh(f"cd {to_wsl(wd)} && yosys -p 'read_verilog {to_wsl(rtl)}; "
                      f"hierarchy -top {top}; proc; opt; memory; opt; fsm; opt; "
                      f"techmap; opt; synth -top {top} -noabc; write_blif {to_wsl(blif)}; stat'")
    if not os.path.exists(blif):
        raise RuntimeError(f"elaboration failed rc={rc}: {(out or err)[-300:]}")
    mm = re.search(r"Number of cells:\s+(\d+)", out)
    return {"blif": blif}

def build(rtl, top, root):
    f = Flow(root, seed="synth-search-v2")
    f.note_env("wsl", "Ubuntu-22.04")
    f.note_env("elaborator", "apt yosys 0.9, synth -noabc")
    f.note_env("optimizer", "berkeley-abc 1.01")
    f.add(rtl, "rtl")
    f.param("top", top)
    r1 = f.run(Stage("elaborate", s_elaborate, ("rtl", "top"), ("blif",), tool="yosys"))
    if not r1.ok:
        return f, r1
    return f, f.run(Stage("search", s_search, ("blif", "top"),
                          ("search_report", "netlist"), tool="berkeley-abc+yosys"))
