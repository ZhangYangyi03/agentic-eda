
"""llm_agent: close the loop. A model proposes, this machine measures, the verifier vetoes.

The difference from evolve_search is where the next candidate comes from. There,
mutation was blind. Here a language model sees the design, sees what its last
attempts measured, and proposes the next script -- which is the thing the
operator asked about ("is this a real closed loop, not a lookup table").

The invariant that makes it honest is unchanged, and it is the whole point:

    the model never reports a number. It only proposes.
    the harness measures, and the verifier decides whether the number is allowed
    to count. A candidate that fails equivalence is recorded as REJECTED and
    never enters the report as a small circuit.

So the model cannot end the run by claiming success. It cannot even influence
what "verified" means. If it proposes a script that produces a 12-gate network
computing the wrong function, the harness shows it the counterexample, and the
candidate counts for nothing.

Feedback given back to the model after each attempt:
    status    ok | rejected | invalid_script | unmeasured
    area      gate count ('and'), or 'aig' after a mapping step -- flagged, not compared
    lev       logic depth
    verify    the counterexample, or "cec equivalent", or the unproven count

Token cost is recorded per attempt, because the operator's question is
explicitly about whether a loop like this is affordable.
"""
from __future__ import annotations
import json, os, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evolve_search import evaluate, PRIMS, LATE_PRIMS
from synth_search import best_by_metric

CONFIG = r"C:\Users\china\.autoforge\config.json"

# The same primitive list the evolutionary search was given, so the two are
# compared on an equal information footing rather than the model being handed
# either more or less.
def command_surface() -> str:
    lines = []
    for name, opts in PRIMS:
        o = " | ".join([" ".join([name] + a).strip() for a in opts])
        lines.append(f"  {o}")
    lines.append("  strash              (required; fx/mfs/renode must come BEFORE it)")
    lines.append("  NOT available in this build: compress, compress2rs, resyn, resyn2rs")
    return "\n".join(lines)

SYSTEM = """You are choosing a synthesis script for a hardware design.

A design in BLIF form is given. Berkeley-ABC will run your script on it, and the
result is measured in two ways:
  area   gate count (fewer is better)
  lev    logic depth / critical path (fewer is better)

You will be told the result of every attempt, including when your script was
rejected because the circuit it produced no longer computes the same function.
A rejected attempt is worth nothing, however small it looked, so proposoing a
script that breaks equivalence is pure waste.

Available commands in this build of ABC (arguments shown are the legal sets):

{surface}

Rules:
  - Any script must contain `strash`.
  - `fx`, `mfs`, `renode` act on the logic network and MUST appear before
    `strash`. After `strash` they are a hard error.
  - Steps are separated by `; `.
  - Attempts are limited, so do not repeat a script you already tried.

Call run_abc_script with your script. After each result, use what you learned.
Work toward the least area, and separately toward the least depth -- they are
usually different designs and both are graded.

When you are done, reply with a short summary and no further tool call."""

TOOL = [{
    "type": "function",
    "function": {
        "name": "run_abc_script",
        "description": ("Run one ABC synthesis script on the current design. Returns the "
                        "measured area and depth, and whether the result was PROVEN "
                        "equivalent to the original design. A rejected result does not count."),
        "parameters": {"type": "object", "properties": {
            "script": {"type": "string", "description": "ABC commands separated by '; '"},
            "reason": {"type": "string", "description": "one line: what you expect and why"}},
            "required": ["script"]}}}]


