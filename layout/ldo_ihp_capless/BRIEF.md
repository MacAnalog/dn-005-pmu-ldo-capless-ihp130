# Layout brief — `ldo_ihp_capless`

**KIND: REFERENCE.** Measured parasitic, matching, leakage and current-density budgets for the
capless FVF LDO, handed from the schematic side to layout. Every number below came out of the
**frozen candidate benches** (`decks/candidate/*.spice`, sha-locked) with one perturbation
spliced into the DUT subckt and all 13 benches re-run through `ldo.metrics.run_decks`. Nothing
here is a rule of thumb; where a quantity could not be measured it says so.

| | |
|---|---|
| cell | `ldo_ihp_capless` |
| netlist of record | `circuits/ldo_ihp_capless/pdk/ihp-sg13g2/netlist.spice` |
| netlist sha256 | `f5c4efb02afe023e931d02ceda9b9916712409b28c9125f165dcafb396a42080` |
| sizing / scorecard | `decks/candidate/design.json`, `decks/candidate/scorecard.json` |
| benches | the 13 frozen decks in `decks/candidate/`, `SHA256SUMS`-locked |
| corner | `mos_tt` / `res_typ` / `cap_typ`, 27 degC — **every budget below is tt/27** |
| margin fraction | **25%** of the remaining pre-layout margin per spec |
| campaign | 261 perturbed scorecards (13 benches each), ledger tags `brief2_*`, `LDO_EXP=006` |
| numeric floor | an identity splice reproduces the certified scorecard **to every printed digit**; the null control (a 1 uOhm series R + a zero-value C + a 0 V dVT source + the split Cout array) moves nothing by more than **0.001 mV** of S7 and **0.00005 uA** of Iq |

## 0. What changed since the 005 brief, and why

**This brief supersedes the one written on the pre-`bf3a4f8` row.** That row's device set was
not the one the layout draws; commit bf3a4f8 replaced it with the drawn set (half-width `…A`/`…B`
bias and error-amp cards, `XR1_1..8` / `XR2_1..8` / `XRB_1..5` segment strings, `XMP` as
`x_dut_xmp_nf_mult` = 4 × 19 = 76 fingers of 2.5 um). Every budget in the superseded brief was
25 % of a margin measured on the old scorecard, so all of them were re-derived here.

| item | 005 row (superseded) | this row (bf3a4f8) | why it moved |
|---|---|---|---|
| scorecard | Iq 36.2771 uA, Vout 1.200072 V, S7 104.847 mV, S4 106.143 mV, PM 72.4188 deg | Iq 33.8054 uA, Vout 1.199499 V, S7 115.057 mV, S4 104.671 mV, PM 72.5064 deg | commit bf3a4f8 made the certified deck the drawn device set: half-width A/B bias and EA cards, 8/8/5-segment resistor strings, XMP as 76 fingers. The independent reviewer attributed the shift device group by device group (REVIEW F19): the bias halving alone is -2.24 uA of Iq and +6.09 mV of S7 |
| S7 margin | 45.15 mV (quarter 11.3) | 34.943 mV (quarter 8.736) | the undershoot baseline moved 104.847 -> 115.057 mV; every S7-bound budget shrinks with it |
| S5 margin | 13.72 uA (quarter 3.43) | 16.195 uA (quarter 4.049) | Iq fell 2.47 uA, so the quiescent-current budgets got LOOSER |
| `gate` capacitance | 29.3 fF budget, hard step at 60-65 fF | **12 fF**, hard step at 12-13 fF | both the margin and the MECHANISM moved. The linear slope rose 0.386 -> +0.507 mV/fF, but the step that was 4.6x outside the linear budget is now INSIDE it: the linear budget would be 17.2 fF and the step arrives at 13 fF |
| `gate` to `vout` (the escape route) | 100 fF, explicitly NOT bracketed | **40 fF**, bracketed (40 fF in box, 45 fF out) | the 005 brief could only say 'in box at 100 fF, out at 300'; it is now measured to 5 fF |
| `fb` capacitance | 27.9 fF (S8hi) | 27.1 fF (S8hi) | coefficient -0.115 deg/fF against -0.111; the PM margin barely moved |
| `x1` capacitance | 46.1 fF, no step known | **28.3 fF**, step at 30-40 fF | the same S7 step, one mirror node away from the gate; never bracketed on the 005 row |
| `y` capacitance | 62 fF, no step known | **39.4 fF**, step at 50-60 fF | as `x1` |
| `fb` to `lp_brk` (parallel with XCFF) | not a listed constraint | **6 fF**, step at 6-8 fF | 10 fF across XCFF was benign on the 005 row; on this row 8 fF crosses the S7 step. The same limit read as a capacitor tolerance is XCFF +6 % in box, +8 % out |
| `vdd` series R | 1.77 Ohm (13.24 mV/Ohm) | 2.31 Ohm (10.34 mV/Ohm) | the dropout coefficient is now I*R to three digits (10.0 mA through the rail); the 005 row's 13.24 mV/Ohm was read off a single point against the unsplit baseline, which carries the offset a node split adds |
| `vout` series R, sense at the pin | 2.35 Ohm | 2.76 Ohm (8.64 mV/Ohm) | same re-measurement |
| `vout` series R, sense at the pass drain | 0.126 Ohm | 0.126 Ohm | unchanged -- it is dI x R and the load step did not move |
| `vss` return R | 17 Ohm (PSRR, -0.4413 dB/Ohm) | **11 Ohm** (S7, step at 11-12 Ohm) | two corrections. The 005 injection moved a HAND LIST of vss instances that omitted XMA/XMB/XMS -- 13 of the ~34 uA -- so it measured a partial return; and the binding mechanism is not PSRR but the S7 step. PSRR at 32 Ohm is 62.0 dB, still in box; S7 there is 218.1 mV, out of it. The step is SHARED-IMPEDANCE: with XCOUT's return separated it disappears (section 4a) |
| `vss` return R, XCOUT returned separately | not measured | **16.5 Ohm** (S6, -0.4553 dB/Ohm) | new: splitting the injection shows the S7 cliff needs XCOUT and the active devices behind the SAME R. Kelvin-return the cap and the cliff is gone; what is left is a soft PSRR cost |
| `ea_o1` / `ea_out` capacitance | ~630 fF (S8lo) | no bound below 500 fF | unchanged in substance: both are still hundreds of fF and still improve S7 |
| `ea_n` capacitance | 980 fF | 91 fF (S8hi) | the 005 number came from a 10 fF point whose binding metric sat on the bench floor |
| `ea_nmos_load` matching | 3.46 mV tolerated, 2.10 sigma, out of box first at 20 mV | **1 mV**, **0.61 sigma**, step at 2 mV | the 005 row probed the XM4 (output-leg) side, which is the safe sign. The XM3 (diode) side crosses the S7 step at 2 mV of dVT. Random mismatch is symmetric, so half the distribution sees the dangerous sign |
| `bias_p_group` matching | 12.4 mV linear / step at 8 mV, 7.16 sigma | **1.2 mV**, **1.07 sigma**, step at 1.5 mV | the bias-current step review F16 predicted would move: the recertified bias branch sits much closer to it. dW on XMT steps at 3 % (2 % in box) |
| `bias_n_group` matching | 8.92 mV, 3.15 sigma, interdigitated | 5 mV, 2.06 sigma, step at 6 mV | the 005 sigma used XMB0's 1/1 um twice; the class is XMB0 (1/1) against XMS (2.2/0.95), so the pair sigma is 2.43 mV, not 2.83 |
| `fb_divider` matching | 1.00 % of single-arm dR/R, 1.71 sigma | 0.989 %, 1.72 sigma | unchanged. sigma re-measured on the SEGMENTED string the deck now draws (0.2873 % of ratio) against the monolithic arms (0.2909 %): segmentation does not change the random part |
| `XCFF` tolerance | 166 % (linear only) | **6 %**, out of box at 8 % | same S7 step, reached as a capacitor tolerance |
| `XRB` tolerance | 20.2 % | **6 %**, out of box at 10 % | same S7 step |
| pass-array current density | 1.05 mA per shared Metal1 column, 2.9x over minimum width; 'not a layout knob, needs a re-sizing campaign' | 0.263 mA per shared column, 0.73x | the recertified pass device IS 76 fingers of 2.5 um, so the shared-column current fell by 4x and a minimum-width Metal1 riser now passes. The whole 'raise nf / Metal2 plate or re-certify' argument of the 005 section 8 is void |

Two things about that table are worth reading twice. First, **most budgets did not move because
the margin moved; they moved because the mechanism did.** The S7 margin shrank by 23 %
(45.15 → 34.94 mV), but the `gate` budget shrank by
59 % — because the load-step undershoot on this row crosses a
slew cliff at 13 fF, where on the old row the same cliff was at 65 fF. Second,
the same cliff is what now binds `x1`, `y`, the `fb`↔`lp_brk` coupling, the `vss` return,
`XCFF`, `XRB` and three of the seven matching classes. **This cell has one failure mode, and
almost every budget in this brief is a distance to it.**

## 1. The margins the budgets are spent out of

