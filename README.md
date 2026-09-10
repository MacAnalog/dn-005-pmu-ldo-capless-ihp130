# ldo-ihp130

Agent-first design repo for a **capless, low-Iq LDO in the open IHP SG13G2 130 nm PDK**,
instantiated from `agentic-design-template`. The reusable machinery (run ledger, lints,
context pack, spec checks) is the SpiceXplorer platform package `spicexplorer-harness`; the
simulator lane is the platform's `NGSpice_Wrapper`; the benches are the analog-db **LDO class**
testbench templates and the reference circuit is analog-db's `ldo_005_buffered_ref`. This repo
holds only what is specific to this design: `harness.yaml`, the docs under `doc/`, the thin
`ldo/` that builds decks and measures them, and the agent definitions under `.claude/`.

Start at [CLAUDE.md](CLAUDE.md) (the entry map), then [doc/target-spec.md](doc/target-spec.md).

## Setup

Six steps from a clean checkout, run at the repo root. `make init` needs `SX_ROOT` pointing at
your `spicexplorer-workspace` checkout (the lab puts it in `~/.sx_env`).

| # | step | command | done when |
|---|---|---|---|
| 1 | link `.sx/platform` + the `.sx/skills` library, link the agents and skills into `.claude/`, and `uv sync` | `make init` | it prints `init OK: …; next: make doctor` |
| 2 | name the PDK install | `export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2` | — |
| 3 | let ngspice load the OSDI models | `export SPICE_USERINIT_DIR=$PDK_ROOT/ihp-sg13g2/libs.tech/ngspice` | — |
| 4 | keep work dirs out of the repo | `export SX_SCRATCH=$HOME/sx-scratch` | — |
| 5 | prove the simulation lane | `make doctor` | it parses a scalar out of an ngspice log |
| 6 | prove the repo | `make check` | lint passes and the reference reproduces its certified scorecard |

```bash
export SX_ROOT=<your spicexplorer-workspace checkout>
make init                                # .sx links + agents/skills + uv sync (step 1)
uv sync                                  # editable path deps on ../../spicexplorer-platform;
                                         # `make init` already ran it, re-run it after a dep change
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2
export SPICE_USERINIT_DIR=$PDK_ROOT/ihp-sg13g2/libs.tech/ngspice   # its .spiceinit loads the OSDI models
export SX_SCRATCH=$HOME/sx-scratch       # work dirs land under here (never in the repo, never in /tmp)
make doctor                              # the lane is alive when this parses a scalar out of an ngspice log
make check                               # lint + the reference reproduces its certified scorecard
```

See [doc/environment.md](doc/environment.md) for the PDK pin and the lane's gotchas.

## Repository map

| path | what |
|---|---|
| `harness.yaml` | the design described to the harness: spec rows, frozen dirs, denylist, ledger columns |
| `CLAUDE.md` | the entry map agents read first |
| `doc/` | target spec, design reference (constraints), benches, environment, experiment log, journal + index, the memory model |
| `ldo/` | `config` (paths, PDK), `sim` (lane), `dut` (the sizing point → deck), `metrics` (measure, check, log) |
| `scripts/lint.py` | repo-specific checks on top of the harness (frozen decks rebuild from `ldo/`) |
| `decks/reference/` | the certified reference benches + `scorecard.json` (provenance block) + `decks.sha256`, sha-locked |
| `signoff/prelayout/decks/` | the **design of record's** 13 certified benches + `scorecard.json`, sha-locked (was `decks/candidate/` before template 2.02) |
| `circuits/ldo_ihp_capless/` | the candidate as an analog-db circuit dir (manifest, datasheet, analyses, IHP binding + `sizing.yaml` = the design of record) |
| `layout/` | `gen_ldo.py` (parameterized gdsfactory generator; sizing read from `sizing.yaml`), `signoff.py` (build/render/DRC/LVS/PEX), `postlayout.py` (frozen benches on the extracted netlist) |
| `experiments/NNN-*/` | one directory per hypothesis; `_template/README.md` is the shape |
| `pdf/` | papers + `INDEX.md` (cite by handle; open-access links preferred over vendored PDFs) |
| `.claude/agents/` | gardener, layout-brief-author, layout-designer, layout-reviewer, layout-schematic-codesign, paper-analyst, schematic-builder, signoff-verifier, variant-runner |
| `.claude/skills/` | the 15 methods linked from `.sx/skills`, including the visual-evidence four: schematic of record, testbench schematics, findings as plots, layout evidence |
| `runs/` | `ledger.ndjson`, git-ignored; keeper numbers graduate into experiment READMEs |

