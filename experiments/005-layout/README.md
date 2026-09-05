# 005 — layout: generator → GDS → DRC / LVS / PEX → post-layout scorecard

**Paper(s):** none
**Hypothesis:** the design of record (003) can be drawn by a *parameterized generator* — `layout/gen_ldo.py`, whose sizing comes from `sizing.yaml` and whose floorplan constants are an optimizer-ready search space — and the resulting cell will be DRC-clean, LVS-identical to the certified netlist, extractable, and will still pass the whole S1–S8 box on its **own frozen benches** run against the extracted netlist. Falsified if any sign-off stage cannot be made to pass, or if a spec falls out of the box post-layout.
**Control:** the pre-layout scorecard of the same sizing point, re-simulated in the same run (not quoted from 003), so every pre→post shift is attributable to the extraction alone; and, for the generator bug in §2, the same generator at the 002 hand sizing, which passed LVS before and after the fix.
**Verdict:** CONFIRMED, then **redrawn**. The first drawing (2026-09-04, §2-§6 below) passed DRC 0 / LVS matched / 13 benches, and independent review `doc/reviews/review-002-capless-ldo.md` then rejected its **floorplan**: the 10 mA path was 12-28x over the process metal current-density limit (B1), the matched pairs had no interdigitation, dummies or guard rings (m3), the LVS golden netlist was written by the generator itself (M7), and half the Metal1-short fix was an unexercised regression (M8). The **second drawing** (§1) closes all four and is the layout of record: **current density 27/27 segments (worst 0.836x), DRC 0, LVS matched at two sizing points, kpex CC + RC, 13/13 benches, 0 spec violations**, in 42 231 um^2 (202.5 x 208.55 um, aspect 1.03:1) against the first drawing's 35 317 um^2. It costs 22.7 mV of undershoot and 3.7 deg of phase margin and gives back 2.5 uA of Iq. Full tables: [`layout/ldo_ihp_capless/REPORT.md`](../../layout/ldo_ihp_capless/REPORT.md); plan and assumed approvals: [`PLAN.md`](../../layout/ldo_ihp_capless/PLAN.md).

**Figure:** `figs/ldo_ihp_capless.png` — the **second drawing**, rendered with PDK
colours (`spicexplorer-layout render`). Reading it: the **pass array** is the top-right block, 76
shared-diffusion fingers inside a closed n-tap ring inside a closed p-substrate ring, with its
Metal2 source/drain combs on top; the **two device rows** are the guard-ringed islands under it —
the wider pair of islands (row A: the A B B A NMOS load pair, the FVF n-fold, the interdigitated
bias group) and the single wide island below them (row B: the p bias group and, in its own quiet
n-well, the A B B A input pair). The **`rhigh` serpentines** are the vertical bars at mid-left (16
divider segments + 2 dummies, and the bias resistor), with the **Miller MIM** directly under them
and the small **feed-forward MIM** at the bottom-left corner. The **2 × 2 XCOUT array** fills the
bottom right about a central vertical TopMetal1 top-plate spine. Over the whole cell: the
TopMetal1 **vdd** strap along the top edge, the **vout** strap down the right edge, **vss** along
the bottom. The empty top-left quadrant is the void named in
[`REPORT.md` §1](../../layout/ldo_ihp_capless/REPORT.md) — the first thing a placement optimizer
should take.

## 1. The second drawing — before / after

The first drawing was rejected on its floorplan, not on its verdicts. What changed:

| | first drawing | second drawing |
|---|---|---|
| outline | 287.4 x 122.9 um | **202.50 x 208.55 um** |
| aspect | 2.34 : 1 | **1.03 : 1** (ceiling 2:1) |
| area | 35 317 um^2 | **42 231 um^2** (+19.6 %) |
| pass device | 19 fingers of 10 um | 76 fingers of 2.5 um (same W = 190 um) |
| 10 mA path | Metal1 0.8 um rail + 0.6 um bus + one Via1 to a 0.2 um pin track | TopMetal1 2 um straps, Metal2 6 um combs, 48-cut via risers, 12 TopVia1 stitches |
| current-density check | none exists | a **blocking** sign-off stage, 27 segments scored |
| matched pairs | mirrored single-finger pairs, no dummies | common-centroid / interdigitated by measured headroom, 16 tied MOS dummies + 2 resistor dummies |
| wells | periodic point taps every 12 um | **5 closed guard rings** (3 n-well islands + 2 p-substrate) |
| LVS reference | the generator's own hand-typed device table | derived from the certified netlist (`layout/netlist_ref.py`) |
| obstacle map | committed, exercised by no case | `layout/router.py` + `layout/test_builder.py`, run first and blocking |
| PEX | CC only, 121 C / 10 R | CC 182 C / 21 R **and** RC 182 C / 8 418 R |
| sizing points verified | record + 002 hand | record + 002 hand |

