# 005 — layout: generator → GDS → DRC / LVS / PEX → post-layout scorecard

**Paper(s):** none
**Hypothesis:** the design of record (003) can be drawn by a *parameterized generator* — `layout/gen_ldo.py`, whose sizing comes from `sizing.yaml` and whose floorplan constants are an optimizer-ready search space — and the resulting cell will be DRC-clean, LVS-identical to the certified netlist, extractable, and will still pass the whole S1–S8 box on its **own frozen benches** run against the extracted netlist. Falsified if any sign-off stage cannot be made to pass, or if a spec falls out of the box post-layout.
**Control:** the pre-layout scorecard of the same sizing point, re-simulated in the same run (not quoted from 003), so every pre→post shift is attributable to the extraction alone; and, for the generator bug in §2, the same generator at the 002 hand sizing, which passed LVS before and after the fix.
**Verdict:** CONFIRMED. **DRC 0 violations, LVS matched, PEX extracted (121 C, 10 R, CC mode), and the extracted cell passes all of S1–S8** (§1). Area 35 317 µm² (287.4 × 122.9 µm). The layout costs 9.1 mV of undershoot and 0.7° of phase margin and gives back 0.08 µA of Iq; nothing else moves by more than its own measurement resolution. The engines are **KLayout** (IHP SG13G2 runsets) for DRC/LVS and **kpex 2.5D** for extraction — not magic/netgen, which the platform's `spicexplorer_signoff` does not drive on this PDK.

**Figure:** `figs/ldo_ihp_capless.png` — the cell rendered with PDK colours
(`spicexplorer-layout render`). Three device rows (NMOS / PMOS / the pass device) between the
vss and vdd rails, one Metal1 track per internal net in the channel between them, the `rhigh`
serpentines left and the MIM array right.

## 1. Pre- vs post-layout scorecard

The cell's own 13 frozen benches, both rows simulated in the same invocation (`out/scorecard.md`, `layout/postlayout.py`):

| cell | v_out_v | i_q_ua | load_reg_mv | line_reg_mv | v_dropout_mv | psrr_1k_db | v_undershoot_mv | pm_loop_deg | pm_loop_lo_deg | pm_loop_hi_deg | loopgain_db | ugf_loop_khz | ms_peak_db | psrr_1m_db | t_transient_us | vn_out_urms | v_line_pp_mv | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pre-layout (schematic) | 1.200 | 36.28 | 0.028 | 0.059 | 106.1 | 69.95 | 104.8 | 72.42 | 72.38 | 72.31 | 49.95 | 836.5 | 7.15 | 15.30 | 0.1254 | 19140 | 51.62 | PASS |
| **post-layout (extracted)** | 1.200 | 36.20 | 0.028 | 0.068 | 106.1 | 69.95 | 113.9 | 71.74 | 71.70 | 71.63 | 49.95 | 817.8 | 6.21 | 15.05 | 0.1496 | 19090 | 51.62 | **PASS** |
| shift | 0 | −0.08 | 0 | +0.009 | 0 | 0 | **+9.1** | **−0.68** | −0.68 | −0.68 | 0 | −18.7 | −0.94 | −0.25 | +0.024 | −50 | 0 | |
| spec box | [1.176, 1.224] | ≤ 50 | ≤ 5 | ≤ 2 | ≤ 200 | ≥ 40 | ≤ 150 | ≥ 60 | ≥ 60 | ≥ 60 | — | — | — | — | — | — | — | |

The shifts are consistent with one cause. Extracted capacitance per net (kpex, CC mode, top nets in fF):

| net | VSUBS | vout | ea_o1 | vdd | gate | ea_out | fb | lp_brk | pbias | ea_tail | x1 | y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ΣC (fF) | 349.9 | 72.0 | 44.7 | 43.3 | **28.4** | 22.6 | 19.2 | 16.4 | 13.9 | 12.1 | 11.5 | 10.6 |