| spec | key | bound | measured (tt/27) | margin left | 25 % of margin | bench resolution |
|---|---|---|---|---|---|---|
| S1 | v_out_v | [1.176, 1.224] | 1.199499 | 0.0235 | 0.00587 | 2e-06 |
| S2 | load_reg_mv | <= 5.0 | 0.026 | 4.974 | 1.24 | 0.001 |
| S3 | line_reg_mv | <= 2.0 | 0.056 | 1.944 | 0.486 | 0.03 |
| S4 | v_dropout_mv | <= 200.0 | 104.671 | 95.33 | 23.8 | 2 |
| S5 | i_q_ua | <= 50.0 | 33.80539 | 16.19 | 4.05 | 0.001 |
| S6 | psrr_1k_db | >= 40.0 | 70.00703 | 30.01 | 7.5 | 0.001 |
| S7 | v_undershoot_mv | <= 150.0 | 115.057 | 34.94 | 8.74 | 0.005 |
| S8 | pm_loop_deg | >= 60.0 | 72.5064 | 12.51 | 3.13 | 0.03 |
| S8lo | pm_loop_lo_deg | >= 60.0 | 72.47302 | 12.47 | 3.12 | 0.03 |
| S8hi | pm_loop_hi_deg | >= 60.0 | 72.41834 | 12.42 | 3.1 | 0.03 |

`v_dropout_mv` is quantised by its own bench (the dropout deck sweeps Vdd in 2 mV steps).
`line_reg_mv`'s 0.03 mV floor is measured, not assumed: it is the largest |delta| any of the
102 **pure-capacitor** cases produces, and a capacitor
cannot move a DC sweep. The rest are the null control's residual floored by the deck's print
precision; the S7 floor is carried over from the 005 brief at 0.005 mV although this row's null
control only reaches 0.001 mV, so the S7 budgets here are if anything conservative. A delta
smaller than the resolution is reported as "no bound", never as zero.

## 2. Net capacitance — budgets, ranked

Unit injection: `C <net> vss` at 1 fF and 10 fF, all 13 benches each, plus a dense sweep on
every net that shows a step. The coefficient quoted is the **1 fF** one — the smallest injection
that clears the bench floor, which is what prices a wire haul. "budget" is the smaller of
(25 % of the binding margin at that slope) and (the last measured point before a step).

| net | role | dS7 mV/fF | dS8 deg/fF | dS6 dB/fF | binds | budget (fF) | hard limit | on the 2nd drawing (fF) | 1 fF / 10 fF |
|---|---|---|---|---|---|---|---|---|---|
| `gate` | FVF fold output -> pass-device gate; pull-down-slew-limited | 0.507 | - | - | S7 | 12 | **step between 12 and 13 fF** | 34.5 | 1.02 |
| `fb` | divider mid-point, error-amp inverting input | -0.243 | -0.115 | - | S8hi | 27.1 | - | 24.05 | 0.999 |
| `x1` | FVF control drain / NMOS fold diode (XMA) | 0.309 | - | - | S7 | 28.3 | **step between 30 and 40 fF** | 11.28 | 1.02 |
| `y` | NMOS fold drain / PMOS fold diode (XMCP) | 0.222 | - | - | S7 | 39.4 | **step between 50 and 60 fF** | 11.5 | 1.02 |
| `ea_n` | error-amp NMOS mirror diode (XM3) | -0.105 | - | - | S8hi | 90.7 | - | 17.72 | - |
| `ea_tail` | error-amp tail node (XMT drain) | 0.0014 | - | - | S7 | 6.24e+03 | - | - | - |
| `pbias` | PMOS bias diode node | 0.001 | - | - | S7 | 8.74e+03 | - | - | - |
| `ea_o1` | error-amp stage-1 output, Miller dominant pole | -0.323 | - | - | - | no bound | - | 64.91 | - |
| `ea_out` | error-amp stage-2 output = FVF control gate | -0.323 | - | - | - | no bound | - | 26.44 | - |
| `lp_brk` | loop-break marker; divider top = vout sense | -0.0003 | - | - | - | no bound | - | - | - |
| `nbias` | NMOS bias diode node | -0.008 | - | - | - | no bound | - | - | - |
| `vout` | output pin / pass drain / FVF source / Cout | -0.00031 | - | - | - | no bound | - | 82.67 | - |
| `vdd` | supply pin | - | - | - | - | no bound | - | 159.2 | - |

**The "on the 2nd drawing" column mixes two accountings, deliberately** (this is review finding
F10 restated, not resolved): for `gate` and `fb` it is the reviewer's *to-rail* number, directly
comparable with the budget beside it; for `ea_o1`, `ea_out`, `ea_n`, `x1`, `y`, `vout` and the
rails it is the extraction's raw **total coupled capacitance**, which is an upper bound on the
to-rail part and in some cases a loose one — section 3 note 4 shows the `ea_o1` figure is mostly
mutual capacitance to its own neighbours, which does not spend this budget. Compare only the two
to-rail rows against their budgets without re-deriving the split.

The "1 fF / 10 fF" column is the linearity check and is blank where the 1 fF point does not
resolve. **Read a budget above ~1 pF as "no bound"**: `ea_tail` and `pbias` clear the S7 floor
by a hair and the arithmetic produces a 6-9 pF "budget", which is not a constraint.

**The pass gate is the whole brief.** `gate` rises +0.507 mV of undershoot per
fF to a rail, and at **13 fF the mechanism changes**: S7 goes
120.970 → **178.522 mV** between 12 and 13 fF, with
the recovery time stepping 0.241 →
0.625 us. That is the FVF's pull-down losing the gate
inside the load step — not a degradation of a slope, a different circuit. The sweep:

| C to rail (fF) | S7 (mV) | recovery t (us) | S8 (deg) | box |
|---|---|---|---|---|
| 1 | 115.564 | 0.159 | 72.5062 | in box |
| 2 | 116.068 | 0.161 | 72.5061 | in box |
| 3 | 116.57 | 0.164 | 72.506 | in box |
| 4 | 117.069 | 0.167 | 72.5058 | in box |
| 5 | 117.565 | 0.17 | 72.5057 | in box |
| 6 | 118.059 | 0.174 | 72.5055 | in box |
| 7 | 118.55 | 0.179 | 72.5054 | in box |
| 8 | 119.039 | 0.184 | 72.5053 | in box |
| 9 | 119.526 | 0.191 | 72.5051 | in box |
| 10 | 120.009 | 0.2 | 72.505 | in box |
| 11 | 120.491 | 0.214 | 72.5048 | in box |
| 12 | 120.97 | 0.241 | 72.5047 | in box |
| 13 | 178.522 | 0.625 | 72.5046 | **OUT: S7** |
| 15 | 195.312 | 0.592 | 72.5043 | **OUT: S7** |
| 20 | 204.182 | 0.575 | 72.5036 | **OUT: S7** |
| 25 | 211.315 | 0.567 | 72.5029 | **OUT: S7** |
| 30 | 208.069 | 0.562 | 72.5022 | **OUT: S7** |
| 35 | 201.691 | 0.559 | 72.5015 | **OUT: S7** |
| 40 | 202.062 | 0.556 | 72.5007 | **OUT: S7** |
| 50 | 218.363 | 0.552 | 72.4993 | **OUT: S7** |
| 60 | 231.285 | 0.55 | 72.4979 | **OUT: S7** |
| 100 | 249.279 | 0.547 | 72.4923 | **OUT: S7** |

**The second drawing spends 34.5 fF of to-rail capacitance on this net** (the reviewer's own
kpex number, REVIEW F10), i.e. **2.9× the budget and past the step**; the
gate-only what-if in section 3b puts that cell at 201.7 mV. The escape route
is section 3.

`x1` and `y` are the fold mirror nodes and carry the same step one and two nodes back
(30-40 fF and 50-60 fF). `fb` has no step: it binds phase margin linearly at
-0.115 deg/fF, and it *improves* S7 (-0.243 mV/fF) — do not bank
that, S8hi runs out first.

## 3. Which rail (or neighbour) a track couples to

| injection | C (fF) | S7 (mV) | S8 (deg) | S6 (dB) | box | what it says |
|---|---|---|---|---|---|---|
| `c_gate_vss_5f` | 5 | 117.565 | 72.5057 | 70.007 | in box | to-rail, below the step |
| `c_gate_vss_10f` | 10 | 120.009 | 72.505 | 70.007 | in box | to-rail, the last decade point below the step |
| `c_gate_vdd_10f` | 10 | 120.009 | 72.505 | 70.007 | in box | vdd and vss are the same AC ground |
| `c_gate_vdd_30f` | 30 | 208.069 | 72.5022 | 70.007 | **OUT** | identical to `c_gate_vss_30f` to 6 digits -- past the step either way |
| `c_gate_vout_10f` | 10 | 115.254 | 72.4874 | 70.007 | in box | bootstrapped: the gate rides its own source |
| `c_gate_vout_20f` | 20 | 115.431 | 72.4684 | 70.007 | in box |  |
| `c_gate_vout_30f` | 30 | 115.592 | 72.4494 | 70.007 | in box | last in-box point of the escape route |
| `c_gate_vout_35f` | 35 | 115.667 | 72.4399 | 70.007 | in box |  |
| `c_gate_vout_40f` | 40 | 115.738 | 72.4304 | 70.007 | in box |  |
| `c_gate_vout_45f` | 45 | 180.135 | 72.4209 | 70.007 | **OUT** |  |
| `c_gate_vout_50f` | 50 | 189.86 | 72.4114 | 70.007 | **OUT** |  |
| `c_gate_vout_100f` | 100 | 202.937 | 72.3165 | 70.0069 | **OUT** |  |
| `c_gate_vout_200f` | 200 | 207.481 | 72.1268 | 70.0068 | **OUT** |  |
| `c_gate_vout_300f` | 300 | 210.595 | 71.9373 | 70.0066 | **OUT** |  |
| `c_gate_vout_500f` | 500 | 214.809 | 71.5592 | 70.0064 | **OUT** |  |
| `c_fb_lp_brk_2f` | 2 | 115.244 | 72.6732 | 70.007 | in box | across XCFF: +2 % of the 0.1 pF feedforward cap |
| `c_fb_lp_brk_4f` | 4 | 115.427 | 72.8354 | 70.0071 | in box |  |
| `c_fb_lp_brk_6f` | 6 | 115.606 | 72.993 | 70.0071 | in box |  |
| `c_fb_lp_brk_8f` | 8 | 194.076 | 73.1459 | 70.0071 | **OUT** |  |
| `c_fb_lp_brk_10f` | 10 | 197.481 | 73.294 | 70.0071 | **OUT** |  |
| `c_fb_vss_10f` | 10 | 112.859 | 71.3695 | 70.0071 | in box | the divider-node pole XCFF cancels |
| `c_fb_vdd_10f` | 10 | 112.859 | 71.3695 | 71.3331 | in box | same S8; PSRR moves the other way |
| `c_fb_vref_10f` | 10 | 112.825 | 71.3695 | 70.0071 | in box | one-sided across the input pair |
| `c_fbvref_bal_10f` | 10 | 112.859 | 71.3695 | 70.0071 | in box | balanced (10 fF on each half) |
| `c_ea_o1_ea_out_30f` | 30 | 115.06 | 72.506 | 69.9689 | in box | adds to XCC: Miller, not a load |
| `c_ea_o1_vss_50f` | 50 | 106.078 | 72.2614 | 69.9935 | in box | S7 *improves*: see note 4 |

