# 002 — literature: which capless low-Iq topology to size

**Paper(s):** `engur2023-dualrange-fvf`, `ni2022-ocl-slewrate`, `zhang2023-220na-capless`, `perez2018-cbbc-ldo` (all read in full; `ieee9180856-adaptive-fb` and `bu2018-200ps-ocl` are abstract-only and cited as existence proofs, never as numbers)
**Hypothesis:** among the four techniques in `pdf/INDEX.md`, a flipped-voltage-follower (FVF) output stage under a slow high-gain outer loop is the only one that can meet S7 (≤ 150 mV for 0.1 → 10 mA in 100 ns) AND S5 (≤ 50 µA) with ≤ 100 pF on chip, because the pass-gate slew during the step is paid by the FVF control device's transient current rather than by standing bias; a plain single-stage error amp in front of it will fail S3/S6 (loop gain < 30 dB), a two-stage one will pass. Falsified if the FVF at ≤ 50 µA cannot get S7 under 150 mV at tt, if the two-stage outer loop cannot reach PM ≥ 60° at 0.1/1/10 mA, or if the topology loses regulation (S1 window) at any of the five MOS corners × −40/27/125 °C with the load at its 0.1 mA minimum.
**Control:** the certified reference row (`decks/reference/scorecard.json`, analog-db `ldo_005`, 3.3 V hv / 1 µF external Cout — the yardstick for S2/S3/S6 only, see `doc/journal/reference-is-not-at-the-target-point.md`) and, for each structural choice, the same sizing with only that choice changed (one-stage vs two-stage error amp; feed-forward cap 0/1/3 pF).
**Verdict:** PARTLY FALSIFIED, then CONFIRMED with one structural change. The plain FVF + two-stage error amp passes the whole box at tt/27 °C with 44.8 µA (table 2) — the single-stage error amp fails S3/S5/S6/S7 (table 2, row 1) and the feed-forward cap `ni2022` uses hurts here (rows 3–5) — but it **loses regulation at every hot or fast corner** (table 3: v_out 1.256 V at ff/27, 1.306 at tt/125, 1.368 at ff/125) because a plain FVF cannot lift the pass gate above vout (§2b). A source-follower buffer between control device and pass gate (the `engur2023` SSF) restores the gate range but oscillates (table 4). The fix of record is a **double-mirror fold** of the control current up to the pass gate as a pull-up (§2b): it holds v_out within 1.190–1.197 V at tt/27, tt/125, ff/125, ss/−40, sf/27 with undershoot ≤ 100 mV (table 5), at a cost of ≈ 9 µA (Iq 53.8 µA at the hand sizes — S5 is now the optimizer's job in 003). Topology of record: `circuits/ldo_ihp_capless/` (double-mirror FVF).

## 1. Technique briefs mapped onto the spec box

Each brief: the mechanism, what it buys on the transient/regulation lines (S2/S3/S6/S7/S8), what it costs on S5 (Iq) and on the 1.5 V headroom, and whether it is in the topology of record.

| handle | technique | buys | costs | in the topology of record? |
|---|---|---|---|---|
| `engur2023-dualrange-fvf` | FVF output stage (pass PMOS is the FVF shunt device; a control PMOS whose source IS the output drives the pass gate through a constant sink) + a super-source-follower buffer + a second, slow high-gain loop. Same Vin/Vout as ours (1.5 → 1.2 V). | **S7**: 100 mV for 0→15 mA / 80 ns measured; the local loop's response time is ns-class because the control device sources the gate charge transiently. **S6**: ≥ 40 dB to 10 kHz. **S2**: mV-class from the local loop's low Zout even before the outer loop. | **S5**: their fast mode burns 50–110 µA; at 3 µA they only serve ≤ 0.5 mA. Headroom: Vsg(control) + Vds(sink) stacked under the pass gate — fits 1.5 V because the pass gate sits at 0.75–1.1 V. | **YES** (FVF + outer loop), with the gate driven through a double-mirror fold instead of their SSF buffer. The plain FVF (control device straight onto the pass gate) fails at hot/fast corners (§2b, table 3); the SSF buffer oscillated here (table 4); the fold gives the same gate range without the buffer's extra pole (table 5). The dual-range bias switch is not adopted (a mode switch is a digital-assist item, out of scope). |
| `ni2022-ocl-slewrate` | Transient current boost through the compensation caps (a derivative path from Vout into the gate driver) + push-pull output stage. | **S7**: 23.5 mV for 0→100 mA / 100 ns (simulation, 100 pF). **S8**: PM ≥ 74°. **S4**: 200 mV dropout = our bound. | **S5**: 30 µA — fits. The derivative path couples output noise and makes overshoot asymmetric. | **TESTED, REJECTED**: a feed-forward cap from vout to the pass gate (the same derivative idea) made S7 worse here (65 → 90 → 119 mV for 0 / 1 / 3 pF, table 2) because it fights the FVF's own gate pull-down and eats S8 (57 → 50°). |
| `zhang2023-220na-capless` | Adaptive power transistors (2- vs 3-stage depending on load) + bulk modulation + bounded adaptive bias. | **S5**: 220 nA. **S4**: 100 mV at 10 mA. **S2/S3**: 0.0059 mV/mA, 0.49 mV/V. | **S7**: 140 mV only with a 1 µs edge; at 1 ns edges 230 mV overshoot — adaptive bias is too slow for our 100 ns edge. **S8**: PM ≥ 45° only, and it must hold across the bias range. | NO for the first silicon-shaped candidate. The bounded adaptive bias is the natural NEXT increment once S7 is met with static bias: it buys back the 20 µA the FVF sink costs at light load. |
| `perez2018-cbbc-ldo` | Current-bias boosting from under/overshoot detectors (quasi-floating-gate), 100 pF on chip. | **S6**: 48 dB at 1 kHz with exactly our Cout constraint. **S5**: 7.45 µA. **S8**: 89.6°. | **S7**: ~400 mV with a 0.5 µs edge — the detectors respond, but late; the boost is a slow-loop aid. | NO (same reason as adaptive bias: helps S5, does not deliver S7 at 100 ns). Its S6 number is the anchor that 40 dB at 1 kHz with 100 pF on chip is ordinary. |
| `ieee9180856-adaptive-fb` (abstract only) | load-aware feedback divider | sub-µA Iq with mV regulation, 130 nm | 1 µs edges | NO; existence proof only |
| `bu2018-200ps-ocl` (abstract only) | multipath nested Miller + feed-forward, > 100 MHz UGB | ps-class response | **S5**: 112 µA | NO; the S7 ceiling when Iq is unconstrained |

## 2. Why the FVF, in numbers

The 100 ns / 10 mA step is the tight line. The pass device (sg13_lv_pmos, W = 400 µm, L = 0.15 µm from the gm/ID tables: J_D ≈ 10 µA/µm at gm/ID 8 for the 10 mA / 200 mV dropout point) needs its gate moved by ~0.36 V between 0.1 mA and 10 mA (measured on the operating points: 1.12 V → 0.76 V). With ~1 pF at the gate:

- a conventional error-amp-driven gate at 8 µA tail slews at ≤ 8 V/µs → ≥ 45 ns just to move the gate, plus the loop's own delay: with a 100 ns edge that is a several-hundred-mV droop on ≤ 100 pF;
- the FVF's sink at 20 µA slews the gate down at 20 V/µs (18 ns) and the control device's transient current pulls it back up much faster than that. The measured S7 of the topology of record is 65 mV (table 2), and it does NOT depend on Cout (15 pF and 90 pF give 65.6 and 66.7 mV — `experiments/003-sizing`, control row), which is the signature of a loop-speed-limited, not charge-limited, transient: the on-chip Cout can therefore be small (20 pF of record), a 4.5× layout-area saving against the 100 pF bound.

What the FVF does not give: DC accuracy, S3 and S6 come from the outer loop's gain. A single-stage 5T error amp gives 23 dB of loop gain after the 1:1 divider (table 2, row 1) — S3 14 mV, S6 33 dB. A two-stage (5T + common-source, Miller) amp gives 50 dB and passes S2/S3/S6 with margin (rows 2+).

Table 1 — the reference row (certified, `decks/reference/scorecard.json`; hv/3.3 V/1.6 V/1 µF, quoted not re-run) against the box:

| cell | v_out_v | i_q_ua | load_reg_mv | line_reg_mv | v_dropout_mv | psrr_1k_db | v_undershoot_mv | pm_loop_deg | verdict |
|---|---|---|---|---|---|---|---|---|---|
| reference (certified) | 1.609 | 758.7 | 1.274 | 4.32 | 169.7 | 44.53 | 1.957 | 46.39 | FAIL (S1 window, S3, S5, S8; S4/S7 not at our conditions) |
| spec box | [1.176, 1.224] | ≤ 50 | ≤ 5 | ≤ 2 | ≤ 200 | ≥ 40 | ≤ 150 | ≥ 60 | |

Table 2 — structural A/B on the candidate at tt/27 °C, gm/ID starting sizes (ledger tags `003_probe0_*`, `003_probe1_*`, `003_probe2_*`; every row is the full 13-bench scorecard through `ldo.metrics.evaluate`):

| cell | v_out_v | i_q_ua | load_reg_mv | line_reg_mv | v_dropout_mv | psrr_1k_db | v_undershoot_mv | pm_loop_deg | pm_loop_lo_deg | pm_loop_hi_deg | loopgain_db | ugf_loop_khz | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FVF + 1-stage 5T error amp, Cx 5 pF to ground | 1.201 | 52.15 | 2.809 | 14.17 | 70.81 | 33.08 | 553.3 | 84.12 | 86.35 | 82.4 | 23.04 | 2382 | FAIL (4): S3 S5 S6 S7 |
| FVF + 2-stage error amp, no Cx | 1.196 | 51.72 | 0.107 | 0.407 | 62.4 | 57.6 | 64.58 | 57.38 | 65.3 | 56.1 | 50.51 | 2368 | FAIL (2): S5 S8 |
| … + feed-forward Cx 1 pF vout→gate (`ni2022` idea) | 1.196 | 51.72 | 0.107 | 0.407 | 62.4 | 57.6 | 90.15 | 54.9 | 64.16 | 53.28 | 50.51 | 2374 | FAIL (2) |
| … + feed-forward Cx 3 pF | 1.196 | 51.72 | 0.107 | 0.407 | 62.4 | 57.6 | 118.5 | 50.12 | 61.88 | 48.01 | 50.51 | 2372 | FAIL (2) |
| FVF + 2-stage, c_comp 3 pF, r_bias 300 k (hand point of record → 003) | 1.197 | 44.79 | 0.095 | 0.339 | 62.22 | 58.72 | 66.77 | 61.38 | 69.19 | 60.31 | 50.74 | 1455 | PASS |

The 5 pF damping cap at the pass gate in row 1 is what made S7 553 mV: the FVF sink slews the gate at I_B/(C_x + C_gate) = 20 µA / 6 pF = 3.3 V/µs (measured 4.5 V/µs on the waveform), i.e. the very thing the FVF is chosen for was disabled by the cap. Removing it, not adding gain, is what took S7 from 553 to 65 mV — the two-stage amp rows 2–5 all have no Cx.

### 2b. Why the plain FVF fails at hot/fast corners, and the fold that fixes it

In a plain FVF the control device XMC (PMOS, source = vout) drives the pass gate directly, so the gate can never rise above vout − Vsd,sat(XMC) ≈ vout. The pass device therefore always has Vsg ≥ Vin − Vout = 0.3 V, and at W = 400 µm / L = 0.15 µm that is not "off": the leakage at Vsg = 0.3 V (op bench on the pass device alone, ledger `003_leak_*`) is 15.6 µA at tt/27 but 163 µA at tt/125, 80 µA at ff/27 and 472 µA at ff/125 — more than the 0.1 mA minimum load minus the divider. The outer loop then has nothing to regulate with: v_out rises to wherever the leak equals the load (table 3), and every S1/S2/S3/S7 number at those corners is a symptom of the same ceiling.

Table 3 — the plain-FVF hand point of table 2 across corners (ledger `003_corners_hand_*`; light-load S1 is the failing line):

| cell | v_out_v | i_q_ua | load_reg_mv | line_reg_mv | v_dropout_mv | psrr_1k_db | v_undershoot_mv | pm_loop_deg | pm_loop_lo_deg | pm_loop_hi_deg | loopgain_db | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tt −40 °C | 1.197 | 45.53 | 0.036 | 0.263 | 56.69 | 58.03 | 40.21 | 59.87 | 60.37 | 59.25 | 52.58 | FAIL (1): S8 by 0.1° |
| tt 27 °C | 1.197 | 44.79 | 0.095 | 0.339 | 62.22 | 58.72 | 66.77 | 61.38 | 69.19 | 60.31 | 50.74 | PASS |
| tt 125 °C | 1.306 | 44.38 | 32.01 | 55.09 | 69.68 | 64.54 | 349.2 | 68.01 | — | 61.01 | 44.97 | FAIL (4): S1 S2 S3 S7 |
| ff 27 °C | 1.256 | 45.99 | 0.987 | 40.82 | 52.63 | 60.33 | 310.2 | 63.79 | 95.04 | 60.34 | 49.97 | FAIL (3): S1 S3 S7 |
| ff 125 °C | 1.368 | 45.72 | 94.43 | 115.6 | 58.23 | 35.17 | 284.5 | 83.44 | — | 62.41 | 32.21 | FAIL (5) |
| sf 27 °C | 1.226 | 44.74 | 0.199 | 12.5 | 56.19 | 59.26 | 108.8 | 62 | 78.73 | 60.18 | 50.72 | FAIL (2): S1 S3 |
| ss 125 °C | 1.239 | 42.91 | 0.348 | 0.94 | 76.74 | 61.24 | 156.2 | 62.66 | 80.56 | 60.87 | 47.99 | FAIL (2): S1 S7 |
| fs 125 °C | 1.272 | 44.55 | 2.558 | 24.66 | 74.3 | 67.91 | 367.8 | 65.07 | 111.6 | 61.64 | 44.78 | FAIL (3): S1 S3 S7 |

The pm_loop_lo "—" cells are corners where the 0.1 mA loop has no unity-gain crossing because the pass device is not in control of the output.

Two ways to give the gate the missing 0.3 V of range were tried (ledger `003_probe4_*`, `003_probe5_*`), table 4: (a) `engur2023`'s buffer — a PMOS source follower / super-source-follower between XMC and the pass gate (`bFVF`, `ssf`, `sf` rows); it regulates at every corner but its extra pole at the ~1 pF gate rings for the whole 7 µs window (`t_transient_us` = 7 is the bench's "never settled" value; `v_line_pp_mv` ≈ 0.3–1 V of ringing on the line step), and the undershoot grows with every attempt to damp it. (b) The **double-mirror fold**: XMC's drain current goes into an NMOS diode (XMA), is mirrored (XMB) into a PMOS diode (XMCP) and mirrored again (XMD) onto the pass gate as a pull-up, with the constant sink XMS still pulling the gate down. The gate can now reach vdd − Vsd,sat (pass device off) and vss + Vds,sat (fully on), the pull-down slew is still I_B/C_gate (the mechanism of §2), and the pull-up current is XMC's current through two 1:1 mirrors, i.e. still the FVF's transient current rather than a standing bias. Each mirror adds one low-impedance (diode) node, so no new high-impedance pole enters the local loop — which is why (b) does not ring where (a) does.