def _post(cfg, payload, timeout=180):
    req = urllib.request.Request(cfg["base_url"].rstrip("/") + "/chat/completions",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {cfg['api_key']}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def run(design, gold, wd, seq, model_name, baseline, steps=12, verbose=True):
    cfg = json.load(open(CONFIG, encoding="utf-8"))
    os.makedirs(wd, exist_ok=True)
    sysmsg = SYSTEM.format(surface=command_surface())
    intro = (f"Design: {design}. It currently measures area={baseline['and']} lev={baseline['lev']} "
             f"under the naive baseline script `balance; rewrite`.\n"
             f"You have {steps} attempts. Beat that on area, on depth, or both.")
    msgs = [{"role": "system", "content": sysmsg}, {"role": "user", "content": intro}]
    transcript, tokens = [], {"prompt": 0, "completion": 0}
    tried = {}
    t_start = time.time()

    for step in range(1, steps + 1):
        payload = {"model": cfg["model"], "messages": msgs, "tools": TOOL,
                   "tool_choice": "auto", "max_tokens": 4000, "temperature": 0.7}
        try:
            d = _post(cfg, payload)
        except Exception as e:
            transcript.append({"step": step, "error": f"{type(e).__name__}: {e}"})
            break
        u = d.get("usage") or {}
        tokens["prompt"] += u.get("prompt_tokens", 0)
        tokens["completion"] += u.get("completion_tokens", 0)
        ch = d["choices"][0]
        msg = ch["message"]
        calls = msg.get("tool_calls") or []
        if not calls:
            fin = ch.get("finish_reason")
            # A truncated answer is not the model choosing to stop, and the two
            # arrive looking identical: both have content and no tool_calls.
            # This model reasons before it answers, so a small max_tokens is
            # spent entirely on reasoning and the visible content comes back
            # empty -- which earlier read as "the model had nothing to propose".
            transcript.append({"step": step,
                               "note": "truncated at max_tokens" if fin == "length" else "model stopped",
                               "finish_reason": fin,
                               "say": (msg.get("content") or msg.get("reasoning_content") or "")[:400]})
            msgs.append({k: v for k, v in msg.items() if k in ("role", "content")})
            if fin == "length":
                msgs.append({"role": "user", "content":
                             "Your reply was cut off before you called the tool. "
                             "Call run_abc_script now, with the script only -- no preamble."})
                continue
            break

        msgs.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
        for c in calls:
            try:
                args = json.loads(c["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                args = {"script": c["function"]["arguments"]}
            script = (args.get("script") or "").strip()
            reason = (args.get("reason") or "")[:160]
            if script in tried:
                res = dict(tried[script]); res["note"] = "already tried, not re-run"
            else:
                r = evaluate(gold, os.path.join(wd, f"s{step:02d}"), seq, model_name,
                             {"a": script}, t=600)
                res = r.get("a", {"status": "unmeasured", "error": "no result"})
                tried[script] = res
            row = {"step": step, "script": script, "reason": reason,
                   "status": res.get("status"), "area": res.get("and"), "lev": res.get("lev"),
                   "metric": res.get("metric"), "verify": res.get("verify"),
                   "error": res.get("error"), "note": res.get("note")}
            transcript.append(row)
            if verbose:
                print(f"   [{step:2d}] {res.get('status'):14s} area={res.get('and')} lev={res.get('lev')}"
                      f"  {script[:66]}", flush=True)
            fb = {"status": res.get("status"), "area": res.get("and"), "depth": res.get("lev")}
            if res.get("metric") == "aig":
                fb["area_unit"] = "aig (mapped network; NOT comparable to the 'and' count)"
            if res.get("verify"):
                fb["equivalence"] = res["verify"]
            if res.get("error"):
                fb["error"] = res["error"]
            if res.get("note"):
                fb["note"] = res["note"]
            msgs.append({"role": "tool", "tool_call_id": c["id"],
                         "content": json.dumps(fb, ensure_ascii=False)})

    ok = [r for r in transcript if r.get("status") == "ok"]
    bad = [r for r in transcript if r.get("status") == "invalid_script"]
    rej = [r for r in transcript if r.get("status") == "rejected"]
    unr = [r for r in transcript if r.get("status") == "unmeasured"]
    out = {"design": design, "baseline": baseline, "steps_used": len(transcript),
           "attempts": len(tried), "seconds": round(time.time() - t_start, 1),
           "tokens": tokens, "counts": {"ok": len(ok), "rejected": len(rej),
                                        "invalid_script": len(bad), "unmeasured": len(unr)},
           "transcript": transcript}
    if ok:
        # ranked inside one metric only; see best_by_metric's docstring for the
        # phantom depth win this prevents
        ba, bd = best_by_metric(ok, "area"), best_by_metric(ok, "lev")
        out["best_area"] = ba["canonical"]
        out["best_depth"] = bd["canonical"]
        out["mapped_best_area"] = ba["mapped"]
        out["mapped_best_depth"] = bd["mapped"]
        out["units"] = {"canonical": f"'and' rows, area=gate count, lev=AIG levels (n={ba['n_canonical']})",
                        "mapped": f"'aig' rows after a mapping step, NOT comparable (n={ba['n_mapped']})"}
        if out["best_area"]:
            out["beats_baseline_area"] = out["best_area"]["area"] < baseline["and"]
        if out["best_depth"]:
            out["beats_baseline_depth"] = out["best_depth"]["lev"] < baseline["lev"]
        # if the mapped rows would have won, say so as the unit error it is
        if ba["mapped"] and (not ba["canonical"] or ba["mapped"]["area"] < ba["canonical"]["area"]):
            out["unit_warning"] = ("a mapped 'aig' row is smaller than any 'and' row; it is "
                                   "reported separately because the two are different units")
    import contextlib
    sp = os.path.join(wd, "..", f"agent_{design}.json")
    json.dump(out, open(sp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    out["report"] = os.path.abspath(sp)
    return out