## Where the design stands

The cell of record is `circuits/ldo_ihp_capless/` — a double-mirror FVF output stage under a
two-stage error amplifier ([doc/design-reference.md](doc/design-reference.md)). It is sized
([003](experiments/003-sizing/README.md)), drawn as a readable five-block hierarchy that provably
carries the certified cell's 50 devices, 33 nets and all 239 of its parameter rows
([004](experiments/004-schematic/README.md)), benched by 13 testbench schematics that each netlist
back to the certified deck they were drawn from
([006](experiments/006-visual-benches/README.md)) and laid out twice. The second drawing
([005](experiments/005-layout/README.md), [`layout/ldo_ihp_capless/REPORT.md`](layout/ldo_ihp_capless/REPORT.md))
is the layout of record.

**Sign-off gates on that drawing**, all from [005](experiments/005-layout/README.md):

| gate | result |
|---|---|
| DRC | 0 violations |
| LVS | matched at two sizing points |
| LVS over the knob walk | 40 of 40 endpoints |
| current density | 30 of 30 segments |
| parasitic extraction (kpex) | CC and RC |
| frozen benches on the extracted netlist | 13 of 13 inside the box |

**The post-layout row of record is the stitched RC extraction**, independently signed off in
[`layout/ldo_ihp_capless/SIGNOFF.md`](layout/ldo_ihp_capless/SIGNOFF.md) (2026-09-05): dropout
134.66 mV of a 200 mV bound (65.3 mV margin), 8/8 spec lines PASS. The CC extraction (same layout,
every wire resistance zeroed) is kept as the ideal-metal comparison row, not the record — its
dropout (104.7 mV) understates the drawn metal's IR drop by design. Every number below is the
analog-db LDO class benches via `ldo.metrics.evaluate`; the reference row is quoted from its own
certification.

| | S1 v_out (V) | S2 load reg (mV) | S3 line reg (mV) | S4 dropout (mV) | S5 Iq (µA) | S6 PSRR 1 kHz (dB) | S7 undershoot (mV) | S8 PM (deg) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **spec box** | [1.176, 1.224] | ≤ 5 | ≤ 2 | ≤ 200 | ≤ 50 | ≥ 40 | ≤ 150 | ≥ 60 | |
| reference `ldo_005` (certified, 3.3 V / 1 µF) | 1.609 | 1.274 | 4.32 | 169.7 | 758.7 | 44.53 | 1.957 | 46.39 | not at this challenge's point |
| sized, tt / 27 °C (design of record) | 1.199 | 0.026 | 0.056 | 104.7 | **33.81** | 70.01 | 115.1 | 72.51 | **PASS** |
| post-layout, RC extraction (record), tt / 27 °C | 1.199 | 0.027 | 0.056 | **134.7** | **33.77** | 70.06 | 129.5 | 69.33 | **PASS** |
| post-layout, CC extraction (ideal-metal comparison), tt / 27 °C | 1.199 | 0.026 | 0.056 | 104.7 | **33.81** | 70.09 | 127.6 | 69.30 | **PASS** |
| worst corner, schematic (5 MOS × −40/27/125 °C) | 1.197 | 0.054 | 0.266 | 131.8 | **58.37** @ ff/125 | 59.02 | **301.8** @ sf/−40 | 70.37 | 8/15 PASS |
| worst corner, post-layout CC (same grid) | 1.197 | 0.054 | 0.266 | 131.8 | **58.37** @ ff/125 | 59.02 | **171.1** @ ss/125 | 67.61 | 10/15 PASS |

Both corner rows are [007](experiments/007-post-layout-corners/README.md) §1, measured at **this**
sizing point (Iq 33.81 µA). Each column is that column's worst over the 15-cell grid, so neither row
describes a single corner. Both are **CC** rows: the RC corner grid was never run, and adding tt/27's
+30.0 mV CC→RC dropout gap to the worst S4 (131.8 mV) is an arithmetic addition, not a measurement
([007 §5](experiments/007-post-layout-corners/README.md)). The row this table carried until
2026-09-10 — **61.9 µA @ ff/125, 310.8 mV @ ss/−40, 12/15 PASS** — is
[003 §3](experiments/003-sizing/README.md) at the **superseded 36.28 µA sizing**; it stays 003's
record and is not a description of the cell this repo holds.

