# 003 — sizing: gm/ID start, optimizer run, design of record, corners

**Paper(s):** none (topology from 002)
**Hypothesis:** starting from the gm/ID-derived hand point of 002 (the double-mirror fold, all of S1–S8 at tt except S5), `spicexplorer-optimize` (Nevergrad NGOpt, the S1–S8 box with margin as constraints, S8 also at 0.1/10 mA, Iq as the objective) finds a point ≤ 35 µA that still meets the whole box at tt/27 °C, and that point holds S1–S8 over the five MOS corners × −40/27/125 °C with at most S8 falling below 60° at ss/−40 °C. Falsified if the optimizer cannot cut Iq by ≥ 20 % without a constraint violation, or if the corner table shows a hard-box violation at tt-adjacent corners.
**Control:** the hand point itself (trial 0, seeded through `seed_from_init`) scored by the same project; and the reference row quoted from `decks/reference/scorecard.json`. Every candidate row is the full 13-bench `lab.metrics.evaluate` scorecard, not the optimizer's own reading.
**Verdict:** PARTLY CONFIRMED. The optimizer cut Iq **50.17 → 36.28 µA (−27.7 %)** and passes the whole box at tt/27 °C with margin on every line (table 1) — so the ≥ 20 % clause holds, but the **≤ 35 µA target is missed by 1.28 µA**; the hypothesis is not retracted, it is scored as missed. The corner clause is **FALSIFIED, and not in the predicted place**: 12 of 15 corners pass, but the failures are **S7 at ss/−40 and ss/27 (311 and 255 mV)** and **S5 at ff/125 (61.9 µA)** — not S8, which never drops below 70.4° anywhere (table 4). Both failures are the same mechanism, and it is not sizing: the resistor-referenced bias spreads Iq **2.4× across corners** (25.6–61.9 µA), and S5 and S7 pull that one knob in opposite directions (§3). Two further findings that only the frozen benches could produce: rounding the optimizer's winner onto a layout grid **breaks S7 twice over** (§2) — once by moving the pass device off its minimum length, once by landing `c_ff_w` on a cliff.

**Figures** (`figs.py`, regenerated from `out/*.json`; every one carries its spec bound):
`figs/points.png` (§1, every "lower is better" spec as a fraction of its bound),
`figs/cff_cliff.png` (§2, the cliff and the phase-margin curve that stays smooth through it),
`figs/corners.png` (§3, S5/S7/S8 over the corner grid with the box drawn).

## 1. The design of record at tt / 27 °C

Every row is the full 13-bench `lab.metrics.evaluate` scorecard (`out/points_all.md`, ledger tags `003_control_tt_27`, `003_raw_tt_27`, `003_rounded_tt_27`, `003_record_tt_27`). The reference row is quoted, not re-run (`decks/reference/scorecard.json`; hv / 3.3 V / 1.6 V / 1 µF, the yardstick for S2/S3/S6 only).

| cell | v_out_v | i_q_ua | load_reg_mv | line_reg_mv | v_dropout_mv | psrr_1k_db | v_undershoot_mv | pm_loop_deg | pm_loop_lo_deg | pm_loop_hi_deg | loopgain_db | ugf_loop_khz | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| reference (certified, quoted) | 1.609 | 758.7 | 1.274 | 4.32 | 169.7 | 44.53 | 1.957 | 46.39 | — | — | 91.9 | 569 | FAIL (S1 window, S3, S5, S8) |
| **control** — 002 fold hand point | 1.196 | 50.17 | 0.024 | 0.328 | 102.3 | 57.58 | 91.96 | 69.72 | 69.62 | 69.48 | 51.71 | 1701 | FAIL (1): S5 |
| optimizer best, raw floats | 1.200 | 36.26 | 0.028 | 0.062 | 106.1 | 70.01 | 107.1 | 74.50 | 74.46 | 74.44 | 49.94 | 912 | PASS |
| … rounded to a 10 nm device grid | 1.200 | 36.28 | 0.028 | 0.059 | 106.1 | 69.95 | **201.3** | 74.57 | 74.53 | 74.48 | 49.95 | 912 | FAIL (1): S7 |
| **design of record** — rounded, `c_ff_w` off the cliff | 1.200 | **36.28** | 0.028 | 0.059 | 106.1 | 69.95 | 104.8 | 72.42 | 72.38 | 72.31 | 49.95 | 836 | **PASS** |
| spec box | [1.176, 1.224] | ≤ 50 | ≤ 5 | ≤ 2 | ≤ 200 | ≥ 40 | ≤ 150 | ≥ 60 | ≥ 60 | ≥ 60 | — | — | |