Four results the designer can act on:

1. **`gate` to `vout` is the escape route, and it is now bracketed.** The pass gate is
   bootstrapped to its own source during the load step, so coupling to `vout` costs
   +0.0197 mV/fF against
   +0.507 mV/fF to a rail — **26× cheaper** —
   and it carries the same step at **40-45 fF**
   (115.738 → 180.135 mV).
   **Route the gate track over or beside the `vout` bus, not in the rail channel, and treat
   40 fF as the hard limit there.** The 005 brief quoted 100 fF and said in terms that it
   had not been bracketed; it now is, and 100 fF is out of the box.
2. **vdd and vss are interchangeable.** `c_gate_vdd_10f` and `c_gate_vss_10f` give identical
   scorecards, as do `c_gate_vdd_30f` and `c_gate_vss_30f`. Both rails are AC ground here; only
   the total node capacitance matters. The one exception is PSRR on `fb`.
3. **`fb` to vdd buys PSRR**: +0.133 dB per fF at 1 kHz.
   Measured and exploitable, **not needed** — S6 has 30.0 dB of margin.
4. **`ea_o1` ↔ `ea_out` coupling is not a load, and the S7 credit those nets show is not
   bankable.** 30 fF between them leaves S7 at 115.060 mV against a
   115.057 mV baseline — it simply adds to the Miller cap. Deliberate C from either net
   to a rail does improve S7 (-0.323 mV/fF), but see section 3b: that
   improvement is a *saturating recovery of a broken gate*, not a per-fF credit, and it must not
   be added to a gate budget.

### 3b. The `gate` budget is GATE-ONLY, and the EA-path recovery is excluded from it

This is the numerical form of review finding **F3**. With 35 fF on `gate` and every other net
ideal, S7 is **201.691 mV** — out of the box. Add realistic capacitance to any
*one* of the three error-amp path nets and most of it comes back; add all three and barely more
comes back than from one:

| case | what is present | S7 (mV) | recovery vs gate-only (mV) | S8 (deg) | box |
|---|---|---|---|---|---|
| `g35_only` | `gate` 35 fF alone, every other net ideal | 201.691 | - | 72.5015 | **OUT** |
| `g35_plus_ea_o1_50f` | + `ea_o1` 50 fF | 122.377 | -79.31 | 72.2565 | in box |
| `g35_plus_ea_o1_100f` | + `ea_o1` 100 fF | 118.244 | -83.45 | 72.0124 | in box |
| `g35_plus_ea_out_25f` | + `ea_out` 25 fF | 125.805 | -75.89 | 72.3796 | in box |
| `g35_plus_fb_24f` | + `fb` 24 fF | 127.428 | -74.26 | 69.8274 | in box |
| `g35_plus_all3` | + all three together | 118.373 | -83.32 | 69.4694 | in box |
| `g25_plus_all3` | `gate` 25 fF + all three | 113.488 | -88.20 | 69.4708 | in box |
| `no_gate_all3` | the three EA nets alone, `gate` ideal | 102.852 | -98.84 | 69.4742 | in box |

`ea_o1` alone recovers -79.31 mV, `ea_out` alone
-75.89, `fb` alone
-74.26, and all three together
-83.32 — **one saturating mechanism, not a sum.**
Doubling `ea_o1` from 50 to 100 fF adds only
-4.13 mV more. The recovery works by
slowing the error-amp path so the FVF is not asked to slew the gate at all; it is a *different
operating regime*, and nothing guarantees it survives a corner, a load slew rate or a Cout
value the benches do not sweep.

**Therefore the `gate` budget of 12 fF in section 2 is stated gate-only and the
EA-path recovery is explicitly NOT part of it.** A layout that lands at 34.5 fF on `gate` and
reports a passing S7 because `ea_o1`/`ea_out`/`fb` happen to be slow is reporting a
cancellation. If the designer wants to bank the recovery, it has to become a *design* decision
(a deliberate capacitor on `ea_o1`, sized and certified) rather than an accident of routing —
`no_gate_all3` shows the EA caps on their own leave S7 at 102.852 mV, better
than baseline, so the credit is real; it is the *combination* that is not additive.

## 4. Series resistance — the Kelvin decision, and the power nets on their own

Injection: the net is split and a resistor inserted between the named devices and the rest. For
`vdd` and `vss` the split now moves **every card inside the subckt that touches the rail**, not
a hand list — with one deliberate exception on `vss`: `VREF` keeps its own ground, because an
off-cell reference does not float with the cell's return. `XCOUT`'s bottom plate **is** in the
moved set, and section 4a shows that the 11 Ohm limit is an
*interaction* between that plate's return and the active devices', not a property of either. Splitting a node adds a fixed offset to some metrics regardless of R, so every
coefficient below is a **two-point slope** between the smallest and the largest still-in-box
injected magnitude, never a difference against the unsplit baseline.

| segment | what the R is between | budget (Ohm) | linear budget (Ohm) | hard limit | binds | coefficient (per Ohm) |
|---|---|---|---|---|---|---|
| `vout_all` | vout bus + pin, sense INSIDE the drop (divider tapped at the pass drain) | 0.126 | 0.126 | - | S2 | load_reg_mv +9.9/Ohm, v_dropout_mv +10/Ohm, v_undershoot_mv -8.863/Ohm |
| `vdd` | supply rail resistance ahead of the whole cell (bulk ties included) | 2.31 | 2.31 | - | S4 | load_reg_mv +0.002759/Ohm, v_dropout_mv +10.34/Ohm, i_q_ua -0.001052/Ohm |
| `vout_pass_only` | R between the pass drain and everything else (sense + Cout + XMC at the pin) | 2.68 | 2.68 | - | S4 | v_dropout_mv +8.893/Ohm, v_undershoot_mv +0.3811/Ohm |
| `vout_sense_at_pin` | R between (pass drain + XMC + Cout) and the pin; VLP/divider at the pin | 2.76 | 2.76 | - | S4 | load_reg_mv +0.03011/Ohm, v_dropout_mv +8.645/Ohm, psrr_1k_db +0.003333/Ohm |
| `vss` | the whole cell's ground return (Iq only; the load returns off-cell) | 11 | 46.1 | **step between 11 and 12 Ohm** | S7 | v_out_v -3.358e-05/Ohm, load_reg_mv -0.00156/Ohm, i_q_ua -0.001029/Ohm |
| `vss_active` | ground return of the ACTIVE devices only -- XCOUT returned separately | 16.5 | 16.5 | - | S6 | v_out_v -3.363e-05/Ohm, load_reg_mv +0.003083/Ohm, line_reg_mv +0.007667/Ohm |
| `gate` | series R between the fold output and the pass gate | 1.77e+04 | 1.77e+04 | - | S7 | v_undershoot_mv +0.0004933/Ohm |
| `fb_tap` | series R in the XM1 gate lead (feedback tap) | 4.8e+05 | 4.8e+05 | - | S8lo | psrr_1k_db +4.134e-06/Ohm, v_undershoot_mv -0.0002649/Ohm, pm_loop_deg -5.437e-06/Ohm |
| `vref` | series R in the XM2 gate lead (reference tap) | 9.14e+05 | 9.14e+05 | - | S8lo | psrr_1k_db -2.376e-06/Ohm, v_undershoot_mv -6.945e-05/Ohm, pm_loop_deg -3.409e-06/Ohm |
| `lp_brk` | series R between the sense point and the divider top | 1.09e+06 | 1.09e+06 | - | S7 | v_out_v +5.37e-07/Ohm, psrr_1k_db -1.49e-06/Ohm, v_undershoot_mv +8e-06/Ohm |
| `vss_cout` | ground return of XCOUT's bottom plate only (the output cap's ESR) | no bound | no bound | - | - | v_undershoot_mv -0.3278/Ohm |

### 4a. The three power nets, stated on their own

