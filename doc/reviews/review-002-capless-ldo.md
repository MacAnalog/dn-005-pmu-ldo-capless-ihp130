# Review — `feat/002-capless-ldo` @ `0d8ba01`

**KIND: REVIEW.** 2026-09-04. Independent sign-off of the capless LDO branch by a verifier who
is not its designer (CLAUDE.md rule 7). Everything below was re-derived from the committed
sources: decks rebuilt from `lab.dut.Design`, the layout rebuilt from `layout/gen_ldo.py`, and
rule-check, connectivity-check, extraction and every bench re-run by the verifier. No number in
this review is quoted from the designer's logs.

## 1. Verdict

**The headline stands as measured.** A capless LDO at 36.28 µA quiescent current passes the whole
S1–S8 box at tt / 27 °C both before and after layout, and every committed number reproduces —
most of them to the last committed digit — from an independent rebuild. The corner story
reproduces at the three corners I re-ran (ss/−40 °C, ff/125 °C and tt/27 °C, all within
0.05 mV of the committed values); the remaining twelve of the fifteen are quoted from the
branch, not independently re-measured.

Four qualifications belong beside that sentence, and none of them is in the repository today:

1. The layout's 10 mA supply path is drawn 12–17× over the process's own metal current-density
   limit. Neither the rule check nor the connectivity check looks at current density, so a
   "DRC 0 / LVS matched" cell can carry this and does (B1).
2. The post-layout PASS is not produced by the frozen measurement path. Under the frozen
   definitions seven of thirteen benches are discarded and three spec lines report *missing*;
   the passing table comes from a local override that lives in `layout/postlayout.py` (M4).
3. The bias mechanism is a **step**, not a ramp, and the named next increment does not follow
   from the evidence as written: a supply-independent bias pinned at the design's own 36.3 µA
   fails S7 at ff/125 °C (M6).
4. The schematic of record does not carry the capacitor sizes or the reference value, and the
   equivalence check that "proves" it passes anyway (M3).

The design itself is sound and the experimental record is unusually honest. The problems are in
what the evidence is claimed to cover.

## 2. Findings

Severity: **B** blocker (must be fixed before the cell is called done), **M** major (a claim in
the repository is wrong or unsupported), **m** minor.

