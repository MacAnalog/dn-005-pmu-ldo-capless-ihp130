# ldo-ihp130

Agent-first design repo for a **capless, low-Iq LDO in the open IHP SG13G2 130 nm PDK**,
instantiated from `agentic-design-template`. The reusable machinery (run ledger, lints,
context pack, spec checks) is the SpiceXplorer platform package `spicexplorer-harness`; the
simulator lane is the platform's `NGSpice_Wrapper`; the benches are the analog-db **LDO class**
testbench templates and the reference circuit is analog-db's `ldo_005_buffered_ref`. This repo
holds only what is specific to this design: `harness.yaml`, the docs under `doc/`, the thin
`ldo/` that builds decks and measures them, and the agent definitions under `.claude/`.

Start at [CLAUDE.md](CLAUDE.md) (the entry map), then [doc/target-spec.md](doc/target-spec.md).

## Where the design stands

The cell of record is `circuits/ldo_ihp_capless/` — a double-mirror FVF output stage under a
two-stage error amplifier ([doc/design-reference.md](doc/design-reference.md)). It is sized
([003](experiments/003-sizing/README.md)), drawn as a readable five-block hierarchy that provably
carries the certified cell's 50 devices, 33 nets and all 239 of its parameter rows
([004](experiments/004-schematic/README.md)), benched by 13 testbench schematics that each netlist
back to the certified deck they were drawn from
([006](experiments/006-visual-benches/README.md)) and laid out twice — the second drawing
([005](experiments/005-layout/README.md), [`layout/ldo_ihp_capless/REPORT.md`](layout/ldo_ihp_capless/REPORT.md))
is the layout of record: current density 27/27 segments, DRC 0, LVS matched at two sizing points,
kpex CC + RC, 13/13 benches inside the box. Every number below is the analog-db LDO class benches
via `ldo.metrics.evaluate`; the reference row is quoted from its own certification.

| | S1 v_out (V) | S2 load reg (mV) | S3 line reg (mV) | S4 dropout (mV) | S5 Iq (µA) | S6 PSRR 1 kHz (dB) | S7 undershoot (mV) | S8 PM (deg) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **spec box** | [1.176, 1.224] | ≤ 5 | ≤ 2 | ≤ 200 | ≤ 50 | ≥ 40 | ≤ 150 | ≥ 60 | |
| reference `ldo_005` (certified, 3.3 V / 1 µF) | 1.609 | 1.274 | 4.32 | 169.7 | 758.7 | 44.53 | 1.957 | 46.39 | not at this challenge's point |
| sized, tt / 27 °C (design of record) | 1.199 | 0.026 | 0.056 | 104.7 | **33.81** | 70.01 | 115.1 | 72.51 | **PASS** |
| post-layout, extracted, tt / 27 °C | 1.199 | 0.026 | 0.056 | 104.7 | **33.81** | 70.11 | 127.6 | 68.76 | **PASS** |
| worst corner (5 MOS × −40/27/125 °C) | 1.198 | 0.056 | 0.248 | 135.0 | **61.9** @ ff/125 | 59.66 | **310.8** @ ss/−40 | 70.35 | 12/15 PASS |

**Re-certified 2026-09-05** on the *drawn* device set (layout review F19): the pass array as 76
unit fingers, every common-centroid member as two half-width cards, the resistors as segment
chains. Iq 36.28 → 33.81 µA and S7 104.8 → 115.1 mV with no layout parasitic involved — the
schematic of record simply did not describe the devices the generator has drawn since its first
round ([`layout/ldo_ihp_capless/PLAN.md` §0.1](layout/ldo_ihp_capless/PLAN.md)). Every S7-derived
parasitic budget in the layout brief tightens ~23 % as a result.

The headline is met: the reference's regulation and PSRR class at **4.5 % of its quiescent
current**, with the output capacitor on chip (21 pF) and phase margin 26° better. The box is
judged at tt/27 °C and passes there before *and* after layout. Sign-off over corners does not:
S5 binds at ff/125 °C and S7 at ss/−40 °C, and both are the **same** cause — a resistor-referenced
bias whose current spreads 2.4× over the corner grid, so the two failures pull one knob in
opposite directions — the resistor corner alone reproduces both failures. A supply-independent
bias is the named next increment, but it does **not** relax both ends at once: pinned at the
design's own 36.3 µA it still fails S7 at ff/125 °C, and the window that clears both corners is
**Iq ≈ 41–50 µA**. **The corner-robust headline is therefore 41–50 µA, not 36.28 µA**
([003 §3](experiments/003-sizing/README.md), [design-reference §4](doc/design-reference.md)).

## Open — independent review `doc/reviews/review-002-capless-ldo.md`

