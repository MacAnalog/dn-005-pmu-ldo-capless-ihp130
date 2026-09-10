# CLAUDE.md — ldo-ihp130 (agentic-design template instance)

**Map, not manual.** This file routes; the docs hold the substance.

## Mission

A **capless, low-quiescent-current LDO** in the open **IHP SG13G2** 130 nm PDK, on thin-oxide
(`sg13_lv_*`, 1.5 V) devices.

- **Operating point.** **Vin 1.5 V nominal, Vout 1.2 V, 0.1–10 mA load, the output capacitor on
  chip (≤ 100 pF)**.
- **Yardstick.** The certified analog-db reference `ldo_005_buffered_ref` (`decks/reference/`,
  IHP tt).
- **Headline.** **Match the reference's load/line regulation and 1 kHz PSRR at ≤ 50 µA quiescent
  current** — an order of magnitude below the reference's — without giving back phase margin,
  dropout or load-step undershoot.
- **Spec of record.** `doc/target-spec.md`; its machine twin is the `spec:` block in
  `harness.yaml`, and `make lint` refuses to let the two drift.

## Read this before that

| you are about to… | read first |
|---|---|
| anything | `doc/target-spec.md` — the acceptance box, pass/fail definitions |
| measure something | `doc/benches.md` — the analog-db LDO class benches are the definitions; the key map from canonical names to spec keys |
| touch the DUT / model it | `doc/design-reference.md` — device map, the reference's structure, the constraints every candidate must respect |
| pick a paper / technique | `references/INDEX.md` |
| run simulations | `ldo/` module docstrings + `doc/environment.md` (native ngspice lane, PDK pin, gotchas) |
| start an experiment | copy `experiments/_template/`; add one row to `doc/experiment-log.md` |
| learn from / add a lesson | `doc/journal.md` (index); one file per entry in `doc/journal/`; supersede, never delete |
| draw a layout | `layout/` (the generator) + `.claude/skills/layout-evidence/SKILL.md` |
| report a result you want believed | `signoff/README.md` — the index of what is signed off, at which fidelity |
| verify someone's claims | `doc/reviews/README.md` — the verifier's report shape |
| know what to read/write when | `doc/memory/README.md` — the four memory tiers and the write-risk ordering |

## How the work is organized

**Five phases, and every experiment names the one it belongs to.** They are not gates — a topology
question reopens at sizing often enough — but the name tells the next agent what kind of evidence
it is reading, and it is the first column of `doc/experiment-log.md`.

| phase | the question it answers | what it usually produces |
|---|---|---|
| `system` | what must this block do, and how will we know? | the spec table, the budgets, a behavioural model |
| `topology` | which circuit can do it at all? | candidates ranked, and the measurement that ranked them |
| `sizing` | which device sizes meet the box? | a sizing point, corners, mismatch |
| `improve` | can the topology itself do better? | a variant that beat the incumbent, and by how much |
| `layout` | does it survive being drawn? | the generator, GDS, DRC/LVS, post-extraction numbers |

## Where things go

**Work freely inside the repo, never beside it.** Open as many experiment directories as the work
needs — that is what they are for. What is not free is where the output lands: every derived
artefact has one home, and raw simulator output has none, because it is not committed at all.

| what you just made | where it goes |
|---|---|
| an exploration, a sweep, an A/B | `experiments/NNN-<slug>/` — `run.py` simulates, `README.md` states the verdict |
| the figure or table carrying its claim | `experiments/NNN-*/figs/`, `.../tables/` |
| a measured result you want believed | `signoff/` — `signoff/README.md` is the index of what is signed off, at which fidelity |
| GDS, DRC and LVS reports, the extracted netlist | `signoff/layout/` — the generator itself stays in `layout/` |
| a lesson worth reusing | one file in `doc/journal/`, one line in `doc/journal.md` |
| a paper, datasheet or standard | `references/` + a row in `references/INDEX.md` (cite by handle) |
| working notes, throwaway scripts, a plot you just want to look at | `experiments/NNN-*/out/` — inside the repo and git-ignored. **Not** `/tmp` |
| rawfiles, work directories, simulator logs | the scratch root (`$SX_SCRATCH`) — never the repo |

