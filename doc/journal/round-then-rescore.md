# 2026-09-04 — rounding a sizing point to the layout grid is a design change; re-score it

KIND: journal entry | type: procedural | status: live

**Observation** (experiment 003 §2). The optimizer returns floats in metres
(`x_dut_xmp_l = 1.3e-07`, `c_ff_w = 9.415138e-06`). A gdsfactory generator snaps geometry to a
5 nm grid and the schematic of record carries the same numbers, so the point that ships must be
rounded. Rounding onto a **50 nm** device grid moved the pass device from 0.13 µm — the PDK
minimum — to 0.15 µm, giving back 15 % of its transconductance: dropout 106 → 126 mV and
undershoot 107 → 248 mV. Rounding onto a **10 nm** grid kept minimum-L but still broke S7,
because it landed `c_ff_w` on the cliff of `optimizer-parks-on-cliffs.md`.

**Rule.** Round the optimizer's winner onto the grid the layout will actually draw, then **re-run
the full frozen scorecard on the rounded point** and treat that as the design of record. Never
publish the raw floats: they cannot be drawn, and a schematic, a netlist and a GDS that disagree
in the fourth digit are three different designs.

Choose the grid from the PDK, not from habit: it must be fine enough to express the minimum
length and width exactly (IHP SG13G2 lv: L 0.13 µm, W 0.15 µm, so 10 nm works and 50 nm does not).
Coarser grids are fine for MIM sides and resistor lengths, where the quantum is a square.

**Where it lives.** `experiments/003-sizing/score.py` — `rounded_point()` applies the grids,
`record_point()` then applies the deliberate back-offs, and `--point all` scores control / raw /
rounded / record in one table so the cost of each step is visible rather than asserted.
