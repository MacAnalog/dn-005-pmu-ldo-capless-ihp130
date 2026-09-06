# 2026-09-04 — the template venv stops at simulation: gm/ID, layout and signoff had to be added

KIND: journal entry | type: procedural | status: live

**Symptom.** The template's `pyproject.toml` pins harness/core/spicexplorer/analog-db/waveview/
circuitgraph/netlist2xschem as path sources, so `import spicexplorer_gmid`,
`spicexplorer_layout`, `spicexplorer_signoff` all raise `ModuleNotFoundError` in `.venv` — the
sizing (003), layout (005) and PEX lanes cannot start. gdsfactory + the IHP PyCells live in a
separate interpreter (`~/miniconda3/envs/ai_env/bin/python`, gdsfactory 9.34.2) on this host, and
`spicexplorer_layout.GdsBuilder(python=…)` is built for exactly that split — but the LDO venv
also needs the layout package itself to drive it.

**Fix (in this repo).** `spicexplorer-gmid`, `spicexplorer-layout`, `spicexplorer-signoff`
added to `dependencies` + `[tool.uv.sources]` (editable path into the sibling platform
checkout), plus `pyyaml`, `nbconvert`/`ipykernel`/`notebook` for the executed walkthrough
notebook. One `uv sync`; `uv run --no-sync` afterwards.

**For the template.** Ship these three sources in `agentic-design-template/pyproject.toml`
from the start (they cost nothing when unused), and document the two-interpreter layout lane
(`gds_python`) in its `doc/environment.md`.
