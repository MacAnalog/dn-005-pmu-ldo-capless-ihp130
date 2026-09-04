# 2026-09-04 — "the tool cannot draw it" was a precedence bug, not a missing symbol

KIND: journal entry | type: semantic | status: live

**Supersedes the diagnosis in** `doc/journal/netlist2xschem-skips-3-terminal-resistors.md`.

**Observation** (review-002-capless-ldo §2). Three `rhigh` resistors (`XR1`, `XR2`, `XRB`) are
skipped by `spicexplorer_netlist2xschem` with `3 nets but res expects 2`, and this repo recorded
that as "the IHP poly resistor is a 3-terminal subcircuit and the tool's `res` symbol has two
pins, so it is not drawable". **That is wrong.** The PDK ships an `rhigh.sym` with **two pins**
and carries the substrate node as a template attribute (`body=sub!`), so the device is perfectly
drawable. The real cause is a precedence bug in `spicexplorer_netlist2xschem/ingest.py:149–162`:
an `XR`-prefixed instance is classified as a two-pin primitive by its prefix and then *dropped*
when it turns out to have three nets, instead of falling through to the generic subcircuit branch
a few lines below, which would have handled it. The fix is a reordering, not a new symbol.

**Rule.** "The tool can't do X" is a claim about the tool, and it needs the same evidence as a
claim about a circuit. Before recording a capability gap, look at what the tool ships and at the
branch that rejected the input. A wrong diagnosis is worse than no diagnosis: it closes the
question and sends the next person to build a symbol that already exists.

**Platform follow-up.** Reorder the prefix test after the subcircuit fallback in `ingest.py`.