`gate` — the pass-device gate — picks up 28.4 fF, and 002 established that any capacitance there is paid at the FVF sink's slew rate (`doc/journal/fvf-gate-cap-is-slew.md`). 28.4 fF against ~1 pF of intrinsic gate capacitance is ~3 %, and S7 moves 104.8 → 113.9 mV (+8.7 %) with recovery 0.125 → 0.150 µs — the same mechanism, in the direction and roughly the magnitude the journal predicts. `ea_o1` (44.7 fF) is the Miller node and explains the 19 kHz of UGF and 0.68° of phase margin given up. Neither shift threatens its bound: S7 keeps 36 mV of margin and S8 keeps 11.6°.

## 2. The bug the layout lane actually found

The first LVS run at the record sizing **did not match**, while the same generator at the 002 hand sizing did. Every device size matched; the extracted netlist showed `fb` merged into `vref` — both error-amplifier input gates on one net. Reverting one knob at a time (13 builds + 13 LVS runs) put it entirely on **`x_dut_xms_l`, a 50 nm length change on a device in a different row**.

The mechanism: `to_track` connects a terminal to its channel track with a Metal2 column, and bridges any x-shift with a **Metal1 stub** at the terminal's y. Column allocation only checked Metal2-to-Metal2 spacing, so when the 50 nm shift made XM2's preferred columns busy, its gate stub walked far enough left to run straight through **XM1's gate bar**, which sits at the same y. Two Metal1 shapes that overlap merge into one legal polygon, so **DRC reported 0 violations on a shorted netlist** — only LVS caught it.

The fix is in the generator, not in the sizing: `Builder` now records every Metal1 feature per net (`m1_claim` on gate bars, straps and stubs) and `alloc` rejects any column whose stub would cross a foreign net's Metal1, searching both directions instead of marching in one. Verified on **both** sizings after the fix — record and 002 hand point, DRC 0 and LVS matched on each. A 50 nm knob change silently shorting two nets is exactly the failure a parameterized generator exists to make impossible, so the check is a permanent part of it.

## 3. Sign-off, stage by stage

| stage | engine | result |
|---|---|---|
| build | gdsfactory 9.34 + ihp-gdsfactory | 35 317 µm² (287.4 × 122.9 µm) |
| render | `spicexplorer-layout render` | `figs/ldo_ihp_capless.png` |
| DRC | KLayout, IHP SG13G2 maximal rule set (36 tables) | **0 violations** |
| LVS | KLayout, IHP SG13G2 runset, `--combine_devices` | **matched** |
| PEX | kpex 2.5D, mode CC | **121 C, 10 R** |
| post-layout | the cell's own 13 frozen benches | **13/13 ran, 0 violations** |

Three PDK-runset quirks had to be handled to get from a passing LVS to a simulable extracted netlist; each is a platform gap, journalled, and fixed in `layout/signoff.py` / `layout/postlayout.py` rather than by hand-editing an artefact:

1. **kpex cannot read a 2-node `rhigh`.** Its bundled deck extracts the poly resistor as 3-terminal (`custom_reader.lvs`: *"Poly resistor should have 3 nodes"*) while the standalone IHP LVS deck accepts 2, so the LVS schematic and the PEX schematic differ by that substrate node.
2. **kpex's element cards are not ngspice cards.** It writes `R$36 lp_brk $37 vss 0.5 rhigh l=85 …`, but ngspice's IHP `rhigh` is a 3-terminal *subcircuit*, so the card must become an `XR` call with unit-suffixed `w`/`l` — otherwise ngspice reports `unknown parameter (vss)`. Its anonymous nets (`\$21`) also have to be renamed, because `$` opens an in-line comment in SPICE.
3. **kpex hangs every ground capacitance on a substrate node `VSUBS` that is not a pin.** Narrowing the extracted header to the schematic's three pins leaves it floating and the operating point is singular; the p-substrate is at `vss` through the layout's own ptap ring, so it is tied with a 0 V source.