**Where the +19.6 % went**, in order: the closed rings and the `ring_gap`/`isl_gap` three n-well
islands need so they do not merge (NW.b 0.62 um); one tied dummy at each end of each of the eight
matching groups; the 6 um Metal2 combs and via risers over the pass array; and a pass array 4x
longer in x. The floorplan went from one 287 um row to a square block, which is why the aspect
improved while the area grew. The largest void is the top-left corner (~60 x 70 um) — the first
thing a placement optimizer should take.

### Current density (review-002 B1)

`spicexplorer_signoff.current_density` over the budget list the **generator emits from its own
drawn geometry**, run by `layout/signoff.py` as a blocking stage. Limits from
`SG13G2_os_process_spec.pdf` §2.15; currents measured (I(vdd) = 10.0318 mA, I(XMP) = 10.0041 mA,
I(vss) = 27.7 uA).

| net | segment | carries (mA) | drawn | limit (mA) | used/allowed |
|---|---|---|---|---|---|
| `vdd` | pass source column Metal1 riser (shared) | 0.263 | metal1 0.31 um | 0.36 | 0.731x |
| `vout` | pass drain column Metal1 riser (shared) | 0.263 | metal1 0.31 um | 0.36 | 0.731x |
| `vdd` | pass source column Via1 (shared) | 0.263 | via1 x4 | 1.60 | 0.165x |
| `vout` | pass drain column Via1 (shared) | 0.263 | via1 x4 | 1.60 | 0.165x |
| `vdd` | pass source column Metal2 finger | 0.263 | metal2 0.31 um | 0.62 | 0.425x |
| `vout` | pass drain column Metal2 finger | 0.263 | metal2 0.31 um | 0.62 | 0.425x |
| `vdd` | pass source Metal2 comb spine | 10.032 | metal2 6 um | 12.00 | 0.836x |
| `vout` | pass drain Metal2 comb spine | 10.004 | metal2 6 um | 12.00 | 0.834x |
| `vout` | pass drain diffusion contacts (shared column) | 0.263 | cnt x4 | 1.20 | 0.219x |
| `vdd` | vdd riser Metal2->Metal3 | 10.032 | via2 x48 | 19.20 | 0.522x |
| `vdd` | vdd riser Metal3->Metal4 | 10.032 | via3 x48 | 19.20 | 0.522x |
| `vdd` | vdd riser Metal4->Metal5 | 10.032 | via4 x48 | 19.20 | 0.522x |
| `vdd` | vdd Metal5->TopMetal1 stitch | 10.032 | topvia1 x12 | 16.80 | 0.597x |
| `vdd` | vdd riser Metal3 pad | 10.032 | metal3 6 um | 12.00 | 0.836x |
| `vdd` | vdd riser Metal4 pad | 10.032 | metal4 6 um | 12.00 | 0.836x |
| `vdd` | vdd riser Metal5 pad | 10.032 | metal5 6 um | 12.00 | 0.836x |
| `vout` | vout riser Metal2->Metal3 | 10.004 | via2 x48 | 19.20 | 0.521x |
| `vout` | vout riser Metal3->Metal4 | 10.004 | via3 x48 | 19.20 | 0.521x |
| `vout` | vout riser Metal4->Metal5 | 10.004 | via4 x48 | 19.20 | 0.521x |
| `vout` | vout Metal5->TopMetal1 stitch | 10.004 | topvia1 x12 | 16.80 | 0.596x |
| `vout` | vout riser Metal3 pad | 10.004 | metal3 6 um | 12.00 | 0.834x |
| `vout` | vout riser Metal4 pad | 10.004 | metal4 6 um | 12.00 | 0.834x |
| `vout` | vout riser Metal5 pad | 10.004 | metal5 6 um | 12.00 | 0.834x |
| `vdd` | cell Metal1 vdd rail (row-B sources + XRB, Iq only) | 0.037 | metal1 0.8 um | 0.80 | 0.046x |
| `vss` | cell Metal1 vss rail (Iq only) | 0.028 | metal1 0.8 um | 0.80 | 0.035x |
| `vdd` | vdd TopMetal1 strap (top edge) | 10.032 | topmetal1 2 um | 30.00 | 0.334x |
| `vout` | vout TopMetal1 strap (right edge + XCOUT bus) | 10.004 | topmetal1 2 um | 30.00 | 0.334x |

