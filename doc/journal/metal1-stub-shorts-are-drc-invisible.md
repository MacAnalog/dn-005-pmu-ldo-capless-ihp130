# 2026-09-04 — a Metal1 short between two nets is DRC-invisible; only LVS finds it

KIND: journal entry | type: semantic | status: live

**Observation** (experiment 005 §2). `layout/gen_ldo.py` passed DRC with **0 violations** and
failed LVS: the extracted netlist had `fb` merged into `vref`, i.e. both error-amplifier input
gates on one net. Every device size matched. Reverting one sizing knob at a time (13 builds, 13
LVS runs) put the whole failure on **`x_dut_xms_l`, a 50 nm length change on a device in a
different row of the floorplan**.

The mechanism is the routing discipline, not the sizing. `to_track` connects a terminal to its
channel track with a Metal2 column and bridges any x-shift with a **Metal1 stub at the terminal's
y**. Column allocation checked only Metal2-to-Metal2 spacing, so when the 50 nm shift made XM2's
nearby columns busy, the search marched left and its gate stub ran straight through **XM1's gate
bar**, which sits at the same y. Two overlapping Metal1 shapes merge into a single legal polygon —
there is no spacing to violate — so DRC is silent.

**Rule.** DRC proves geometry, never connectivity. Any generator that routes by "walk until a
free column" must carry a **per-net obstacle map of the layer it draws on**, and refuse a column
whose connecting stub would cross a foreign net's shapes on that layer. Run LVS on every sizing
point the generator is expected to draw, not just the first one: the bug is latent in the
floorplan and a knob change orders of magnitude too small to think about will expose it.

**Where it lives.** `Builder.m1_claim` records every Metal1 feature (gate bars, S/D straps,
stubs) against its net; `Builder.stub_clear` tests a candidate stub against them; `alloc` now
searches **both** directions from the terminal instead of marching in one, and raises with a
"widen `LayoutParams.dev_gap`" hint if no column works. Verified at two sizings (design of record
and the 002 hand point): DRC 0 and LVS matched on both.
