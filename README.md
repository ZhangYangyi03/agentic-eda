# agentic-eda

Synthesis-script search on open-source EDA, with a verifier that can veto.

You write Verilog. Something has to turn it into gates. That something is a
synthesiser with tens of knobs and a script language, and the choice of script
changes the resulting circuit by 8-30% in area and up to 61% in depth. Nobody
knows the right script in advance, so you try many.

This is that search, plus the part most such attempts skip:

> **A smaller circuit that computes the wrong function is not progress.**

Every candidate is proven equivalent to the original before its number is
allowed to mean anything. A candidate that fails equivalence is recorded as
**rejected**, never as a small one.

## Pipeline

    RTL (.v)
      |  yosys  -- elaborator only:  synth -top X -noabc   ->  BLIF
      |  abc    -- the search subject:  <script>; print_stats; write_blif
      |  verifier -- chosen by shape, not by habit
      v
    manifest.json  (hash-chained receipt)  +  mapped BLIF

```
combinational  ->  abc "cec <reference.blif>"        counterexample if it fails
sequential     ->  yosys equiv_make / equiv_simple -seq 5
                   / equiv_induct -seq 5 / equiv_status   (0 unproven required)
```

## Measured results

13 hand-written strategies x 11 benchmarks, all generated locally so the run
needs no GitHub access. All 110 verified candidates are in `bench/table.json`;
every one passed its verifier and its manifest check, and the verifier's own
self-test refused the deliberately corrupted netlist in 11/11 cases.

Improvement over the naive `balance; rewrite` baseline:

    benchmark     area      depth
    adder32      -30.1%    -61.2%
    adder16      -27.8%    -42.9%
    arbiter16    -25.9%    -18.8%
    prio32       -16.3%    -50.0%
    mult4        -11.8%     -6.2%
    mult8         -8.3%    -22.2%
    mult12        -8.0%    -34.0%
    mult16        -7.5%    -41.2%
    adder8       -26.0%    -22.2%
    barrel16       0.0%      0.0%
    lfsr16         0.0%      0.0%

`barrel16` and `lfsr16` are 0.0% on purpose. They are already shallow and
regular, the strategy set saturates immediately, and no script beats the
baseline. That is a real result, not a bug, and it is left in rather than
tuned away.

## Search, not a table

`agentic/evolve_search.py` mutates and selects *scripts* -- parameters, step
order, insertion, deletion -- under the same verifier. A candidate owns its own
`strash` position, because `fx`, `mfs` and `renode` act on the logic network
and ABC rejects them outright once the network is strashed.

Against the hand-written set on 5 benchmarks:

    prio32    area  77 -> 68   (-11.7%)   fx; mfs; strash; rewrite -l; resub -K 8; dc2
    adder32   depth 26 -> 25
    mult8 / barrel16 / lfsr16   parity, or 0.2-0.3% worse

Honest reading: the search wins on one shape. The winner appeared in generation
zero, in the seed set, so it was not found by mutation. Attributing a win to
"the search works" needs repeated experiments across seeds with a controlled
budget, which has not been done here. Three of five benchmarks show no gain.

## Three ways this harness lied, and what caught each

These are kept because they are the actual cost of the work, and because each
one is the kind of failure that reports success.

**1. `cec` with no argument is a rubber stamp.** Bare `cec` compares nothing
and prints "equivalent" for an AND network against an OR network. The first
equivalence check passed 7/7 that way. The correct form is `cec <reference>`,
which returns `a=1 b=0` as a counterexample. The fix is accompanied by a
mandatory self-test: corrupt one `11 1` to `10 1` in a real product and the
verifier must refuse it. If it does not, the run aborts rather than reporting.

**2. A different metric is not a failure.** After `if`, ABC reports a mapped
network as `aig = 1157 lev = 5` with no `and` field at all, and an area regex
finds nothing. Separately, `and = 473 (choice = 22)  lev = 35` carries an
optional `(choice = N)` infix that a `\s+lev` pattern never matches. Ten
legal candidates were scored as failures because of this, which had produced
the false conclusion that the search loses to the hand-written set. Statistics
are now parsed field by field, and an absent metric is reported as `unmeasured`
rather than `failed`.

**3. A timestamp is not non-determinism.** ABC writes
`# Benchmark "x" written by ABC on <date>` as line 1. Two identical runs
hashed differently. Normalising that line before hashing shows the products are
byte-identical across independent runs.

Also worth writing down, from the toolchain: `2>&1 | tail -4` swallows the
statistics line, because WSL injects localhost proxy warnings on stderr;
concurrent `wsl.exe` calls intermittently return empty stdout, which in a
threaded harness is indistinguishable from a candidate producing nothing.

## Running it

Requires WSL with `yosys` and `berkeley-abc` (`apt install yosys
berkeley-abc`), Python 3.10+.

    python agentic/run_bench.py        # 11 benchmarks through the hand-written set
    python evolve_run.py               # search vs the hand-written set
    python determinism_check.py        # two independent runs, compare hashes
    python selftest_spine.py           # manifest integrity: tamper and truncate

## Files

    agentic/spine.py          typed stages, hash-chained manifest, verify_manifest
    agentic/synth_search.py   elaboration, search, strategy set, parse_stats, gate self-test
    agentic/evolve_search.py  mutation and selection over scripts
    agentic/bench_gen.py      11 benchmark generators (no external corpus needed)
    agentic/run_bench.py      the 11-benchmark sweep
    bench/table.json          its result
    evolve/results.json       the search result, every candidate row included

## What is not here

No place and route, no GDSII, no timing closure, no analogue layout. The flow
stops at a verified netlist. The interesting directions above that -- circuit
as code, self-evolving synthesis, compilers for in-memory-compute macros -- all
need something this repo does not have: an analogue benchmark corpus, a device
model, a PDK. Writing more code would not supply them, so nothing is claimed
about them.

MIT.