| # | sev | where | what | why it matters | fix | status |
|---|---|---|---|---|---|---|
| B1 | B | `layout/gen_ldo.py:102` (`rail_w=0.8`), `:492` (vout bus `0.6`), `:55` (`W_M1=0.2`), `:205` (`vstack`), `:564`/`:571` (pin track + label) | The whole load current is carried on minimum-ish Metal1. Process limit (process spec §2.15): Metal1 **1 mA/µm** for w > 0.36 µm, **0.36 mA total** for w = 0.16–0.36 µm, **0.4 mA per Via1**. Drawn: vdd rail 0.8 µm → 0.8 mA against 10 mA (**12.5×**); vout drain bus 0.6 µm → 0.6 mA against 10 mA (**16.7×**); each pass-device source/drain column drop is a 0.2 µm bar carrying ≈1 mA against 0.36 mA (**2.8×**); `vstack` at `VPAD=0.38` places exactly **one** Via1 per layer transition (0.4 mA). The **`vout` pin is the worst point**: the pin label (`:571`) sits on the channel track drawn at the default `W_M1` = 0.2 µm (`:564`), and `to_track` (`:270`) reaches it from the 0.6 µm drain bus through a single 0.2 µm Metal2 column with one Via1 at each end (`vert`, `:228`) — 10 mA into a 0.36 mA bar and a 0.4 mA via, i.e. **25–28×**, worse than the 16.7× on the bus. | Electromigration is not a rule-deck check and not a connectivity check, so nothing in the flow can see it. A cell that fails it is not manufacturable at its rated load, whatever the box says. | Route the supply and output on upper metal (TopMetal1 is 15 mA/µm), widen the rails to ≥ 12 µm equivalent, multiply vias in the power path, and add a current-density stage to `layout/signoff.py`. | reproduced (generator constants + process spec) |
| M1 | M | `spicexplorer-harness/.../lint.py::_backing_rows` vs `lab/metrics.py::certify` | The author says `make lint` is red only for want of a signed verifier row. It is not. `_backing_rows` matches a signed row on `data.get("tag")` — the scorecard's **top-level** `tag` — while `certify()` writes the tag inside `provenance` and writes no `script_sha` / `raw_sha` / `computation_hash`. Neither the exact-hash path nor the loose path can ever match. | No admissible ledger row can turn the lint green in this scorecard shape, so the failure is a permanent false alarm rather than a missing signature. | Either have `certify()` emit a top-level `tag` (plus `corner`) and a hash block, or have `_backing_rows` fall back to `provenance.tag`. | **reproduced**: two admissible signed rows appended, lint still reports `(tag None)` for both scorecards |
| M2 | M | analog-db LDO class template `.../classes/ldo/testbench-templates/noise.spice:22` | `let vn_out_rms = sqrt(onoise_total)` takes an extra square root: in this simulator build `onoise_total` is already the integrated output noise in volts RMS. | Every scorecard in the repository carries a wrong output-noise number, and the error is in a shared class template, so it is not local to this design. | Report `onoise_total` directly. | **reproduced** on a case with an exact analytical answer: a 1 MΩ/1 MΩ divider (true 288 µVrms over 10 Hz–10 MHz) returns `onoise_total = 2.879e-4` (correct) and `vn_out_rms = 17.0 mVrms` (√ of a voltage). Corrected values: candidate **366 µVrms** (reported 19 142 µV), reference **25.4 µVrms** (reported 5 038 µV) |
| M3 | M | `circuits/ldo_ihp_capless/xschem/ldo_ihp_capless.sch`; claim in `experiments/004-schematic/README.md` §1 and the notebook §5 | Netlisting the committed drawing yields `XCFF lp_brk fb cap_cmim m=1`, `XCC ea_out ea_o1 cap_cmim m=1`, `XCOUT vout vss cap_cmim m=c_out_m` — **no `w`, no `l`** — and `VREF vref vss 3` in place of `dc {vref_val}`. The device model's own defaults are 7 µm × 7 µm ≈ 74 fF, against the certified 0.1 pF, 4.4 pF and 4 × 5 pF. The equivalence check still returns `equivalent=True, 22 components, 15 nets`. | The README states the drawing matches "by model, connectivity and parameter expression" and therefore "cannot drift from the design of record". For the three capacitors and the reference source that is false, and the drawing does not netlist to a working circuit. This is the same class of silent verifier failure the repository already journals under `vacuous-equivalence-passes.md`, and it slipped past that lesson. | Either compare parameters as well as topology (and fail on a device whose size is absent), or restate the claim as topology-only. | reproduced (drawing re-netlisted, both equivalence verdicts re-run) — and confirmed against the designer's own committed artefact `experiments/004-schematic/out/ldo_ihp_capless.spice:4,6,17,25`, which carries the identical `VREF vref vss 3` and size-less `cap_cmim` lines, so this is not an artefact of the verifier's netlisting setup |
| M4 | M | `layout/postlayout.py:111–137`; `experiments/005-layout/README.md` §1 | Run through the frozen `lab.metrics.run_decks`, the extracted netlist fails **7 of 13** benches and the box reports `S3 missing, S6 missing, S8 missing`. The PASS comes from `run_tolerant`, a local rule that is not in `lab/`. The README and the code comment both say "six"; the journal says seven. Seven is correct. | Rule 2 says the frozen definitions certify. The post-layout row is therefore evidence from a different measurement path than the pre-layout row it is compared against, which is exactly the divergence the verifier brief calls a harness finding that outranks the design verdict. | Apply the fix in `lab/sim.py` (see M5) so both rows come from one path; correct "six" to "seven". | reproduced (strict path run first, then the tolerant path) |
| M5 | M | `lab/sim.py:55–103` vs `spicexplorer_core.spice_engine.deck_run` + `.sim_log` | `lab/sim.py` re-implements, more crudely, a platform module that already exists: deck text in, own run directory out, log read back, `parse_measures`, fatal-line scan, a `RunResult` with `measures`/`failed`/`fatal`, a deck hash. The platform's `sim_log._LEVEL_PATTERNS` already orders the `Warning:` pattern **before** the bare `singular matrix` pattern, with the comment that a warning during gmin stepping is recoverable — i.e. the platform had already solved the bug the local copy re-introduced. | The journal carries a "proposed diff" for a fix that is not needed: the correct action is to delete the local fatal scan and call the platform. Two copies of `parse_measures` also exist (the platform's is documented as the wider form). | Replace `lab/sim.py`'s scan with `sim_log.fatal_lines`, or replace the module with `run_deck`. | **reproduced**: `fatal_lines()` returns **0** lines on all seven discarded logs, and the measures parse |
| M6 | M | `doc/design-reference.md` §4 ("Facts that constrain every candidate", item 4); `doc/journal/resistor-bias-spread-binds-both-ends.md`; `experiments/003-sizing/README.md` §3 | Two claims do not survive measurement. (a) "the gate slews proportionally slower and S7 fails by 2×" — S7 against bias current is a **step**: at ss/−40 °C, S7 is 83.8 mV at Iq 30.9 µA, 88.3 mV at 28.8 µA and **309.8 mV at 27.8 µA**, a 3.5× jump for a 3.4 % current change. The recovery time steps with it — 0.143 µs at 30.9 µA and 0.203 µs at 28.8 µA against **1.27–1.33 µs** across the four failing points (125–134 µm bias resistor) — the same signature as the `c_ff_w` cliff, i.e. a change of mechanism rather than a degradation of one. The same threshold exists at tt/27 °C (118.8 mV at 30.7 µA, 200.8 mV at 25.9 µA). (b) "a PVT-stable reference collapses the spread and relaxes both ends at once" — a bias pinned at the design's own 36.3 µA gives S7 = **165 mV (fail)** at ff/125 °C. The window that clears both corners is Iq ≈ 41–50 µA at ff/125 °C, i.e. the headline current would have to rise 13–38 %. | The named next increment is the branch's stated exit path. As written it under-states what it costs: it trades most of the S5 margin the 36 µA headline is built on. A constant-transconductance reference is also the wrong prescription in kind — it holds *gm* constant, while the quantity that sets the pass-gate slew is a current, and a beta-multiplier current still tracks the resistor and mobility. | Restate the mechanism as a threshold in the gate-sink current; state the required nominal Iq window and its S5 cost; sweep `r_bias_l` locally the way `optimizer-parks-on-cliffs.md` already requires for a knob at an odd interior value (138.5 µm sits ~11 % from a step). | **reproduced**: 18 bias points across three corners |
| M7 | M | `layout/gen_ldo.py:576` (`write_lvs_reference`); `experiments/005-layout/README.md` hypothesis; notebook §5 | The connectivity check compares the layout against a netlist that the **layout generator itself** writes from its own `MOS` table — not against the certified circuit binding. Nothing in the repository checks the two agree. | "LVS-identical to the certified netlist" is not what the flow proves; a divergence between `gen_ldo.MOS` and `circuits/.../netlist.spice` would still pass. | Generate the reference netlist from the circuit binding, or add a lint that diffs the two. | verified by hand this time: all 17 transistors and the 3 resistors / 3 capacitors agree device-for-device (the pass device is folded to one 190 µm device, deliberately) |
| M8 | M | `layout/gen_ldo.py:243` (`stub_clear`), `:255` (`alloc`); `doc/journal/metal1-stub-shorts-are-drc-invisible.md` | The Metal1 short reproduces only when **both** committed changes are reverted. Reverting `stub_clear` alone (leaving the two-directional column search) still gives 0 rule violations and a matched netlist at the record sizing. So no committed sizing exercises the obstacle map; the bidirectional search is what actually avoids the collision here. | The journal presents the obstacle map as the permanent guarantee. It is currently unproven, and a regression that no case exercises will rot. | Commit a sizing point (or a unit test on `Builder`) that fails without `stub_clear` and passes with it. | **reproduced**, all three variants built and checked |
| m1 | m | `layout/signoff.py:84` | The rule check runs with density and fill rules disabled (`no_density=True`). With them enabled the cell reports **12** violations: `AFil.g`, `AFil.g2`, `GFil.g`, `M1.j`–`M4.j` (minimum global metal density) and `M1Fil.h`–`M4Fil.h`, `TM2.c`. | These are expected for a standalone cell and are resolved by fill at chip assembly, but "0 violations, maximal rule set (36 tables)" reads as unconditional. | Say `--no_density` in the README table and note the 12 density items. | reproduced |
| m2 | m | `circuits/.../netlist.spice:42` vs `layout/gen_ldo.py:418–419` | The pass device is **simulated** as 19 separate single-finger 10 µm devices (`m=19`) and **drawn** as one 19-finger 190 µm device with shared source/drain diffusions. Junction area and perimeter at `vout` and the gate therefore differ between the deck and the silicon. | The connectivity check is run with device combining, so it cannot see this by construction. The schematic is the conservative side (more junction capacitance at `vout`), so the direction is safe, but the pre-layout number is not the drawn device. | Netlist the pass device with a finger count, or state the difference in the design reference. | reproduced (extracted device is `W=190u AS=37.6p AD=37.6p`) |
| m3 | m | `layout/gen_ldo.py:433`, `:461` (`mirror`), `:502` (taps) | Matched pairs (`XM1/XM2`, `XM3/XM4`, `XMA/XMB`, `XMCP/XMD`) are placed as adjacent **mirrored single-finger** devices: no interdigitation, no common centroid, no dummy devices at row ends. Well and substrate ties are periodic point contacts every 12 µm, not guard rings, and the process's latch-up rules are off by default in the rule deck. No mismatch or Monte-Carlo run exists anywhere in the branch. | The error amplifier's input pair sets the DC accuracy the S1/S2/S3 numbers depend on, and a 0.028 mV load regulation is a number mismatch would dominate long before systematics. | Interdigitate or common-centroid the input pair and the two mirrors, add dummies, and run a mismatch Monte Carlo on S1 before quoting the regulation figures. | inspected (generator), not simulated |
| m4 | m | `circuits/ldo_ihp_capless/analyses/loop_stability.yaml`; deck `.control` | `zout_peak_db` is defined as `max(|Zout|) − |Zout| at 10 Hz`, which is the total rise of output impedance from DC, not peaking. It reads **100.2 dB** on a loop with 72° phase margin. The definition is not the whole story: the reference design reads **5.88 dB** on the identical definition. The three-order-of-magnitude rise is real for *this* topology — a capless output whose ≈20 pF only takes the node over in the tens of MHz — but the column is still not peaking and reads as an alarm. | Report-only, and the design reference already says the proxy is not used for S8 — but it is still printed in every scorecard and listed as a report column. | Define it against the high-frequency asymptote, or drop it. | reproduced |
| m5 | m | `circuits/.../analyses/dropout.yaml` (`VOUT_THRESH: 1.14`) | The parameter does not appear in the rendered deck; the actual criterion is `abs(Vout − 1.2) ≤ 0.05` **and** `abs(dVout/dVin) ≤ 0.1`. | A declared bench condition that the bench ignores is a trap for the next reader. | Remove it or wire it through the class template. | reproduced (frozen deck read) |
| m12 | m | `experiments/003-sizing/score.py:7`, `:94` (`POINTS["control (002 fold hand point)"] = {}`) | The control point is defined as "the sizing.yaml defaults", but 003 **moved** those defaults onto the optimizer winner (`git diff 76eddd6 602f073 -- circuits/ldo_ihp_capless/pdk/ihp-sg13g2/sizing.yaml`: `r_bias_l` 100 µm → 138.5 µm, `x_dut_xmc_w` 13 µm → 15.76 µm, and eight more). At HEAD, `score.py --point control` re-renders the **record**, not the 002 hand point, so the 50.17 µA control row in the experiment's own table cannot be reproduced without checking out `76eddd6`'s sizing file. | The comparison the experiment rests on is no longer re-runnable from the committed script. The control is still a *fair* one — same benches, same conditions, same corner — so the conclusion holds; only its reproduction is broken. | Pin the 002 overrides explicitly in `POINTS["control"]` rather than leaving it empty. | reproduced (source diff; the `sizing.yaml` header itself documents the move) |
| m6 | m | `experiments/003-sizing/score.py:52` | Cites `doc/journal/round-the-pass-device-last.md`; the file is `round-then-rescore.md`. | Broken provenance link. | Fix the name. | reproduced |
| m7 | m | `layout/signoff.py:12–17`, `:97` | The `SIGNOFF_PYTHON` warning is **true but host-specific, and the failure is not silent where the author says it is**. Pointing it at the extraction interpreter does break the connectivity check: `matched=False`, an empty run directory, and an empty `reason` — but the cause (`ModuleNotFoundError: No module named 'docopt'`) *is* in the returned log. The other interpreter used by this flow has both that module and the layout API and would work. | The real defect is in the platform: `run_lvs` does not promote a non-zero exit or a traceback into `reason`, and `layout/signoff.py` records only `matched` and `reason`. Blanket advice hides a fixable platform gap. | Have `run_lvs` set `reason` from the runner's exit status; reword the docstring as "the interpreter must import both `docopt` and the layout API". | **reproduced** both ways | 
| m8 | m | `notebooks/ldo_walkthrough.ipynb` cells 11, 14 | Both read `experiments/*/out/`, which is git-ignored. They execute here only because this checkout still holds the designer's run artefacts; a fresh clone prints the fallback and shows no corner table and no post-layout table. | The walkthrough is the reviewer-facing artefact and is the one place a reader meets the corner finding. | Commit the two small JSON summaries, or regenerate them in the notebook. | reproduced by inspection; the notebook itself executes with **0 errors and no host paths** |
| m9 | m | `doc/journal/template-gaps-t8.md` | Written at instantiation and never extended. The platform gaps found in 003–005 (device-prefix precedence in the schematic writer, extraction card translation, the warning classifier, the silent connectivity-check failure) are journalled separately but none is added to the "fix that belongs in the template or the platform" list the file exists to hold. | The file is the branch's hand-off to the template, and it is missing the four most actionable items. | Add them. | reproduced |
| m10 | m | `circuits/.../sizing.yaml` (`c_out_w` max 80 µm, `c_comp_w` max 73 µm) | The capacitor model documents a validated side range of 7–75 µm. The record's 58 / 54 / 8 µm are inside it; the search bounds are not. | An optimizer is free to walk outside the model's validated range and would not be told. | Clamp the bounds to 75 µm. | reproduced (model file read) |
| m11 | m | `harness.yaml` `spec:` S8; scorecards | S8 constrains phase margin only. At the light load the loop is much less damped than 72° suggests: gain margin **5.75 dB** and sensitivity peak **14.09 dB** at 0.1 mA, tt / 27 °C (post-layout 6.25 dB / 10.25 dB). Across the three corners re-measured, light-load gain margin stays 5.5–5.8 dB. | A 6 dB gain margin and a 14 dB sensitivity peak are the numbers a reviewer will ask about; neither is in the box and neither is in the README. | Add gain margin and sensitivity peak at 0.1 mA to the reported columns, with a stated floor. | reproduced |

