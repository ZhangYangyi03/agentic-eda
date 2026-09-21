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


## Down to the package, and up from experience

Two more flows, same shape as the ones above -- propose, run, veto, feed back --
and they close the two loops that were open.

`agentic/packflow.py` starts from the die `physflow.py` actually produced and
answers the question the die cannot answer for itself. The pad ring does not fit:
`adder8` is 229 um^2 of logic, a 15 um square, and 23 pads at 60 um pitch need a
390 um edge. The die has to grow, and the flow computes by how much instead of
discovering it at assembly.

    design    pins  die grew to  substrate  part chosen                        layers  Tj
    adder8      23      390 um     4560 um  Texas_DSBGA-12_1.36x1.86mm            2   26.1 C
    adder16     43      690 um     5700 um  BGA-81_4.496x4.377mm_P0.4mm           1   25.8 C
    mult4       20      330 um     4460 um  Texas_S-PDSO-N10_EP1.2x2mm             2   26.1 C
    mult8       40      630 um     6100 um  Texas_VQFN-RHL-20_ThermalVias          3   25.8 C
    mult16      60      930 um     5700 um  BGA-81_4.496x4.377mm_P0.4mm           2   25.8 C
    prio32      40      630 um     6100 um  Texas_VQFN-RHL-20_ThermalVias          3   25.8 C

The parts are real: 11,994 footprints from the KiCad library, indexed and read,
their pad coordinates taken as given. Substrates are 2-4 layer BT or alumina --
that choice is a search, and each iteration changes exactly one thing the
previous veto named, with the reason recorded in `pack/results.json`.
`pack/mult8/mult8_substrate_top.gbr` is exported RS-274X, one copper layer, and
the writer refuses to emit a coordinate outside the outline it declares.

Package selection is the weakest step and says so: the shortlist is ranked by
outline area and then it walks to a coarser-pin part, which is not the same as
an area-and-cost trade study, and no assembly yield or coplanarity is modelled.
The 0.4 mm pitch of a BGA is the binding constraint on how many pins can escape
one substrate layer, and that number is measured (14.0-69.3 um between an escape
and a foreign pad) rather than vetoed, because a constant-width straight line
cannot satisfy a constant clearance rule across a pad field whose own separation
varies 20x. That took three wrong versions to admit.

`agentic/lessons.py` is the other closed loop, and it is the one this repo was
missing: what was learned now lives in records instead of in this file. A lesson
has four required prose fields -- problem, decision, applicability,
prevention_action -- and evidence with the measured numbers, bound to the hash of
the artefact it came from. `lessons.db` holds 14, every one of them a failure this
repo actually hit: the BLIF net defined in the last token not the second, the
signoff deck's 1221 against the router's 0, `make_tracks` before `read_liberty`,
three separate factor-of-1000 unit errors, Stoney curvature refusing ceramic
packages because tf/ts was 0.37 and the model needs 0.1.

The discipline is borrowed whole from `Milkdomeda/ai-mechanical-3dcad-design-agent`
(Apache-2.0): knowledge is an accelerator, never a precondition. `search` returns
`[]` on a missing or empty store and never raises; every run records which lessons
it consulted, so "ran without experience" and "ran against experience" are
different facts afterwards. Lessons are evaluated after the artefact is confirmed
and nothing publishes itself, and the scope split is theirs -- a lesson that is
true only here is `project_only` and is excluded from publication, so it cannot be
read next month as general.

## What none of this is

The signature of the mechanical-agent project, and it is the right one: **a
passing report proves the checks that ran against one exact revision. It is not
FEA, not a manufacturing release, not a safety certification, not a legal
standards certification. Final engineering responsibility stays with the user or
an authorised engineer.**

For this repo, concretely:

  * The GDS files are stream-out geometry. Every one carries signoff DRC
    violations this OpenROAD cannot repair (27-1221 boxes, min-area). Not
    manufacturable, and not claimed to be.
  * The thermal number is a lumped theta-JA = 7.7/sqrt(area_cm2). No board
    copper, no thermal vias, no neighbours, no FEM.
  * The warpage number is Stoney curvature, valid only for tf/ts < 0.1, and at
    0.37 it says NOT EVALUATED rather than guessing.
  * The substrate "DRC" is a clearance and containment check on geometry this
    file wrote. It is not a fab's deck, and there is no via, impedance, EM,
    solder-mask or drill check at all.
  * The ATPG coverage numbers come from a fault simulator cross-checked against
    `iverilog` and integer arithmetic on 1470 random probes, not against a
    commercial tool and not against silicon.


## Fault coverage, and the difference between "not found" and "cannot exist"

`agentic/testflow.py` is the third flow and it is the simplest to state: take the
netlist the synthesis search produced, ask how much of it a stuck-at test could
observe, and be exact about which of the two questions a number answers.

    design     gates faults   coverage  ceiling  provably redundant  enumerated  vectors  closed
    adder8         ?   316      0.9324        -                   -           -      400   no
    adder16        ?   302      0.9669        -                   -           -      400   no
    mult4          ?   316      0.4747   0.4747                 166         256      400   yes
    mult8          ?  1422      0.5120        -                   -           -      400   no
    mult12         ?  3307      0.5205        -                   -           -      400   no
    prio32         ?   424      0.5307        -                   -           -      499   no
    arbiter16      ?   296      0.7736        -                   -           -      422   no
    barrel16       ?   221      1.0000        -                   -           -      400   yes
    lfsr16         ?    74      0.0135   0.0135                  73           4      403   yes

Two thirds of the faults in a 4-bit multiplier are redundant: no input vector
distinguishes them from the fault-free circuit. That is not a coverage shortfall,
it is the ceiling, and it is a proof rather than a gap because 2**8 vectors is the
whole input space and all 256 were simulated. The `mult4` row is the flow working.

`lfsr16` at 0.0135 is the same statement about a shift register, under the
assumption the driver states out loud: latches are treated as pseudo-inputs and
pseudo-outputs, full-scan style. Under that assumption 73 of 74 faults are
redundant. Without it the number means something else entirely, which is why the
assumption is written down instead of left in the tool.

Six designs are **not** closed and the report says why in each case: the input
space was too large to enumerate, so `not_detected` is the honest word and
`undetectable` is not available. `repair` is not attempted and the wall-clock
budget of the guided stage is a first-class parameter, because the operator's
point is that cost is the difficulty, not the algorithm.

The numbers come from a fault simulator cross-checked against `iverilog` and
against integer arithmetic on 1470 random probes -- not against a commercial ATPG
tool, and not against silicon.

MIT.