| net | what the R is between | budget (Ohm) | hard limit | binds | dS4 mV/Ohm | dS2 mV/Ohm | dS7 mV/Ohm | dS6 dB/Ohm |
|---|---|---|---|---|---|---|---|---|
| vdd | the whole cell behind one R to the vdd pin (bulk ties included) | 2.31 | - | S4 | 10.34 | 0.002759 | 0.4728 | -0.005003 |
| vout, sense at the PIN | R between (pass drain + XMC + Cout) and the pin; VLP/divider tapped at the pin | 2.76 | - | S4 | 8.645 | 0.03011 | 1.413 | 0.003333 |
| vout, sense at the PASS DRAIN | R between the whole cell and the pin; the divider is INSIDE the drop | 0.126 | - | S2 | 10 | 9.9 | -8.863 | 0 |
| vss | the whole cell's ground return: XMA/XMB/XMS AND XCOUT's bottom plate behind one R (VREF excluded -- an off-cell reference does not float with the cell) | 11 | **step between 11 and 12 Ohm** | S7 | 0 | -0.00156 | 0.1894 | 0.1827 |
| vss, active devices only | the same return with XCOUT's bottom plate strapped to the pin instead (Kelvin cap return) | 16.5 | - | S6 | 0 | 0.003083 | 0.01371 | -0.4553 |
| vss, XCOUT return only | R in XCOUT's bottom-plate lead alone -- the output cap's own ESR | no bound | - | - | 0 | 0 | -0.3278 | 0 |

**`vdd` and `vout` share one dropout pool.** Both bind S4 and both are essentially `I × R` at
the 10 mA load — the measured slopes are 10.34 and
8.64 mV/Ohm against an ideal 10.03 mV/Ohm; the excess is
the dropout bench's own 2 mV Vdd quantisation read over a ~30 mV span, so treat these as
≈ 10 mV/Ohm each and the pooled rule below as slightly conservative. They are therefore not
independent budgets: what the layout has to satisfy is

> **10.34 × R(vdd) + 8.64 × R(vout) ≤ 23.83 mV** (25 % of the 95.3 mV dropout margin)

| how the pool is spent | allowed (Ohm) | costs (mV of dropout per Ohm) |
|---|---|---|
| `vdd` alone | 2.31 | 10.34 |
| `vout` alone (sense at the pin) | 2.76 | 8.64 |
| both, in the ratio the drawn straps have (1.13 : 1.03) | 2.50 total | 9.53 |

**The drawn cell, measured against that pool.** Review finding **F1** established that the RC
extraction never put wire resistance into the circuit, and carried a hand model instead:
125 um of 2.0 um TopMetal1 on `vdd` and 114 um on `vout` at the PDK's 18 mOhm/sq, i.e.
**1.13 Ohm + 1.03 Ohm**. Spliced into the frozen benches, both present at once:

| case | S4 dropout (mV) | dS4 (mV) | S2 (mV) | S7 (mV) | S6 (dB) | box |
|---|---|---|---|---|---|---|
| `vdd` 1.13 Ohm alone (125 um of 2 um TopMetal1 at 18 mOhm/sq) | 114.705 | +10.034 | 0.029 | 115.596 | 70.0014 | in box |
| `vout` 1.03 Ohm alone, sense at the pin (114 um) | 112.735 | +8.064 | 0.057 | 116.512 | 70.0105 | in box |
| `vout` 1.03 Ohm alone, sense at the pass drain | 114.971 | +10.300 | 10.223 | 105.932 | 70.007 | **OUT** |
| **both, sense at the pin** -- the drawn cell's hand model | 124.714 | +20.043 | 0.059 | 117.048 | 70.0048 | in box |
| both, sense at the pass drain | 125.005 | +20.334 | 10.226 | 106.47 | 70.0014 | **OUT** |
| both + the drawn 32 Ohm vss return | 125.23 | +20.559 | 0.072 | 229.348 | 62.0365 | **OUT** |
| `vss` 32 Ohm alone (the drawn return, F9) | 103.182 | -1.489 | 0.074 | 218.059 | 62.0415 | **OUT** |
| `vss` 8 Ohm alone (F9's proposed fix) | 104.802 | +0.131 | 0 | 116.499 | 72.9685 | in box |
| `vdd` 0.56 Ohm alone (F9's `pwr_w` 2 -> 4 um) | 108.717 | +4.046 | 0.027 | 115.325 | 70.0042 | in box |
| `vss` 32 Ohm on the ACTIVE devices only (XCOUT returned to the pin) | 103.182 | -1.489 | 0.074 | 115.497 | 62.0419 | in box |
| `vss` 32 Ohm on XCOUT's bottom plate alone | 104.671 | +0.000 | 0.026 | 103.199 | 69.9894 | in box |

- **Sense at the pin: dropout 124.714 mV, i.e. +20.04 mV, which is 84 % of the pool and 21 % of the whole dropout margin.** In box, with 2.16 Ohm against a
  ~2.50 Ohm pooled allowance. F1's headline was **+28.5 mV**; that figure used the
  005 brief's 13.24 / 13.21 mV/Ohm coefficients. Re-measured on this row the answer is
  **+20.04 mV**. F1's *conclusion* stands — a real, unmeasured
  2.2 Ohm that both scorecards report as zero — but the number is 30 % smaller.
- **Sense at the pass drain: S2 = 10.23 mV against a 5 mV spec — OUT.**
  This is review finding **F8** as a measurement rather than a hand estimate (F8 predicted
  10.2 mV; measured 10.22 mV for the `vout` leg alone). The GDS
  does not currently draw the tap at all, so which of these two numbers the cell has is
  undecided. **Tap the divider at the pin.** With the tap at the pin the same metal is allowed
  2.76 Ohm; at the pass drain it is allowed
  0.126 Ohm —
  22× less.
- **`vss` is a hard 11 Ohm *only while `XCOUT` shares the return*, and
  the drawn return is over it.** F9 measured the drawn return at ≈ 32 Ohm (one 0.8 um Metal1
  riser 134.8 um long plus the bottom rail). With the whole cell behind it, S7 at 32 Ohm is
  **218.1 mV — out of the box** — with PSRR at 62.0 dB,
  still comfortably inside. So F9's severity was right and its *mechanism* was not: the vss
  return is an undershoot constraint, not a PSRR one, and its combined budget is
  11 Ohm, not 17. F9's proposed fix (8 Ohm) measures
  116.499 mV — in box, with 72.969 dB of PSRR, better than
  baseline.
- **But the 11 Ohm is a *shared-impedance* number, not a rail-width number — and that is a
  floorplan lever, not a metal-width one.** Splitting the injection settles it. Move only the
  active devices — the full moved set is `pert.touches("vss")` minus `VREF` and `XCOUT`, i.e.
  `XM3A/B`, `XM4A/B`, `XM5`, `XMA`, `XMB`, `XMB0A/B`, `XMB1A/B`, `XMSA/B` and the `bn` bodies of
  `XR1_1..8`, `XR2_1..8`, `XRB_1..5`; `XCFF` does not touch this rail — and the
  step disappears: 32 Ohm gives S7 115.50 mV, i.e.
  +0.44 mV over 32 Ohm — nothing. Move only `XCOUT`'s bottom
  plate and S7 *improves*: 110.08 mV at 11 Ohm and
  103.20 mV at 32 Ohm, the textbook ESR-zero damping. Static arithmetic
  says the same thing — 26.0 uA through 11 Ohm is 0.4 mV of ground
  shift, which cannot move a 115 mV undershoot. **The cliff needs both halves behind the same
  R**: Cout's load-step displacement current develops a ground bounce that the FVF's sources and
  the EA see as a reference step, and the loop slews. So:
  - **Route `XCOUT`'s bottom plate to the `vss` *pin* on its own strap (a Kelvin cap return),
    and the 11 Ohm S7 cliff is lifted.** What is left is a *soft,
    linear* PSRR cost, and it is a real one: the active return then binds S6 at
    **16.5 Ohm**
    (-0.4553 dB/Ohm on the 11→32 Ohm two-point slope).
    Read against the certified baseline instead of the local slope the drawn 32 Ohm gives
    S6 = 62.04 dB — 7.97 dB below the
    certified 70.01 dB and still 22.0 dB above the 40 dB spec,
    i.e. it spends 106 % of the quarter-margin
    allowance on this one item. PSRR is *non-monotonic* in this R (it improves to
    72.97 dB at 8 Ohm before falling), which is why the two numbers differ;
    take **16 Ohm as the budget** and treat 32 Ohm as in-box-but-fully-spent.
  - **If the two must share one strap, 11 Ohm is the number** and F9's
    fix (widen the riser to ≈ 8 Ohm) is the right one.
  This is the one place in the brief where the cheap fix is a *connection*, not a width.

`fb`, `lp_brk`, `gate` and `vref` are kOhm-class: series resistance in the signal taps is a
don't-care.

## 5. Hi-Z nodes and the leakage budget

Injection: `I <node> vss dc 1 nA` — **positive = current pulled OUT of the node to ground**, i.e.
a leak. (The platform's `inject_isource` uses the opposite sign.)

| node | branch current (nA) | budget (nA) | budget (pA) | binds | coefficient |
|---|---|---|---|---|---|
| `fb` | 539.2 | 5.3 | 5.3e+03 | S1 | v_out_v +0.001109/nA, psrr_1k_db +0.00371/nA |
| `ea_n` | 2176 | 12.4 | 1.24e+04 | S6 | v_out_v -3.9e-05/nA, psrr_1k_db -0.6056/nA |
| `nbias` | 2496 | 301 | 3.01e+05 | S7 | i_q_ua -0.01041/nA, psrr_1k_db -0.00204/nA |
| `ea_out` | 2515 | 329 | 3.29e+05 | S6 | v_out_v -2e-06/nA, i_q_ua -0.00444/nA |
| `y` | 7751 | 794 | 7.94e+05 | S7 | v_undershoot_mv +0.011/nA |
| `gate` | 7474 | 1.49e+03 | 1.49e+06 | S5 | load_reg_mv -0.002/nA, i_q_ua +0.00271/nA |
| `pbias` | 4333 | 1.6e+03 | 1.6e+06 | S5 | i_q_ua +0.00253/nA |
| `lp_brk` | 539.2 | no bound | - | - | - |
| `ea_o1` | 2165 | no bound | - | - | v_out_v +4e-05/nA, psrr_1k_db +0.6378/nA |
| `ea_tail` | 4341 | no bound | - | - | psrr_1k_db +0.01088/nA, v_undershoot_mv -0.006/nA |
| `x1` | 4356 | no bound | - | - | v_undershoot_mv -0.017/nA |
| `vout` | 4895 | no bound | - | - | - |

- **`fb` — 5.30 nA**, binding S1.
  The divider carries 539.2 nA through
  1.1 MOhm arms, so the node's Thevenin resistance is ~550 kOhm and the loop multiplies the
  error by the divider ratio. **No ESD diode, no antenna diode and no large diffusion on `fb` or
  `lp_brk` without a leakage number** — `fb` drives XM1's gates, so a long Metal1 track will
  attract an antenna fix, and that fix is what spends this budget.
- **`ea_n` — 12.4 nA**, binding
  S6 at -0.606 dB/nA. It
  is diode-connected, so it looks low-impedance, but unbalancing the error amp's mirror is what
  PSRR is made of; `ea_o1`, the other leg, moves PSRR the other way by the same amount.
- Everything else has 300 nA or more, which no realistic junction has at these areas.

## 6. Matching

MOS mismatch is injected as a dc source in series with **every card the design device is drawn
as** (`XM1` = `XM1A` + `XM1B`), so the numbers are class mismatch, not intra-device asymmetry;
the device sees `net - dVT` (the platform's `inject_vsource` is the opposite sign). Half-only
injections are section 6b. The 1-sigma columns are the PDK's own numbers:
`delvto = agauss(0, A_VT/sqrt(m*L*W))` with A_VT = 2.0 mV*um (lv nmos) / 2.5 mV*um (lv pmos) and
`dw_mm` = 4 nm / 5 nm absolute (`sg13g2_moslv_mismatch.lib`); the pair sigma is
`sqrt(sigma_a^2 + sigma_b^2)` computed **per member from its own W·L·m**, which matters where
the two members are not the same size (`bias_n_group`). "headroom" = tolerated / 1 sigma, where
"tolerated" is the smaller of the 25 %-margin figure and the last point before a step.
Pattern: < 3 sigma → common centroid + dummies; 3-6 → interdigitated + dummies;
6-20 → same row, same orientation; > 20 → any.

| class | devices | W/L (um) | linear tol. dVT (mV) | out of box at (mV) | PDK 1 sigma dVT (mV) | headroom (sigma) | binds | tol. dW (%) | 1 sigma dW (%) | pattern |
|---|---|---|---|---|---|---|---|---|---|---|
| `ea_nmos_load` | `XM3` + `XM4` | 2.95/1 + 2.95/1 | 3.44 | **2** | 1.65 | 0.607 | S1 | 1.95 | 0.192 | common_centroid+dummies |
| `bias_p_group` | `XMBP` + `XMT` + `XM6` | 10/1 + 10/1 | 11.7 | **1.5** | 1.12 | 1.07 | S8hi | 31.2 | 0.0707 | common_centroid+dummies |
| `ea_in_pair` | `XM1` + `XM2` | 9.53/0.5 + 9.53/0.5 | 2.95 | - | 1.62 | 1.82 | S1 | 2.19 | 0.0742 | common_centroid+dummies |
| `bias_n_group` | `XMB0` + `XMS` | 1/1 + 2.2/0.95 | 8.1 | **6** | 2.43 | 2.06 | S7 | 18.6 | 0.566 | common_centroid+dummies |
| `fvf_fold_p` | `XMCP` + `XMD` | 9.02/0.5 + 9.02/0.5 | 20.8 | - | 1.66 | 12.5 | S7 | 54.3 | 0.0784 | same_row_same_orientation |
| `fvf_fold_n` | `XMA` + `XMB` | 5.79/0.5 + 5.79/0.5 | 40.6 | - | 1.66 | 24.4 | S7 | 243 | 0.0977 | any |
| `pass_array` | `XMP` | 2.5/0.13 x76 | - | - | 0.503 | 125 | - | 25 | 0.2 | any |

| class | devices | unit | tolerated | linear | out of box at | 1 sigma (%) | headroom (sigma) | binds | pattern |
|---|---|---|---|---|---|---|---|---|---|
| `fb_divider` | `XR1`, `XR2` | %dR/R on one arm (all 8 segments) | 0.989 | 0.989 | - | 0.575 | 1.72 | S1 | common_centroid+dummies |
| `mim_feedforward` | `XCFF` | %dC/C | 6 | 96 | **8** | 1.25 | 4.8 | S7 | interdigitated+dummies |
| `fb_divider_segment` | `XR2_1` | %dR/R on ONE segment of eight | 7.92 | 7.92 | - | 1.62 | 4.87 | S1 | interdigitated+dummies |
| `mim_miller` | `XCC` | %dC/C | 135 | 135 | - | 0.185 | 728 | S6 | any |
| `bias_resistor` | `XRB` | %dR/R (all 5 segments) | 6 | 12.3 | **10** | - | - | S7 | any |
| `bias_resistor_segment` | `XRB_1` | %dR/R on 1 of 5 | 61.1 | 61.1 | - | - | - | S7 | any |
| `mim_cout` | `XCOUT (m=4)` | %dC/C | no bound | no bound | - | 0.0862 | no bound | - | any |
| `mim_cout_unit` | `one XCOUT unit` | %dC/C on 1 of 4 | no bound | no bound | - | 0.172 | no bound | - | any |

**Three classes now sit at or below 2 sigma, and two of them are step-limited.**

- **`ea_nmos_load` (`XM3`/`XM4`) — 1 mV, 0.61 sigma. The tightest class in the cell.**
  The linear budget is 3.44 mV (S1, at
  +1.71 mV of Vout per mV of dVT), but the **XM3 (diode) side crosses
  the S7 step at 2 mV**: S7 115.318 → **200.382 mV**. The
  XM4 side at the same magnitude is harmless for S7 (112.497 mV at 10 mV) but
  costs -10.03 dB of PSRR. Random mismatch is symmetric, so **half
  the distribution sees the dangerous sign**, and 1 mV of it is 0.61 sigma. Common centroid,
  dummies, identical routing on both drains, identical thermal environment — and understand that
  layout cannot fix the random part of a sub-sigma budget.
- **`bias_p_group` (`XMBP` → `XMT` and `XM6`) — 1.2 mV, 1.07 sigma.**
  S7 is flat to 1.2 mV (115.606 mV) and steps to
  184.265 mV at 1.5 mV. **Only one sign is dangerous**: the side that makes
  `XMT` carry more current than `XMBP`'s ratio dictates. −5 mV gives S7 = 112.939 mV
  and −10 mV gives 111.050 mV, both better than baseline. A systematic layout
  offset that *weakens* XMT is free; one that strengthens it by 1.5 mV loses the cell. The dW
  form of the same step is at 3 % (115.625 → 200.047 mV).
  This is review finding **F16** made quantitative: the recertified bias branch spent most of
  the distance to this step.
- **`fb_divider` (`XR1`/`XR2`) — 0.989 % of single-arm dR/R, 1.72 sigma.**
  1 % of one arm costs 5.94 mV of Vout, linear from 0.1 % to 3 %.
  A 2000-sample Monte Carlo with the PDK's own `res_typ_mismatch` models on the **segmented
  string the deck now draws** gives sigma(R2/(R1+R2)) = 0.2873 %, i.e.
  **sigma(Vout) = 3.45 mV** against a 5.87 mV quarter margin.
  The monolithic arms give 0.2909 % — **segmentation does not change
  the random part** (the eight per-segment sigmas add in quadrature exactly as the area says).
  It buys the *gradient* part, which is where XMP's
  3.0 mW sits. One segment of eight mismatched by 1 % costs
  0.742 mV — 1/8 of the arm, as it should.
- `ea_in_pair` (`XM1`/`XM2`) at 1.82 sigma is unchanged in kind:
  perfectly linear at +1.99 mV of Vout per mV of dVT from 1 to
  20 mV, no step, dW 29 sigma looser than dVT.
  It is a threshold-voltage matching problem: common centroid, dummies, same orientation.
- `bias_n_group` is 2.06 sigma with its step at
  6 mV; the FVF folds and the pass array are 12 sigma or looser.
- **`XCFF` and `XRB` are step-limited too**, at +6 % and
  +6 % — the same S7 cliff reached through a capacitor
  and a resistor value. Neither is a *matching* constraint (both are single devices); they are
  absolute-value constraints, and they are listed here because the layout can move them: XCFF is
  a 8 x 8 um MIM of about 0.1 pF, so 6 fF of stray capacitance between `fb` and
  `lp_brk` **is** the +6 % limit — the two measurements are the same cliff
  reached from two directions, and they agree.

### 6b. Half-vs-half inside one common-centroid member

New on this row, because the deck now draws the matched devices as two cards. A dVT on one half
is an intra-member asymmetry — exactly what review finding **F6** measures geometrically (the
two `XM1` halves are routed differently: 3.69 um² of XOR, 4 vs 3 Via1).

| class | half card | dS1 (V) | /whole | dS5 (uA) | /whole | dS7 (mV) | /whole | dS6 (dB) | /whole |
|---|---|---|---|---|---|---|---|---|---|
| `ea_in_pair` | `XM1A` | +0.0104 | 0.52 | -0.00095 | 0.51 | +0.125 | 0.43 | +2.853 | 51.97 |
| `ea_in_pair` | `XM2A` | -0.01041 | 0.52 | +0.00293 | 0.53 | -0.179 | 0.65 | -3.442 | 18.12 |
| `ea_nmos_load` | `XM3A` | +0.008227 | 0.48 | -0.00154 | 0.48 | +102.6 | 0.76 | +3.296 | -0.57 |
| `bias_n_group` | `XMB0A` | -2e-06 | 0.50 | +1.753 | 0.48 | -4.72 | 0.53 | +0.2885 | 0.50 |
| `bias_n_group` | `XMSA` | -8e-06 | 0.47 | -1.171 | 0.50 | +5.268 | 0.05 | -0.01711 | 0.43 |

The ratio columns are the half-only delta over the whole-device delta at the same 10 mV. For
`ea_in_pair` and `bias_n_group` it is ≈ 0.5, as two parallel halves should give: **half-vs-half
mismatch is worth half of member-vs-member mismatch**, so the F6 routing asymmetry is a real
but second-order effect on S1 and Iq. `XM3A`'s row is past the S7 step at 10 mV (S7
203.1 mV already at 5 mV), so its ratios are not a linear comparison; the
half-vs-half rule is read off `ea_in_pair` and `bias_n_group`.

The exception is PSRR. A 10 mV offset on the **whole** `XM1` does not move S6 at all
(+0.05 dB, at the bench floor); the same 10 mV on **one half**
moves it +2.85 dB. Stated as a ratio it is a factor of
52, but the denominator
is a floor-level number, so read the two absolute figures and not the ratio: intra-member
imbalance is a differential error the class-level injection cancels entirely. **PSRR is the metric that punishes asymmetric routing between the two halves
of one member**, and it is the reason F6's fix (a mirrored column pair reserved per
common-centroid member) is worth doing even though S1 barely notices.

## 7. Devices — currents, voltages, wells

Measured at the operating point of the frozen `dc_op` deck with 0 V ammeters spliced into every
**card's** drain (model-agnostic), at no load and at a 10 mA load; a design device's current is
the sum over its cards for parallel halves and the common current for a series resistor string.
Current is into the drain node, so it is **negative for a PMOS**; `Vds`/`Vgs` are signed for the
device type (positive = on).

| device | group | flavour | cards | I no load (uA) | I at 10 mA (uA) | Vds (mV) | Vgs (mV) | Vsb (mV) | bulk / well | Vds at 10 mA (mV) |
|---|---|---|---|---|---|---|---|---|---|---|
| `XMB0` | bias | lv_nmos | 2 | 2.496 | 2.4957 | 365.5 | 365.5 | 0 | vss | 365.5 |
| `XMB1` | bias | lv_nmos | 2 | 4.333 | 4.3333 | 1065 | 365.5 | 0 | vss | 1065 |
| `XMBP` | bias | lv_pmos | 1 | -4.333 | -4.3333 | 434.8 | 434.8 | -0 | vdd | 434.8 |
| `XMT` | error amp | lv_pmos | 1 | -4.341 | -4.3412 | 451.9 | 434.8 | -0 | vdd | 451.9 |
| `XM1` | error amp | lv_pmos | 2 | -2.176 | -2.1765 | 757.1 | 448.3 | 452 | vdd | 757.1 |
| `XM2` | error amp | lv_pmos | 2 | -2.165 | -2.1646 | 763.5 | 448.1 | 452 | vdd | 763.9 |
| `XM3` | error amp | lv_nmos | 2 | 2.176 | 2.1765 | 291 | 291 | 0 | vss | 291 |
| `XM4` | error amp | lv_nmos | 2 | 2.165 | 2.1646 | 284.6 | 291 | 0 | vss | 284.2 |
| `XM5` | error amp | lv_nmos | 1 | 2.515 | 2.5128 | 767.3 | 284.6 | 0 | vss | 780 |
| `XM6` | error amp | lv_pmos | 1 | -2.515 | -2.5128 | 732.7 | 434.8 | -0 | vdd | 720 |
| `XMC` | FVF | lv_pmos | 1 | -4.356 | -3.1977 | 925.1 | 432.2 | 301 | vdd | 937.7 |
| `XMA` | FVF | lv_nmos | 1 | 4.356 | 3.1977 | 274.4 | 274.4 | 0 | vss | 261.8 |
| `XMB` | FVF | lv_nmos | 1 | 7.751 | 5.9781 | 1053 | 274.4 | 0 | vss | 1070 |
| `XMCP` | FVF | lv_pmos | 1 | -7.751 | -5.9781 | 446.6 | 446.6 | -0 | vdd | 430.4 |
| `XMD` | FVF | lv_pmos | 1 | -7.474 | -6.308 | 280.7 | 446.6 | -0 | vdd | 864.9 |
| `XMS` | FVF | lv_nmos | 2 | 7.474 | 6.3087 | 1219 | 365.5 | 0 | vss | 635.1 |
| `XMP` | output | lv_pmos | 1 | -4.895 | -10004 | 300.5 | 280.7 | -0 | vdd | 300.5 |
| `XRB` | bias | rhigh | 5 | 2.496 | 2.4957 | 1135 | - | 0 | vss | 1135 |
| `XR1` | feedback | rhigh | 8 | 0.5392 | 0.53915 | 599.7 | - | 0 | vss | 599.7 |
| `XR2` | feedback | rhigh | 8 | 0.5392 | 0.53915 | 599.8 | - | 0 | vss | 599.7 |

- All nine PMOS have bulk = vdd in the netlist of record. XMC's source is `vout`
  (Vsb = 301 mV) and XM1/XM2's source
  is `ea_tail` (Vsb = 452 mV): these
  are DELIBERATE. Do not give XMC or the input pair its own nwell tied to its source — that is a
  design change, not a layout fix.
- Separate nwell islands are therefore for ISOLATION only, all tied to vdd: (a) XMP alone (hot,
  10 mA, fast dV/dt); (b) quiet: XMBP/XMT/XM1/XM2/XM6; (c) FVF: XMC/XMCP/XMD.
- All eight NMOS have bulk = vss in the common p-substrate; the rhigh bodies (`bn`) are vss as
  well. `vss` is a budgeted net now (section 4a), so the ptap rings are **part of the return
  path, not just a bulk tie**: draw them as closed rings stitched to the vss strap at both ends,
  not as point taps on a pitch. They carry the *active* return, whose budget is
  16 Ohm on PSRR — it becomes
  11 Ohm on undershoot only if `XCOUT` shares the same strap.
- `XM1` and `XM2` do not carry equal current (-2.1762
  vs -2.1650 uA): the cell
  regulates to Vout = 1.199499 V, i.e. -0.501 mV of built-in offset
  against the 0.6 V reference. That is a design fact, not a layout target.

## 8. Power path — per-net DC current budget

Currents measured (`i_supply` and the XMP ammeter at a 10 mA load); limits from the PDK's own
**`SG13G2_os_process_spec.pdf` section 2.15**, "Maximum Current Densities", 11 years at
105 degC, scored with `spicexplorer_signoff.current_density.check_current_density`. Measured:
**I(vdd) = 10.0297 mA**, **I(XMP) = 10.0037 mA**,
**0.1316 mA per finger** (nf = 76, w = 2.5 um)
and **0.2633 mA per shared diffusion column**, and only
**26.0 uA** on the cell's own `vss` — the bench returns the load current
to the top-level ground, so the 10 mA ground return is a *chip*-level path, not a cell-level one.
**If the ground return is ever routed through this cell, `vss` inherits the `vdd` row**, and its
11 Ohm signal-integrity budget (section 4) becomes an electromigration problem as well.

**The finger split changed this section more than anything else in the brief.** The certified
pass device is now 76 fingers of 2.5 um, not 19 of 10 um, so the
current in the conductor that was 2.9× over the Metal1 allowance on the 005 row is 4× smaller:

| net | segment | carries (mA) | drawn | limit (mA) | over |
|---|---|---|---|---|---|
| `vdd` | vdd strap, TopMetal1 over the stack | 10.03 | topmetal1 2um | 30 | 0.334x |
| `vout` | vout strap, TopMetal1 over the stack | 10 | topmetal1 2um | 30 | 0.334x |
| `vdd` | pass-array Metal2 comb spine (worst segment) | 10.03 | metal2 6um | 12 | 0.836x |
| `vout` | pass-array Metal2 comb spine, drain side | 10 | metal2 6um | 12 | 0.834x |
| `vdd` | pass source column riser, shared (2 fingers) | 0.2633 | metal1 0.2um | 0.36 | 0.731x |
| `vout` | pass drain column riser, shared (2 fingers) | 0.2633 | metal1 0.2um | 0.36 | 0.731x |
| `vdd` | Via1 per shared S/D column (2 cuts, F4) | 0.2633 | via1 x2 | 0.8 | 0.329x |
| `vout` | Via1 per shared S/D column (2 cuts, F4) | 0.2633 | via1 x2 | 0.8 | 0.329x |
| `vout` | diffusion contacts per shared column (PDK cell) | 0.2633 | contact x7 | 2.1 | 0.125x |
| `vout` | pass drain END column riser (1 finger) | 0.1316 | metal1 0.2um | 0.36 | 0.366x |
| `vss` | cell vss rail (Iq only) | 0.02601 | metal1 0.8um | 0.8 | 0.0325x |

Geometry for those rows is the **independent reviewer's** measurement of the second drawing
(REVIEW.md's geometry table and finding **F4**, which corrected the Via1 count from the reported
×4 to the drawn ×2), not a live read of `layout/gen_ldo.py` — that file is under revision while
this brief is written. Worst over-factor **0.836×**, at the Metal2 comb
spine, which is the segment that carries the whole 10 mA.

**Minimum width / via count per segment.** The arithmetic minimum is `I / J`:
TopMetal1 **0.67 um** for the output (and
0.67 um for vdd) — below `TM1.a`'s 1.64 um minimum width, so on
TopMetal1 the electromigration requirement is *free* and it is the floorplan (`TM1.b` 1.64 um
space, `TV1.d` 0.42 um enclosure) that costs. Metal1 would need
**10.0 um** for the whole current, which does not fit a routing
channel; Metal2 or Metal5 need 5.0 um. Vias:
**25 Via1** (or Via2/3/4) at 0.4 mA each,
**7 TopVia1** at 1.4 mA each, one TopVia2. Per shared S/D
column the arithmetic minimum at 1 mA/um is **0.263 um of
Metal1** — but that width sits inside the 0.16-0.36 um band where the process spec gives a
**flat 0.36 mA total** rather than a density, so the drawn 0.2 um riser carries
0.263 mA at 0.73x of limit
(1.37x headroom) and passes on its own. Vias and contacts per
column: 0.66 → **1 Via1** (the drawing has 2) and
0.88 → **1 diffusion contact** (the PDK cell draws 7).

**What the 005 brief said here is now void.** It required a Metal2 plate over the pass array, or
`nf >= 56`, and stated that raising `nf` "is not a layout knob… taking it means re-running the
003 sizing campaign and re-certifying". That is exactly what happened: the certified device *is*
76 fingers, the shared-column current is 0.263 mA, and the Metal1 riser
passes on its own. The Metal2 comb the second drawing already has is still the right structure —
it is what makes the 0.836× spine the worst segment instead of a
column — but it is no longer a *requirement*, and no argument in this brief depends on it.

**What to draw** (≥ 1.5× headroom on every segment; `passed = True`, worst
0.731×):

| net | segment | carries (mA) | drawn | limit (mA) | over |
|---|---|---|---|---|---|
| `vdd` | vdd strap, TopMetal1 over the stack | 10.03 | topmetal1 2um | 30 | 0.334x |
| `vout` | vout strap, TopMetal1 over the stack | 10 | topmetal1 2um | 30 | 0.334x |
| `vdd` | pass-array Metal2 comb spine (1.5x headroom) | 10.03 | metal2 9um | 18 | 0.557x |
| `vout` | pass-array Metal2 comb spine, drain side | 10 | metal2 9um | 18 | 0.556x |
| `vout` | vout M5->TopMetal1 stitch | 10 | topvia1 x12 | 16.8 | 0.596x |
| `vdd` | vdd M5->TopMetal1 stitch | 10.03 | topvia1 x12 | 16.8 | 0.597x |
| `vout` | vout M5 landing pad under the TopVia1 row | 10 | metal5 8um | 16 | 0.625x |
| `vdd` | vdd M5 landing pad | 10.03 | metal5 8um | 16 | 0.627x |
| `vout` | vout M1->M2 stitch (whole-current riser) | 10 | via1 x40 | 16 | 0.625x |
| `vout` | vout M2->M3 | 10 | via2 x40 | 16 | 0.625x |
| `vout` | vout M3->M4 | 10 | via3 x40 | 16 | 0.625x |
| `vout` | vout M4->M5 | 10 | via4 x40 | 16 | 0.625x |
| `vdd` | vdd M1->M2 stitch (same count as vout) | 10.03 | via1 x40 | 16 | 0.627x |
| `vdd` | pass source column riser, shared (2 fingers) | 0.2633 | metal1 0.2um | 0.36 | 0.731x |
| `vout` | pass drain column riser, shared (2 fingers) | 0.2633 | metal1 0.2um | 0.36 | 0.731x |
| `vdd` | Via1 per shared S/D column | 0.2633 | via1 x2 | 0.8 | 0.329x |
| `vout` | Via1 per shared S/D column | 0.2633 | via1 x2 | 0.8 | 0.329x |
| `vout` | diffusion contacts per shared column | 0.2633 | contact x4 | 1.2 | 0.219x |
| `vss` | cell vss rail, unchanged | 0.02601 | metal1 0.8um | 0.8 | 0.0325x |

The only row that changes against the drawing is the Metal2 spine: 6.0 um gives
0.836×, which passes but leaves under 20 % headroom on the one
conductor that carries the entire load current. 9 um restores 1.5×.

## 9. Structure, pin intent, keep-aparts

**Symmetry axis: vertical, one local axis per matched pair; the cell has NO global differential axis** — the only differential net pair is (fb, vref) at the error-amp inputs and `vref` is driven by an ideal source inside the subckt, so balanced and one-sided injection measure the same thing (`c_fbvref_bal_10f` and `c_fb_vss_10f` both give S7 112.859 mV and PM 71.3695 deg). Mirror pairs:
`XM1`/`XM2`, `XM3`/`XM4`, `XMA`/`XMB`, `XMCP`/`XMD`, `XMBP`/`XMT`, `XR1`/`XR2`.

**The sub-arrays that must sit ON their local axis**, in order:

1. XM3/XM4 -- the tightest matching class in the cell and the one whose diode side crosses the S7 step; its two drains (`ea_n`, `ea_o1`) must sit symmetrically about the local axis
2. XMBP/XMT -- second tightest, and the leg that carries the bias step
3. XR1/XR2 -- the only thing that sets Vout against Vref

**Pin intent** (the cell of record has three pins — `vdd`, `vout`, `vss`; `vref` and `fb` are
internal today):

| side | pin |
|---|---|
| top | vdd (= vin; TopMetal1 strap over the device stack) |
| bottom | vss (a BUDGETED net now: 11 Ohm while XCOUT shares the return, 16 Ohm if XCOUT gets its own strap to the pin -- see section 4a) |
| right | vout (TopMetal1, beside the pass device; the divider must tap HERE) |
| left | vref (future pin, when a bandgap replaces VREF); fb (test/trim only; keep away from the output bus) |

**Keep apart:**

- XMP dissipates 3.0 mW at 10 mA
  (0.3005 V ×
  10.00 mA). rhigh `tc1` = −2300 ppm/K and 1 % of single-arm dR/R costs
  5.94 mV of Vout, so 1 K of gradient across XR1↔XR2 costs
  1.37 mV =
  23 % of the S1 quarter-margin. Keep the
  divider serpentines at the far end from XMP and interdigitate them ABBA.
- XRB sets every branch current from the same `tc1`, and its own tolerance is now step-limited at
  +6 %: keep it out of XMP's heat too.
- `gate` and `vout` carry the fast edges. Keep `gate` off `fb`, `lp_brk`, `x1` and `y` — and note
  that "off `lp_brk`" is now a hard number for `fb`: 6 fF between `fb` and `lp_brk` is
  the limit, because that capacitance lands in parallel with XCFF.

**MIM plate orientation** (bottom plate = Metal5, the plate kpex extracts; top-plate coupling is
not extracted at all, so put the sensitive terminal on top):

- XCFF: bottom plate (Metal5, the plate kpex extracts) on `lp_brk`, not on `fb`. Both ends are now constrained -- `fb` has a 27.1 fF to-rail budget and the fb<->lp_brk coupling itself has a 6 fF hard limit -- so this is no longer a free choice; it is the cheaper of two constrained ends.
- XCOUT: bottom plate on `vss` -- **and on its own strap straight to the `vss` pin.** Section 4a shows the 11 Ohm undershoot cliff is a shared-impedance effect between this plate's return current and the active devices' return; separate the two and the cliff is gone. Cheapest constraint relief in the brief, and it costs one strap.
- XCC: bottom plate on `ea_out` (the lower-Z stage-2 side); the C sensitivities of `ea_o1` and `ea_out` are equal to 3 digits, so this is a tie broken by impedance.

## 10. Don't-cares

| axis | explicitly not a constraint |
|---|---|
| capacitance | `vout`, `vdd`, `lp_brk`, `ea_tail`, `nbias`, `pbias`, `ea_o1`, `ea_out`, `vref`, `vss` |
| series_resistance | `lp_brk`, `gate`, `fb`, `vref` |
| leakage | `lp_brk`, `ea_tail`, `x1`, `vout`, `y`, `pbias`, `gate` |
| matching | `XMA/XMB`, `XMCP/XMD`, `XMP fingers`, `XCOUT unit-to-unit`, `XCC`, `XR2 segment-to-segment inside one arm` |

A net can be a don't-care on one axis and the tightest constraint on another: `gate` has no
series-resistance and no leakage constraint and the smallest capacitance budget in the cell;
`vout` and `vdd` have no capacitance constraint and the two tightest resistance budgets.
**`vss` has left this list on the resistance axis** — it was a don't-care in the 005 brief at
17 Ohm and it is an 11 Ohm hard limit here.

Two nets are unmeasurable rather than generous, and are listed as such: `vref` is driven by an
ideal source inside the subckt (`c_vref_vss_10f` reproduces the baseline exactly), and `vss` is
the reference node for capacitance. When a real bandgap replaces `VREF`, `vref` must be
re-measured.

## What I would watch

**One mechanism owns this cell.** The load-step undershoot has a cliff, and on this row the cell
sits 34.9 mV from the spec but only **12 fF, 11 Ohm
of ground return, 1 mV of XM3 mismatch, 1.2 mV
of XMT mismatch, 6 % of XCFF and 6 fF of fb-to-lp_brk coupling**
from the cliff, in six different directions. Past it S7 lands at 180-230 mV against a 150 mV
spec, with the recovery time roughly tripling — there is no graceful degradation to trade
against, and no reason to believe the six directions are independent when several are crossed at
once. I would not sign this layout off on a scorecard alone; I would want the recovery time
(`t_transient_us`, 0.156 us at the certified point) watched as a leading indicator, because it moves *before* S7 does
(0.241 us at the last good gate point against
0.156 us clean).

**The second drawing is over three of these budgets.** 34.5 fF on `gate` against
12; ≈ 32 Ohm of `vss` return against 11 — and a
separate `XCOUT` strap does not retire that one, it *demotes* it, from a hard S7 cliff
(218 mV, out of box) to a soft PSRR cost against a
16 Ohm budget that the drawn 32 Ohm still
exceeds 2x. F9's riser widening is still required — for a different reason, and to a different
target; and a divider
tap that is not drawn at all, so S2 is either 0.059 mV or
10.23 mV depending on a decision nobody has recorded. The `gate` one is
the hardest: 12 fF is less than the Metal1+GatPoly gate bar the drawing already
needs to reach 76 fingers. F3 measured that bar at 38.75 um and its capacitance at 5.8 fF per
unit of `xmp_nf_mult` on a 24 fF fixed remainder — 34.5 fF to rail at `nf_mult` = 4, and 26.5 fF
even at `nf_mult` = 2, which is still over budget and leaves the column 1.46x over on EM. **I do not believe this net can be routed to budget in Metal1 in the
rail channel.** The two ways out that this brief can price are (a) drive the gate from a
Metal2/Metal3 bus that runs *over the array*, coupled to `vout` rather than to a rail, where the
budget is 40 fF instead of 12, and (b) shield it with `vout` rather than
with a rail wherever it must cross the channel. Both are floorplan decisions, not width choices,
and both should be made before the next drawing rather than measured after it.

**Everything here is tt / 27 degC.** Experiment 003 already showed S7 failing at ss/−40 before
any layout existed, and this row's S7 baseline is 10.2 mV worse than the row that measurement was
made on. Every fF on `gate` is therefore spent twice. The corner re-run belongs after the layout
exists — but it belongs before anyone calls the cell done, and review finding **F16** says the
same thing.

**Three matching classes are inside 2 sigma and two of them are inside 1.1.** `ea_nmos_load` at
0.61 sigma and `bias_p_group` at 1.07 sigma are
not layout problems: a common centroid removes the systematic part, and the random part is
already larger than the budget. **This is a device-sizing conversation and it should happen
before the cell is drawn a third time.** The cheap direction is visible in the data — both
classes are step-limited on one sign only, and both steps are the same S7 cliff, so anything that
moves the cliff (bias current, XMS strength, Cout) buys margin on all six axes at once.

## Reproduce

```bash
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2 \
       SPICE_USERINIT_DIR=$PDK_ROOT/ihp-sg13g2/libs.tech/ngspice \
       SX_SCRATCH=$HOME/sx-scratch LDO_JOBS=12 LDO_EXP=006 \
       OPENBLAS_NUM_THREADS=1 LDO_NGSPICE=$HOME/local/bin/ngspice

(cd decks/candidate && sha256sum -c SHA256SUMS)   # the benches were never edited
make runs ARGS="--exp 006 --kind bench"           # every brief2_* row of the campaign
```

The campaign driver is `$SX_SCRATCH/ldo-brief2/{pert,campaign,analyse,report,emit_tables,emit}.py`:
`pert.build(mutator)` reads each frozen deck **byte for byte**, rewrites only the
`.subckt ldo_ihp_capless … .ends` block, and hands the 13 decks to `ldo.metrics.run_decks`, so
the perturbed runs use the same measurement definitions as the certified scorecard and land in
the same ledger. Stage → table:

| table | stage(s) | cases |
|---|---|---|
| section 1 floor | `null` | `null_identity`, `null_zeros` |
| section 2 | `cap_vss`, `gate`, `gate_fine`, `cap_big`, `steps` | `c_<net>_vss_<X>f` |
| section 3 | `cap_vdd`, `cap_nb`, `steps` | `c_<net>_<other>_<X>f` |
| section 3b | `gate_only` | `g35_*`, `g25_*`, `no_gate_all3` |
| section 4 | `res`, `res_hand`, `vss_step`, `vss_split` | `r_*`, `r_vssnc_*`, `r_vsscout_*` |
| section 5 | `leak` | `i_<node>_1n`, `i_<node>_10n` |
| section 6 | `match`, `bias_step`, `match_step`, `passive_step` | `dvt_*`, `dw_*`, `dr_*`, `dc_*` |
| section 6b | `match_half` | `dvt_<card>A_10m` |
| section 7 | `op.py` | 0 V ammeters on all 24 MOS + 21 resistor cards, `print all` |
| section 8 | `power_path.py` | `spicexplorer_signoff.current_density` |
| divider sigma | `mc/mc_seg8.spice`, `mc/mc_2k.spice` | 2000 `mc_source` samples each |

**Repo lint.** `make lint` on this checkout reports **2 failures, both pre-existing and neither
in these two files**: `decks/reference/scorecard.json` and `decks/candidate/scorecard.json` each
carry a provenance block with no signed ledger row behind it (the signing run was logged in a
different checkout). The brief adds no lint row.

**Platform equivalence.** `spicexplorer_signoff.sensitivity` already provides these primitives
(`inject_caps`, `inject_resistor(at_devices=…)`, `inject_vsource(pin="g")`, `inject_isource`);
`pert.build` produces the same subckt modulo element names. Two sign conventions differ and are
stated above: the platform injects current *into* the net and puts the source so the device sees
`net + dv`. The piece the platform lacks is a `measure()` that runs all 13 frozen decks — that is
`ldo.metrics.run_decks` over `splice_subckt`, and it is what `sensitivity.sweep` would take as
its callable. **The driver is not durable**: it lives under `$SX_SCRATCH/ldo-brief2/`, which is
evidence scratch, not the repo. Under rule 10 this brief only *proposes*, and does not apply, two
procedural changes: adopt `pert.py` + `campaign.py` as `layout/sensitivity.py` in this repo, or
contribute the `run_decks` `measure()` to `spicexplorer_signoff.sensitivity.sweep` upstream.

Three method changes against the 005 campaign, each of which changes a published number:

1. **Rail injections move every card that touches the rail**, found by scanning the frozen
   subckt, not a hand list — except `VREF` on `vss`, held out because an off-cell reference does
   not float with the cell's return. The 005 `vss` list omitted `XMA`, `XMB` and `XMS` — 13 of
   the ~34 uA — so its 17 Ohm budget was measured on a partial return. The `vss_split` stage then
   holds `XCOUT` out as well, which is how section 4a separates the shared-impedance cliff from
   the rail's own resistance.
2. **Series-R coefficients are two-point slopes** between injected magnitudes. Splitting a node
   adds a fixed offset to `line_reg_mv` at any R, which a one-point slope against the unsplit
   baseline reads as a coefficient.
3. **A "step" is distinguished from a linear violation**: a point is only reported as a hard
   limit when its departure exceeds 2× what the linear coefficient predicts. Without that test,
   `vout_all` at 1 Ohm (S2 = 9.93 mV, exactly `dI × R`) would be
   mislabelled a cliff.

## What was not measured

- **Corners and Monte Carlo on the cell.** Every budget is tt/27 degC (rule 9). The only
  statistical number here is the divider ratio sigma.
- **`vref` and `vss` capacitance** — unmeasurable by construction (section 10).
- **The full net-to-net coupling matrix.** Four pairs were run (`fb`|`vref`, `fb`|`lp_brk`,
  `ea_o1`|`ea_out`, `gate`|`vout`); the rest of section 2 is net-to-rail.
- **Whether the six step-limited axes are independent.** Each was crossed alone. A layout that
  spends 80 % of several at once has not been simulated, and the one combined case that was
  (`r_hand_both_pin_vss32`) is worse than either part.
- **Per-finger resistance inside `XMP`.** The pass device is one card with `m=76`.
- **Junction and gate leakage in absolute terms.** Section 5 gives the budget in nA; converting
  it to a diffusion area needs a PDK leakage number that was not looked up.
- **Self-heating.** The 3.0 mW figure for XMP is `Vds × Id`, not
  a thermal simulation; the per-kelvin divider gradient uses the model card's `tc1`, not an
  extracted thermal profile.
- **The drawn geometry.** Sections 8's "as drawn" rows are quoted from REVIEW.md, not
  re-measured here; this brief does not open the GDS.