### The gap in the schematic is not "not drawable"

The branch states that the three `rhigh` resistors are "not drawable". The process kit ships an
`rhigh` symbol with **two pins** and the substrate node carried as a template attribute, so the
device is perfectly drawable. The real cause is a precedence bug in the schematic writer
(`spicexplorer_netlist2xschem/ingest.py:149–162`): an `XR`-prefixed instance is classified as a
two-pin primitive and dropped when it has three nets, instead of falling through to the generic
subcircuit branch a few lines below, which would have handled it. The fix is a reordering, not a
new symbol. Reword the finding and the journal accordingly.

## 3. Re-measured against claimed

### 3.1 Pre-layout, tt / 27 °C — rebuilt from `lab.dut.CANDIDATE`, all 13 benches

Every frozen deck rebuilds byte-identically from `design.json`, both `SHA256SUMS` verify, and
every value reproduces to the last committed digit (largest deviation 1.1e-13 on the loop unity-gain
frequency, i.e. floating-point noise). Harness drift tolerances applied; the two loop twins and
the 1 MHz supply-rejection column were checked against their siblings' tolerances.

| | claimed | re-measured | Δ | bound | verdict |
|---|---|---|---|---|---|
| S1 v_out (V) | 1.200072 | 1.200072 | 0 | [1.176, 1.224] | PASS |
| S2 load reg (mV) | 0.028 | 0.028 | 0 | ≤ 5 | PASS |
| S3 line reg (mV) | 0.059 | 0.059 | 0 | ≤ 2 | PASS |
| S4 dropout (mV) | 106.143 | 106.143 | 0 | ≤ 200 | PASS |
| S5 Iq (µA) | 36.27715 | 36.27715 | 0 | ≤ 50 | PASS |
| S6 PSRR 1 kHz (dB) | 69.953 | 69.953 | 0 | ≥ 40 | PASS |
| S7 undershoot (mV) | 104.847 | 104.847 | 0 | ≤ 150 | PASS |
| S8 PM 1 mA (deg) | 72.419 | 72.419 | 0 | ≥ 60 | PASS |
| S8 PM 0.1 / 10 mA (deg) | 72.383 / 72.310 | 72.383 / 72.310 | 0 | ≥ 60 | PASS |
| loop gain (dB) / UGF (kHz) | 49.945 / 836.50 | 49.945 / 836.50 | 0 | — | — |
| gain margin 1 mA / 0.1 mA (dB) | 6.427 / 5.747 | 6.427 / 5.747 | 0 | — | see m11 |
| sensitivity peak 1 mA / 0.1 mA (dB) | 7.150 / 14.089 | 7.150 / 14.089 | 0 | — | see m11 |
| output noise (µVrms) | 19 142 | 19 142 as defined; **366 corrected** | — | — | see M2 |
| Zout "peaking" (dB) | 100.16 | 100.16 | 0 | — | see m4 |

