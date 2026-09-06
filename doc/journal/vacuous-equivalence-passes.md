# 2026-09-04 — an equivalence check that matched zero components is not a pass

KIND: journal entry | type: procedural | status: live

**Observation** (experiment 004 §1). Proving the schematic of record IS the certified netlist took
three attempts, and the first two **returned `equivalent=True` while proving nothing**:

| what was compared | verdict | components matched |
|---|---|---|
| two files that each only `.subckt`-**define** the cell | `equivalent=True` | **0** |
| same, plus one top-level `XDUT` instance of the cell | `equivalent=True` | **1** (the instance) |
| the cell body **flat**, at top level, in both files | `equivalent=True` | **22** + 15 nets |

`compare_netlists` matches instances at the top level of what it is given. A file that only
defines a subcircuit has no top-level instances, so the comparison is between two empty graphs and
succeeds trivially. Wrapping the cell and instantiating it once is worse, because it looks like a
real result: it matches the single `XDUT` node and never descends into it.

**Rule.** Never report `equivalent` on its own. Report **`components_matched` beside it**, and
treat a comparison that matched fewer devices than the netlist contains as a failed check, not a
passed one — `build_sch.py` carries an explicit `vacuous` flag for exactly this. To compare a
single cell, hand circuitgraph the **flat** body of that cell on both sides.

**Generalization.** This is the shape of every silent verifier failure: the tool answered a
narrower question than the one asked. Any check whose pass is compatible with "there was nothing
to check" needs a second output that counts what it examined — and that count needs an expected
value to be compared against.