The design of record is the `sizing.yaml` defaults, so a bare `lab.dut.CANDIDATE` renders it; it is certified into `decks/candidate/` with `SHA256SUMS` (13/13 benches ok, 0 violations). Against the reference it is what the challenge asked for: **the same regulation and PSRR class at 4.8 % of the quiescent current** (36.3 µA against 758.7), with load regulation 45× better, line regulation 73× better, PSRR 25 dB better and phase margin 26° better — at 1.5 V into an on-chip 21 pF instead of 3.3 V into 1 µF.

## 2. What rounding costs, and why the optimizer's winner is not the design

The optimizer returns floats (`c_ff_w = 9.415138 µm`). A layout snaps to a 5 nm grid and the schematic of record carries the same numbers, so the point that ships must be a rounded one. Rounding was measured, not assumed, and it broke S7 **twice**:

| point | v_undershoot_mv | t_transient_us | pm_loop_deg | what changed |
|---|---|---|---|---|
| raw floats | 107.1 | 0.188 | 74.50 | — |
| rounded on a **50 nm** device grid | 247.6 | 0.319 | 74.52 | `x_dut_xmp_l` 0.13 → 0.15 µm |
| rounded on a **10 nm** device grid | 201.3 | 0.374 | 74.57 | `c_ff_w` 9.415 → 9.5 µm |
| **record** (10 nm grid, `c_ff_w` = 8 µm) | 104.8 | 0.125 | 72.42 | — |

The first is a rule, not a surprise: a 50 nm grid cannot express the PDK's minimum length, so it rounded the pass device *off* minimum-L and gave back 15 % of its transconductance. The second is the interesting one. A one-knob-at-a-time revert (17 builds, one bench each) put the whole 107 → 201 mV step on `c_ff_w` alone; sweeping it shows a **cliff between 9.4 and 9.5 µm** — a 0.9 % change of the MIM side:

| c_ff_w | 3u | 4u | 5u | 6u | 7u | **8u** | 8.5u | 9u | 9.2u | **9.4u** | **9.5u** | 10u | 11u | 12u |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v_undershoot_mv | 112.2 | 96.8 | 98.9 | 101.0 | 103.1 | **104.9** | 105.7 | 106.4 | 106.7 | **107.0** | **201.3** | 225.3 | 221.9 | 252.6 |
| t_transient_us | 0.397 | 0.281 | 0.141 | 0.124 | 0.107 | **0.125** | 0.137 | 0.150 | 0.158 | 0.180 | 0.374 | 0.312 | 0.694 | 0.882 |
| pm_loop_deg | 62.1 | 63.8 | 65.8 | 68.0 | 70.3 | **72.4** | 73.3 | 74.1 | 74.3 | 74.5 | 74.6 | 74.8 | 74.1 | 72.2 |
| v_line_pp_mv | 397.7 | 326.7 | 220.5 | 70.6 | 53.0 | **51.6** | 50.9 | 50.7 | 50.7 | 50.6 | 50.6 | 50.4 | 50.0 | 49.6 |

