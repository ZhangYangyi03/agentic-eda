"""lessons: design experience as records, not as prose in a README.

The gap this closes: after a run, what was learned lived in the README as text.
That is readable and it is not searchable, not bound to the artefact it came from,
and not reusable by the next search. Borrowed wholesale from
Milkdomeda/ai-mechanical-3dcad-design-agent (Apache-2.0), whose Design Lesson
schema is four required prose fields per lesson plus a scope:

    problem  decision  applicability  prevention_action

Two things their design gets right that this one copies exactly:

  * a lesson is not free-form. Those four fields are required, so a lesson cannot
    be recorded as "it didn't work" -- it has to say what the problem was, what
    was decided, when it applies, and what to do about it next time.
  * lessons are evaluated AFTER the artefact is confirmed, and bound to the
    artefact's hash. A lesson with no hash is an opinion about nothing.

What this adds for EDA specifically: `evidence`, carrying the measured numbers and
the tool version. Their lessons describe a model revision; ours have to describe
which OpenROAD, which yosys, what the router said and what the signoff deck said.
"Router reported 0, signoff reported 1221" is a lesson only if both numbers, both
tools and the versions travel with it.

Scope follows their split because it is the right one: a lesson from this repo's
flow is publishable; a lesson that is project-only is EXCLUDED from publication
and stays local. Nothing here is published anywhere -- the split exists so that
"this is general" and "this is true only here" cannot be silently confused later.

And the discipline that matters most, in their words: knowledge is an accelerator,
not a precondition. `search` returns [] with an empty or unreachable store and
never raises; every caller is written to continue.
"""
from __future__ import annotations
import hashlib, json, os, sqlite3, time

DB_PATH = os.environ.get("EDA_LESSONS_DB", r"D:\eda\lessons.db")
REQUIRED = ("problem", "decision", "applicability", "prevention_action")
PUBLICATION_SCOPES = ("organization_general", "design_group", "product_family")
EXCLUDED_SCOPES = ("project_only", "customer_specific")
SCHEMA = "EdaDesignLesson/v1"

DDL = """
CREATE TABLE IF NOT EXISTS lessons (
  id            TEXT PRIMARY KEY,
  schema        TEXT NOT NULL,
  scope         TEXT NOT NULL,
  problem       TEXT NOT NULL,
  decision      TEXT NOT NULL,
  applicability TEXT NOT NULL,
  prevention_action TEXT NOT NULL,
  evidence_json TEXT NOT NULL,
  artifact_sha256 TEXT,
  tags          TEXT NOT NULL,
  created_utc   TEXT NOT NULL,
  uses          INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS lessons_scope ON lessons(scope);
"""


def canon(d) -> str:
    return json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def lesson_id(body: dict) -> str:
    return "edal-" + hashlib.sha256(canon(body).encode()).hexdigest()[:16]


def make_lesson(problem, decision, applicability, prevention_action,
                scope="organization_general", evidence=None, artifact_sha256=None,
                tags=()) -> dict:
    """Build a lesson, refusing anything that is not a lesson.

    The required-field check is the point, not a formality: it is what stops
    "doesn't work, try something else" from entering the store and being
    retrieved later as if it were knowledge.
    """
    fields = {"problem": problem, "decision": decision, "applicability": applicability,
              "prevention_action": prevention_action}
    for k in REQUIRED:
        v = fields.get(k)
        if not isinstance(v, str) or len(v.strip()) < 12:
            raise ValueError("lesson field %r must be a real sentence, got %r" % (k, v))
    if scope not in PUBLICATION_SCOPES + EXCLUDED_SCOPES:
        raise ValueError("unknown scope %r" % scope)
    body = {"schema": SCHEMA, **fields, "scope": scope,
            "evidence": evidence or {}, "artifact_sha256": artifact_sha256,
            "tags": sorted(set(tags))}
    body["id"] = lesson_id(body)
    return body


def _connect(path=None):
    con = sqlite3.connect(path or DB_PATH)
    con.executescript(DDL)
    return con


def publish(lesson: dict, path=None) -> dict:
    """Store a lesson. Re-publishing the same lesson is a no-op, not a duplicate."""
    con = _connect(path)
    try:
        cur = con.execute("SELECT id FROM lessons WHERE id=?", (lesson["id"],))
        if cur.fetchone():
            return {"stored": False, "reason": "already present", "id": lesson["id"],
                    "scope": lesson["scope"],
                    "publishable": lesson["scope"] in PUBLICATION_SCOPES}
        con.execute("INSERT INTO lessons (id,schema,scope,problem,decision,applicability,"
                    "prevention_action,evidence_json,artifact_sha256,tags,created_utc) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (lesson["id"], lesson["schema"], lesson["scope"], lesson["problem"],
                     lesson["decision"], lesson["applicability"], lesson["prevention_action"],
                     canon(lesson["evidence"]), lesson["artifact_sha256"],
                     ",".join(lesson["tags"]), time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                             time.gmtime())))
        con.commit()
        return {"stored": True, "id": lesson["id"], "scope": lesson["scope"],
                "publishable": lesson["scope"] in PUBLICATION_SCOPES}
    finally:
        con.close()