Benches: 13/13 ran. Violations: 0. The 002 hand point is a fair control — the same 13 benches at
the same conditions through the same builder, entered as the optimizer's trial 0.

### 3.2 Post-layout, tt / 27 °C — layout rebuilt, all sign-off stages re-run by the verifier

Rebuilt GDS: **35 317 µm²** (identical bounding box). Rule check **0 violations** (density off,
see m1). Connectivity check **matched**. Extraction **121 C, 10 R**. All values below are from
the verifier's own extraction, not the designer's.

| | claimed pre | mine pre | claimed post | mine post | shift (mine) | verdict |
|---|---|---|---|---|---|---|
| S1 v_out (V) | 1.200 | 1.20007 | 1.200 | 1.20007 | 0 | PASS |
| S2 load reg (mV) | 0.028 | 0.028 | 0.028 | 0.028 | 0 | PASS |
| S3 line reg (mV) | 0.059 | 0.059 | 0.068 | 0.068 | +0.009 | PASS |
| S4 dropout (mV) | 106.1 | 106.14 | 106.1 | 106.14 | 0 | PASS |
| S5 Iq (µA) | 36.28 | 36.277 | 36.20 | 36.199 | −0.078 | PASS |
| S6 PSRR (dB) | 69.95 | 69.953 | 69.95 | 69.954 | +0.001 | PASS |
| S7 undershoot (mV) | 104.8 | 104.85 | 113.9 | 113.88 | **+9.04** | PASS |
| S8 PM (deg) | 72.42 | 72.419 | 71.74 | 71.736 | **−0.68** | PASS |
| S8 PM lo / hi (deg) | 72.38 / 72.31 | 72.383 / 72.310 | 71.70 / 71.63 | 71.704 / 71.632 | −0.68 | PASS |
| UGF (kHz) | 836.5 | 836.50 | 817.8 | 817.81 | −18.7 | — |
| recovery (µs) | 0.1254 | 0.12539 | 0.1496 | 0.14961 | +0.024 | — |

