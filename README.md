# ldo-ihp130

Agent-first design repo for a **capless, low-Iq LDO in the open IHP SG13G2 130 nm PDK**,
instantiated from `agentic-design-template`. The reusable machinery (run ledger, lints,
context pack, spec checks) is the SpiceXplorer platform package `spicexplorer-harness`; the
simulator lane is the platform's `NGSpice_Wrapper`; the benches are the analog-db **LDO class**
testbench templates and the reference circuit is analog-db's `ldo_005_buffered_ref`. This repo
holds only what is specific to this design: `harness.yaml`, the docs under `doc/`, the thin
`lab/` that builds decks and measures them, and the agent definitions under `.claude/`.

Start at [CLAUDE.md](CLAUDE.md) (the entry map), then [doc/target-spec.md](doc/target-spec.md).

## Where the design stands

The cell of record is `circuits/ldo_ihp_capless/` — a double-mirror FVF output stage under a
two-stage error amplifier ([doc/design-reference.md](doc/design-reference.md)). It is sized
([003](experiments/003-sizing/README.md)), drawn as a schematic
([004](experiments/004-schematic/README.md)) and laid out, DRC/LVS-clean and extracted
([005](experiments/005-layout/README.md)). Every number below is the analog-db LDO class benches
via `lab.metrics.evaluate`; the reference row is quoted from its own certification.

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
opposite directions. A PVT-stable bias is the named next increment, not more sizing
([003 §3](experiments/003-sizing/README.md)).

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
| `lab/` | `config` (paths, PDK), `sim` (lane), `dut` (the sizing point → deck), `metrics` (measure, check, log) |
| `scripts/lint.py` | repo-specific checks on top of the harness (frozen decks rebuild from `lab/`) |
| `decks/reference/` | the certified reference benches + `scorecard.json`, sha-locked |
| `decks/candidate/` | the **design of record's** 13 certified benches + `scorecard.json`, sha-locked |
| `circuits/ldo_ihp_capless/` | the candidate as an analog-db circuit dir (manifest, datasheet, analyses, IHP binding + `sizing.yaml` = the design of record) |
| `layout/` | `gen_ldo.py` (parameterized gdsfactory generator; sizing read from `sizing.yaml`), `signoff.py` (build/render/DRC/LVS/PEX), `postlayout.py` (frozen benches on the extracted netlist) |
| `experiments/NNN-*/` | one directory per hypothesis; `_template/README.md` is the shape |
| `pdf/` | papers + `INDEX.md` (cite by handle; open-access links preferred over vendored PDFs) |
| `.claude/agents/` | variant-runner, signoff-verifier, schematic-builder, paper-analyst, gardener |
| `.claude/skills/` | the visual-evidence methods: schematic of record, testbench schematics, findings as plots, layout evidence |
| `runs/` | `ledger.ndjson`, git-ignored; keeper numbers graduate into experiment READMEs |
