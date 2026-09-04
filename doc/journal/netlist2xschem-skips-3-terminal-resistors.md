# 2026-09-04 — netlist2xschem drops 3-terminal resistors and still reports success

KIND: journal entry | type: procedural | status: live

**Observation** (experiment 004). `spicexplorer_netlist2xschem` turned the certified cell into a
schematic and reported `wrote ldo_ihp_capless.sch (22 devices, 44 labels)` — the cell has **25**.
Three lines went to stderr and nowhere else:

```
skipping XR1: 3 nets but res expects 2
skipping XR2: 3 nets but res expects 2
skipping XRB: 3 nets but res expects 2
```

The IHP poly resistor is a 3-terminal subcircuit (`.subckt rhigh 1 2 bn`: two ports plus the
substrate/well tie) and the tool's `res` symbol has two pins, so `rhigh`, `rppd` and `rsil` are
all silently absent from any IHP schematic it draws. The exit status is 0 and the `.sch` is
otherwise correct, so nothing downstream notices.

**Rule.** After generating a schematic, **diff the device count against the source netlist** and
fail the step if they differ. Then make the equivalence check say which devices are missing rather
than just "not equivalent": compare the drawing's netlist against the certified cell *and* against
the certified cell **minus exactly the skipped devices**. The pair of verdicts separates "the
drawing is wrong" from "the tool cannot draw this device" — here 22 components and 15 nets matched
under a wiring-preserving isomorphism once the three resistors were removed from both sides.

**Platform fix, when it is in scope.** A 3-pin resistor symbol for the IHP PDK in
`spicexplorer_netlist2xschem`, or a bulk-pin-aware fallback that ties the third pin to a label.

**Where it lives.** `experiments/004-schematic/build_sch.py` records `skipped` from stderr and
reports both comparisons in `out/schematic.json`.