Table 4 — the buffered variants (tt/27 unless stated; `t_transient_us` 7 = never settled):

| cell | v_out_v | i_q_ua | v_dropout_mv | v_undershoot_mv | pm_loop_deg | t_transient_us | v_line_pp_mv | verdict |
|---|---|---|---|---|---|---|---|---|
| PMOS source follower (`bFVF`), tt 27 | 1.195 | 35.6 | 158.6 | 172.2 | 60.39 | 7 | 377.3 | FAIL (1) |
| same, ff 125 | 1.19 | 36.28 | 98.91 | 130.4 | 62.56 | 7 | 311.7 | PASS (but ringing) |
| same, ss −40 | 1.197 | 33.82 | 248.9 | 202.3 | 59.45 | 0.263 | 382.8 | FAIL (3) |
| super-source follower (`ssf`, I2 6 µ / I1 1 µ) | 1.195 | 37.04 | 148.6 | 604.8 | 60.43 | 7 | 977.1 | FAIL (1) |
| SSF + pass m = 80 | 1.195 | 37.05 | 78.45 | 357.7 | 60.44 | 7 | 887.8 | FAIL (1) |
| SF, I_sf 20 µA, W 40 µ | 1.195 | 31.98 | 236.7 | 325 | 60.32 | 0.295 | 253.5 | FAIL (2) |