**Worst 0.836x.** The brief's own remedy (a 1.1 um Metal1 riser per shared S/D column) is not
drawable — at L = 0.13 um the contacted column pitch is ~0.51 um and every Metal1 width from 0.16
to 0.36 um carries the same flat 0.36 mA — and its alternative (raise `nf` to >= 56) would change
`x_dut_xmp_m`. Neither is needed: folding `m = 19` into **4x as many, 4x narrower** fingers
(`xmp_nf_mult = 4`) leaves `w = 10 um, m = 19` untouched in `sizing.yaml` and the extracted device
at W = 190 um / L = 0.13 um — what `--combine_devices` compares — while the shared-column current
falls from 1.053 mA to **0.263 mA**. What it does change is junction area/perimeter and the gate
bar's length, both measured below.

### Pre- vs post-layout, and where each delta comes from

All rows through the frozen path (`ldo.sim.run` + `ldo.metrics.promote`, `layout/postlayout.py`).
Column 3 is a **schematic-only what-if**: the certified subckt with exactly the split the layout
draws (every matched device as two half-width instances, the pass array as 76 fingers) and **no
parasitics**, so the device increment and the parasitic increment are separable.

| metric | pre-layout | + drawn device split (no parasitics) | + parasitics = post-layout | total delta | cause |
|---|---|---|---|---|---|
| `v_out_v` | 1.2 | 1.199 | **1.199** | -0.000573 | device split (present with no parasitics) |
| `i_q_ua` | 36.28 | 34.05 | **33.81** | -2.472 | **device split**: -2.23 uA of it with no parasitics at all; a second what-if isolates -0.26 uA to the serpentine segmentation. A 0.5 um NMOS is not half of a 1 um one |
| `load_reg_mv` | 0.028 | 0.026 | **0.026** | -0.002 | split; 2 resolution steps |
| `line_reg_mv` | 0.059 | 0.057 | **0.056** | -0.003 | split; 3 resolution steps |
| `v_dropout_mv` | 106.1 | 104.7 | **104.7** | -1.472 | split; **below the 2 mV bench resolution - no bound** |
| `psrr_1k_db` | 69.95 | 70.03 | **70.11** | 0.1539 | split; improvement |
| `v_undershoot_mv` | 104.8 | 110.7 | **127.6** | 22.73 | +5.9 split, **+16.9 parasitic**: `gate` 47.5 fF (~35 fF to-rail-equivalent) at +0.386 mV/fF, minus `ea_o1` 64.9 fF at -0.181 mV/fF. S7 keeps 22 mV |
| `pm_loop_deg` | 72.42 | 72.35 | **68.76** | -3.657 | **`fb` 34.0 fF x -0.111 deg/fF = -3.77 deg** (measured -3.66). S8 keeps 8.8 deg |
| `pm_loop_lo_deg` | 72.38 | 72.31 | **68.73** | -3.651 | same cause |
| `pm_loop_hi_deg` | 72.31 | 72.23 | **68.64** | -3.665 | same cause |
| `loopgain_db` | 49.95 | 50.21 | **50.22** | 0.2789 | split; 1 resolution step |
| `ugf_loop_khz` | 836.5 | 809.9 | **771.9** | -64.59 | -26.6 split, -38 parasitic (`ea_o1` on the Miller node). No spec line |
| `gm_loop_db` | 6.427 | 6.396 | **7.972** | 1.546 | the loop's gain margin rises with the added lag. No spec line |
| `ms_peak_db` | 7.15 | 7.07 | **9.059** | 1.909 | closed-loop peaking, same cause. No spec line |
| `psrr_1m_db` | 15.3 | 15.1 | **14.19** | -1.116 | parasitic, high frequency. No spec line |
| `t_transient_us` | 0.1254 | 0.1407 | **0.2005** | 0.07513 | the recovery time of the same `gate` slew as S7 |
| `vn_out_urms` | 366.4 | 369.7 | **360.4** | -6.01 | split. No spec line |
| `v_line_pp_mv` | 51.62 | 51.63 | **55.63** | 4.016 | parasitic. No spec line |