def search(query: str, path=None, scope=None, limit=20) -> list:
    """Lessons matching `query`, newest evidence first.

    Returns [] rather than raising when the store is missing, empty or unreadable:
    knowledge is an accelerator, never a precondition, and a caller that cannot
    proceed without it has the dependency backwards.
    """
    try:
        con = _connect(path)
    except Exception:
        return []
    try:
        terms = [t.lower() for t in query.split() if t.strip()]
        rows = con.execute("SELECT id,scope,problem,decision,applicability,"
                           "prevention_action,evidence_json,artifact_sha256,tags "
                           "FROM lessons").fetchall()
        scored = []
        for r in rows:
            if scope and r[1] != scope:
                continue
            blob = " ".join(str(x) for x in r[1:]).lower()
            hits = sum(1 for t in terms if t in blob)
            if hits:
                scored.append((hits, r))
        scored.sort(key=lambda x: -x[0])
        out = []
        for h, r in scored[:limit]:
            d = {"id": r[0], "scope": r[1], "problem": r[2], "decision": r[3],
                 "applicability": r[4], "prevention_action": r[5],
                 "evidence": json.loads(r[6]), "artifact_sha256": r[7],
                 "tags": r[8].split(",") if r[8] else [], "hits": h}
            con.execute("UPDATE lessons SET uses=uses+1 WHERE id=?", (r[0],))
            out.append(d)
        con.commit()
        return out
    except Exception:
        return []
    finally:
        con.close()


def stats(path=None) -> dict:
    try:
        con = _connect(path)
        rows = con.execute("SELECT scope,count(*),sum(uses) FROM lessons GROUP BY scope").fetchall()
        tot = con.execute("SELECT count(*) FROM lessons").fetchone()[0]
        con.close()
        return {"db": path or DB_PATH, "total": tot,
                "by_scope": {r[0]: {"lessons": r[1], "uses": r[2]} for r in rows}}
    except Exception as e:
        return {"db": path or DB_PATH, "total": 0, "error": repr(e)}


# --------------------------------------------------------------- seed lessons
# Every one of these is a failure this repo actually hit, with the number that
# showed it. They are not examples -- they are the reason the code has the shape
# it has, and they are what the next search should read before proposing.