Two more things were needed and are worth naming. Every track is now **labelled** in the generator, not just the pins: the extractor names nets after labels, which is what makes the per-net C table above readable and lets the post-layout deck re-attach the MIM capacitors by name. And the MIM capacitors themselves are **not extracted** — kpex cannot handle IHP `cap_cmim`, so their plates are stripped from the GDS before extraction and the schematic capacitors are spliced back in. **What that costs is stated, not hidden:** MIM bottom-plate (Metal5) coupling to the neighbourhood is extracted, top-plate coupling is not.

## 4. The generator is a search space, not a drawing

`layout/gen_ldo.py` takes `LayoutParams` — `dev_gap`, `grp_gap`, `track_pitch`, `ch_margin`, `rail_w`, `rail_gap`, `mim_gap`, `res_pitch`, `blk_gap`, `tap_pitch` — each with DRC-safe bounds in `BOUNDS`, which is the interface a `sim_engine: layout` co-design run (`layout-schematic-codesign`) would drive. Sizing is **not** duplicated here: the module reads `circuits/ldo_ihp_capless/pdk/ihp-sg13g2/sizing.yaml` directly, so re-sizing the cell redraws it with no edit to the generator. That co-design loop was not run — the post-layout scorecard passes, so there is nothing for it to repair yet.

The **GDS itself is deliberately not committed**: the layout of record is the *generator*
(`.claude/skills/layout-evidence` — "the layout of record is code"), so a checked-in 845 kB binary
could only drift from `gen_ldo.py` + `sizing.yaml`. Rebuild it with
`LDO_EXP=005 uv run --no-sync python layout/signoff.py --stages build`; `--all` re-runs the whole
sign-off chain above.

## 5. What was not done

- **No independent `layout-reviewer` pass.** The `layout-evidence` method asks for a numbered `REVIEW.md`/`REVIEW.yaml`/`REVIEW.png` from an agent that rebuilds and re-measures everything itself (rule 7, designer ≠ verifier). Everything here was produced by the designer; the sign-off is reproducible from the committed generator (`layout/signoff.py`), but it has not been independently re-measured.
- **No layout brief.** `layout-brief-author` should have produced per-net parasitic budgets *before* drawing; §1 reads the budgets off the finished extraction instead, which cannot say whether 28.4 fF on `gate` was the best available.
- **No corner or Monte-Carlo run post-layout.** The extracted scorecard is tt/27 °C only. Given that 003 §3 shows S5 and S7 already binding at corners *pre*-layout, the +9.1 mV of undershoot the layout adds would make ss/−40 worse, not better.
- **No `iterations/` snapshots.** One iteration was recorded, so `spicexplorer-layout snapshot`/`diff` had nothing to compare; the LVS fix in §2 changed the generator, not the floorplan.

## Lessons to graduate

- (`005`) A Metal1 short between two nets is **DRC-invisible** — overlapping same-layer shapes merge into one legal polygon — so a generator that routes by "find a free column" must carry its own per-net obstacle map, and LVS is the only thing that will catch it. Journal: `doc/journal/metal1-stub-shorts-are-drc-invisible.md`.
- (`005`) kpex's extracted netlist is an LVS artefact, not a simulable deck: primitive cards for subcircuit devices, `$`-prefixed net names, and a substrate node that is not a pin. Journal: `doc/journal/kpex-cards-are-not-ngspice-cards.md`.
- (`005`) `Warning: singular matrix` is what ngspice prints *while* stepping to an operating point; on an extracted netlist it appears once and the analysis then converges and prints every measure. `ldo.sim`'s own fatal-line table matched the substring with no severity ordering and threw away **seven** of thirteen benches whose results were sitting in the log. FIXED: `ldo/sim.py` now calls the platform's `sim_log.fatal_lines`, whose patterns are ordered so a `Warning:` prefix outranks the bare form, and `layout/postlayout.py`'s local `run_tolerant` override is gone — the post-layout row below comes from the frozen path, **13 of 13 benches**. Journal: `doc/journal/singular-matrix-is-a-warning.md` (review-002 M4/M5).