The corner grid at the current sizing point, plotted:
[`experiments/007-post-layout-corners/figs/corners_s5_s7.png`](experiments/007-post-layout-corners/figs/corners_s5_s7.png)
— S5 and S7 across the grid, schematic and extracted.
[`experiments/003-sizing/figs/corners.png`](experiments/003-sizing/figs/corners.png) draws the same
three specs (S5, S7, S8) against temperature at the **36.28 µA** point
(`experiments/003-sizing/figs.py::corner_figs`, from that experiment's `out/corners.json`); it is
003's record, not a plot of the cell of record. The drawn cell:
[`experiments/005-layout/figs/ldo_ihp_capless_labelled.png`](experiments/005-layout/figs/ldo_ihp_capless_labelled.png)
(`make fig-layout`, from the rebuilt GDS + `layout/ldo_ihp_capless/labels.yaml`).

### Re-certified 2026-09-05 on the drawn device set

Layout review F19 recertified the cell on the devices the generator draws: the pass array as 76
unit fingers, every common-centroid member as two half-width cards, the resistors as segment
chains. Iq 36.28 → 33.81 µA and S7 104.8 → 115.1 mV, with no layout parasitic involved — the
schematic of record simply did not describe the devices the generator has drawn since its first
round ([`layout/ldo_ihp_capless/PLAN.md` §0.1](layout/ldo_ihp_capless/PLAN.md)). Every S7-derived
parasitic budget in the layout brief tightens ~23 % as a result.

### The headline, and the corners where it does not hold

Every number in this section is [007](experiments/007-post-layout-corners/README.md) §1–§3, at the
re-certified 33.81 µA sizing point.

- **Met at tt / 27 °C, before and after layout.** The reference's regulation and PSRR class at
  **4.5 % of its quiescent current**, with the output capacitor on chip (21 pF) and phase margin
  26° better.
- **Sign-off over corners is not met, and the two failing lines are no longer one story.** At
  36.28 µA ([003 §3](experiments/003-sizing/README.md)) S5 and S7 were the same resistor-bias
  mechanism pulled in opposite directions. At the sizing point the repo now holds, S5 still is that
  — and S7 is not:

| lane | corners that fail | spec that binds | measured | bound |
|---|---|---|---|---|
| schematic **and** post-layout | ff / 125 °C | S5 quiescent current | 58.37 µA, identical to five digits in both | ≤ 50 µA |
| schematic | 6 of 15: tt, ss, sf, fs / −40 °C and ss / 27 °C, ss / 125 °C | S7 load-step undershoot | 152.8–301.8 mV | ≤ 150 mV |
| post-layout (CC) | 4 of 15: tt, ss, sf, fs / 125 °C | S7 load-step undershoot | 152.1–171.1 mV | ≤ 150 mV |

- **S5 is a schematic-level failure of the bias**, not a layout one: pre and post read the same
  58.37 µA, so nothing in the layout lane can move it
  ([007 §2](experiments/007-post-layout-corners/README.md)). The mechanism is the
  resistor-referenced bias, and 007's own `i_q_ua` column carries the spread at this sizing point
  — 24.32 µA at ss / −40 °C to 58.37 µA at ff / 125 °C, **2.4×** on a 33.81 µA nominal.
- **S7 does not fail where 003 said it does.** The drawn cell's parasitics *rescue* the cold
  corners — ≈44 fF of undesigned capacitance on the error-amp output node `ea_o1` takes tt / −40 °C
  from 288.7 mV (schematic) to 106.9 mV (extracted) — and spend margin at 125 °C, where the
  extraction's +34.45 fF on `gate` puts four of five corners out of the box. The post-layout S7
  constraint is **temperature**, not the `gate` parasitic budget
  ([007 §2–§3](experiments/007-post-layout-corners/README.md)).
- **S8 never binds** anywhere on the grid: worst post-layout phase margin 67.61° at ff / 125 °C,
  7.6° above the line.

**What is still quoted from the old sizing point.** 007 re-ran the corner grid at 33.81 µA, so the
corner verdict above is current. These were derived at **36.28 µA** and have not been re-derived:

- the `r_bias_l` threshold sweep and the **Iq ≈ 41–50 µA** window that clears both ends — the exit
  path's price ([003 §3](experiments/003-sizing/README.md),
  [review-002 §3.4 + M6](doc/reviews/review-002-capless-ldo.md),
  [design-reference §4](doc/design-reference.md)). It is a figure for a bias increment, not a
  measurement of the cell of record;