`artifact-home` in `scripts/lint.py` enforces the table, one failure per directory with its fix.
**The reason is not tidiness:** a reviewer who cannot find the evidence treats the claim as
unsupported, and six weeks later so does the agent that wrote it. It is not a straitjacket either —
`experiments/` is wide open, and a design with its own durable output directory adds one line to
`ARTIFACT_HOMES` saying what lives there.

**The two frozen deck sets are not the same kind of thing.** `signoff/README.md` says which is
which. The design of record moved under `signoff/`; the yardstick stayed, because `signoff/` is
for this design's results.

| directory | what it is |
|---|---|
| `signoff/prelayout/decks/` | **this design's own** certified benches — the design of record |
| `decks/reference/` | the analog-db **yardstick** `ldo_005_buffered_ref`, the prior art this design is measured against. Frozen, reproduced by `make check`, and not a result of ours |

## Harness commands

`spicexplorer-harness` (platform package, an editable path dependency — `uv sync` once per
checkout) does the generic work, driven by `harness.yaml`; `Makefile` wraps it.

- `make init` — set this checkout up: `.sx/platform` → `$SX_ROOT/spicexplorer-platform`, the
  `.sx/skills` library, the agent/skill links into `.claude/`, then `uv sync`. Needs `SX_ROOT`.
- `make doctor` — is the simulation lane alive? (`ldo/sim.py`: ngspice + the PDK model libs)
- `make pack K="psrr iq"` — assemble **working memory** for a task. Run at task start;
  re-run with `S="loop gain fell to 0 dB"` on any new failure signature before diagnosing.
- `make lint` — repo invariants (`harness.yaml` drives them). Failure messages carry their fix.
- `make check` — lint + the reference reproduces its certified scorecard.
- `make runs ARGS="--fails | --best i_q_ua | --exp 001 | --kind bench"` — query the run ledger
  (`runs/ledger.ndjson`; every `ldo.metrics.evaluate()` appends a row).
- `python -m ldo.metrics --certify [DIR]` — (re)certify a frozen dir from its own `design.json`
  (default `decks/reference/`); there is no `make certify` target.
- `make freeze` — write `SHA256SUMS` into the frozen dirs after certifying a reference.
- `make sign DIR=decks/reference AUTHOR=<designer> VERIFIED_BY=<you>` — the SECOND actor re-measures a frozen dir and signs it only if it reproduces bit for bit (clears the `scorecard-recompute` "unverifiable" lint in the checkout where it runs; rule 7).
- `make baseline` — simulate the frozen reference decks and print the scorecard.

## Simulation lanes and reuse (contract for every agent in this repo)

- **Open-source PDK (IHP SG13G2, sky130, gf180 …) → the open lane.** ngspice (with OSDI/openvaf
  models) through this repo's lane module `ldo/sim.py`, KLayout / magic / netgen / kpex for layout
  and sign-off, xschem for schematics — natively on the workstation; `make doctor` proves the lane.
  An open-PDK bench is never routed through the commercial tools.
