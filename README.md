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
([003](experiments/003-sizing/README.md)), drawn as a schematic
([004](experiments/004-schematic/README.md)) and laid out, DRC/LVS-clean and extracted
([005](experiments/005-layout/README.md)). Every number below is the analog-db LDO class benches
via `ldo.metrics.evaluate`; the reference row is quoted from its own certification.

| | S1 v_out (V) | S2 load reg (mV) | S3 line reg (mV) | S4 dropout (mV) | S5 Iq (µA) | S6 PSRR 1 kHz (dB) | S7 undershoot (mV) | S8 PM (deg) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **spec box** | [1.176, 1.224] | ≤ 5 | ≤ 2 | ≤ 200 | ≤ 50 | ≥ 40 | ≤ 150 | ≥ 60 | |
| reference `ldo_005` (certified, 3.3 V / 1 µF) | 1.609 | 1.274 | 4.32 | 169.7 | 758.7 | 44.53 | 1.957 | 46.39 | not at this challenge's point |
| sized, tt / 27 °C (design of record) | 1.200 | 0.028 | 0.059 | 106.1 | **36.28** | 69.95 | 104.8 | 72.42 | **PASS** |
| post-layout, extracted, tt / 27 °C | 1.200 | 0.028 | 0.068 | 106.1 | **36.20** | 69.95 | 113.9 | 71.74 | **PASS** |
| worst corner (5 MOS × −40/27/125 °C) | 1.198 | 0.056 | 0.248 | 135.0 | **61.9** @ ff/125 | 59.66 | **310.8** @ ss/−40 | 70.35 | 12/15 PASS |

The headline is met: the reference's regulation and PSRR class at **4.8 % of its quiescent
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
post-layout row to within 0.05 mV. The headline above stands as measured. What that review left
open, and this branch has not closed:

| id | what | why it is still open |
|---|---|---|
| **B1** | **The 10 mA path is 12–28× over the process metal current-density limit.** vdd rail 0.8 µm (12.5×), vout bus 0.6 µm (16.7×), and the **vout pin on a 0.2 µm track reached by one Via1 (25–28×)**. | Neither the rule check nor the connectivity check looks at current density, so a DRC-0 / LVS-matched cell carries it. Widening in place was **tried and does not work**: a 3 µm rail and output track give 117 Metal1 width/space violations against a 1.6 µm rail gap and a 0.7 µm track pitch. The fix needs upper metal (TopMetal1 is 15 mA/µm) and a floorplan that reserves room for the straps — a floorplan change, not a parameter change. Arithmetic and the failed attempt: `doc/journal/metal-current-density-is-nobodys-check.md`. **This is the one finding that changes whether the cell works.** |
| **M3** | The schematic of record netlists `cap_cmim` with no `w`/`l` and `VREF vref vss 3`, and the equivalence check passes anyway. | The equivalence check compares topology, not parameters, so the 004 claim that the drawing "cannot drift from the design of record" is false for the three capacitors and the reference. Needs a parameter-presence assertion in `build_sch.py` and a restated claim. The drawing is a tool output — hand-editing it is overwritten by the next run. |
| **M7** | The LVS golden netlist is written by the generator from its own device table, not derived from the certified circuit binding. | "LVS-identical to the certified netlist" is not what the flow proves. The verifier checked the two agree by hand this time (all 17 transistors, 3 resistors, 3 capacitors); nothing checks it mechanically. |
| **M1** | `make lint` is red and **cannot be greened by any admissible signed row**. | `certify()` writes the tag inside `provenance` and no hash block; the harness's `_backing_rows` matches a top-level `tag`. Two signed rows were appended by the verifier and the lint still reports `(tag None)`. A harness fix, not a repo fix — deliberately not worked around here. `doc/journal/a-signed-row-that-can-never-match.md`. |
| **M8** | The Metal1-short journal presents the obstacle map as the guarantee; the short actually reproduces only when the bidirectional column search is *also* reverted. | No committed sizing exercises `stub_clear` alone, so that half of the fix is an unexercised regression. Needs a committed sizing point or a `Builder` unit test. |
| **M2** | The shared analog-db LDO class template takes an extra `sqrt` on the integrated output noise. | The template lives in a platform submodule and is out of scope to edit here. Every `vn_out_urms` in this repo is therefore √-wrong: **candidate 366 µVrms** (printed 19 142), **reference 25.4 µVrms** (printed 5 038). Noise is not in the S1–S8 box, so no verdict moves. |
| **m3** | No interdigitation, common centroid, dummies or guard rings on the matched pairs; **no mismatch or Monte Carlo run exists anywhere in this branch**. | The input pair sets the DC accuracy S1/S2/S3 rest on, and a 0.028 mV load regulation is a number mismatch would dominate. The regulation figures should be read as systematic-only until a mismatch Monte Carlo exists. |
| **m11** | S8 constrains phase margin only; light-load gain margin is **5.75 dB** and the sensitivity peak **14.09 dB** at 0.1 mA. | Neither is in the box or the reported columns. |
| **m4** | `zout_peak_db` is the rise of output impedance from DC, not peaking; it reads 100.2 dB on a 72°-phase-margin loop (the reference reads 5.88 dB on the identical definition). | Report-only and not used for S8, but it is printed in every scorecard and reads as an alarm. Renaming it changes a bench definition, which would re-freeze the decks — deferred deliberately. |

Closed from that review in this branch: **M4/M5** (the post-layout row now comes from the frozen
path, 13 of 13 benches), **M6** (the bias finding restated as a threshold with its cost),
**m1** (density rules run on demand — 12 fill/density items, listed in [005](experiments/005-layout/README.md)),
**m5**, **m6**, **m7**, **m10**, **m12**.

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
| `decks/reference/` | the certified reference benches + `scorecard.json`, sha-locked |
| `decks/candidate/` | the **design of record's** 13 certified benches + `scorecard.json`, sha-locked |
| `circuits/ldo_ihp_capless/` | the candidate as an analog-db circuit dir (manifest, datasheet, analyses, IHP binding + `sizing.yaml` = the design of record) |
| `layout/` | `gen_ldo.py` (parameterized gdsfactory generator; sizing read from `sizing.yaml`), `signoff.py` (build/render/DRC/LVS/PEX), `postlayout.py` (frozen benches on the extracted netlist) |
| `experiments/NNN-*/` | one directory per hypothesis; `_template/README.md` is the shape |
| `pdf/` | papers + `INDEX.md` (cite by handle; open-access links preferred over vendored PDFs) |
| `.claude/agents/` | variant-runner, signoff-verifier, schematic-builder, paper-analyst, gardener |
| `.claude/skills/` | the visual-evidence methods: schematic of record, testbench schematics, findings as plots, layout evidence |
| `runs/` | `ledger.ndjson`, git-ignored; keeper numbers graduate into experiment READMEs |