- `experiments/003-sizing/figs/corners.png`, that grid's figure.

Never run at either sizing point: the **RC** corner grid, and any joint corners × mismatch sweep
([007 §5](experiments/007-post-layout-corners/README.md)).

## Open findings — independent review `doc/reviews/review-002-capless-ldo.md`

An independent verifier re-derived every committed number from the sources on 2026-09-04 and
**signed both scorecards**: the pre-layout row reproduces to the last committed digit and the
first drawing's post-layout row to within 0.05 mV. The headline above stands as measured.

Four findings were closed by the **designer** in the second drawing, so under rule 7 they needed a
`layout-reviewer` pass before anyone treated them as verified. **Updated 2026-09-05**: a second
independent pass, [`layout/ldo_ihp_capless/SIGNOFF.md`](layout/ldo_ihp_capless/SIGNOFF.md),
re-measured the current (`it13`) drawing from raw artefacts and signed both post-layout extractions
— `verify_postlayout_post` (CC, the ideal-metal comparison row) and `verify_postlayout_rc` (RC, now
the **post-layout row of record**) — so the RC row no longer carries `evidence="awaiting"` in that
checkout. The previous verifier's signed `005_postlayout_post` row still belongs to the *first*
drawing.

| id | finding | state | why it is still listed |
|---|---|---|---|
| **B1** | the 10 mA path is 12–28× over the process metal current-density limit | closed 2026-09-04, second drawing | the redraw is measured (30/30 segments); the floorplan/routing review proper is still open |
| **M3** | the schematic of record netlists `cap_cmim` with no `w`/`l` and `VREF vref vss 3`, and the equivalence check passes anyway | green at the recertified cell | closing the finding is the verifier's call (rule 7) and that re-measure is pending |
| **M7** | the LVS golden netlist was written by the generator from its own device table | closed 2026-09-04 | listed for the record of how it closed |
| **M8** | half the Metal1-short fix (`stub_clear`) was an unexercised regression | closed 2026-09-04 | listed for the record of how it closed |
| **m5-r** | deleting `VOUT_THRESH: 1.14` from the candidate's `analyses/dropout.yaml` makes the `dropout` bench fail to assemble — 1 of 13, which sinks every scorecard — and nothing noticed for a review round | open | re-measured 2026-09-10: the dead placeholder is still in the analog-db class template at the pinned commit, so the binding is still load-bearing |
| **m3** | no interdigitation, common centroid, dummies or guard rings on the matched pairs; no mismatch or Monte Carlo run anywhere in this branch | layout part closed 2026-09-04 | routing is not matched half-for-half and no mismatch Monte Carlo exists |
| **m11** | S8 constrains phase margin only; light-load gain margin is **5.75 dB** and the sensitivity peak **14.09 dB** at 0.1 mA | open | neither is in the box or the reported columns |
| **m4** | `zout_peak_db` is the rise of output impedance from DC, not peaking; it reads 100.2 dB on a 72°-phase-margin loop (the reference reads 5.88 dB on the identical definition) | open, deferred | report-only and not used for S8, but printed in every scorecard, where it reads as an alarm; renaming it changes a bench definition, which would re-freeze the decks, so it is deferred deliberately |

### B1 — the 10 mA path, redrawn on upper metal

Redrawn on TopMetal1 (2 µm straps, 15 mA/µm) fed by 6 µm Metal2 combs and 48-cut via risers, with
the pass array folded to 76 fingers (`xmp_nf_mult = 4`) so a shared source/drain column carries
0.263 mA against the 0.36 mA flat limit. `w`/`m` in `sizing.yaml` are untouched, so this is not a
re-sizing. **30 of 30 segments pass, worst 0.836×** (the round-5 drawing added two rows for the
split `vss` returns; still 0.836× worst-case), and the check is now a *blocking* sign-off stage
(`spicexplorer_signoff.current_density` over budgets the generator emits from its own drawn
geometry), not a hand calculation. Cost: +19.6 % area, S7 +22.7 mV, S8 −3.7°, all inside the box.
[005 §1](experiments/005-layout/README.md), `doc/journal/a-floorplan-is-bought-not-found.md`.

