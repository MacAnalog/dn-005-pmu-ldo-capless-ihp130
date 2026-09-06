# 2026-09-04 — the extracted netlist is an LVS artefact, not a simulable deck

KIND: journal entry | type: procedural | status: live

**Observation** (experiment 005 §3). kpex extraction succeeded (121 C, 10 R) and every one of the
13 post-layout benches then failed. Three separate reasons, none of them about the layout:

1. **Primitive cards for subcircuit devices.** kpex writes
   `R$36 lp_brk \$37 vss 0.5 rhigh l=85 ps=0 b=0 m=1` — three nodes, then the width, then the
   model. ngspice's IHP `rhigh` is a **3-terminal subcircuit** (`.subckt rhigh 1 2 bn`), so this
   has to become `XR$36 lp_brk n_37 vss rhigh w=0.5u l=85u`. Unconverted, ngspice reads the third
   node as the resistance and reports `unknown parameter (vss)`. Note the units: kpex writes µm
   with **no suffix**, which SPICE reads as metres.
2. **`$` in net names.** The extractor's anonymous nets are `\$21`, and `$` opens an in-line
   comment in SPICE. Rename them before ngspice sees them.
3. **A substrate node that is not a pin.** Every extracted ground capacitance hangs on `VSUBS`,
   which is absent from the subckt pin list. Narrow the header to the schematic's pins and it
   floats: `singular matrix: check node xdut.vsubs`. Tie it to `vss` (a 0 V source rather than a
   rename, so the substrate branch stays visible to a reviewer) — correct here because the
   p-substrate is at `vss` through the layout's own ptap ring.

Two more, upstream: the **kpex-bundled LVS deck disagrees with the PDK's own** — it extracts poly
resistors as 3-terminal (`custom_reader.lvs`: *"Poly resistor should have 3 nodes"*) where the
standalone IHP deck accepts 2, so the LVS schematic and the PEX schematic are different files. And
the PDK's `run_lvs.py` imports **`docopt`**, which the KLayout/kpex conda interpreter does not
have — so `SIGNOFF_PYTHON` must point at an interpreter that does (the repo venv), or `run_lvs`
returns "not matched" with an empty run directory and no reason.

**Rule.** Treat a PEX netlist as a *report* that has to be translated before it is a deck, and
make the translation a committed function with the reasons in its docstring — never a hand edit,
which cannot be re-run when the layout changes.

**Where it lives.** `layout/postlayout.py`: `ngspice_cards()` (1 + 2), `REINSERT` (3),
`pex_subckt()` (header narrowing). `layout/signoff.py`: `pex_schematic()` (the 3-node LVS twin).
