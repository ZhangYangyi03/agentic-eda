
"""agentic-eda spine: typed stages, hashed artifacts, verifiable manifests.

Three rules, and everything else hangs off them:
  1. a stage declares its inputs and outputs; an artifact not declared is not accepted
  2. every artifact is content-addressed (sha256) at the moment it is produced
  3. the manifest is a hash chain, so a tampered or lost output is visible

This is the piece the whole project rests on: unless a result is reproducible
from a manifest, an agent cannot tell a better netlist from a lucky one.
"""
from __future__ import annotations
import dataclasses as dc, hashlib, json, os, shutil, subprocess, time
from typing import Callable, Optional

ART = "artifacts"

def sha256(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

@dc.dataclass
class Stage:
    name: str
    run: Callable[[dict, str], dict]   # (inputs, workdir) -> declared outputs {role: path}
    inputs: tuple = ()                 # roles this stage consumes
    outputs: tuple = ()                # roles this stage produces
    tool: str = ""
    timeout: int = 900

@dc.dataclass
class Result:
    stage: str
    ok: bool
    hashes: dict
    seconds: float
    error: str = ""

class Flow:
    """Deterministic stage runner. Same inputs -> same manifest, or a recorded reason why not."""

    def __init__(self, root: str, seed: str = ""):
        self.root = os.path.abspath(root)
        self.seed = seed
        self.run_id = time.strftime("%Y%m%dT%H%M%S")
        self.art = os.path.join(self.root, ART)
        os.makedirs(self.art, exist_ok=True)
        self.artifacts: dict[str, str] = {}          # role -> path
        self.results: list[Result] = []
        self.env_notes: dict = {}

    def note_env(self, key, val):
        self.env_notes[key] = val

    def add(self, path: str, role: str) -> str:
        """Register an externally supplied artifact (a source RTL, a PDK waivers file)."""
        p = os.path.abspath(path)
        if not os.path.exists(p):
            raise FileNotFoundError(p)
        self.artifacts[role] = p
        return p

    def param(self, role: str, value) -> None:
        """Register a scalar input (a top-module name, a target clock period).

        Kept separate from add() so that a *path* input is still checked to
        exist: the distinction between 'here is a file' and 'here is a value'
        is exactly the kind of thing that turns into a silent wrong answer.
        """
        self.artifacts[role] = value

    def run(self, stage: Stage, workdir: Optional[str] = None) -> Result:
        for r in stage.inputs:
            if r not in self.artifacts:
                raise KeyError(f"stage {stage.name}: input role {r!r} missing "
                               f"(have {sorted(self.artifacts)})")
        wd = workdir or os.path.join(self.root, "work", stage.name)
        # A stage owns its directory. Leftovers from a previous run are cleared
        # first, because a stale artifact is indistinguishable from a fresh one
        # once it is on disk -- during this build a 634-byte gold.blif from a
        # failed run was read as the current output and made a working run look
        # broken. A failed stage must leave its predecessor's output absent,
        # not merely superseded.
        if workdir is None and os.path.isdir(wd):
            shutil.rmtree(wd, ignore_errors=True)
        os.makedirs(wd, exist_ok=True)
        t0 = time.time()
        try:
            out = stage.run({r: self.artifacts[r] for r in stage.inputs}, wd)
            missing = [r for r in stage.outputs if r not in out]
            if missing:
                raise RuntimeError(f"declared output(s) {missing} not produced")
            extra = [r for r in out if r not in stage.outputs]
            if extra:
                raise RuntimeError(f"undeclared output(s) {extra} produced")
            hs = {}
            for role, path in out.items():
                if not os.path.exists(path):
                    raise RuntimeError(f"{role}: declared path does not exist: {path}")
                hs[role] = {"sha256": sha256(path), "path": os.path.abspath(path),
                            "bytes": os.path.getsize(path)}
                self.artifacts[role] = path
            res = Result(stage.name, True, hs, round(time.time() - t0, 3))
        except Exception as e:
            res = Result(stage.name, False, {}, round(time.time() - t0, 3),
                         f"{type(e).__name__}: {e}")
        self.results.append(res)
        return res

    def manifest(self) -> dict:
        """Hash chain over stages, so a silently rewritten result shows up."""
        prev = "genesis"
        chain = []
        for r in self.results:
            core = {"prev": prev, "stage": r.stage, "ok": r.ok,
                    "hashes": {k: (v if isinstance(v, str) else v["sha256"])
                               for k, v in r.hashes.items()}}
            blob = json.dumps(core, sort_keys=True).encode()
            link = hashlib.sha256(blob).hexdigest()
            chain.append({"stage": r.stage, "ok": r.ok, "hashes": r.hashes,
                          "link": link, "prev": prev, "seconds": r.seconds,
                          "error": r.error})
            prev = link
        return {"root": self.root, "seed": self.seed, "run_id": self.run_id,
                "env": self.env_notes, "stages": chain, "head": prev}

    def save(self, path: Optional[str] = None) -> str:
        path = path or os.path.join(self.root, "manifest.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.manifest(), f, indent=2)
        return path

def verify_manifest(path: str, check_files: bool = True) -> tuple[bool, list[str]]:
    """Re-derive the hash chain, and re-hash every artifact on disk.

    Two different failures, deliberately reported separately:
      - a broken or truncated chain  -> the *record* was edited
      - an artifact whose bytes moved -> the *work* was edited
    A manifest that cannot catch the second one is decoration, not evidence, so the
    artifact paths and byte counts are stored alongside the hash.
    """
    with open(path, encoding="utf-8") as f:
        m = json.load(f)
    prev, problems = "genesis", []
    for s in m["stages"]:
        for role, rec in s["hashes"].items():
            if isinstance(rec, str):                     # legacy: bare hex digest
                continue
            blob = json.dumps({"role": role, "sha256": rec["sha256"],
                               "path": rec.get("path", "")}, sort_keys=True).encode()
        core = {"prev": prev, "stage": s["stage"], "ok": s["ok"],
                "hashes": {r: (v if isinstance(v, str) else v["sha256"])
                           for r, v in s["hashes"].items()}}
        if hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest() != s["link"]:
            problems.append(f"chain break at stage {s['stage']!r}: record was edited")
        prev = s["link"]
        if check_files:
            for role, rec in s["hashes"].items():
                if isinstance(rec, str):
                    continue
                fp = rec.get("path")
                if not fp or not os.path.exists(fp):
                    problems.append(f"{s['stage']}/{role}: artifact missing: {fp}")
                    continue
                h = hashlib.sha256()
                with open(fp, "rb") as fh:
                    for b in iter(lambda: fh.read(1 << 20), b""):
                        h.update(b)
                if h.hexdigest() != rec["sha256"]:
                    problems.append(f"{s['stage']}/{role}: artifact changed on disk: {fp}")
    if prev != m["head"]:
        problems.append("head mismatch: manifest tail edited or truncated")
    return (not problems), problems