### M3 — the drawing is the certified netlist, devices AND sizes

`build_sch.py::check_parameters` joins the certified netlist and the drawing's netlist device by
device and compares **every parameter by number** (symbols resolved against the deck's own
`.param` bindings, SI suffixes normalised through the platform's parsers); `w`/`l` may never be
defaulted, `VREF` is checked against `vref_val` = 0.6 V by name, and the step **exits non-zero**
rather than reporting. It reads **239 of 239 rows green** over the recertified cell's 50 devices
(`bf3a4f8`), with `VREF` at 0.6 V. Both causes were emitter defects and are fixed upstream
(`spicexplorer-platform @1775a67`).

The same assertion runs on the flat drawing and on the five-block hierarchy that replaced it. Its
value half, extended to the benches in [006](experiments/006-visual-benches/README.md), then caught
a further emitter defect that truncated a `pulse(...)` stimulus in the netlist of two bench sheets.
The honest claim remains that the drawing **cannot drift unnoticed** — the netlist stays the design
of record. [004 §2](experiments/004-schematic/README.md),
`doc/journal/an-isomorphism-carries-no-sizes.md`.

### M7 — one device table feeds both the placer and the LVS reference

`layout/netlist_ref.py` parses the certified binding once and hands out **both** the device list
the generator places **and** the LVS reference, so there is no second table to drift. The only
thing the reference adds is the layout's dummy devices — needed because the IHP deck extracts a
shorted dummy as a device and `--purge` does not remove it (measured) — and the emitter **asserts
each dummy has all four terminals on one rail**, so a dummy card can only ever be inert while a
real device's size still comes from the certified file. `gen_ldo.py` no longer carries a device
table at all.

### M8 — the obstacle map now has its own cases, and a negative control

The obstacle map moved to `layout/router.py` (no gdsfactory, so it runs in the repo venv) and
`layout/test_builder.py` builds the collision by hand — **twenty-one cases in the current suite**
(ten of them the router obstacle-map cases this finding is about; the rest were added later for the
RC/PEX netlist-selection findings, F24/F26/F27).

The reviewer ran the negative control rather than taking the claim: with `claim_box` stubbed out to a no-op, **4 of 9 router cases fail** and the
suite exits 1, `test_without_the_claim_the_allocator_walks_into_the_comb` reporting *"alloc
returned 44.1, inside the comb"*.

`layout/signoff.py` runs the suite as its first, blocking stage, so the guard is exercised every
round rather than waiting for a sizing point to happen to produce the collision.

The second drawing then found the same class of bug one layer up — `gate` merged into `vout` on a
Metal2 power-comb spine, DRC 0 again — and the fix is **structural**: the map is layer-aware and
`claim_box()` records any drawn rectangle, so the power combs are obstacles to Metal2 and simply
are not on Metal3's layer. The hard-coded `to_track_m3` bypass is **deleted**, and the class is
gone by measurement (`col_vias` 3 and 4, which extracted `gate|vout` before, both LVS-match in the
40-endpoint walk). `xmp_nf_mult` is no longer a layout knob — it is a sizing knob in `sizing.yaml`,
where an off-grid value now raises instead of silently drawing a different device.

### m5-r — the deleted placeholder that broke every candidate deck

**Re-measured 2026-09-10.** The bench really does ignore the parameter (m5 stands), and the binding
is still load-bearing anyway. `assemble()` renders the class template with
`Template.safe_substitute` and then scans the **rendered** text — comment lines included — for
unresolved `${…}`; `ldo.dut.Design.deck()` strips comments only afterwards. Delete the binding and
rebuild all 13 candidate benches and **12 still build**: only `dropout` raises
`AssembleError: … unresolved placeholders ['VOUT_THRESH']`. A 13-bench scorecard needs all 13, which
is what "un-assemblable" meant. The binding is restored with the reason written beside it, and
`deck_rebuild` now guards **every** frozen dir, which is what would have caught the deletion.

**What it is waiting on, precisely.** The real fix — dropping the dead placeholder from the class
template — is an analog-db change, and it has **not merged**: `${VOUT_THRESH}` is still in
`_shared/classes/ldo/testbench-templates/dropout.spice` on analog-db `origin/main` (`3b9535f7`) and
at the commit the shared root is pinned to (`2da526c5`). The retirement exists only on an unmerged
working branch. So m5-r closes when that change is on `main` **and** the shared root has re-pinned
past it — not when the branch exists.

When it lands, nothing here breaks: `safe_substitute` ignores mapping keys the template does not
use, so the binding turns inert rather than into an error, and it can be deleted at leisure.
`scripts/lint.py::dropout_threshold_binding` is what will say so — it fails in **both** directions,
a template that needs the binding without one and a binding that outlives its placeholder.
`doc/journal/one-guarded-frozen-dir-guards-one-frozen-dir.md`.

### m3 — matching drawn, mismatch measured at two edges, distribution still unsimulated

The second drawing gives each matching class the pattern its measured headroom asks for:
`ea_in_pair` and `ea_nmos_load` **A B B A** common-centroid (each member split in two half-width
instances), the `fb_divider` as **[A B B A] × 4** serpentine segments with both centroids on the
block centre, `bias_n_group` interdigitated about one axis, the rest same-row/same-orientation —
with a tied dummy at each end of all eight groups (16 MOS + 2 resistor dummies, declared in the LVS
reference) and **5 closed guard rings** replacing the periodic point taps.

What is **not** closed: routing is not matched half-for-half (the channel allocator finds each
terminal a free column), and **no mismatch Monte Carlo exists**.

What is now measured, on the extracted cell rather than argued from the brief's coefficients:
[007](experiments/007-post-layout-corners/README.md) injects each class's offset into
`layout/ldo_ihp_capless/asbuilt/core_pex.sp` and finds the dVT at which the box opens, so the two
sub-σ classes carry a **measured** out-of-box threshold instead of an estimate:

| class | out-of-box dVT | in sigma | reading at tt / 27 °C |
|---|---|---|---|
| `ea_nmos_load` | +15.0 mV | 9.1 σ | no measurable yield loss |
| `bias_p_group` | +20.0 mV | 17.9 σ | no measurable yield loss |

007 also carries the control that keeps that from being a null result: delete the extracted
capacitance and the brief's cliff reappears exactly where the brief puts it (+2.0 mV → S7
198.0 mV, out of the box), and the single net `ea_o1` removes it again. The distribution itself is
still not simulated (the PDK's mismatch sections cannot be selected without editing the certified
`corners.yaml`), and routing is still not matched half-for-half — although the reviewer's own
translation-XOR reads **0.000 µm² on all seven classes** at device bbox + 1.2 µm, with equal via
counts.

