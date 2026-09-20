
"""evolve_search: mutate and select synthesis scripts, under a verifier that can veto.

The hand-written STRATEGIES table in synth_search is a starting point, not a
search: thirteen fixed scripts, chosen by knowing roughly what ABC's commands do.
This module searches instead. A candidate is a *sequence of steps with
parameters*, so mutation can change a parameter (resub -K 8 -> -K 10), swap a
step, insert one, or delete one, and the result is still a legal-shaped script.

Two things make this honest rather than a demo:

 1. Nothing is selected on area alone. Every candidate is verified first -- abc
    cec for combinational, yosys equiv_induct for sequential -- and a candidate
    whose function changed is recorded as REJECTED, not as a small circuit. A
    search that ranks unverified designs will always find a wonderfully small
    wrong answer, which is the failure mode this whole project exists to avoid.

 2. Illegal scripts are a third outcome, not a bad score. ABC answers an
    unusable command with "cmd error" and no statistics; reporting that as
    "candidate produced nothing" would hide the fact that a large fraction of
    the mutation space is simply not valid in this build.

The trajectory is kept: which generation found what, and how many candidates
were illegal or rejected along the way.
"""
from __future__ import annotations
import json, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_search import (WSL, sh, to_wsl, model_name, gate_selftest, parse_stats)

# primitives this build of berkeley-abc accepts, with their legal argument sets
PRIMS = [
    ("balance", [[]]),
    ("rewrite", [[], ["-l"], ["-z"], ["-lz"]]),
    ("resub",   [["-K", "4"], ["-K", "6"], ["-K", "8"], ["-K", "10"], ["-K", "8", "-N", "2"]]),
    ("dc2",     [[]]),
    ("dch",     [[]]),
    ("if",      [["-K", "4"], ["-K", "6"], ["-K", "8"]]),
    ("drw",     [[], ["-l"]]),
    ("fx",      [[]]),
    ("mfs",     [[]]),
    ("renode",  [[]]),
]

# usable only before strash: they act on the logic network, not the AIG
LATE_PRIMS = [("fx", [[]]), ("mfs", [[]]), ("renode", [[]])]

def _legal(steps) -> bool:
    seen_strash = False
    for c, _a in steps:
        if c == "strash":
            seen_strash = True
        elif c in ("fx", "mfs", "renode") and seen_strash:
            return False
    return seen_strash

STRASH = ("strash", [])

def render(steps) -> str:
    return "; ".join(" ".join([c] + a) for c, a in steps)

def two_phase(gold: str, wd: str, seq: bool, model: str, batch: dict, t=1200):
    return evaluate(gold, wd, seq, model, batch, t=t)

def seed_population(pop: int, rng: random.Random):
    """A few known-good shapes plus random ones, so the search does not start
    entirely inside a bad region but is not seeded with the answer either."""
    # A candidate now positions strash itself instead of having it prepended.
    # That is not cosmetic: fx, mfs and renode operate on the logic network, and
    # ABC rejects them outright once strash has run. With strash pinned at the
    # front, three of the ten primitives could never be used at all -- 9 of 12
    # random seeds were dying on "can only be applied to a logic network", which
    # is a hole in the searchable space, not in the candidates.
    seeds = [
        [("balance", []), ("rewrite", []), STRASH, ("balance", []), ("rewrite", [])],
        [("balance", []), ("rewrite", []), STRASH, ("dc2", []), ("dch", []), ("balance", [])],
        [("fx", []), ("mfs", []), STRASH, ("rewrite", ["-l"]), ("resub", ["-K", "8"]), ("dc2", [])],
    ]
    pop_list = [list(s) for s in seeds]
    while len(pop_list) < pop:
        n = rng.randint(2, 4)
        pre = [(nm, list(rng.choice(opts))) for nm, opts in
               (rng.choice(LATE_PRIMS) for _ in range(rng.randint(0, 2)))]
        post = [(nm, list(rng.choice(opts))) for nm, opts in
                (rng.choice(PRIMS) for _ in range(n))]
        pop_list.append(pre + [STRASH] + post)
    return pop_list[:pop]