Everything the optimizer scored is smooth and monotone through the cliff — phase margin, line-step deviation and Iq do not notice it at all — so **the optimizer had no way to see it and parked its winner 15 nm from the edge**. The record backs `c_ff_w` off to 8 µm: 19 % of margin for 2 mV of undershoot and 2.1° of phase margin. This is the generalizable lesson of the experiment (`doc/journal/optimizer-parks-on-cliffs.md`): an optimizer's answer is a *point*, and a point on a cliff is not a design — the deliverable is the point plus the local sweep that shows it is not on one.

## 3. Corners: what actually binds

The record over five MOS corners × −40/27/125 °C (`out/corners.md`, ledger `003_record_<corner>_<T>C`). Bold = out of box.

| corner | v_out_v | i_q_ua | load_reg_mv | line_reg_mv | v_dropout_mv | psrr_1k_db | v_undershoot_mv | pm_loop_deg | pm_loop_lo_deg | pm_loop_hi_deg | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tt −40 | 1.201 | 31.84 | 0.017 | 0.051 | 97.4 | 72.57 | 86.2 | 72.45 | 72.43 | 72.37 | PASS |
| tt 27 | 1.200 | 36.28 | 0.028 | 0.059 | 106.1 | 69.95 | 104.8 | 72.42 | 72.38 | 72.31 | PASS |
| tt 125 | 1.199 | 44.85 | 0.050 | 0.157 | 116.0 | 63.08 | 128.6 | 71.22 | 71.17 | 71.14 | PASS |
| ss −40 | 1.201 | 25.58 | 0.017 | 0.046 | 110.9 | 71.62 | **310.8** | 73.15 | 73.15 | 73.11 | FAIL (1): S7 |
| ss 27 | 1.201 | 29.05 | 0.029 | 0.048 | 121.5 | 69.38 | **254.6** | 73.36 | 73.33 | 73.22 | FAIL (1): S7 |
| ss 125 | 1.199 | 35.56 | 0.050 | 0.123 | 135.0 | 64.02 | 144.1 | 72.21 | 72.17 | 72.12 | PASS |
| ff −40 | 1.200 | 41.85 | 0.017 | 0.042 | 79.9 | 74.36 | 74.3 | 71.80 | 71.78 | 71.73 | PASS |
| ff 27 | 1.199 | 47.80 | 0.027 | 0.057 | 86.8 | 71.22 | 89.9 | 71.54 | 71.49 | 71.43 | PASS |
| ff 125 | 1.198 | **61.93** | 0.056 | 0.248 | 95.2 | 59.66 | 109.8 | 70.45 | 70.35 | 70.34 | FAIL (1): S5 |
| sf −40 | 1.201 | 31.96 | 0.017 | 0.045 | 89.2 | 72.54 | 87.6 | 72.50 | 72.47 | 72.42 | PASS |
| sf 27 | 1.200 | 36.27 | 0.027 | 0.056 | 95.9 | 70.21 | 106.3 | 72.38 | 72.34 | 72.24 | PASS |
| sf 125 | 1.199 | 45.35 | 0.047 | 0.140 | 105.6 | 63.84 | 130.8 | 71.06 | 71.00 | 70.98 | PASS |
| fs −40 | 1.201 | 31.67 | 0.017 | 0.042 | 103.5 | 73.04 | 84.5 | 72.53 | 72.50 | 72.39 | PASS |
| fs 27 | 1.200 | 36.21 | 0.028 | 0.058 | 114.3 | 70.11 | 103.0 | 72.55 | 72.51 | 72.46 | PASS |
| fs 125 | 1.198 | 44.69 | 0.053 | 0.186 | 126.3 | 61.79 | 125.9 | 71.51 | 71.46 | 71.43 | PASS |