Every claimed post-layout number reproduces. The `+9.1 mV` undershoot and `−0.68°` phase-margin
costs, and their attribution to 28.4 fF on the pass gate and 44.7 fF on the compensation node,
are supported.

**On-chip output capacitance is honoured, and measured from the geometry.** Summing the
capacitor-plate layer over the rebuilt GDS gives **16 436 µm²** of plate area, of which the
output array is **4 × 58 µm × 58 µm = 13 456 µm²**; at the model's plate density (`cap_carea = 1.5E-15` F/µm², `libs.tech/ngspice/models/cornerCAP.lib:22`, `cmim_core` `CJ=cap_carea`) this is
**≈ 20.2 pF**, plus the 1 pF bench parasitic, i.e. **≈ 21.2 pF against the ≤ 100 pF bound**.
Note that extraction strips the capacitor plates and the schematic devices are spliced back, so
the post-layout run never *measured* the output capacitor; the geometric count above is what
verifies the constraint.

**Is 2.5D extraction the right tool here?** Yes, for this cell. The loop closes below 1 MHz and
the cell has no transmission-line-like structure, so a 2.5D parasitic model with lateral coupling
retained is adequate for the metrics in the box; nothing in the pre→post shift needs a full 3D
field solve. The extraction gap that does matter is the stripped capacitor plates described
above, which is a modelling choice rather than a solver limitation.