def mutate(steps, rng: random.Random):
    steps = [[c, list(a)] for c, a in steps]
    if not any(c == "strash" for c, _ in steps):
        steps.insert(0, ["strash", []])
    op = rng.choice(["arg", "replace", "insert", "delete", "swap", "move", "arg"])
    if op == "arg" and steps:
        i = rng.randrange(len(steps))
        name = steps[i][0]
        opts = dict(PRIMS).get(name, [[]])
        steps[i] = [name, rng.choice(opts)]
    elif op == "replace" and steps:
        i = rng.randrange(len(steps))
        name = rng.choice(PRIMS)[0]
        steps[i] = [name, rng.choice(dict(PRIMS)[name])]
    elif op == "insert" and len(steps) < 6:
        name = rng.choice(PRIMS)[0]
        steps.insert(rng.randrange(len(steps) + 1), [name, rng.choice(dict(PRIMS)[name])])
    elif op == "delete" and len(steps) > 3:
        steps.pop(rng.randrange(len(steps)))
    elif op == "swap" and len(steps) > 1:
        i, j = rng.randrange(len(steps)), rng.randrange(len(steps))
        steps[i], steps[j] = steps[j], steps[i]
    elif op == "move":
        # move a step across the strash boundary -- the one edit that can turn a
        # dead primitive into a live one
        si = next((k for k, (c, _) in enumerate(steps) if c == "strash"), None)
        if si is not None and len(steps) > 2:
            i = rng.randrange(len(steps))
            if i != si:
                st = steps.pop(i)
                si = next(k for k, (c, _) in enumerate(steps) if c == "strash")
                steps.insert(rng.randrange(si + 1), st)
    return [(c, a) for c, a in steps]

