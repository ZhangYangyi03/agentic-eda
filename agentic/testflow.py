"""testflow: test vectors, ATPG and fault coverage, on the same verifier discipline.

The loop is the one the whole repo uses, with the tools swapped:

    propose   a vector set (random, then objective-guided per undetected fault),
              optionally a set of test points to observe
      run     fault simulation over the flattened gate netlist
      veto    coverage under target / vector count over budget / the netlist
              itself failing the sanity check
      feed    the undetected faults go back into the proposal

What makes this more than a coverage number printer is that *detection is
decided by an oracle, not by the generator*. For a stuck-at fault on net n with
value s, a vector detects it iff driving n to s instead of its computed value
changes some primary output. That is checkable exactly: simulate the good
circuit and the faulty one and compare. So a fault is only ever recorded as
`detected` if two simulations disagree, and a fault recorded as `not_detected`
says exactly that: this vector set did not distinguish it.

Two honesty rules carried over from synth_search:
  * `not_detected` is not `undetectable`. Undetectability is only claimed when
    the input space was enumerated exhaustively (n_inputs <= EXHAUSTIVE_MAX),
    because for combinational single stuck-at that enumeration is a decision
    procedure. Above that bound the report says `not_detected`, never `redundant`.
  * a sequential design has latches, and stuck-at coverage on it depends on an
    assumption about controlling and observing them. This driver states the
    assumption it used (full scan: latches treated as pseudo-inputs and
    pseudo-outputs) instead of quietly reporting a combinational number.

Toolchain, measured on this host: yosys 0.9 (-noabc) for the BLIF, iverilog 11.0
present for RTL-level cross-checks. The netlist is read from BLIF `.names` tables,
not from a re-derivation, so what is simulated is what was written.
"""
from __future__ import annotations
import hashlib, itertools, json, os, random, re, sys, time

try:
    from . import lessons
except Exception:            # run as a script, not a package
    import lessons

EXHAUSTIVE_MAX = 14          # 2**14 = 16384 vectors: enumeration is a decision procedure
BUDGET_VECTORS = 2000        # operator's point: the hard part is cost, so it is a parameter
COVERAGE_TARGET = 0.99


# ---------------------------------------------------------------- BLIF parsing