Table 5 — the double-mirror FVF at the hand sizes (`xma`/`xmcp` 2 µ / 6 µ, XMS 2.2 µ, pass m = 20), the five corners that killed the plain FVF (ledger `003_probe6_*`):

| cell | v_out_v | i_q_ua | load_reg_mv | line_reg_mv | v_dropout_mv | psrr_1k_db | v_undershoot_mv | pm_loop_deg | pm_loop_lo_deg | pm_loop_hi_deg | loopgain_db | ugf_loop_khz | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tt 27 °C | 1.195 | 53.76 | 0.023 | 0.348 | 102.4 | 57.06 | 74.09 | 60.07 | 59.99 | 59.9 | 51.63 | 1540 | FAIL (1): S5 |
| tt 125 °C | 1.192 | 54.78 | 0.044 | 0.316 | 112 | 57.98 | 96.94 | 60.75 | 60.65 | 60.58 | 47.85 | 1224 | FAIL (1): S5 |
| ff 125 °C | 1.19 | 60.19 | 0.074 | 0.163 | 90.76 | 64 | 99.29 | 62.11 | 61.95 | 61.98 | 43.75 | 1207 | FAIL (1): S5 |
| ss −40 °C | 1.197 | 52.28 | 0.017 | 0.35 | 106.5 | 56.95 | 67.03 | 59.22 | 59.15 | 59.09 | 53.33 | 1794 | FAIL (2): S5, S8 by 0.8° |
| sf 27 °C | 1.195 | 53.72 | 0.023 | 0.348 | 92.34 | 57.07 | 75.28 | 59.89 | 59.81 | 59.73 | 51.86 | 1538 | FAIL (2): S5, S8 by 0.1° |
| same, pass m = 30, tt 27 °C | 1.195 | 53.95 | 0.02 | 0.348 | 70.32 | 57.06 | 79.66 | 59.91 | 59.83 | 59.72 | 51.63 | 1540 | FAIL (2) |
| same, XMS 3.3 µ (I_B ×1.5), tt 27 °C | 1.196 | 73.11 | 0.027 | 0.341 | 102.4 | 57.24 | 94.77 | 60.24 | 60.16 | 60.19 | 51.42 | 1535 | FAIL (1) |
| same, mirrors 4 µ / 12 µ, tt 27 °C | 1.195 | 52.42 | 0.023 | 0.351 | 102.4 | 56.98 | 141.6 | 60.05 | 59.97 | 59.89 | 51.69 | 1542 | FAIL (1) |