An independent verifier re-derived every committed number from the sources on 2026-09-04 and
**signed both scorecards**: the pre-layout row reproduces to the last committed digit and the
first drawing's post-layout row to within 0.05 mV. The headline above stands as measured. Its
findings, with the four the second drawing addressed marked *(closed)* — those four are closed by
the **designer**, so they need a `layout-reviewer` pass before anyone should treat them as
verified (rule 7). The post-layout row above carries **no signature**: `layout/postlayout.py`
logs it `evidence="awaiting"` into the (per-checkout, git-ignored) ledger, and the previous
verifier's signed `005_postlayout_post` row belongs to the *first* drawing:

| id | what | why it is still open |
|---|---|---|
| **B1** | *(closed 2026-09-04, second drawing)* **The 10 mA path is 12–28× over the process metal current-density limit.** | Redrawn on TopMetal1 (2 µm straps, 15 mA/µm) fed by 6 µm Metal2 combs and 48-cut via risers, with the pass array folded to 76 fingers (`xmp_nf_mult = 4`) so a shared source/drain column carries 0.263 mA against the 0.36 mA flat limit — `w`/`m` in `sizing.yaml` untouched, so it is not a re-sizing. **27 of 27 segments pass, worst 0.836×**, and the check is now a *blocking* sign-off stage (`spicexplorer_signoff.current_density` over budgets the generator emits from its own drawn geometry), not a hand calculation. Cost: +19.6 % area, S7 +22.7 mV, S8 −3.7°, all inside the box. [005 §1](experiments/005-layout/README.md), `doc/journal/a-floorplan-is-bought-not-found.md`. |
| **M3** | *(green at the recertified cell; verifier re-measure pending)* The schematic of record netlists `cap_cmim` with no `w`/`l` and `VREF vref vss 3`, and the equivalence check passes anyway. | **Green: the drawing is the certified netlist, devices AND sizes** — closing the finding is the verifier's call (rule 7), and that re-measure is pending. `build_sch.py::check_parameters` joins the certified netlist and the drawing's netlist device by device and compares **every parameter by number** (symbols resolved against the deck's own `.param` bindings, SI suffixes normalised through the platform's parsers); `w`/`l` may never be defaulted, `VREF` is checked against `vref_val` = 0.6 V by name, and the step **exits non-zero** rather than reporting. It reads **239 of 239 rows green** over the recertified cell's 50 devices (`bf3a4f8`), with `VREF` at 0.6 V: both causes were emitter defects and are fixed upstream (`spicexplorer-platform @1775a67`). The same assertion runs on the flat drawing and on the five-block hierarchy that replaced it, and the value half of it, extended to the benches in [006](experiments/006-visual-benches/README.md), then caught a further emitter defect that truncated a `pulse(...)` stimulus in the netlist of two bench sheets. The honest claim remains that the drawing **cannot drift unnoticed** — the netlist stays the design of record. [004 §2](experiments/004-schematic/README.md), `doc/journal/an-isomorphism-carries-no-sizes.md`. |
| **M7** | *(closed 2026-09-04)* The LVS golden netlist was written by the generator from its own device table. | `layout/netlist_ref.py` parses the certified binding once and hands out **both** the device list the generator places **and** the LVS reference, so there is no second table to drift. The only thing the reference adds is the layout's dummy devices — needed because the IHP deck extracts a shorted dummy as a device and `--purge` does not remove it (measured) — and the emitter **asserts each dummy has all four terminals on one rail**, so a dummy card can only ever be inert while a real device's size still comes from the certified file. `gen_ldo.py` no longer carries a device table at all. |
| **M8** | *(closed 2026-09-04)* Half the Metal1-short fix (`stub_clear`) was an unexercised regression. | The obstacle map moved to `layout/router.py` (no gdsfactory, so it runs in the repo venv) and `layout/test_builder.py` builds the collision by hand: five cases, one of which stubs `stub_clear` out and **asserts the allocator then returns the shorting column**. `layout/signoff.py` runs them as its first, blocking stage, so the guard is exercised every round rather than waiting for a sizing point to happen to produce the collision. The second drawing then found the same class of bug one layer up — `gate` merged into `vout` on a Metal2 power-comb spine, DRC 0 again. Guard rings, MIM plate pads and resistor end pads are now **claimed** in the map; the power combs are **routed around** on Metal3 (`to_track_m3`) rather than claimed, so the Metal2-on-Metal2 class has a fix but — the M8 lesson applied to this round — **no case that fails without it**. That the bypass is not universal is visible in `REPORT.md` §10.5: at `xmp_nf_mult = 1` the build still extracts `gate` shorted to `vout`. |
| **m5-r** | Closing m5 by DELETING `VOUT_THRESH: 1.14` from the candidate's `analyses/dropout.yaml` left the whole candidate circuit un-assemblable, and nothing noticed for a review round. | The bench really does ignore the parameter (m5 stands), but the class template still carries `${VOUT_THRESH}` in its comment header and analog-db's `assemble()` scans the rendered text, comments included. The binding is restored with the reason written beside it; `deck_rebuild` now guards **every** frozen dir, which is what would have caught it. The real fix — dropping the dead placeholder from the class template — is an analog-db change. `doc/journal/one-guarded-frozen-dir-guards-one-frozen-dir.md`. |
| **m3** | *(layout part closed 2026-09-04; the mismatch run is still open)* No interdigitation, common centroid, dummies or guard rings on the matched pairs; **no mismatch or Monte Carlo run exists anywhere in this branch**. | The second drawing gives each matching class the pattern its measured headroom asks for: `ea_in_pair` and `ea_nmos_load` **A B B A** common-centroid (each member split in two half-width instances), the `fb_divider` as **[A B B A] × 4** serpentine segments with both centroids on the block centre, `bias_n_group` interdigitated about one axis, the rest same-row/same-orientation — with a tied dummy at each end of all eight groups (16 MOS + 2 resistor dummies, declared in the LVS reference) and **5 closed guard rings** replacing the periodic point taps. What is **not** closed: routing is not matched half-for-half (the channel allocator finds each terminal a free column), and **no mismatch Monte Carlo exists**, so the 0.028 mV load regulation is still systematic-only. The brief's own measurement is that the three tight classes already sit inside 3σ of the PDK's *random* mismatch, which layout cannot fix. |
| **m11** | S8 constrains phase margin only; light-load gain margin is **5.75 dB** and the sensitivity peak **14.09 dB** at 0.1 mA. | Neither is in the box or the reported columns. |
| **m4** | `zout_peak_db` is the rise of output impedance from DC, not peaking; it reads 100.2 dB on a 72°-phase-margin loop (the reference reads 5.88 dB on the identical definition). | Report-only and not used for S8, but it is printed in every scorecard and reads as an alarm. Renaming it changes a bench definition, which would re-freeze the decks — deferred deliberately. |

