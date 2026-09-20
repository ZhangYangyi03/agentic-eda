# agentic-eda

Synthesis-script search, then place and route to GDSII, on open-source EDA --
with a verifier that can veto at every stage.

You write Verilog. Something has to turn it into gates. That something is a
synthesiser with tens of knobs and a script language, and the choice of script
changes the resulting circuit by 8-30% in area and up to 61% in depth. Nobody
knows the right script in advance, so you try many.

Below the search, `agentic/physflow.py` carries a verified netlist all the way to
GDSII: OpenROAD for floorplan/place/CTS/route, magic for stream-out and signoff
DRC, open_pdks sky130A as the PDK. 11/11 benchmarks route, 11/11 have signoff
violations this OpenROAD cannot repair, and the README says which number is which.

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
    python agentic/physflow.py         # 11 benchmarks netlist -> GDSII + signoff DRC

The physical flow additionally needs, in WSL:

    micromamba install -p ~/eda-env -c litex-hub -c conda-forge open_pdks.sky130a magic
    apt install yosys openroad                    # openroad also ships on litex-hub

and the PDK is 2.7 GB unpacked under `~/eda-env/share/pdk/sky130A` (the 1.26 GB
tarball lands in micromamba's own cache; if `share/pdk` is empty afterwards the
package downloaded and unpacked but was not linked into the environment, and a
symlink is the fix -- not another download).

## Files

    agentic/spine.py          typed stages, hash-chained manifest, verify_manifest
    agentic/synth_search.py   elaboration, search, strategy set, parse_stats, gate self-test
    agentic/evolve_search.py  mutation and selection over scripts
    agentic/bench_gen.py      11 benchmark generators (no external corpus needed)
    agentic/run_bench.py      the 11-benchmark sweep
    agentic/llm_agent.py      the model-driven searcher (key read from outside the repo)
    agentic/physflow.py       netlist -> GDSII: OpenROAD, magic, sky130 signoff DRC
    bench/table.json          the synthesis result
    evolve/results.json       the search result, every candidate row included
    phys/results.json         the physical result: per-design hashes, both violation counts

## All the way to GDSII

The synthesis search above stops at a verified netlist. `agentic/physflow.py`
carries that netlist the rest of the way to silicon layout on the same open
toolchain, and it does it as a driver rather than a recipe:

    verified netlist
      |  OpenROAD    floorplan -> tracks -> pin place -> global place
      |              -> detailed place -> CTS -> filler -> route        -> DEF
      |  magic       stream out with the PDK's own GDSII cell library    -> GDS
      |  magic       signoff DRC, the PDK's rule deck, by name           -> violations
      v
    results.json  (per-design artifact hashes, both violation counts)

11 benchmarks, every stage green on 11/11, 430 s for the sweep:

    design     sky130 cells   area um2   util  router   signoff   GDS
    adder8            3          229      34%      0        27    50 KB
    adder16          18          512      31%      0        63   184 KB
    adder32          30         1085      32%      0       177   363 KB
    arbiter16        14          214      33%      0        37   122 KB
    barrel16         20          596      31%      0        74   205 KB
    lfsr16            6          502      33%      0        39   107 KB   (sequential, CTS ran)
    mult4            30          382      33%      0        54   238 KB
    mult8            37         1912      30%      0       293   476 KB
    mult12           50         4792      30%      0       640   938 KB
    mult16           57         8647      30%      0      1221  1509 KB
    prio32           20          425      32%      0        44   195 KB

**Two violation counts, because they are two different claims.** The router
reports 0 on all 11 designs: TritonRoute is satisfied with what it built. The
signoff deck disagrees on all 11: 27-1221 boxes. The rules are minimum *area*,
met1.6 (0.083 um^2), met2.6 (0.0676 um^2), met3.6 (0.24 um^2), and once a met1
spacing. They are in the technology LEF -- `AREA 0.083` sits right there under
`LAYER met1` -- but this OpenROAD does not repair them: there is no min-area
repair pass, no `add_met_fill`, and `detailed_route -help` is not even
supported. A flow that printed only the router's number would call all 11
layouts clean.

These three are the same kind of bug as the harness lies above: they report
success. The order of two commands is the whole difference between them:

  * The technology LEF is `techlef/sky130_fd_sc_hd__nom.tlef`. The corner
    suffix is part of the name. The LEF under `lef/` carries MACROs and zero
    `LAYER` statements, so reading it alone yields 0 technology layers and a
    design that reads, links, floorplans -- and then cannot route.
  * `make_tracks` must come after `read_liberty` (it takes microns; without a
    liberty it returns "command units uninitialized" and creates nothing) and
    after `initialize_floorplan` (tracks are laid over the current die). Wrong
    order creates zero tracks, and the failure surfaces two stages later in
    `place_pins` as "no horizontal tracks for met3".

And one that looks like a layout bug and is not: `arbiter16` has a `1'b1`
constant, yosys turns it into a net, OpenROAD's Verilog reader labels that net
`GROUND` by name, and TritonRoute refuses it -- "[DRT-0305] Net zero_ of signal
type GROUND is not routable". Nothing is wrong with the layout; the net's type
is. The driver demotes GROUND/POWER back to SIGNAL on every net that is not one
of the PDK's own power nets, before the floorplan. Designs without a constant
never hit it.

## What is still not here

No timing closure, no analogue layout, no tapeout. The GDS files are real,
stream-out, DRC-checked layout geometry -- and every one of them has signoff
violations that this OpenROAD version cannot repair, so they are evidence the
flow works, not evidence of manufacturability. A newer OpenROAD (litex-hub is
at 2.0_9990, this is 2.0_3175) may close the min-area gap; that has not been
measured here.

The analogue and in-memory-compute directions still need what they needed
before: a device model, an analogue benchmark corpus. The PDK part of that gap
is now closed -- open_pdks sky130A is installed and in use.

MIT.