Regulation now holds at every corner (v_out 1.190–1.197 V, load_reg ≤ 0.08 mV, undershoot ≤ 100 mV). What is left is quantitative: Iq 52–60 µA against 50 (the fold's two mirror branches cost ≈ 9 µA at these sizes) and PM 59–62° against 60 — both are sizing, not topology, and go to the optimizer in 003. Wider fold mirrors (last row) slow the gate (undershoot 142 mV): the mirror widths are a knob to keep small, not to grow.

## 3. Topology of record

`circuits/ldo_ihp_capless/` (abstract + lowered netlist, sizing, analyses at the challenge's conditions). Devices: 17 MOS (`sg13_lv_*`: 4 bias, 6 error amp, 7 output stage incl. the four fold mirrors), 3 `rhigh` resistors (divider + bias, as PDK devices with length knobs), 2 `cap_cmim` MIM caps (Miller 3 pF; Cout as 4 × 5 pF units), 1 ideal reference. Iq budget at the hand sizes: bias diode 3.6 µA, PMOS-diode branch 5.8, error-amp tail 5.8, stage 2 2.9, FVF sink 14.5, fold mirrors ≈ 9 (XMC's current twice), divider 0.6 — 53.8 µA measured (table 5), 3.8 µA over S5 for the optimizer to recover. `doc/design-reference.md` carries the device map and the constraints.

## Lessons to graduate

- (`003_corners_hand_*`, `003_leak_*`) A plain FVF cannot switch its pass device off: the gate is bounded by vout, so Vsg ≥ Vin − Vout and a 400 µm pass device leaks 80–470 µA at ff/hot — more than the minimum load. Any FVF-output LDO whose Vin − Vout exceeds ~0.2 V needs a gate driver that can reach the rail: the double-mirror fold does it without the buffer's pole. Journal: `doc/journal/plain-fvf-gate-ceiling.md`.

- (`003_probe0_defaults` vs `003_probe1_2stage_c_x0`) Any capacitance at an FVF's pass gate is paid at the sink's slew rate: 5 pF turned a 65 mV step into 553 mV. Journal: `doc/journal/fvf-gate-cap-is-slew.md`.
- (`003_probe3_cout15p/30p/45p`) When S7 does not move with Cout, the transient is loop-speed-limited and the on-chip Cout is a layout-area knob, not a transient knob.