### Closed from that review in this branch

| finding | closed by |
|---|---|
| **M1** | the harness fix landed (platform #129) and `certify()` now writes the helper's provenance block, so `make lint` is red only for the two scorecards no verifier has signed yet |
| **M2** | the analog-db template dropped the second `sqrt` (analog-db PR #68) and both frozen dirs are re-certified on the corrected bench: **candidate 366.4 µVrms**, **reference 25.38 µVrms**; noise is not in the S1–S8 box, so no verdict moved |
| **M4/M5** | the post-layout row now comes from the frozen path, 13 of 13 benches |
| **M6** | the bias finding restated as a threshold with its cost |
| **m1** | density rules run on demand — 12 fill/density items, listed in [005](experiments/005-layout/README.md) |
| **m6, m7, m10, m12** | closed |
| **m5** | closed the finding and opened `m5-r` above |
| **B1, M7, M8, layout half of m3** | closed in the second drawing (sections above), designer-signed; `SIGNOFF.md` (2026-09-05) has since independently re-measured DRC, LVS, current density and both PEX extractions on the `it13` drawing from raw artefacts and signed them (its Claims 1, 2, 3), so those four no longer need a `layout-reviewer` pass to be trusted at the record row |

Still open behind those closures: a `layout-reviewer` pass for the floorplan/routing review proper
(REPORT §10 item 1). The mismatch and corner halves of **m3** are addressed but not fully closed —
`SIGNOFF.md` Claim 5 independently reproduces the three decisive corner rows (signed) and Claim 4
reproduces both mismatch box edges and rules that **the designer's numbers describe the cell as
built**, but a proper Monte Carlo and a joint corners × mismatch sweep are still open (PLAN §6b.1).