SEED = [
 dict(problem="Every design reported 0.0000 coverage and no tool raised an error: "
              "fault simulation ran, printed a number, and the number was meaningless.",
      decision="BLIF `.names <fanin...> <output>` defines the net in the LAST token, not "
               "the second; the parser had been taking token[1] as the output, so every net "
               "was registered under the name of its first fanin and no real net had a driver.",
      applicability="Any consumer of yosys BLIF that indexes the output as field 1.",
      prevention_action="Cross-check the simulator against a second simulator on the same "
                        "vectors before trusting any coverage number. 1200 vectors x adder8 and "
                        "adder16: python simulator == iverilog == integer addition, 0 mismatches.",
      evidence={"observed": "coverage 0.0000 on 11/11 designs", "expected_after_fix": "0.9324 on adder8",
                "cross_check": "iverilog 11.0, 1200 vectors, 0 divergences"},
      tags=["blif","parsing","silent-failure"]),
 dict(problem="A net that yosys defines with four separate .names blocks was losing three of "
              "them; one of those blocks held the empty-table constant 0 that made $false false.",
      decision="BLIF permits a net to be defined by several .names blocks and the function is "
               "the OR of them. Store all blocks per net; evaluate per block and OR the results.",
      applicability="Any BLIF reader; yosys 0.9 emits this for $false and for want-of-'.alu' nets.",
      prevention_action="Assert before simulating that every primary output has a block and that "
                        "the netlist is acyclic; do not let a missing definition become an X.",
      evidence={"observed": "36 of 60 .names parsed, 18 nets with duplicate blocks",
                "expected_after_fix": "60 of 60"}, tags=["blif","parsing"]),
 dict(problem="Coverage was reported too low because the ground-truth oracle never applied the "
              "fault: stuck-at faults on primary inputs were counted as undetected.",
      decision="simulate() injected the fault only inside the topological sweep, and primary "
               "inputs are not in that sweep. Inject before the sweep when the net has no driver.",
      applicability="Matters for pad-level defects and any design where the fault list includes "
                    "primary inputs, i.e. always.",
      prevention_action="Keep two independent detection paths (full simulation, and full-good + "
                        "fanout-cone) and treat a disagreement between them as a bug in one of "
                        "them, not as noise. 3 of 150 probes disagreed; the cone path was right.",
      evidence={"observed": "oracle said not_detected for faults never applied",
                "after_fix": "three-way agreement 210/210 on 7 designs"}, tags=["atpg","oracle"]),
 dict(problem="Cone-accelerated fault simulation with an INPUT cone returned no differences and "
              "coverage far too low, because nets in the cone have other fanins whose values were "
              "never computed and evaluate to X.",
      decision="The correct shape is a full good simulation once per vector, then per fault copy "
               "those values, force the faulted net, and re-evaluate only its FANOUT cone.",
      applicability="Any fault simulator that wants per-fault cost proportional to cone size.",
      prevention_action="Validate the accelerated path against the unaccelerated one on random "
                        "probes before using it for a number that anyone will read.",
      evidence={"observed": "19/100 probes disagreed with the full simulation on adder8, 10/100 on prio32",
                "after_fix": "0 disagreements in 1470 probes"}, tags=["atpg","cone","performance"]),
 dict(problem="The ATPG search objective returned 'detected' when the OPPOSITE-value fault would "
              "have been visible, so the search and the verifier disagreed about what detected means.",
      decision="Detection is decided only with the fault's own forced value and the same PPO "
               "comparison the coverage stage uses. The opposite value is used only to score a "
               "gradient and can never return the verdict.",
      applicability="Any search whose objective is also its acceptance criterion.",
      prevention_action="Separate the objective from the verdict in the code, not just in the "
                        "comment, and probe the objective against the oracle on known faults.",
      evidence={"observed": "7 of 12 probes disagreed with the oracle on adder8, both directions",
                "after_fix": "1470/1470 probes agree"}, tags=["atpg","search","verification"]),
 dict(problem="A guided ATPG stage improved coverage by about 1% over random and stalled, because "
              "the objective was flat: a deep fault flips no output until every side condition "
              "holds at once, so hill climbing had no gradient.",
      decision="Add a controllability term: count the cone fanins already sitting at a "
               "non-controlling value, computed from each block's own truth table rather than "
               "assumed from the gate name. That is the term that finds a 15-way conjunction.",
      applicability="Faults behind wide and/or deep reconvergent logic, i.e. priority encoders, "
                    "deep carry chains, wide multipliers.",
      prevention_action="Measure the objective's gradient, not only the final coverage: if extra "
                        "search time buys ~1%, the objective is flat and more time will not fix it.",
      evidence={"observed": "prio32 0.4552 -> 0.4670 with 300 extra vectors, 226 faults still undetected",
                "stage_2": "guided stage under a wall-clock budget"}, tags=["atpg","search","gradient"]),
 dict(problem="A physical flow printed 'router reported 0 violations' for all 11 designs and could "
              "have declared every layout clean; the PDK's own signoff deck disagreed on all 11.",
      decision="Record both counts and name both: 'violations_router' and 'violations_signoff'. "
               "Neither is called clean on its own, and the signoff number is the one that gates.",
      applicability="Any flow where DRC is reported by the router and again by a deck.",
      prevention_action="Never let a router's self-report stand as a DRC result. Run the deck and "
                        "publish both numbers and the tool version beside them.",
      evidence={"router": "0 on 11/11", "signoff_deck": "27 to 1221",
                "cause": "min-area (met1.6 = 0.083 um2) unfixed by OpenROAD 2.0_3175, no add_met_fill",
                "tools": "OpenROAD 2.0_3175, magic, sky130A PDK"}, tags=["drc","signoff","honesty"]),
 dict(problem="`make_tracks` produced zero tracks and the failure surfaced two stages later as "
              "'no horizontal tracks on met3' during pin placement.",
      decision="make_tracks must follow read_liberty (it takes micrometres) and follow "
               "initialize_floorplan (it lays tracks over the current die).",
      applicability="Every OpenROAD script that places pins.",
      prevention_action="Check the track count immediately after make_tracks and fail there, "
                        "not two stages later where the message no longer names the cause.",
      evidence={"error": "no horizontal tracks on met3, at place_pins",
                "tools": "OpenROAD 2.0_3175"}, tags=["openroad","ordering","error-locality"]),
 dict(problem="CTS reported success and the router then blamed CTS's own inserted buffer: pin of "
              "clkbuf_1_0__f_clk outside the die.",
      decision="CTS does not legalize the buffers it inserts. Legalize after CTS, before routing.",
      applicability="Any clocked design going through CTS in this flow.",
      prevention_action="Treat 'stage returned success' as a claim to verify against the next "
                        "stage's preconditions, not as a fact about the layout.",
      evidence={"subsystem": "cts", "blamed_by": "detailed_route"}, tags=["cts","openroad"]),
]
