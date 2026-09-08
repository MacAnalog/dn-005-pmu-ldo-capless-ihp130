# CLAUDE.md — ldo-ihp130 (agentic-design template instance)

**Map, not manual.** This file routes; the docs hold the substance.

## Mission

A **capless, low-quiescent-current LDO** in the open **IHP SG13G2** 130 nm PDK, thin-oxide
(`sg13_lv_*`, 1.5 V) devices: **Vin 1.5 V nominal, Vout 1.2 V, 0.1–10 mA load, the output
capacitor on chip (≤ 100 pF)**. The yardstick is the certified analog-db reference
`ldo_005_buffered_ref` (`decks/reference/`, IHP tt): the headline is to **match its load/line
regulation and 1 kHz PSRR at ≤ 50 µA quiescent current** — an order of magnitude below the
reference's — without giving back phase margin, dropout or load-step undershoot. The spec of
record is `doc/target-spec.md`; its machine twin is the `spec:` block in `harness.yaml`, and
`make lint` refuses to let the two drift.

## Read this before that

| you are about to… | read first |
|---|---|
| anything | `doc/target-spec.md` — the acceptance box, pass/fail definitions |
| measure something | `doc/benches.md` — the analog-db LDO class benches are the definitions; the key map from canonical names to spec keys |
| touch the DUT / model it | `doc/design-reference.md` — device map, the reference's structure, the constraints every candidate must respect |
| pick a paper / technique | `pdf/INDEX.md` |
| run simulations | `ldo/` module docstrings + `doc/environment.md` (native ngspice lane, PDK pin, gotchas) |
| start an experiment | copy `experiments/_template/`; add one row to `doc/experiment-log.md` |
| learn from / add a lesson | `doc/journal.md` (index); one file per entry in `doc/journal/`; supersede, never delete |
| know what to read/write when | `doc/memory/README.md` — the four memory tiers and the write-risk ordering |

## Harness commands

`spicexplorer-harness` (platform package, an editable path dependency — `uv sync` once per
checkout) does the generic work, driven by `harness.yaml`; `Makefile` wraps it.

- `make doctor` — is the simulation lane alive? (`ldo/sim.py`: ngspice + the PDK model libs)
- `make pack K="psrr iq"` — assemble **working memory** for a task. Run at task start;
  re-run with `S="loop gain fell to 0 dB"` on any new failure signature before diagnosing.
- `make lint` — repo invariants (`harness.yaml` drives them). Failure messages carry their fix.
- `make check` — lint + the reference reproduces its certified scorecard.
- `make runs ARGS="--fails | --best i_q_ua | --exp 001 | --kind bench"` — query the run ledger
  (`runs/ledger.ndjson`; every `ldo.metrics.evaluate()` appends a row).
- `make freeze` — write `SHA256SUMS` into the frozen dirs after certifying a reference.
- `make sign DIR=decks/reference AUTHOR=<designer> VERIFIED_BY=<you>` — the SECOND actor re-measures a frozen dir and signs it only if it reproduces bit for bit (clears the `scorecard-recompute` "unverifiable" lint in the checkout where it runs; rule 7).
- `make baseline` — simulate the frozen reference decks and print the scorecard.

## Simulation lanes and reuse (contract for every agent in this repo)

- **Open-source PDK (IHP SG13G2, sky130, gf180 …) → the open lane.** ngspice (with OSDI/openvaf models) through this repo's lane
  module (`design/sim.py` or its equivalent here), KLayout / magic / netgen / kpex for layout and sign-off, xschem for schematics — natively
  on the workstation; `make doctor` proves the lane. An open-PDK bench is never routed through the commercial tools.
- **Commercial PDK under NDA → the bridge lane only.** Those simulations run on the EDA server through the lab's
  remote-simulator bridge (the bridge submodule of the lab's `analog-skill-directory` and its two simulator skills): decks are built here, uploaded by basename with *relative* `include`s,
  simulated there, and only results come back. Kit bytes never reach the workstation or the model (`pdk_guard`
  blocks it); every server-side artifact is design-named, never tool-named (`naming_guard`).
  **A declined `/CMC` prompt is never a stop:** continue without those bytes (the kit is consumed by path
  on the server; open-PDK files are unrestricted; ask the person one sentence if a kit fact is needed).
- **SpiceXplorer first.** Before writing a script, use what exists and compose it: the platform packages
  (`spicexplorer_core` — `spice_engine.run_deck`, measurements; `spicexplorer_harness` — ledger, pack, lint,
  spec; `spicexplorer-optimize`; `spicexplorer_gmid`; `spicexplorer_layout` + `spicexplorer_signoff`;
  `spicexplorer_waveview`; `spicexplorer_circuitgraph`; `spicexplorer_netlist2xschem`), the orchestration
  workflows and MCP tools (`spicexplorer_orchestration.workflows`: layout, sizing, campaign, sign-off,
  literature), and the reusable agents and skills in the lab's `analog-skill-directory` (this repo's `.sx/skills` once its template migration lands). A missing function is added to the platform or the
  library by PR (gap-as-signal), never reimplemented privately in this repo.