### 3.3 Three corners re-measured

| corner | quantity | claimed | re-measured | verdict |
|---|---|---|---|---|
| ss / −40 °C | Iq (µA) | 25.58 | 25.580 | PASS |
| | S7 (mV) | 310.8 | **310.75** | **FAIL** (≤ 150) |
| | PM 1 mA / gain margin 0.1 mA (deg / dB) | 73.15 / — | 73.154 / 5.61 | PASS |
| ff / 125 °C | Iq (µA) | 61.93 | **61.928** | **FAIL** (≤ 50) |
| | S7 (mV) | 109.8 | 109.84 | PASS |
| | PM 1 mA / gain margin 0.1 mA | 70.45 / — | 70.451 / 5.77 | PASS |
| tt / 125 °C | Iq (µA) | 44.85 | 44.855 | PASS |
| | S7 (mV) | 128.6 | 128.55 | PASS |
| | PM 1 mA / gain margin 0.1 mA | 71.22 / — | 71.224 / 5.46 | PASS |

Largest deviation across all three corners and all eight spec lines: **0.05 mV** on S7. The
corner table is trustworthy.

### 3.4 The "one mechanism" claim, decoupled

The corner bundles tie the transistor corner, the resistor corner and the capacitor corner
together, so the published table cannot separate them. Re-running with hybrid bundles (transistor
corner alone, resistor corner alone, capacitor corner alone) settles it:

| bundle | Iq (µA) | S7 (mV) |
|---|---|---|
| nominal, tt / 27 °C | 36.28 | 104.8 |
| ss bundle, −40 °C | 25.58 | **310.8** |
| slow transistors only, −40 °C | 30.82 | 83.6 |
| worst-case resistors only, tt, −40 °C | 26.40 | **256.9** |
| worst-case capacitors only, tt, −40 °C | 31.84 | 86.7 |
| ff bundle, 125 °C | **61.93** | 109.8 |
| fast transistors only, 125 °C | 49.30 | 128.6 |
| best-case resistors only, tt, 125 °C | **56.82** | 109.9 |