**The binding spec is S5 at ff/125 and S7 at ss/−40, and they are one mechanism.** Read the `i_q_ua` column alone: 25.58 µA at ss/−40 to 61.93 µA at ff/125, a **2.4× spread** on a design whose nominal is 36.28. The bias is resistor-referenced — `I_ref = (VDD − Vgs(XMB0)) / R(r_bias_l)` with `rhigh` sheet resistance moving from `res_wcs` to `res_bcs` — so every branch current, including the FVF gate sink that sets the pass-gate pull-down slew, scales with the corner. At ff/125 there is 24 % too much of it and S5 fails; at ss/−40 there is 30 % too little, the gate slews proportionally slower, and S7 fails by 2×. The two failures therefore pull `r_bias_l` in **opposite directions**, which is why they are not a sizing problem: no static value of that knob passes both. Consistent with this, the specs that do not depend on bias magnitude — S1, S2, S3, S4, S6 and all three S8 columns — hold at every one of the 15 corners with margin (v_out 1.198–1.201 V, PM ≥ 70.3°).

The predicted failure (S8 at ss/−40) did not happen: phase margin is the *least* corner-sensitive line in the table, varying 70.3–73.4° over the whole grid. The 002 hand point had PM 59–62° and was the thing to protect; the optimizer bought 12° of it for free while cutting Iq, and that margin is what absorbs the corner spread.

**The named next increment is a PVT-stable bias** (constant-gm / beta-multiplier, or `zhang2023`'s bounded adaptive bias), not more sizing. That is a topology change and is out of this experiment's scope; the box is judged at tt/27 °C (`doc/target-spec.md`), where the record passes, and this table is the sign-off evidence that says exactly what a second increment has to fix.

## 4. How the optimizer was driven

`run_opt.py` builds the project YAML from `lab.dut.CANDIDATE` itself: decks are rendered with **no overrides**, so every knob is defined exactly once (its `sizing.yaml` `.param` default) and the optimizer's by-name `.param` rewrite hits the live line. 17 of the 31 knobs were searched, the rest frozen at their defaults; `seed_from_init` makes the 002 hand point trial 0, which is what makes the control row and the reported cut comparable. Budget 120 trials, NGOpt, 8 workers, ~9.7 s/trial, best score −0.2506 at trial 104.

- objective: `i(i_supply)` minimize, target 30 µA, log reward, weight 2
- constraints with margin against the box: `v(vout_dc)` 1.2 ± 20 mV, `load_reg` ≤ 4 mV, `line_reg` ≤ 1.5 mV, `v_dropout` ≤ 170 mV, `psrr_vdd_db` ≥ 43 dB, `v_undershoot` ≤ 120 mV (weight 1.5), and phase margin ≥ 63° on all three of `ac_loopgain`, `ac_loopgain_lo`, `ac_loopgain_hi`

The three loop benches all `print` the same `pm_loop` name and the optimizer keys specs by name, so each is read through the Tier-1 registry recipe `{meas: pm, out: tloop}` on the saved loop-gain wave; that recipe was validated against the deck's own `meas` on the smoke run before the full budget was spent.

## Lessons to graduate

- (`003_cffsweep_*`) An optimizer's winner can sit on a cliff that none of its own scored metrics can see: `c_ff_w` 9.4 → 9.5 µm takes S7 from 107 to 201 mV while phase margin, line step and Iq stay smooth. Ship the point **plus the local sweep**, and back every knob off the nearest edge. Journal: `doc/journal/optimizer-parks-on-cliffs.md`.
- (`003_rounded_tt_27` vs `003_record_tt_27`) Round the sizing to the grid the layout will draw, then **re-score** — rounding is a design change. A grid coarser than the PDK's minimum length silently moves a minimum-length device off minimum. Journal: `doc/journal/round-then-rescore.md`.
- (`003_record_*_*C`) When one corner fails a current spec and another fails a slew spec, look at the Iq column before the sizing: a resistor-referenced bias spreads every branch current by the sheet-resistance ratio, and no static knob value satisfies both ends. Journal: `doc/journal/resistor-bias-spread-binds-both-ends.md`.