- **Visual evidence and reports.** Every design cell and every testbench has a **human-readable xschem
  sheet** (the `schematic-of-record` and `testbench-schematic` skills): generated from the certified netlist with `spicexplorer-netlist2xschem`, proven equal
  to it, PNG render committed — never a hand drawing offered as a schematic. When a cell must live in the
  commercial schematic editor it is **ported from that sheet** through the bridge's `xvport` lane and
  re-proven identical with `circuitgraph`. Findings are **tables or plots regenerated from simulated
  data** with the spec boxes drawn (the `findings-as-plots` skill); a simulation report is one `experiments/NNN-*/` directory —
  `run.py` simulates into git-ignored `out/*.json`, figures land in committed `figs/`, `mk_readme.py`
  rewrites its README from `out/` — or this repo's documented equivalent, so no number is typed into prose.

## Rules (mechanically enforced where possible; the rest is contract)

1. **Reference first.** A number that has not passed the frozen definitions is a claim.
2. **Decks are built, never text-edited.** A sizing point is an `ldo.dut.Design`; every deck is
   generated from it (analog-db class template + the circuit's lowered netlist + the sizing).
   Frozen dirs are sha-locked.
3. Every experiment: **falsifiable hypothesis first**; a control whenever a knob moves.
4. Findings are **tables or plots**; prose is interpretation. Keeper numbers graduate from the
   ledger into the experiment README — the repo is the memory.
5. **Parallelize batches** (`spicexplorer_harness.batch`; the width env var is `LDO_JOBS`).
6. **Clean provenance.** Reference the PDK by name, pin its version in `doc/environment.md`,
   never vendor model bytes. `denylist:` in `harness.yaml` is a build failure, not a style note.
7. **Designer ≠ verifier.** Delivery claims are re-measured from raw artefacts.
8. **Gap-as-signal.** If you struggle, fix the harness (lint, helper, doc line) and journal it.
9. **Sim economy.** Expensive runs (corners, Monte Carlo, long transients) only after the cheap
   scorecard passes the box.
10. **Write-risk ordering.** Episodic writes are automatic; semantic writes need provenance and
    supersede-don't-delete; procedural writes (`ldo/`, `scripts/`, agent defs, this file) are
    human-reviewed — agents propose diffs, never self-apply them.

## Agents and methods

In `.claude/agents/` (each starts from `make pack`, reads `harness.yaml`, obeys rules 7–10):

- `paper-analyst` — one paper → a falsifiable technique brief + its `pdf/INDEX.md` row. Never simulates.
- `variant-runner` — parallel netlist-lane batches; scorecard tables only; reference first row, control when a knob moves.
- `signoff-verifier` — independent re-measurement of delivery claims from raw artefacts (rule 7). Reports; never fixes.
- `schematic-builder` — the reviewable `.sch`/`.sym` of record, proven equal to netlist and simulation.
- `gardener` — report-only consistency sweep. Has no write tools, by design.

Visual evidence is not optional: the methods in `.claude/skills/` — `schematic-of-record`,
`testbench-schematic` (components, not text), `findings-as-plots` (spec boxes drawn on every
figure), `layout-evidence` (generator → GDS → DRC/LVS/PEX → review overlay) — say how each
artefact is produced and gated. Layout work uses the workspace's `layout-*` agents.

## Parallel sessions & blast radius

One experiment = one session = one git worktree on `feat/NNN-<technique>`; `LDO_EXP=NNN` stamps
the ledger. The ledger and work dirs are per checkout. Shared docs (`doc/journal.md`,
`doc/experiment-log.md`, `pdf/INDEX.md`) are written at close-out only; during the work, write
into your own `experiments/NNN-*/README.md`.

## Git

`feat/<name>` off `main`, PR, squash. **Ask before pushing.** Never commit `runs/`, work dirs,
rawfiles or PDK content.