def evaluate(gold: str, wd: str, seq: bool, model: str, batch: dict, t=1200):
    """One WSL call per generation, exactly as in synth_search and for the same
    reason: concurrent wsl.exe loses stdout, and a lost stdout is indistinguishable
    from a candidate that produced nothing."""
    # evaluate owns its working directory: it writes gen.sh there before any
    # mkdir in the script runs, so a caller that passed a not-yet-created path
    # got FileNotFoundError on a directory it never had to know about.
    os.makedirs(wd, exist_ok=True)
    lines = ["set -u"]
    for name, script in batch.items():
        cd = os.path.join(wd, name)
        lines.append(f'mkdir -p "{to_wsl(cd)}"')
        lines.append(f'echo "--BEGIN {name}"')
        lines.append(f'cd "{to_wsl(cd)}" && timeout 240 yosys-abc -c '
                     f'"read_blif {to_wsl(gold)}; {script}; print_stats; '
                     f'write_blif {to_wsl(cd)}/mapped.blif" 2>/dev/null')
        lines.append(f'echo "--OPT {name} rc=$?"')
        lines.append(f'if [ -f "{to_wsl(cd)}/mapped.blif" ]; then')
        if seq:
            lines.append(f'  timeout 300 yosys -p "read_blif {to_wsl(gold)}; rename {model} gold; '
                         f'read_blif {to_wsl(cd)}/mapped.blif; rename {model} impl; '
                         f'equiv_make gold impl equiv; hierarchy -top equiv; '
                         f'equiv_simple -seq 5; equiv_induct -seq 5; equiv_status" 2>/dev/null')
        else:
            lines.append(f'  timeout 240 yosys-abc -c "read_blif {to_wsl(cd)}/mapped.blif; '
                         f'cec {to_wsl(gold)}" 2>/dev/null')
        lines.append('fi')
        lines.append(f'echo "--END {name}"')
    sp = os.path.join(wd, "gen.sh")
    open(sp, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    rc, out, err = sh(f"bash {to_wsl(sp)}", t=t)
    results = {}
    for name in batch:
        m = re.search(rf"--BEGIN {re.escape(name)}(.*?)--END {re.escape(name)}", out, re.S)
        body = m.group(1) if m else ""
        errs = [l.strip()[:80] for l in body.splitlines()
                if "cmd error" in l or l.strip().startswith("Error")]
        st = parse_stats(body)
        mapped = os.path.join(wd, name, "mapped.blif")
        if errs:
            results[name] = {"status": "invalid_script", "error": errs[0]}
        elif st is None or not os.path.exists(mapped):
            # rc=124 is a timeout: ABC was still working when the budget ran out,
            # which is a different fact from "the script produced nothing" and is
            # the honest explanation for most of the no_result rows here.
            rcm = re.search(rf"--OPT {re.escape(name)} rc=(\d+)", out)
            code = rcm.group(1) if rcm else "?"
            results[name] = {"status": "unmeasured",
                             "error": "timeout" if code == "124" else f"no stats line (rc={code})"}
        else:
            ands, lev, lat = st["area"], st["lev"], st["lat"]
            if seq:
                mm = re.search(r"(\d+) are proven and (\d+) are unproven", body)
                ok = bool(mm) and int(mm.group(2)) == 0
                why = f"{mm.group(1)}/{int(mm.group(1))+int(mm.group(2))} proven" if mm else "no status"
            else:
                ok = ("Networks are equivalent" in body) and ("Verification failed" not in body)
                cex = next((l.strip() for l in body.splitlines()
                            if l.startswith("Input pattern")), "")
                why = cex or "cec equivalent"
            results[name] = {"status": "ok" if ok else "rejected", "and": ands, "lev": lev,
                             "lat": lat, "metric": st["metric"], "verify": why, "blif": mapped}
    return results

def pareto(rows):
    """(area, depth) front. Both ends are kept deliberately: the smallest circuit
    and the shallowest one are usually different designs, and a single scalar
    would silently pick one of them."""
    good = [r for r in rows if r["status"] == "ok"]
    front = []
    for r in good:
        if not any((o["and"] <= r["and"] and o["lev"] <= r["lev"] and
                    (o["and"] < r["and"] or o["lev"] < r["lev"])) for o in good):
            front.append(r)
    return front

def run(gold: str, wd: str, seq: bool, model: str, pop=10, gens=5, seed=1, t=1500):
    os.makedirs(wd, exist_ok=True)
    rng = random.Random(seed)
    popn = seed_population(pop, rng)
    seen, archive, traj = set(), [], []
    for g in range(gens):
        batch, scripts = {}, {}
        i = 0
        for steps in popn:
            key = render(steps)
            if key in seen:
                continue
            seen.add(key)
            nm = f"g{g}_{i:02d}"
            batch[nm] = key
            scripts[nm] = steps
            i += 1
        if not batch:
            break
        res = evaluate(gold, wd, seq, model, batch)
        rows = []
        for nm, r in res.items():
            # both forms are needed and they are not interchangeable: the rendered
            # string goes into the report, the step list goes back into mutation.
            r = dict(r); r["gen"] = g; r["name"] = nm
            r["script"] = batch[nm]
            r["steps"] = [list(x) for x in scripts[nm]]
            rows.append(r)
        archive.extend(rows)
        counts = {}
        for r in rows:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        front = pareto(archive)
        traj.append({"gen": g, "evaluated": len(rows), "counts": counts,
                     "front": [{"script": r["script"], "and": r["and"], "lev": r["lev"]}
                               for r in sorted(front, key=lambda r: (r["and"], r["lev"]))[:6]]})
        best = min((r for r in archive if r["status"] == "ok"),
                   key=lambda r: (r["and"], r["lev"]), default=None)
        print(f"  gen{g}: n={len(rows)} {counts} best_area={best['and'] if best else '?'}"
              f"/lev={best['lev'] if best else '?'} front={len(front)}", flush=True)
        nxt = [[tuple(x) for x in r["steps"]] for r in front][:max(1, pop // 2)]
        if not nxt:
            nxt = [[tuple(x) for x in scripts[min(scripts)]]]
        guard = 0
        while len(nxt) < pop and guard < pop * 20:
            guard += 1
            cand = mutate(rng.choice(nxt), rng)
            if _legal(cand):
                nxt.append(cand)
        # every generation also gets fresh blood, so a saturated front cannot
        # freeze the search on its first local optimum
        for _ in range(max(1, pop // 4)):
            nxt[-1] = mutate(nxt[-1], rng)
        popn = nxt
    good = [r for r in archive if r["status"] == "ok"]
    if not good:
        return {"error": "no legal, verified candidate in the whole search",
                "trajectory": traj, "all": archive}
    ba = min(good, key=lambda r: r["and"])
    bd = min(good, key=lambda r: r["lev"])
    gate_ok, gate_msg = gate_selftest(gold, ba["blif"], wd, seq, model)
    out = {"sequential": seq, "generations": traj, "evaluated": len(archive),
           "status_counts": {s: sum(1 for r in archive if r["status"] == s)
                             for s in ("ok", "rejected", "invalid_script", "no_result")},
           "best_area": {k: ba[k] for k in ("script", "and", "lev", "gen")},
           "best_depth": {k: bd[k] for k in ("script", "and", "lev", "gen")},
           "gate_selftest": gate_msg, "gate_ok": gate_ok,
           "pareto": sorted({(r["and"], r["lev"], r["script"]) for r in pareto(archive)}),
           "rows": [{"gen": r["gen"], "script": r["script"], "status": r["status"],
                     "and": r.get("and"), "lev": r.get("lev"),
                     "error": r.get("error"), "verify": r.get("verify")} for r in archive]}
    return out