Closed from that review in this branch: **M1** (the harness fix landed — platform #129 —
and `certify()` now writes the helper's provenance block, so `make lint` is red only for the two
scorecards no verifier has signed yet), **M2** (the analog-db template dropped the second `sqrt`
— analog-db PR #68 — and both frozen dirs are re-certified on the corrected bench: **candidate
366.4 µVrms**, **reference 25.38 µVrms**; noise is not in the S1–S8 box, so no verdict moved),
**M4/M5** (the post-layout row now comes from the frozen path, 13 of 13 benches), **M6** (the bias
finding restated as a threshold with its cost),
**m1** (density rules run on demand — 12 fill/density items, listed in [005](experiments/005-layout/README.md)),
**m6**, **m7**, **m10**, **m12**. **m5** closed the finding and opened `m5-r` above. **B1**, **M7**,
**M8** and the layout half of **m3** are closed in the second drawing (rows above), designer-signed
and awaiting review.

## Setup

```bash
uv sync                                  # editable path deps on ../../spicexplorer-platform
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2
export SPICE_USERINIT_DIR=$PDK_ROOT/ihp-sg13g2/libs.tech/ngspice   # its .spiceinit loads the OSDI models
export SX_SCRATCH=$HOME/sx-scratch       # work dirs land under here (never in the repo, never in /tmp)
make doctor                              # the lane is alive when this parses a scalar out of an ngspice log
make check                               # lint + the reference reproduces its certified scorecard
```

See [doc/environment.md](doc/environment.md) for the PDK pin and the lane's gotchas.

## Layout

| path | what |
|---|---|
| `harness.yaml` | the design described to the harness: spec rows, frozen dirs, denylist, ledger columns |
| `CLAUDE.md` | the entry map agents read first |
| `doc/` | target spec, design reference (constraints), benches, environment, experiment log, journal + index, the memory model |
| `ldo/` | `config` (paths, PDK), `sim` (lane), `dut` (the sizing point → deck), `metrics` (measure, check, log) |
| `scripts/lint.py` | repo-specific checks on top of the harness (frozen decks rebuild from `ldo/`) |
| `decks/reference/` | the certified reference benches + `scorecard.json` (provenance block) + `decks.sha256`, sha-locked |
| `decks/candidate/` | the **design of record's** 13 certified benches + `scorecard.json`, sha-locked |
| `circuits/ldo_ihp_capless/` | the candidate as an analog-db circuit dir (manifest, datasheet, analyses, IHP binding + `sizing.yaml` = the design of record) |
| `layout/` | `gen_ldo.py` (parameterized gdsfactory generator; sizing read from `sizing.yaml`), `signoff.py` (build/render/DRC/LVS/PEX), `postlayout.py` (frozen benches on the extracted netlist) |
| `experiments/NNN-*/` | one directory per hypothesis; `_template/README.md` is the shape |
| `pdf/` | papers + `INDEX.md` (cite by handle; open-access links preferred over vendored PDFs) |
| `.claude/agents/` | variant-runner, signoff-verifier, schematic-builder, paper-analyst, gardener |
| `.claude/skills/` | the visual-evidence methods: schematic of record, testbench schematics, findings as plots, layout evidence |
| `runs/` | `ledger.ndjson`, git-ignored; keeper numbers graduate into experiment READMEs |
