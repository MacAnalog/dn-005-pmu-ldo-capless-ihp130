# 2026-09-05 — a readable hierarchy is a drawing change, and has to be proved to be one

KIND: journal entry | type: procedural | status: live

**Observation** (experiment 004). The flat schematic of record passed both gates — 25 components,
15 nets, 114 parameter rows — and was still not a drawing anyone would read: one wide row of 25
devices with the parameter text overlapping. Redrawing it as a hierarchy (five block subcircuits on
a top sheet, one child sheet each) makes it readable, but it also changes what xschem netlists back
out: `xea_stage1 ... ea_stage1` plus a `.subckt` per block, against a certified cell that is flat.
The gates cannot compare those directly, and the parameter assertion in particular joins the two
netlists **by instance name**, so anything that renames a leaf breaks it silently.

**Rule.** A hierarchy is a drawing change, so keep the gates and change only the input to them:
splice the blocks back inline before comparing, and preserve the leaf instance names while doing it.

Three things make that splice safe, and all three are cheap:

- **Use the platform's netlist parser to find the nets, not a regular expression.** A leaf line's
  net tokens are `tokens[1:1+n]` where `n` is the parser's own node count for that device; the rest
  of the line (model, `w`, `l`, `m`, `b`) is copied through untouched. No SPICE parsing is
  reimplemented, and a device the parser understands is a device the splice understands.
- **Do not prefix the leaves.** The obvious flattener (`x1.XM1`, or `XM1_x1`) is exactly what the
  parameter join cannot survive. Map only the formal-to-actual boundary nets; internal net names
  come from the original flat netlist and are already unique.
- **Assert that uniqueness rather than assume it.** The splice refuses to run if two blocks share a
  leaf reference or an internal net name, which is the only way the flat result could be ambiguous.

**Both drawings, both gates.** The flat sheet is still built beside the hierarchy from the same
frozen deck and put through the same two gates. Two drawings returning the same two verdicts is what
distinguishes "the hierarchy is readable" from "the hierarchy is different".

**What the hierarchy constrains that the flat sheet did not.** A block boundary is a namespace: a
device inside a block is reached as `xdut.x<block>.<ref>`, not `xdut.<ref>`. The three
`ac_loopgain` decks alter `@v.xdut.vlp[acmag]` and read `v(xdut.lp_brk)`, so the loop-break marker
has to stay at the cell level or the benches that measure phase margin stop finding it. Grep the
decks and the measurement code for hierarchical paths **before** choosing the blocks; here only
`vlp` and `lp_brk` were reached that way, and both were left loose deliberately.

**Where it lives.** `experiments/004-schematic/sch_support.py::flatten_hierarchy`, called by the
hierarchical branch of `build_sch.py::gate`.
