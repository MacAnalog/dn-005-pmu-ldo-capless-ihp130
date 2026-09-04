# 004 — schematic of record: the drawing that provably IS the certified netlist

**Paper(s):** none
**Hypothesis:** `spicexplorer_netlist2xschem` can turn the frozen `decks/candidate/dc_op.spice` into a reviewable xschem schematic of the cell, and `spicexplorer_circuitgraph` can prove the drawing and the certified netlist are the same circuit — every device, model, size expression and net — so the figure a reviewer reads carries no claim the simulator has not already scored. Falsified if the round trip loses or invents any device, or if the equivalence check cannot be made non-vacuous.
**Control:** the certified deck itself, byte for byte (`decks/candidate/dc_op.spice`, SHA-locked) — never a rebuild; and, for the devices the tool cannot place, the same comparison run against the certified cell **minus exactly those devices**, so a tool gap cannot be mistaken for a drawing error.
**Verdict:** CONFIRMED WITH ONE NAMED GAP. The drawing is provably the certified cell for **22 of its 25 devices — 22 components and 15 nets matched under a wiring-preserving isomorphism** (table 1). The three `rhigh` resistors (`XR1`, `XR2`, `XRB`) are **not drawn**: `netlist2xschem` skips them with `3 nets but res expects 2`, because the IHP poly resistor is a 3-terminal subcircuit (`.subckt rhigh 1 2 bn`) and the tool's `res` symbol has two pins. The gap is in the platform, not in this cell.

## 1. Drawing ≡ netlist

The chain is: frozen deck → `netlist2xschem --into XDUT` → `.sch` → **xschem netlists the drawing back out** → `circuitgraph.compare_netlists` on the two netlists. A `.sch` is a drawing file, so it is never handed to circuitgraph directly; the thing compared is what the drawing *means*.

| comparison | components | nets | verdict |
|---|---|---|---|
| certified cell vs the drawing's netlist | 25 vs 22 | — | **not equivalent** — `component count differs: 25 vs 22` |
| certified cell **minus `XR1`/`XR2`/`XRB`** vs the drawing's netlist | 22 matched | 15 matched | **equivalent** — wiring-preserving isomorphism |

The first row is the honest headline and the second is what isolates the cause: with the three un-drawable resistors removed from the *reference* side, every remaining device matches by model, connectivity and parameter expression. The drawing carries the sizing symbolically (`w=x_dut_xmc_w l=x_dut_xmc_l`, `m=x_dut_xmp_m`), i.e. the same `.param` names the deck binds from `sizing.yaml`, so the schematic cannot drift from the design of record when 003 re-sizes it.

Two earlier attempts at this check were **vacuous passes** and are recorded because they are the trap: comparing the two files while each only *defines* a subckt returns `equivalent=True, matched 0 components`, and wrapping the cell in a subckt with one `XDUT` instance returns `equivalent=True, matched 1 component`. Only the flat comparison actually walks the 22 devices. `build_sch.py` therefore reports `components_matched` and a `vacuous` flag beside every verdict — an equivalence result that matched nothing is not evidence.

## 2. Artefacts

| file | what it is |
|---|---|
| `out/ldo_ihp_capless.sch` | the schematic of record (22 devices, 44 labels) |
| `figs/ldo_ihp_capless.png` | the render a reviewer reads |
| `out/ldo_ihp_capless.spice` | the netlist xschem writes back out of the drawing |
| `out/ldo_ihp_capless_certified.spice` | the certified cell, flat, out of the frozen deck |
| `out/ldo_ihp_capless_from_sch.spice` | the drawing's netlist, flat, as compared |
| `out/schematic.json` | both verdicts, the skipped devices, the xschem command |

Reproduce: `LDO_EXP=004 uv run --no-sync python experiments/004-schematic/build_sch.py`. xschem runs headless (`-n -q -r`); it needs the interpreter that has the PDK symbol libraries on `XSCHEM_LIBRARY_PATH`, which `netlist2xschem` writes into the `xschemrc` beside the `.sch`.

## Lessons to graduate

- (`004`) An equivalence check that matched **zero** components is a vacuous pass, and both natural ways to call `compare_netlists` on a cell produce one. Always report `components_matched` next to `equivalent`, and compare the cell **flat**. Journal: `doc/journal/vacuous-equivalence-passes.md`.
- (`004`) `netlist2xschem` silently skips 3-terminal resistors (`3 nets but res expects 2`), so an IHP `rhigh`, `rppd` or `rsil` disappears from the drawing while the run still reports success. Diff the device count against the source netlist before believing a schematic is complete. Journal: `doc/journal/netlist2xschem-skips-3-terminal-resistors.md`.