Verdict on the extracted cell: **13/13 benches ran, 0 spec violations, PASS**. The two columns
that moved materially are S7 (+22.7 mV, 22 mV of margin left) and S8 (-3.66 deg, 8.8 deg left),
and each has a single named parasitic. Per-net C against the brief's budgets — `gate` 47.5 fF
(1.62x raw, ~1.19x once gate-to-`vout` is weighted at the brief's own coefficient) and `fb`
34.0 fF (1.22x), everything else <= 0.10x — is tabulated in
[`REPORT.md` §7](../../layout/ldo_ihp_capless/REPORT.md).

**RC mode does not converge in these benches**: 11 of 13 abort with `Warning: singular matrix:
check node xdut.n_25.n_2.17` — dangling nodes in the R mesh of the `rhigh` serpentines — and the
op point then fails. The two transient benches that do converge reproduce the CC row to the last
digit (127.6 mV, 0.2005 us, 55.63 mV), so extracted wire resistance moves nothing this cell is
measured on. A `.nodeset` was not attempted.

Nine snapshotted rounds with before|after diffs:
[`layout/ldo_ihp_capless/iterations/`](../../layout/ldo_ihp_capless/iterations/), tabulated in
[`REPORT.md` §9](../../layout/ldo_ihp_capless/REPORT.md). What the floorplan cost, as a lesson:
`doc/journal/a-floorplan-is-bought-not-found.md`.

## 2. The first drawing — pre- vs post-layout scorecard

The cell's own 13 frozen benches, both rows simulated in the same invocation (`out/scorecard.md`, `layout/postlayout.py`). Re-run 2026-09-04 after the LDO class noise bench dropped its extra `sqrt` (review-002 M2, analog-db PR #68): `vn_out_urms` is the only column that moved, from 19 140 / 19 090 to the values below.

| cell | v_out_v | i_q_ua | load_reg_mv | line_reg_mv | v_dropout_mv | psrr_1k_db | v_undershoot_mv | pm_loop_deg | pm_loop_lo_deg | pm_loop_hi_deg | loopgain_db | ugf_loop_khz | ms_peak_db | psrr_1m_db | t_transient_us | vn_out_urms | v_line_pp_mv | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pre-layout (schematic) | 1.200 | 36.28 | 0.028 | 0.059 | 106.1 | 69.95 | 104.8 | 72.42 | 72.38 | 72.31 | 49.95 | 836.5 | 7.15 | 15.30 | 0.1254 | 366.4 | 51.62 | PASS |
| **post-layout (extracted)** | 1.200 | 36.20 | 0.028 | 0.068 | 106.1 | 69.95 | 113.9 | 71.74 | 71.70 | 71.63 | 49.95 | 817.8 | 6.21 | 15.05 | 0.1496 | 364.4 | 51.62 | **PASS** |
| shift | 0 | −0.08 | 0 | +0.009 | 0 | 0 | **+9.1** | **−0.68** | −0.68 | −0.68 | 0 | −18.7 | −0.94 | −0.25 | +0.024 | −2.05 | 0 | |
| spec box | [1.176, 1.224] | ≤ 50 | ≤ 5 | ≤ 2 | ≤ 200 | ≥ 40 | ≤ 150 | ≥ 60 | ≥ 60 | ≥ 60 | — | — | — | — | — | — | — | |

The shifts are consistent with one cause. Extracted capacitance per net (kpex, CC mode, top nets in fF):

| net | VSUBS | vout | ea_o1 | vdd | gate | ea_out | fb | lp_brk | pbias | ea_tail | x1 | y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ΣC (fF) | 349.9 | 72.0 | 44.7 | 43.3 | **28.4** | 22.6 | 19.2 | 16.4 | 13.9 | 12.1 | 11.5 | 10.6 |

`gate` — the pass-device gate — picks up 28.4 fF, and 002 established that any capacitance there is paid at the FVF sink's slew rate (`doc/journal/fvf-gate-cap-is-slew.md`). 28.4 fF against ~1 pF of intrinsic gate capacitance is ~3 %, and S7 moves 104.8 → 113.9 mV (+8.7 %) with recovery 0.125 → 0.150 µs — the same mechanism, in the direction and roughly the magnitude the journal predicts. `ea_o1` (44.7 fF) is the Miller node and explains the 19 kHz of UGF and 0.68° of phase margin given up. Neither shift threatens its bound: S7 keeps 36 mV of margin and S8 keeps 11.6°.

## 3. The bug the first drawing actually found

The first LVS run at the record sizing **did not match**, while the same generator at the 002 hand sizing did. Every device size matched; the extracted netlist showed `fb` merged into `vref` — both error-amplifier input gates on one net. Reverting one knob at a time (13 builds + 13 LVS runs) put it entirely on **`x_dut_xms_l`, a 50 nm length change on a device in a different row**.

The mechanism: `to_track` connects a terminal to its channel track with a Metal2 column, and bridges any x-shift with a **Metal1 stub** at the terminal's y. Column allocation only checked Metal2-to-Metal2 spacing, so when the 50 nm shift made XM2's preferred columns busy, its gate stub walked far enough left to run straight through **XM1's gate bar**, which sits at the same y. Two Metal1 shapes that overlap merge into one legal polygon, so **DRC reported 0 violations on a shorted netlist** — only LVS caught it.

The fix is in the generator, not in the sizing: `Builder` now records every Metal1 feature per net (`m1_claim` on gate bars, straps and stubs) and `alloc` rejects any column whose stub would cross a foreign net's Metal1, searching both directions instead of marching in one. Verified on **both** sizings after the fix — record and 002 hand point, DRC 0 and LVS matched on each. A 50 nm knob change silently shorting two nets is exactly the failure a parameterized generator exists to make impossible, so the check is a permanent part of it.

## 4. Sign-off, stage by stage (first drawing)

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

## 5. The generator is a search space, not a drawing

`layout/gen_ldo.py` takes `LayoutParams` — 21 fields in the second drawing: the placement knobs
(`dev_gap`, `grp_gap`, `track_pitch`, `ch_margin`, `isl_gap`, `blk_gap`, `mim_gap`, `res_pitch`,
`r_segs`, `rb_segs`), the power-path knobs (`pwr_w`, `pwr_stitch`, `pwr_riser_vias`, `pwr_band_w`,
`col_vias`, `xmp_nf_mult`, `rail_w`, `rail_gap`), and the matching knobs (`n_dummy`, `ring_w`,
`ring_gap`) — each with bounds in `BOUNDS`, which is the interface a `sim_engine: layout`
co-design run (`layout-schematic-codesign`) would drive. Only `xmp_nf_mult = 4` is *verified*
(at two sizing points); the other ranges are declared, not swept. Sizing is **not** duplicated here: the module reads `circuits/ldo_ihp_capless/pdk/ihp-sg13g2/sizing.yaml` directly, so re-sizing the cell redraws it with no edit to the generator. That co-design loop was not run — the post-layout scorecard passes, so there is nothing for it to repair yet.

The **GDS itself is deliberately not committed**: the layout of record is the *generator*
(`.claude/skills/layout-evidence` — "the layout of record is code"), so a checked-in 845 kB binary
could only drift from `gen_ldo.py` + `sizing.yaml`. Rebuild it with
`LDO_EXP=005 uv run --no-sync python layout/signoff.py --stages build`; `--all` re-runs the whole
sign-off chain above.

## 6. What was not done

- **No independent `layout-reviewer` pass.** The `layout-evidence` method asks for a numbered `REVIEW.md`/`REVIEW.yaml`/`REVIEW.png` from an agent that rebuilds and re-measures everything itself (rule 7, designer ≠ verifier). Everything here was produced by the designer; the sign-off is reproducible from the committed generator (`layout/signoff.py`), but it has not been independently re-measured.
- **No corner or Monte-Carlo run post-layout.** The extracted scorecard is tt/27 °C only. Given that 003 §3 shows S5 and S7 already binding at corners *pre*-layout, and that the second drawing adds **+22.7 mV** of undershoot, ss/−40 gets worse, not better. This is the next run.
- **Routing is not matched half-for-half.** The channel allocator finds each terminal a free column, so the two halves of a common-centroid pair do not get identical routing topology. The devices are matched; the routing is not, and the cost is not measured.
- **`gate` and `fb` are over their brief budgets** (1.19x to-rail and 1.22x). Both inside their hard limits and inside the spec box, both explained in [`REPORT.md` §7](../../layout/ldo_ihp_capless/REPORT.md), neither fixed.
- **The DRC-0 result is conditional on the density/fill tables being off** — the only rule group switched off, and nothing else is waived. Fill and sealring are chip-assembly steps and distort the PEX of a bare cell.

Closed since the first drawing: the layout brief now exists (`layout/ldo_ihp_capless/BRIEF.md`, measured budgets *before* drawing), and nine `iterations/` snapshots with before|after diffs are committed.

## Lessons to graduate

- (`005`) **A floorplan is bought, not found.** Closing the current-density finding cost +19.6 % of area, and the two nets the brief flagged went *over* budget doing it: `gate` grew because `xmp_nf_mult = 4` makes the pass gate bar 4x longer, which is the fix for B1, and `fb` grew because the divider and the input pair are further apart in a square block than in a 287 um row. Both are paid in S7 and S8 margin and both are still inside the box. Journal: `doc/journal/a-floorplan-is-bought-not-found.md`.
- (`005`) **An obstacle map that covers one layer is half a guard.** The first drawing's map covered Metal1 gate bars; the second drawing shorted `gate` to `vout` on a **Metal2** power-comb spine, with DRC at 0 again. Claim every shape a router can walk into — power combs, guard rings, MIM plate pads, resistor end pads — not just the ones that bit last time.
- (`005`) **`cap_cmim` is polarised in the LVS deck.** `nodes[0]` is the top (PLUS) plate. The brief asked for the sensitive terminal on top (kpex does not extract the top plate); for two of three capacitors that is the opposite of the certified card, and LVS said so. Swapping the plates moves the bottom-plate parasitic to the other node — a **design** change, so the generator reads the assignment off the netlist and the brief's preference stays a re-sizing question.
- (`005`) **`ihp.cells.guard_ring` is not DRC-clean**: Cnt.b (0.18 um contact space) at every corner, measured standalone at seven width/spacing combinations. `Builder.ring` draws the ring instead, corner contact *on* the corner.
- (`005`) A Metal1 short between two nets is **DRC-invisible** — overlapping same-layer shapes merge into one legal polygon — so a generator that routes by "find a free column" must carry its own per-net obstacle map, and LVS is the only thing that will catch it. Journal: `doc/journal/metal1-stub-shorts-are-drc-invisible.md`.
- (`005`) kpex's extracted netlist is an LVS artefact, not a simulable deck: primitive cards for subcircuit devices, `$`-prefixed net names, and a substrate node that is not a pin. Journal: `doc/journal/kpex-cards-are-not-ngspice-cards.md`.
- (`005`) `Warning: singular matrix` is what ngspice prints *while* stepping to an operating point; on an extracted netlist it appears once and the analysis then converges and prints every measure. `ldo.sim`'s own fatal-line table matched the substring with no severity ordering and threw away **seven** of thirteen benches whose results were sitting in the log. FIXED: `ldo/sim.py` now calls the platform's `sim_log.fatal_lines`, whose patterns are ordered so a `Warning:` prefix outranks the bare form, and `layout/postlayout.py`'s local `run_tolerant` override is gone — the post-layout row below comes from the frozen path, **13 of 13 benches**. Journal: `doc/journal/singular-matrix-is-a-warning.md` (review-002 M4/M5).