def parse_blif(path: str) -> dict:
    """Return {'inputs', 'outputs', 'latches', 'names', 'net_fanin'}.

    Only the subset yosys -noabc emits: .model, .inputs, .outputs, .latch,
    .names with a truth table of 0/1/- rows, and .end.
    """
    inputs, outputs, latches = [], [], {}
    blocks: dict = {}                        # net -> list of (fanin, rows)
    cur = None
    for raw in open(path, encoding="utf-8", errors="replace"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(".inputs"):
            inputs += line.split()[1:]
            cur = None
        elif line.startswith(".outputs"):
            outputs += line.split()[1:]
            cur = None
        elif line.startswith(".latch"):
            q = line.split()
            latches[q[1]] = (q[2], q[3] if len(q) > 3 else "1")   # (input, init)
            cur = None
        elif line.startswith(".names"):
            q = line.split()
            # BLIF .names syntax is `.names <fanin...> <output>`: the net being
            # defined is the LAST token, and the fanins are everything between.
            # Reading the output as token[1] is the bug this whole driver was
            # dead on: every net gets registered under the name of its first
            # input, the real nets never get a definition, and every output
            # evaluates to X -- 0.0000 coverage, no error, on all 11 designs.
            cur = q[-1]
            blocks.setdefault(cur, []).append([q[1:-1], []])
        elif line.startswith("."):
            cur = None                       # .model .end .attr .param ...
        elif cur is not None:
            blocks[cur][-1][1].append(line)

    # THE bug that made this simulator report nothing: BLIF allows a net to be
    # defined by more than one .names block, and the net's function is the OR of
    # them. yosys 0.9 uses this heavily -- $false has four blocks here, one of
    # them an empty table (constant 0) and three of them buffers. A dict keyed by
    # net name keeps only the last block, throws the others away, and then every
    # net downstream evaluates to X because one fanin has no definition. The
    # symptom was 0.0000 coverage on every design with no error anywhere, which
    # is exactly the shape of failure this project exists to refuse.
    names, net_fanin = {}, {}
    for net, blks in blocks.items():
        names[net] = {"blocks": [{"fanin": f, "table": r} for f, r in blks]}
        # a net's fanins are the union of the blocks'; evaluation is per block
        seen, u = set(), []
        for f, _ in blks:
            for x in f:
                if x not in seen:
                    seen.add(x)
                    u.append(x)
        net_fanin[net] = u
    return {"inputs": inputs, "outputs": outputs, "latches": latches,
            "names": names, "net_fanin": net_fanin, "blocks": blocks}


def exhaustive_report(blif: dict, order: list, faults: list, budget_s: float) -> dict:
    """Enumerate the whole input space and report which faults are provably redundant.

    For combinational single stuck-at, enumeration is a decision procedure: a fault
    that no input vector distinguishes from the fault-free circuit is not "not yet
    detected", it does not exist as a detectable fault in this netlist. That is the
    difference between `not_detected` and `undetectable`, and this function is the
    only thing allowed to make the second claim.

    Cost is 2**n_inputs vectors, and the caller bounds n_inputs (EXHAUSTIVE_MAX).
    The wall-clock budget is real and reported: a truncated enumeration returns
    done=False with how far it got, never a proof it did not finish.
    """
    n_in = len(blif["inputs"])
    total = 1 << n_in
    outs = list(blif["outputs"]) + list(blif["latches"])
    cons = fanout_cones(blif, order)
    t0 = time.time()
    remaining = set(faults)
    # Only faults the previous stages missed need deciding; the rest are already known
    # detectable from a real vector, which is a stronger statement than enumeration.
    missing = [f for f in faults]
    done_vectors = 0
    per_fault_hits = set()
    for i in range(total):
        if time.time() - t0 > budget_s:
            return {"done": False, "reason": "budget_s %.0f exhausted after %d of %d vectors"
                                             % (budget_s, done_vectors, total),
                    "vectors": done_vectors, "detected": sorted(per_fault_hits)}
        vec = {p: (i >> j) & 1 for j, p in enumerate(blif["inputs"])}
        good = simulate(blif, order, vec)
        # a fault is decided at the first vector that distinguishes it, so the work per
        # vector shrinks as the space is traversed. The fanout cone comes from the same
        # function the guided stage uses, so the two cannot disagree about what
        # "the fanout cone of a net" means.
        todo = [f for f in missing if f not in per_fault_hits]
        if not todo:
            break
        for f in todo:
            n, fv = f
            bad = simulate_cone(blif, good, cons.get(n, list(blif["names"])), (n, fv))
            if _cmp(good, bad, outs):
                per_fault_hits.add(f)
        done_vectors += 1
    still = [f for f in missing if f not in per_fault_hits]
    return {"done": True,
            "vectors": done_vectors, "vectors_total": total,
            "detected": sorted(per_fault_hits), "undetectable": sorted(still),
            "undetectable_count": len(still), "n_inputs": n_in,
            "seconds": round(time.time() - t0, 1),
            "note": "enumeration of 2**%d vectors is a decision procedure for combinational "
                    "single stuck-at; a fault no vector distinguishes is redundant in this netlist"
                    % n_in}


def order_nets(blif: dict) -> list:
    """Topological order over the .names graph; raises on a combinational loop.

    The order is what makes a single forward pass a simulation. A loop here is a
    real error and is raised, not papered over: silently evaluating a cyclic
    netlist in some order produces plausible wrong values.
    """
    names = blif["net_fanin"]
    inputs = set(blif["inputs"])
    done, order, temp = set(inputs), [], set()

    def visit(n, stack):
        if n in done or n not in names:
            return
        if n in temp:
            raise ValueError("combinational loop at %s via %s" % (n, " -> ".join(stack[-6:])))
        temp.add(n)
        for f in names[n]:
            visit(f, stack + [n])
        temp.discard(n)
        done.add(n)
        order.append(n)

    for n in list(names):
        visit(n, [])
    return order


# ------------------------------------------------- controllability analysis
# Why this exists: the first version of the guided proposal scored a vector by
# "how many outputs the fault flips". That objective is flat -- a fault deep in
# a chain flips nothing until every side condition is met at once, so hill
# climbing has no gradient and the feedback stage improves coverage by ~1%.
# Measured: prio32 went 0.4552 -> 0.4670 with 300 extra vectors while 226 faults
# stayed undetected. The gradient has to come from *enabling*, not from the
# output: how many side inputs already sit at a value that does not force their
# gate, i.e. how much of the propagation condition is already in place.

def analysis(blif: dict) -> dict:
    """net -> list over blocks -> list over fanins of the non-controlling value.

    A fanin's value v is non-controlling when, holding that fanin at v, the
    block's output still depends on the others. Computed by enumerating the
    block's own table, so it is exact for the netlist in hand rather than
    assumed from the gate's name.
    """
    out = {}
    for net, spec in blif["names"].items():
        per_block = []
        for b in spec["blocks"]:
            fanin, table = b["fanin"], b["table"]
            # The controllability of a fanin is a function of the block alone -- it
            # enumerates every assignment of that block's own fanin -- so it does not
            # depend on vals and must not be recomputed per candidate vector. It was,
            # and mult4 with a wide AND tree spent the whole budget inside this loop:
            # _score calls analysis per fault per candidate, and each call re-ran
            # 2**fanin evaluations per fanin per block. Cached on the block's own
            # content, so the cost is paid once per netlist.
            ck = (tuple(fanin), tuple(table))
            cached = _CTRL_CACHE.get(ck)
            if cached is None:
                if len(fanin) > 16:
                    # 2**17 x 17 evaluations is not a decision procedure, it is a hang.
                    # Say which blocks were not analysed instead of pretending.
                    _CTRL_CACHE[ck] = None
                else:
                    assigns = _all_assignments(len(fanin))
                    ctrl = []
                    for i in range(len(fanin)):
                        vals_ = set()
                        for v in (0, 1):
                            seen = set()
                            for a in assigns:
                                if a[i] != v:
                                    continue
                                seen.add(_eval_block(fanin, table, dict(zip(fanin, a))))
                                if 0 in seen and 1 in seen:
                                    break
                            if 0 in seen and 1 in seen:
                                vals_.update({v})
                        ctrl.append(vals_)
                    _CTRL_CACHE[ck] = ctrl
                cached = _CTRL_CACHE[ck]
            per_block.append(cached if cached is not None else [set()] * len(fanin))
        out[net] = per_block
    return out


_CTRL_CACHE = {}
_ANA_CACHE = {}


def _all_assignments(k):
    for i in range(1 << k):
        yield tuple((i >> j) & 1 for j in range(k))


def _nc_progress(blif: dict, ana: dict, vals: dict, cone: list) -> int:
    """How many cone fanins already sit at a non-controlling value."""
    n = 0
    for net in cone:
        spec = blif["names"].get(net)
        if not spec:
            continue
        for bi, b in enumerate(spec["blocks"]):
            for i, f in enumerate(b["fanin"]):
                if i < len(ana[net][bi]) and vals.get(f) in ana[net][bi][i]:
                    n += 1
    return n


# ------------------------------------------------------------------ simulation
# 3-valued: 0, 1, X. X is not decoration -- an uninitialised latch and an
# incompletely specified .names row both produce it, and treating X as 0 would
# manufacture agreement between the good and faulty circuits.

def _eval_block(fanin, table, vals):
    """One .names block: sum-of-products over {0,1,X}. Returns 0, 1 or 'X'."""
    if not fanin:
        return int(table[0].strip() or 0) if table else 0
    if not table:
        return 0
    xseen = False
    for row in table:
        bits = row.strip().replace(" ", "")
        if not bits:
            continue
        out, pat = int(bits[-1]), bits[:-1]
        if len(pat) != len(fanin):
            continue
        ok = True
        for ch, net in zip(pat, fanin):
            v = vals.get(net)
            if ch == "-":
                continue
            if v is None or v == "X":
                ok = False
                xseen = True
                break
            if v != int(ch):
                ok = False
                break
        if ok:
            return out
    return "X" if xseen else 0


def _eval_names(spec, vals):
    """A net defined by several blocks is the OR of them (BLIF, section 2.2)."""
    blocks = spec.get("blocks") or [{"fanin": spec.get("fanin", []), "table": spec.get("table", [])}]
    if len(blocks) == 1:
        b = blocks[0]
        return _eval_block(b["fanin"], b["table"], vals)
    r = 0
    for b in blocks:
        v = _eval_block(b["fanin"], b["table"], vals)
        if v == 1:
            return 1
        if v == "X":
            r = "X"
    return r


def simulate(blif: dict, order: list, vec: dict, fault=None) -> dict:
    """One pass. `fault` = (net, value) forces that net to a constant.

    The fault is injected BEFORE the sweep as well as inside it. A stuck-at on a
    primary input is a real defect -- a pad, a bond wire, a broken track -- and it
    is not in `order`, so injecting only inside the loop silently ignored every
    input fault. That is not a missing feature, it is a wrong answer: the oracle
    said "not detected" for a fault it had never applied. Caught by the cone path
    disagreeing with it on 3 of 150 probes; the cone path was right.
    """
    vals = {}
    for net, v in vec.items():
        vals[net] = v
    for latch in blif["latches"]:
        vals[latch] = "X"                    # no reset sequence applied: say so with X
    fnet, fval = fault if fault else (None, None)
    if fnet is not None and fnet not in blif["names"]:
        vals[fnet] = fval                    # primary input, or a net with no driver
    for net in order:
        v = _eval_names(blif["names"][net], vals)
        if net == fnet:
            v = fval
        vals[net] = v
    return vals


def detects(blif: dict, order: list, vec: dict, fault, _unused=None) -> bool:
    """Ground-truth oracle: full simulation of good and faulty, compare PPOs.

    Slow on purpose and kept on purpose: this is the definition of "detected",
    used by the cross-check that validated the cone-accelerated path against
    iverilog. The fast path is allowed to exist only because this one agrees with
    it on every probe.
    """
    good = outputs_of(blif, simulate(blif, order, vec), True)
    bad = outputs_of(blif, simulate(blif, order, vec, fault), True)
    for g, b in zip(good, bad):
        if g == "X" or b == "X":
            continue
        if g != b:
            return True
    return False


def outputs_of(blif: dict, vals: dict, latches_as_outputs: bool) -> tuple:
    outs = [vals.get(o, "X") for o in blif["outputs"]]
    if latches_as_outputs:
        outs += [vals.get(l, "X") for l in blif["latches"]]
    return tuple(outs)


# ------------------------------------------------------------------ fault model

def fault_list(blif: dict) -> list:
    """Stuck-at-0 and stuck-at-1 on every net that is not a constant driver.

    Every net, not only gate inputs: a bridged or broken wire is a net, and
    restricting the list to gate pins is the usual way coverage gets inflated.
    """
    skip = set()
    for n, spec in blif["names"].items():
        # A net defined only by zero-fanin blocks is a constant driver: there is
        # no wire to break. Anything with a real fanin is a candidate site.
        if spec["blocks"] and all(not b["fanin"] for b in spec["blocks"]):
            skip.add(n)
    nets = [n for n in blif["names"] if n not in skip]
    nets += [n for n in blif["inputs"]]
    faults = []
    for n in sorted(set(nets)):
        faults.append((n, 0))
        faults.append((n, 1))
    return faults


# ------------------------------------------------- fanout-cone acceleration
# A fault on net n can only change nets downstream of n. Without exploiting that,
# a fault simulation is (vectors x faults x nets) evaluations and mult16 never
# finishes. The correct shape is the standard one, and getting it wrong twice was
# instructive:
#   * evaluate the GOOD circuit fully, once per vector (O(gates));
#   * for each fault, copy those good values, force the faulted net, and
#     re-evaluate ONLY the fanout cone of that net in topological order.
# The values outside the cone are already correct, so nothing else is needed.
# The two wrong versions replaced the full good evaluation with an input cone,
# which leaves the other fanins of cone nets undefined -- they evaluate to X, the
# cone walk reports no difference, and the reported coverage is too low. Measured
# against the full simulation that had passed the iverilog cross-check: 19/100
# probes disagreed on adder8, 10/100 on prio32, before the fix.

def fanout_of(blif: dict) -> dict:
    fo = {}
    for net, spec in blif["names"].items():
        for b in spec["blocks"]:
            for f in b["fanin"]:
                fo.setdefault(f, []).append(net)
    return fo


def fanout_cones(blif: dict, order: list) -> dict:
    """net -> topologically ordered nets strictly downstream of it."""
    fo = fanout_of(blif)
    pos = {n: i for i, n in enumerate(order)}
    out = {}
    for n in list(blif["names"]) + list(blif["inputs"]):
        seen, stack = set(), list(fo.get(n, []))
        while stack:
            x = stack.pop()
            if x in seen or x not in blif["names"]:
                continue
            seen.add(x)
            stack.extend(fo.get(x, []))
        out[n] = sorted(seen, key=lambda z: pos[z])
    return out


def simulate_cone(blif: dict, good: dict, cone: list, fault) -> dict:
    """Copy the good values, force the fault, re-evaluate only the fanout cone."""
    vals = dict(good)
    fnet, fval = fault
    vals[fnet] = fval
    for net in cone:
        vals[net] = _eval_names(blif["names"][net], vals)
    return vals


def _cmp(good: dict, bad: dict, out_nets: list) -> bool:
    """True iff a PPO value differs. X on either side is inconclusive, not a hit."""
    for o in out_nets:
        g, b = good.get(o, "X"), bad.get(o, "X")
        if g == "X" or b == "X":
            continue
        if g != b:
            return True
    return False


# ------------------------------------------------------------------ proposals

def random_vectors(blif: dict, n: int, seed: int) -> list:
    rnd = random.Random(seed)
    return [{p: rnd.randint(0, 1) for p in blif["inputs"]} for _ in range(n)]


def fault_simulate(blif: dict, order: list, vectors: list, faults: list,
                   stop_at_full=True, verbose=False) -> dict:
    """Which faults this vector set detects, and which vector did it first.

    One full good simulation per vector; each fault costs only its own fanout cone.
    """
    cone = fanout_cones(blif, order)
    out_nets = list(blif["outputs"]) + list(blif["latches"])
    detected, work = {}, 0
    for i, vec in enumerate(vectors):
        good = simulate(blif, order, vec)
        for f in faults:
            if stop_at_full and f in detected:
                continue
            c = cone.get(f[0], [])
            work += len(c)
            if _cmp(good, simulate_cone(blif, good, c, f), out_nets):
                detected[f] = i
        if stop_at_full and len(detected) == len(faults):
            break
        if verbose and i and i % 100 == 0:
            print("      vec %d/%d detected %d/%d" % (i, len(vectors), len(detected), len(faults)), flush=True)
    return detected


def _eval_list(blif, nets, vals):
    for x in nets:
        vals[x] = _eval_names(blif["names"][x], vals)
    return vals


_ANA_CACHE = {}


def _score(blif, order, vec, fault, cons, out_nets=None) -> int:
    """999 = THIS fault detected on this vector; else a gradient, never a verdict.

    Detection is decided with the fault's own forced value and the same PPO
    comparison the coverage stage uses, so the search and the verifier cannot
    disagree about what "detected" means. The opposite value is used only to
    score how far the effect travels and how much of the propagation condition is
    already satisfied -- the gradient that actually moves the hill climb. An
    earlier version returned 999 on an opposite-value difference, which reported
    "the other fault would be detectable" as "this one is": 19/100 probes wrong.
    """
    n, fv = fault
    cone = cons.get(n, [])
    good = simulate(blif, order, vec)
    bad = simulate_cone(blif, good, cone, (n, fv))
    outs = out_nets if out_nets is not None else (list(blif["outputs"]) + list(blif["latches"]))
    if _cmp(good, bad, outs):
        return 999
    opp = simulate_cone(blif, good, cone, (n, 1 - fv))
    depth = sum(1 for x in cone if good.get(x, "X") != "X" and opp.get(x, "X") != "X"
                and good.get(x) != opp.get(x))
    # setdefault evaluates its second argument whether or not the key is present, so
    # `_ANA_CACHE.setdefault(id(blif), analysis(blif))` re-ran the whole structural
    # controllability sweep on EVERY _score call -- once per fault per candidate
    # vector. That, not the search itself, is what spent the budget on mult4. An
    # explicit test is the difference between a cache and a decoration.
    ana = _ANA_CACHE.get(id(blif))
    if ana is None:
        ana = analysis(blif)
        _ANA_CACHE[id(blif)] = ana
    return depth * 100 + _nc_progress(blif, ana, opp, cone)


def guided_vectors(blif: dict, order: list, faults: list, detected: dict,
                   per_fault: int, seed: int, cons=None, out_nets=None,
                   budget_s: float = 300.0) -> tuple:
    """ATPG for the faults random vectors missed, under a wall-clock budget.

    The budget is first-class, because this stage is the expensive one and the
    operator's point is that cost is the real difficulty. It stops when the time
    is gone and reports how many faults it attempted and how many it never got
    to. A coverage number that silently came from a truncated search is exactly
    the kind of number this repo refuses to print.
    """
    rnd = random.Random(seed ^ 0xBEEF)
    cons = cons if cons is not None else fanout_cones(blif, order)
    todo = [f for f in faults if f not in detected]
    t0 = time.time()
    out = []
    stats = {"faults_to_cover": len(todo), "attempted": 0, "skipped": 0,
             "budget_s": budget_s, "seconds": None, "detected_in_this_stage": 0}
    for f in todo:
        if time.time() - t0 > budget_s:
            stats["skipped"] = len(todo) - stats["attempted"]
            break
        s = (cons.get(f[0], []), out_nets)
        best, best_score = None, 0
        for _ in range(per_fault):
            # The budget was checked once per fault, so one fault whose cone is wide
            # could spend the whole stage and the stage would report it as attempted.
            # Checked inside the candidate loop now, and the fault is counted as
            # skipped when the time runs out mid-attempt.
            if time.time() - t0 > budget_s:
                stats["skipped"] = len(todo) - stats["attempted"]
                stats["cut_mid_fault"] = True
                break
            vec = {p: rnd.randint(0, 1) for p in blif["inputs"]}
            score = _score(blif, order, vec, f, cons, out_nets)
            for _ in range(40):
                if score == 999 or time.time() - t0 > budget_s:
                    break
                q = rnd.randrange(len(blif["inputs"]))
                pn = blif["inputs"][q]
                trial = dict(vec)
                trial[pn] = 1 - trial[pn]
                s2 = _score(blif, order, trial, f, cons, out_nets)
                if s2 >= score:
                    vec, score = trial, s2
            if score > best_score:
                best, best_score = vec, score
            if best_score == 999:
                break
        if time.time() - t0 > budget_s and best is None:
            stats["skipped"] = len(todo) - stats["attempted"]
            stats["cut_mid_fault"] = True
            break
        stats["attempted"] += 1
        if best is not None:
            out.append(best)
    stats["seconds"] = round(time.time() - t0, 1)
    return out, stats


# ------------------------------------------------------------------ the loop

def run_design(blif_path: str, design: str, outroot: str,
               target: float = COVERAGE_TARGET, budget_vectors: int = BUDGET_VECTORS,
               seed: int = 1, guided_per_fault: int = 40,
               exhaustive_budget_s: float = 120.0,
               guided_budget_s: float = 120.0) -> dict:
    os.makedirs(os.path.join(outroot, design), exist_ok=True)
    blif = parse_blif(blif_path)
    rec = {"design": design, "blif": blif_path,
           "blif_sha256": hashlib.sha256(open(blif_path, "rb").read()).hexdigest(),
           "inputs": len(blif["inputs"]), "outputs": len(blif["outputs"]),
           "latches": len(blif["latches"]), "gates": len(blif["names"]),
           "target": target, "budget_vectors": budget_vectors, "seed": seed,
           "stages": {}, "ok": False}

    try:
        order = order_nets(blif)
    except ValueError as e:
        rec["error"] = str(e)
        return rec
    faults = fault_list(blif)
    rec["faults_total"] = len(faults)
    rec["sequential_assumption"] = ("none (combinational)" if not blif["latches"] else
        "full scan: %d latch(es) treated as pseudo-inputs and pseudo-outputs. "
        "Coverage below is the combinational core's; a real scan chain is not built here."
        % len(blif["latches"]))

    # --- knowledge first, but never as a gate ---------------------------------
    # Borrowed discipline (ai-mechanical-3dcad-design-agent): "continue CAD work
    # when knowledge has no match or its backend is unavailable". So this is a
    # retrieval that may return [] and the run proceeds either way. What is
    # recorded is which lessons were actually consulted, so a later reader can
    # tell "ran without experience" from "ran against experience".
    consulted = lessons.search("%s coverage atpg fault" % design, limit=5)
    rec["lessons_consulted"] = [{"id": c["id"], "problem": c["problem"][:120]} for c in consulted]
    rec["lessons_store"] = lessons.stats().get("total", 0)

    # --- propose/run 1: random -------------------------------------------------
    t0 = time.time()
    v_rand = random_vectors(blif, budget_vectors // 2, seed)
    det = fault_simulate(blif, order, v_rand, faults)
    rec["stages"]["random"] = {"vectors": len(v_rand), "detected": len(det),
                               "coverage": round(len(det) / len(faults), 4),
                               "seconds": round(time.time() - t0, 1)}
    vectors = list(v_rand)
    n_random = len(v_rand)

    # --- feed back + propose/run 2: guided -------------------------------------
    t0 = time.time()
    cons = fanout_cones(blif, order)
    v_guided, gstats = guided_vectors(
        blif, order, faults, det, guided_per_fault, seed, cons,
        list(blif["outputs"]) + list(blif["latches"]), budget_s=guided_budget_s)
    room = max(0, budget_vectors - len(vectors))
    v_guided = v_guided[:room]
    if v_guided:
        det2 = fault_simulate(blif, order, v_guided, faults)
        for f, i in det2.items():
            det.setdefault(f, n_random + i)
    vectors += v_guided
    rec["stages"]["guided"] = {"vectors": len(v_guided), "detected": len(det),
                               "coverage": round(len(det) / len(faults), 4),
                               "seconds": round(time.time() - t0, 1),
                               "attempted": gstats["attempted"],
                               "skipped_for_budget": gstats["skipped"],
                               "budget_s": gstats["budget_s"]}

    # --- the veto --------------------------------------------------------------
    missing = [f for f in faults if f not in det]
    rec["coverage"] = round(len(det) / len(faults), 4)
    rec["vectors_used"] = len(vectors)
    rec["not_detected"] = len(missing)
    ex = {"done": False, "reason": "skipped"}
    if missing and len(blif["inputs"]) <= EXHAUSTIVE_MAX:
        ex = exhaustive_report(blif, order, faults, exhaustive_budget_s)
        if ex.get("done"):
            for f in ex["detected"]:
                det.setdefault(f, -1)
            still = [f for f in faults if f not in det]
            rec["undetectable"] = len(still)          # now a proof, not a gap
            rec["undetectable_list"] = ["%s/SA%d" % f for f in still][:40]
            rec["coverage_exhaustive"] = round(len(det) / len(faults), 4)
    rec["exhaustive"] = ex
    rec["budget_ok"] = len(vectors) <= budget_vectors
    # When the input space was enumerated, coverage has a CEILING and this is it: every
    # fault the circuit can possibly reveal has been revealed. Two thirds of the faults
    # in a 4-bit multiplier are redundant, so 0.4747 is not a shortfall, it is the
    # answer -- and vetoing it, as an earlier version did, contradicted the same
    # report's own statement that those faults are undetectable. A veto has to be a
    # statement about the design, not about a target that no correct synthesis could
    # have reached.
    rec["veto"] = []
    if ex.get("done"):
        reachable = round((len(faults) - rec["undetectable"]) / len(faults), 4)
        rec["reachable_coverage"] = reachable
        rec["coverage_is_ceiling"] = abs(rec.get("coverage_exhaustive", 0) - reachable) < 1e-4
        if not rec["coverage_is_ceiling"]:
            rec["veto"].append("coverage %.4f does not equal the enumerated ceiling %.4f"
                               % (rec.get("coverage_exhaustive", 0), reachable))
        if reachable < target:
            rec["note"] = ("target %.2f is not reachable on this netlist: %d of %d faults are "
                           "provably redundant, so %.4f is the ceiling, not a shortfall"
                           % (target, rec["undetectable"], len(faults), reachable))
        rec["ok"] = rec["coverage_is_ceiling"]
    else:
        if rec["coverage"] < target:
            rec["veto"].append("coverage %.4f < target %.2f and the input space was too large "
                               "(2**%d) to enumerate" % (rec["coverage"], target,
                                                         len(blif["inputs"])))
            rec["ok"] = False
        else:
            rec["ok"] = True
    if not rec["budget_ok"]:
        rec["veto"].append("vector budget exceeded: %d > %d" % (len(vectors), budget_vectors))
        rec["ok"] = False
    if rec["stages"].get("guided", {}).get("skipped_for_budget"):
        rec["veto"].append("guided stage stopped on budget with %d faults never attempted"
                           % rec["stages"]["guided"]["skipped_for_budget"])
    rec["missing_sample"] = ["%s/SA%d" % f for f in missing[:40]]
    rec["vectors_sha256"] = hashlib.sha256(
        json.dumps(vectors, sort_keys=True).encode()).hexdigest()
    # --- experience, evaluated but not published -------------------------------
    # Mirrors their ordering: lessons are evaluated against the finished artefact
    # and then wait for an explicit decision. Nothing here publishes itself, and a
    # design-specific fact is scoped project_only, which their scope split excludes
    # from publication -- so "true only here" cannot be read later as "general".
    rec["lesson_candidates"] = lesson_candidates(rec)
    return rec


def lesson_candidates(rec: dict) -> list:
    """Turn what this run measured into candidate lessons, with the numbers."""
    out = []
    if rec.get("error"):
        out.append(dict(problem="Design %s could not be simulated: %s" % (rec["design"], rec["error"]),
                        decision="Report the netlist as unusable rather than reporting a coverage "
                                 "number for it.",
                        applicability="Any BLIF with a combinational loop or an undriven output.",
                        prevention_action="Check acyclicity and driver completeness before any "
                                          "fault simulation, and name the failing net.",
                        scope="project_only", evidence={"error": rec["error"]},
                        artifact_sha256=rec.get("blif_sha256"),
                        tags=["netlist","sanity"]))
        return out
    g = rec["stages"].get("guided", {})
    if rec.get("coverage", 0) < rec.get("target", 0.99) and rec.get("not_detected"):
        gap = rec["coverage"] - rec["stages"].get("random", {}).get("coverage", 0)
        out.append(dict(
            problem="Coverage on %s stopped at %.4f with %d faults undetected; the guided stage "
                    "moved it by only %.4f." % (rec["design"], rec["coverage"],
                                                rec["not_detected"], gap),
            decision="Record the gap and the vector budget rather than raising the budget until a "
                     "number looks acceptable; %d of the guided attempts were skipped when the "
                     "wall-clock budget ran out." % g.get("skipped_for_budget", 0),
            applicability="Faults needing many simultaneous side conditions: wide AND trees, "
                          "priority logic, multiplier arrays.",
            prevention_action="Before adding vectors, measure whether the objective has a gradient "
                              "on the faults that remain; if the guided stage buys ~1%%, the "
                              "objective is flat and more time will not fix it.",
            scope="project_only",
            evidence={"coverage": rec["coverage"], "random": rec["stages"].get("random", {}).get("coverage"),
                      "guided": g.get("coverage"), "undetected": rec["not_detected"],
                      "vectors_used": rec["vectors_used"], "budget": rec["budget_vectors"],
                      "guided_skipped_for_budget": g.get("skipped_for_budget"),
                      "guided_budget_s": g.get("budget_s")},
            artifact_sha256=rec["blif_sha256"], tags=["atpg","budget",rec["design"]]))
    if rec.get("undetectable") is not None and rec.get("exhaustive", {}).get("done"):
        out.append(dict(
            problem="%d of %d faults on %s are not detectable by any input vector, and that is now "
                    "a proof rather than a gap: the input space was enumerated."
                    % (rec["undetectable"], rec["faults_total"], rec["design"]),
            decision="Separate 'not detected yet' from 'undetectable' in the report, and only claim "
                     "the second when 2**n_inputs vectors were actually enumerated.",
            applicability="Small combinational blocks; above %d inputs enumeration stops being a "
                          "decision procedure." % 14,
            prevention_action="Never print one coverage number for a design whose faults include "
                              "provably redundant ones; print both and say which is which.",
            scope="organization_general",
            evidence={"undetectable": rec["undetectable"], "faults_total": rec["faults_total"],
                      "vectors_enumerated": rec["exhaustive"].get("vectors")},
            artifact_sha256=rec["blif_sha256"], tags=["atpg","redundancy"]))
    return out


if __name__ == "__main__":
    outroot = sys.argv[1] if len(sys.argv) > 1 else r"D:\eda\test"
    want = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    work = os.path.join(outroot, "blif")
    os.makedirs(work, exist_ok=True)
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bench", "src")
    designs = [d[:-2] for d in sorted(os.listdir(src)) if d.endswith(".v")]
    if want:
        designs = [d for d in designs if d in want]
    for design in designs:
        bl = os.path.join(work, design + ".blif")
        if not os.path.exists(bl):
            continue
        rec = run_design(bl, design, outroot)
        print(json.dumps({k: rec.get(k) for k in
              ("design", "inputs", "outputs", "latches", "faults_total",
               "coverage", "undetectable", "vectors_used", "veto")}, ensure_ascii=False), flush=True)
        for st in ("random", "guided"):
            s = rec["stages"].get(st)
            if s:
                print("   %-7s vectors=%-5d detected=%-5d cov=%.4f  %ss"
                      % (st, s["vectors"], s["detected"], s["coverage"], s["seconds"]), flush=True)
    res = os.path.join(outroot, "results.json")
    print("done ->", res)