**The mechanism is confirmed and is the resistor spread**, at both ends: the resistor corner alone
reproduces both failures, and neither the transistor corner nor the capacitor corner does. Two
refinements the branch does not state. First, the quiescent-current column is a **misleading
proxy**: slow transistors at −40 °C *lower* Iq by 15 % and *improve* S7 from 105 to 84 mV, so it
is the bias-branch current, not total Iq, that drives S7. Second, the relation is a **threshold**,
not a proportionality (see M6): sweeping the bias resistor,

| corner | Iq (µA) | 30.9 | 28.8 | 27.8 | 26.8 | 25.6 |
|---|---|---|---|---|---|---|
| ss / −40 °C | S7 (mV) | 83.8 | 88.3 | **309.8** | 301.3 | 310.8 |

and at ff / 125 °C, holding the current down to the design's own value re-breaks S7:

| Iq (µA) | 61.9 | 58.1 | 52.7 | 48.3 | 44.7 | 40.9 | 35.9 |
|---|---|---|---|---|---|---|---|
| S7 (mV) | 109.8 | 115.2 | 123.2 | 130.6 | 139.1 | 148.4 | **165.2** |

### 3.5 Other design claims, checked

| claim | verdict |
|---|---|
| Quiescent current measured at no load, bias-resistor current included | **Correct.** The operating-point deck has no load and no load capacitor and takes `abs(i(Vdd))`, so the bias resistor from the supply and the ≈0.65 µA feedback divider (drawn through the pass device) are both counted. |
| Supply rejection at 1 mA with the right source impedance | **Correct and conventional.** An ideal supply source carries the small-signal excitation (zero source impedance) and the load is an ideal current source (infinite small-signal impedance). Matches the reference bench. |
| Undershoot 0.1 → 10 mA with the spec's edge | **Correct.** `pulse(0.1m 10m 1u 100n 100n 10u 20u)` — a 100 ns edge, as the spec states. Undershoot is measured against the settled heavy-load level rather than the pre-step level; with 0.028 mV of load regulation the difference is immaterial. |
| Line regulation 1.4 → 1.65 V at 1 mA | **Correct.** Swept at 5 mV steps with a 1 mA load. |
| Dropout definition | **Defensible but loose.** Supply swept 0.9 → 1.6 V at 10 mA; the first point where output is within 50 mV of 1.2 V *and* the slope is ≤ 0.1 is taken. That is a level-plus-slope criterion, so the reported 106.1 mV is the supply minus the output at that point, not a percentage-drop definition. The declared threshold parameter is dead (m5). |
| `c_ff_w` cliff is real | **Reproduced exactly.** 8 µm → 104.85 mV, 9.4 µm → 107.02 mV, 9.5 µm → **201.26 mV**. The record's 19 % back-off is justified. |
| Metal1 short is rule-check-invisible and connectivity-check-visible | **Reproduced exactly.** With the fixes reverted, the record sizing gives 0 rule violations and a failed connectivity check, whose extracted netlist shows both amplifier input gates on one net (`fb|vref`); the 002 sizing (50 nm longer sink) passes both. See M8 for which half of the fix does the work. |
| The optimizer's 17 floats in `score.py` | **Clean.** All 17 reproduce `opt_best.json` exactly, and the rounding function reproduces every `sizing.yaml` default exactly. The duplication is sourced and harmless. |
| The 003 control is a fair comparison | **Fair, but no longer re-runnable.** Control and record are scored on the same benches, corner and conditions, so the comparison is sound. But the control point is now empty overrides against defaults that 003 itself moved, so the committed script no longer regenerates the 50.17 µA row (m12). |
| Schematic reproducible | **Clean.** Regenerating the drawing from the frozen deck produces a file byte-identical to the committed one, with the same three skipped resistors. |

## 4. Confirmed clean

- Working tree clean; `git ls-files` contains no run directory, raw file, experiment output,
  GDS or absolute host path. The scratch naming audit reports 0 findings.
- Both frozen directories verify against their manifests, and all 13 candidate decks rebuild
  byte-identically from `design.json` through `lab.dut.Design`.
- The reference reproduces its certified scorecard with **zero drift** — the second half of
  `make check` passes. The lint half fails for M1 only.
- Every experiment directory has its README with the required rows and its row in the experiment
  log; every journal entry is indexed, dated and typed; the spec table and its machine twin agree.
  All of these are mechanically checked and all pass.
- The provenance scrub passes: no proprietary tool or foundry name anywhere in the branch.
- The walkthrough executes end to end with no errors and no host paths in its outputs.
- The README headline table matches the re-measured numbers line for line.
- There is no test target and no test directory in this repository; `make lint`, `make check`
  and `make doctor` are the whole gate.

