# ldo-ihp130

Agent-first design repo for a **capless, low-Iq LDO in the open IHP SG13G2 130 nm PDK**,
instantiated from `agentic-design-template`. The reusable machinery (run ledger, lints,
context pack, spec checks) is the SpiceXplorer platform package `spicexplorer-harness`; the
simulator lane is the platform's `NGSpice_Wrapper`; the benches are the analog-db **LDO class**
testbench templates and the reference circuit is analog-db's `ldo_005_buffered_ref`. This repo
holds only what is specific to this design: `harness.yaml`, the docs under `doc/`, the thin
`lab/` that builds decks and measures them, and the agent definitions under `.claude/`.

Start at [CLAUDE.md](CLAUDE.md) (the entry map), then [doc/target-spec.md](doc/target-spec.md).

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
| `experiments/NNN-*/` | one directory per hypothesis; `_template/README.md` is the shape |
| `pdf/` | papers + `INDEX.md` (cite by handle; open-access links preferred over vendored PDFs) |
| `.claude/agents/` | variant-runner, signoff-verifier, schematic-builder, paper-analyst, gardener |
| `.claude/skills/` | the visual-evidence methods: schematic of record, testbench schematics, findings as plots, layout evidence |
| `runs/` | `ledger.ndjson`, git-ignored; keeper numbers graduate into experiment READMEs |