- **Commercial PDK under NDA → the bridge lane only.** Those simulations run on the EDA server through the lab's
  remote-simulator bridge (the bridge submodule of the lab's `analog-skill-directory` and its two simulator skills): decks are built here, uploaded by basename with *relative* `include`s,
  simulated there, and only results come back. Kit bytes never reach the workstation or the model (`pdk_guard`
  blocks it); every server-side artifact is design-named, never tool-named (`naming_guard`).
  **A declined `/CMC` prompt is never a stop:** continue without those bytes (the kit is consumed by path
  on the server; open-PDK files are unrestricted; ask the person one sentence if a kit fact is needed).
- **SpiceXplorer first.** Before writing a script, use what exists and compose it. A missing function
  is added to the platform or the library by PR (gap-as-signal), never reimplemented privately here.
  - **Platform packages:** `spicexplorer_core` (`spice_engine.run_deck`, measurements),
    `spicexplorer_harness` (ledger, pack, lint, spec), `spicexplorer-optimize`, `spicexplorer_gmid`,
    `spicexplorer_layout` + `spicexplorer_signoff`, `spicexplorer_waveview`,
    `spicexplorer_circuitgraph`, `spicexplorer_netlist2xschem`.
  - **Orchestration workflows and MCP tools:** `spicexplorer_orchestration.workflows` — layout,
    sizing, campaign, sign-off, literature.
  - **Reusable agents and skills:** the lab's `analog-skill-directory`, this repo's `.sx/skills`
    submodule; `make skills-update` moves it to the library's main.
- **Visual evidence and reports.**
  - **Every design cell and every testbench has a human-readable xschem sheet** (the
    `schematic-of-record` and `testbench-schematic` skills): generated from the certified netlist
    with `spicexplorer-netlist2xschem`, proven equal to it, PNG render committed — never a hand
    drawing offered as a schematic. When a cell must live in the commercial schematic editor it is
    **ported from that sheet** through the bridge's `xvport` lane and re-proven identical with
    `circuitgraph`.
  - **Findings are tables or plots regenerated from simulated data** with the spec boxes drawn (the
    `findings-as-plots` skill).
  - **A simulation report is one `experiments/NNN-*/` directory** — `run.py` simulates into
    git-ignored `out/*.json`, figures land in committed `figs/`, `mk_readme.py` rewrites its README
    from `out/` — or this repo's documented equivalent, so no number is typed into prose.

## Rules (mechanically enforced where possible; the rest is contract)

1. **Reference first.** A number that has not passed the frozen definitions is a claim. The
   reduction that produces it — the code that turns a simulated waveform into the number the spec
   is written in — lives in the PACKAGE (`ldo/metrics.py`), never only in an experiment:
   `python -m ldo.metrics --certify` freezes what `metrics.run_decks` produced, so a number
   computed inside an `experiments/NNN-*/run.py` is a report, not a reference.
2. **Decks are built, never text-edited, and portable.** A sizing point is an `ldo.dut.Design`;
   every deck is generated from it. No machine-specific absolute path may appear in a frozen deck —
   `deck-portable` in `scripts/lint.py` refuses one, because a certified deck naming a path only
   this machine has reproduces nowhere else, and redacting it on write fails `deck-rebuild`'s byte
   comparison.
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

Nine agents in `.claude/agents/`, linked from `.sx/skills` (each starts from `make pack`, reads
`harness.yaml`, obeys rules 7–10):

| agent | what it does |
|---|---|
| `paper-analyst` | one paper → a falsifiable technique brief + its `references/INDEX.md` row. Never simulates. |
| `variant-runner` | parallel netlist-lane batches; scorecard tables only; reference first row, control when a knob moves. |
| `signoff-verifier` | independent re-measurement of delivery claims from raw artefacts (rule 7). Reports; never fixes. |
| `schematic-builder` | the reviewable `.sch`/`.sym` of record, proven equal to netlist and simulation. |
| `gardener` | report-only consistency sweep. Has no write tools, by design. |
| `layout-brief-author` | the cell's LAYOUT BRIEF: net-sensitivity and parasitic budgets, tolerated mismatch per device class, per-net DC current budgets — all measured on the frozen benches before anything is drawn. |
| `layout-designer` | certified netlist → parameterized gdsfactory generator → GDS, proven DRC-clean and LVS-identical, extracted, and re-run on the cell's own frozen benches. |
| `layout-reviewer` | report-only independent review: rebuilds the GDS, re-runs DRC/LVS/PEX itself, and returns findings as `REVIEW.md` + `REVIEW.yaml` + `REVIEW.png`. Never edits the layout. |
| `layout-schematic-codesign` | the joint sizing + layout search as a `sim_engine: layout` project driven by `spicexplorer-optimize`, one round per generator repair. |

Visual evidence is not optional: the methods in `.claude/skills/` — `schematic-of-record`,
`testbench-schematic` (components, not text), `findings-as-plots` (spec boxes drawn on every
figure), `layout-evidence` (generator → GDS → DRC/LVS/PEX → review overlay) — say how each
artefact is produced and gated.

## Parallel sessions & blast radius

One experiment = one session = one git worktree on `feat/NNN-<technique>`; `LDO_EXP=NNN` stamps
the ledger. The ledger and work dirs are per checkout. Shared docs (`doc/journal.md`,
`doc/experiment-log.md`, `references/INDEX.md`) are written at close-out only; during the work, write
into your own `experiments/NNN-*/README.md`.

## Git

`feat/<name>` off `main`, PR, squash. **Ask before pushing.** Never commit `runs/`, work dirs,
rawfiles or PDK content.