## 5. Sign-off decision

| scorecard | decision | basis |
|---|---|---|
| `decks/candidate/scorecard.json` | **SIGNED** | Decks rebuilt from the design of record (never text-edited), all 13 benches re-run with the frozen definitions, every value equal to the certified one to the last committed digit, 0 violations. Ledger row `candidate_certify`, `evidence=signed`. |
| post-layout / extracted | **SIGNED, qualified** | Layout rebuilt from the generator; rule check, connectivity check and extraction re-run by the verifier; all 13 benches re-run on the verifier's own extracted netlist; every number in the 005 table reproduces. Qualified because the numbers come from the local tolerant rule rather than the frozen path (M4), because the output capacitor is spliced back rather than extracted, and because **no committed artefact carries them** — `experiments/005-layout/out/` is git-ignored, so this row backs a table in a README, not a file. Ledger row `005_postlayout_post`, `evidence=signed`. |
| `decks/reference/scorecard.json` | not signed (out of scope) | Re-measured in this session with zero drift, so an admissible row could be added at any time. It fails the same lint check for the same reason (M1). |

Sign-off rows were written with `author=ldo-design-agent`, `verified_by=signoff-verifier`. Note the
API constraint: `evidence=signed` is rejected when author and verifier fold to the same actor, so
a signed row cannot name the verifier in both fields — the author field must name the party whose
claim is being verified.

**What `make lint` does after signing: still red, both scorecards, same message.** See M1. **What
a fresh clone sees: also red** — the ledger is git-ignored and per checkout, so no clone has any
signed row at all, and `make check` is red on arrival for every reader of this branch. Until M1 is
fixed, "the lint is red only because nobody has signed" is not a reproducible statement.

## 6. Reproduction

Environment: the native simulator lane and the pinned process kit as `doc/environment.md`
describes, with the work directory and every scratch artefact under `$SX_SCRATCH/ldo-review/`.

```
# gates
make lint ; python -m lab.metrics --check ; python scripts/naming_guard.py --scan .

# 3.1 / 3.3 — rebuild and re-measure (candidate at tt/27 and three corners)
python -c "from lab.metrics import evaluate; from lab.dut import CANDIDATE; \
           evaluate(CANDIDATE, 'REVIEW_candidate_tt_27')"
python -c "from lab.metrics import evaluate; from lab.dut import CANDIDATE; \
           [evaluate(CANDIDATE.at(c,t), f'REVIEW_record_{c}_{t:g}C') \
            for c,t in (('ss',-40.),('ff',125.),('tt',125.))]"

# 3.2 — layout rebuilt and re-signed off into a scratch directory
python layout/signoff.py --out $SX_SCRATCH/ldo-review/layout \
       --stages build,render,drc,lvs,pex
python layout/postlayout.py --pex $SX_SCRATCH/ldo-review/layout/pex   # writes into the repo:
                                                                      # import its functions instead
# density rules on (m1): call the rule runner with no_density=False
# capacitor area (§3.2): sum the plate layer over the rebuilt GDS with the layout API

# M5 — the platform already classifies the warning correctly
python -c "from spicexplorer_core.spice_engine.sim_log import fatal_lines, classify_line; \
           print(classify_line('Warning: singular matrix:  check node xdut.n_37'))"

# M2 — the noise metric, on a case with an exact answer
#   1 Mohm / 1 Mohm divider, .noise over 10 Hz..10 MHz: true 288 uVrms
#   onoise_total = 2.879e-4 (correct), sqrt(onoise_total) = 17.0 mV (the bug)

# M8 — the Metal1 short: copy the generator, disable stub_clear AND the two-directional
#   column search, rebuild at the record sizing, then re-run the rule and connectivity checks
```

## 7. What to do next, in order

1. Fix the supply and output metallization (B1) and add a current-density stage to the sign-off
   chain. Nothing else on this list changes whether the cell works.
2. Replace `lab/sim.py`'s fatal scan with the platform's classifier (M5); the post-layout row then
   comes from the frozen path and M4 disappears with it.
3. Fix the scorecard/ledger key mismatch (M1) so signing means something, then re-sign.
4. Correct the output-noise metric in the shared class template (M2) and re-issue the affected
   numbers.
5. Restate the bias finding as a threshold with its quiescent-current window and its S5 cost (M6);
   sweep the bias resistor locally, as the repository's own rule for optimizer knobs requires.
6. Either strengthen the schematic equivalence check to compare parameters or weaken the claim
   (M3); reword the "not drawable" finding as the precedence bug it is.
7. Interdigitate the matched pairs, add dummies and guard rings, and run a mismatch Monte Carlo
   before the regulation numbers are quoted anywhere (m3).
