# Layout brief — `ldo_ihp_capless`

**KIND: REFERENCE.** Measured parasitic, matching, leakage and current-density budgets for the
capless FVF LDO, handed from the schematic side to layout. Every number below came out of the
**frozen candidate benches** (`decks/candidate/*.spice`, sha-locked) with one perturbation
spliced into the DUT subckt and all 13 benches re-run through `lab.metrics.run_decks`. Nothing
here is a rule of thumb; where a quantity could not be measured it says so.

| | |
|---|---|
| cell | `ldo_ihp_capless` |
| netlist of record | `circuits/ldo_ihp_capless/pdk/ihp-sg13g2/netlist.spice` |
| netlist sha256 | `18bd9c959a74f1fccb9bc9a9bdf8aed9b3fa1e2ae86774c214a51c8ec02a818b` |
| sizing / scorecard | `decks/candidate/design.json`, `decks/candidate/scorecard.json` |
| benches | the 13 frozen decks in `decks/candidate/`, `SHA256SUMS`-locked |
| corner | `mos_tt` / `res_typ` / `cap_typ`, 27 degC — **every budget below is tt/27** |
| margin fraction | **25%** of the remaining pre-layout margin per spec |
| campaign | 163 perturbed scorecards (13 benches each), ledger tags `brief_*`, `LDO_EXP=005` |
| numeric floor | the null control (a 1 uOhm series R + a zero-value C + a 0 V dVT source + the split Cout array) moves nothing by more than **0.022 deg** of phase margin and **0.0005 %** of Iq; an identity splice reproduces the certified scorecard **bit for bit** |

## 1. The margins the budgets are spent out of

| spec | key | bound | measured (tt/27) | margin left | 25 % of margin | bench resolution |
|---|---|---|---|---|---|---|
| S1 | v_out_v | [1.176, 1.224] | 1.20007 | 0.02393 | 0.00598 | 2e-06 |
| S2 | load_reg_mv | <= 5.0 | 0.028 | 4.972 | 1.24 | 0.001 |
| S3 | line_reg_mv | <= 2.0 | 0.059 | 1.941 | 0.485 | 0.001 |
| S4 | v_dropout_mv | <= 200.0 | 106.143 | 93.86 | 23.5 | 2 |
| S5 | i_q_ua | <= 50.0 | 36.2771 | 13.72 | 3.43 | 0.001 |
| S6 | psrr_1k_db | >= 40.0 | 69.9531 | 29.95 | 7.49 | 0.001 |
| S7 | v_undershoot_mv | <= 150.0 | 104.847 | 45.15 | 11.3 | 0.005 |
| S8 | pm_loop_deg | >= 60.0 | 72.4188 | 12.42 | 3.1 | 0.03 |
| S8lo | pm_loop_lo_deg | >= 60.0 | 72.3829 | 12.38 | 3.1 | 0.03 |
| S8hi | pm_loop_hi_deg | >= 60.0 | 72.3101 | 12.31 | 3.08 | 0.03 |

`v_dropout_mv` is quantised by its own bench (the dropout deck sweeps Vdd in 2 mV steps); the
other resolutions are the null control's residual floored by the deck's print precision. A delta
smaller than the resolution is reported as "no bound", never as zero.

## 2. Net capacitance — budgets, ranked

Unit injection: `C <net> vss` at 1 fF and 10 fF, all 13 benches each. The coefficient quoted is
the 10 fF one; the last column is the 1 fF/10 fF ratio, i.e. the linearity check — every
resolvable net is linear to within 3 %.

| net | role | dS7 mV/fF | dS8 deg/fF | dS6 dB/fF | binds | budget (fF) | hard limit | spent by the 005 cell (fF) | 1 fF / 10 fF |
|---|---|---|---|---|---|---|---|---|---|
| `fb` | divider mid-point, error-amp inverting input | -0.113 | -0.111 | - | S8hi | 27.9 | ~125 fF (S8 = 60 deg by extrapolation from 30/100 fF) | 19.2 | 1.02 |
| `gate` | FVF fold output -> pass-device gate; pull-down-slew-limited | 0.386 | - | - | S7 | 29.3 | **step between 60 and 65 fF** | 28.4 | 1.03 |
| `x1` | FVF control drain / NMOS fold diode (XMA) | 0.245 | - | - | S7 | 46.1 | - | 11.5 | 1.03 |
| `y` | NMOS fold drain / PMOS fold diode (XMCP) | 0.182 | - | - | S7 | 62 | - | 10.6 | 1.02 |
| `ea_o1` | error-amp stage-1 output, Miller dominant pole | -0.181 | -0.00493 | -0.00025 | S8lo | 627 | - | 44.7 | 1 |
| `ea_out` | error-amp stage-2 output = FVF control gate | -0.182 | -0.0049 | - | S8lo | 631 | - | 22.6 | 1 |
| `ea_n` | error-amp NMOS mirror diode (XM3) | -0.0592 | -0.00316 | 0.00022 | S8lo | 980 | - | - | 1 |
| `pbias` | PMOS bias diode node | 0.0007 | - | - | S7 | 1.61e+04 | - | 13.9 | - |
| `ea_tail` | error-amp tail node (XMT drain) | -0.0062 | - | - | - | no bound | - | 12.1 | - |
| `lp_brk` | loop-break marker; divider top = vout sense | -0.0008 | - | - | - | no bound | - | 16.4 | - |
| `nbias` | NMOS bias diode node | -0.0068 | - | - | - | no bound | - | - | - |
| `vout` | output pin / pass drain / FVF source / Cout | -0.0008 | - | - | - | no bound | - | 72 | - |
| `vdd` | supply pin | - | - | - | - | no bound | - | 43.3 | - |

**Read a budget above ~1 pF as "no bound".** `pbias` is the example: its S7 delta at 10 fF is
0.007 mV against a 0.005 mV resolution, so it clears the floor by a hair and the arithmetic
produces a 16 nF "budget" and a meaningless 1 fF/10 fF ratio (blanked above). Nothing in this
cell has a physical capacitance budget in the nanofarads; those rows are don't-cares
(section 10), not constraints. The same caution applies to `ea_o1`/`ea_out`/`ea_n` at ~630 fF —
real, but far outside anything a router will build.

**The two that bind.**

- **`gate` — 29 fF, and a hard step at 60-65 fF.** The pass gate is pull-down-slew-limited
  (`journal/fvf-gate-cap-is-slew.md`), so S7 rises +0.386 mV per fF. Above ~60 fF the sink can no
  longer slew the gate inside the load step and the mechanism changes: S7 130.98 mV at 60 fF,
  **191.78 mV at 65 fF**, 207.68 at 70 fF, with recovery stepping 0.247 -> 0.55 us. That is the
  same signature as the `c_ff_w` cliff of 003 section 2 and the bias-current threshold of 003
  section 3 — a change of mechanism, not a degradation of one. **The 005 cell already spends
  28.4 fF here, i.e. 97 % of the budget and 47 % of the distance to the step.** There is no room
  on this net; see section 3 for the one way to buy some.
- **`fb` — 28 fF, binding S8.** -0.111 deg of phase margin per fF (the divider-node pole the
  0.1 pF `XCFF` exists to cancel). S8 reaches its 60 deg bound at about 125 fF. `fb` also
  *improves* S7 slightly (-0.113 mV/fF) — do not bank that; S8 runs out first.

`x1` (46 fF) and `y` (62 fF) are the fold mirror nodes and matter for the same slew reason, one
step removed. Everything else on this list has hundreds of fF or no measurable bound.

## 3. Which rail (or neighbour) a track couples to

| injection | C (fF) | S7 (mV) | S8 (deg) | coefficient | budget |
|---|---|---|---|---|---|
| `gate` -> vss | 10 | 108.702 | 72.4174 | +0.386 mV/fF | 29 fF (S7) |
| `gate` -> vdd | 30 | 118.115 | 72.4146 | identical to `gate` -> vss at 30 fF (118.115 mV) | 29 fF (S7) |
| `gate` -> vout | 10 | 105.012 | 72.4001 | +0.0165 mV/fF at 10 fF, rising to +0.0386 at 100 fF (not linear) | **100 fF hard limit** (in box there; step 100-300 fF, not bracketed) |
| `fb` -> vss | 10 | 103.721 | 71.3108 | -0.111 deg/fF | 28 fF (S8) |
| `fb` -> vdd | 10 | 103.721 | 71.3108 | same S8, PSRR **+0.122 dB/fF** | 28 fF (S8) |
| `fb` -> vref | 10 | 103.721 | 71.3108 | same as fb -> vss | 28 fF (S8) |
| `fb`+`vref` both -> vss | 10 each | 103.721 | 71.3108 | same as fb alone | 28 fF (S8) |
| `ea_o1` <-> `ea_out` | 30 | 104.849 | 72.415 | adds to XCC; S7 unmoved | > 1 pF |
| `ea_o1` -> vss | 50 | 98.128 | 72.1725 | -0.181 mV/fF (S7 improves) | 630 fF (S8) |

Three results the designer can act on:

1. **`gate` to `vout` is much cheaper than `gate` to a rail — but the ratio is not a constant.**
   The pass gate is bootstrapped to its own source during the load step, so coupling to `vout`
   divides by the bootstrap factor; **route the gate track over/beside the `vout` bus, not
   between the rails.** The coefficient is 0.0165 mV/fF at 10 fF, 0.0187 at 30 fF and 0.0386 at
   100 fF: the discount *shrinks* as the load grows (24x, 21x, then 10x against the
   0.386 mV/fF to-rail slope). 100 fF of gate-to-vout gives S7 = 108.71 mV, which is the same
   five digits as 10 fF of gate-to-rail — one coincident point, not a law. The step is somewhere
   between 100 and 300 fF and was **not bracketed**; the to-rail step is at 60-65 fF, so the
   cliff moves out by only 1.5-5x, not 10x. **Treat 100 fF as the hard limit on gate-to-vout**
   until someone brackets it.
2. **vdd and vss are interchangeable** for every net measured: `c_gate_vdd_30f` and
   `c_gate_vss_30f` give identical scorecards. Both rails are AC ground here; only the total
   node capacitance matters. The one exception is PSRR on `fb`.
3. **`fb` to vdd buys PSRR**: +0.122 dB per fF at 1 kHz (and +0.023 dB/fF at 1 MHz, against
   -0.028 dB/fF to vss). At `fb`'s 28 fF budget that is up to +3.4 dB. Measured, exploitable,
   **not needed** — S6 has 30 dB of margin. Take it only if it is free.
4. **`ea_o1` <-> `ea_out` coupling is not a load.** 30 fF between them leaves S7 at 104.85 mV
   (baseline 104.847) — it simply adds to the 4.4 pF Miller cap. This matters for reading the
   005 extraction: the 44.7 fF on `ea_o1` and 22.6 fF on `ea_out` reported by kpex in CC mode are
   largely *mutual*, so the -0.18 mV/fF S7 credit those nets show for **deliberate C to a rail**
   must **not** be banked from incidental routing. Per-net budgets in section 2 are to-rail;
   a CC-mode per-net sum is an upper bound on the to-rail part.

## 4. Series resistance — the Kelvin decision

Injection: the net is split and a resistor inserted between the named devices and the rest.

| segment | what the R is between | budget (Ohm) | binds | coefficient (per Ohm) |
|---|---|---|---|---|
| `vout_all` | vout bus + pin, sense INSIDE the drop (divider tapped at the pass drain) | 0.126 | S2 | load_reg_mv +9.9/Ohm, v_undershoot_mv -8.967/Ohm |
| `vdd` | supply rail resistance ahead of the whole cell (bulk ties included) | 1.77 | S4 | line_reg_mv +0.003333/Ohm, v_dropout_mv +13.24/Ohm, v_undershoot_mv +0.35/Ohm |
| `vout_pass_only` | R between the pass drain and everything else (sense + Cout + XMC at the pin) | 1.78 | S4 | v_dropout_mv +13.21/Ohm, v_undershoot_mv +0.2767/Ohm |
| `vout_sense_at_pin` | R between (pass drain + XMC + Cout) and the pin; VLP/divider at the pin | 2.35 | S4 | load_reg_mv +0.031/Ohm, line_reg_mv +0.001/Ohm, v_dropout_mv +10/Ohm |
| `vss` | cell ground return (Iq only; the load returns off-cell) | 17 | S6 | load_reg_mv -0.01/Ohm, line_reg_mv +0.01/Ohm, psrr_1k_db -0.4413/Ohm |
| `lp_brk` | series R between the sense point and the divider top | 1.1e+04 | S1 | line_reg_mv +1e-06/Ohm, psrr_1k_db -1.23e-06/Ohm, v_out_v +5.42e-07/Ohm |
| `gate` | series R between the fold output and the pass gate | 2.51e+04 | S7 | v_undershoot_mv +0.00045/Ohm |
| `fb_tap` | series R in the XM1 gate lead (feedback tap) | 4.53e+05 | S8lo | psrr_1k_db +2.285e-06/Ohm, v_undershoot_mv -0.0001863/Ohm, pm_loop_deg -6.83e-06/Ohm |
| `vref` | series R in the XM2 gate lead (reference tap) | 8.56e+05 | S8lo | line_reg_mv +1e-08/Ohm, psrr_1k_db -2.286e-06/Ohm, v_undershoot_mv -4.905e-05/Ohm |

**This is the tightest budget in the brief and it is a floorplan decision, not a width.**
With the divider tapped at the pass drain (everything inside the drop) the budget is
**0.126 Ohm**, because S2 is then literally `dI x R`: the measured coefficient is 9.9 mV/Ohm
against a 9.9 mA load step. Move the `VLP`/divider tap to the **vout pin** and the same metal is
allowed **1.78 Ohm** — 14x more — and S2 stops responding at all (0.028 mV at 1 Ohm, unchanged).
Sense at the pin.

`vdd` (1.77 Ohm) binds through dropout at 13.2 mV/Ohm, again just `I x R`. `vss` is 17 Ohm and
binds through PSRR (-0.44 dB/Ohm). `fb`, `lp_brk`, `gate` and `vref` are kOhm-class: series
resistance in the signal taps is a don't-care.

## 5. Hi-Z nodes and the leakage budget

Injection: `I <node> vss dc 1 nA` — **positive = current pulled OUT of the node to ground**, i.e.
a leak. (The platform's `inject_isource` uses the opposite sign.)

| node | branch current (nA) | budget (nA) | budget (pA) | binds | coefficient |
|---|---|---|---|---|---|
| `fb` | 543.4 | 5.43 | 5.43e+03 | S1 | v_out_v +0.001101/nA, line_reg_mv +0.001/nA |
| `ea_n` | 2282 | 12.5 | 1.25e+04 | S6 | v_out_v -3.7e-05/nA, line_reg_mv +0.007/nA |
| `ea_o1` | 2284 | 153 | 1.53e+05 | S1 | v_out_v +3.9e-05/nA, load_reg_mv -0.001/nA |
| `ea_out` | 2646 | 327 | 3.27e+05 | S6 | psrr_1k_db -0.02287/nA, v_undershoot_mv +0.006/nA |
| `nbias` | 2515 | 491 | 4.91e+05 | S7 | i_q_ua -0.01083/nA, psrr_1k_db -0.00173/nA |
| `gate` | 8155 | 1.26e+03 | 1.26e+06 | S5 | i_q_ua +0.00273/nA, v_undershoot_mv -0.009/nA |
| `pbias` | 4561 | 1.36e+03 | 1.36e+06 | S5 | i_q_ua +0.00253/nA |
| `y` | 8455 | 1.41e+03 | 1.41e+06 | S7 | v_undershoot_mv +0.008/nA |
| `lp_brk` | 543.4 | no bound | - | - | - |
| `ea_tail` | 4566 | no bound | - | - | psrr_1k_db +0.01301/nA |
| `x1` | 4835 | no bound | - | - | v_undershoot_mv -0.012/nA |
| `vout` | 5378 | no bound | - | - | - |

- **`fb` — 5.43 nA.** The divider carries 0.543 uA through 1.1 MOhm arms, so the node's Thevenin
  resistance is 552 kOhm and the loop multiplies the error by the divider ratio: the measured
  1.101 mV per nA is exactly `552 kOhm x 2`. **No ESD diode, no antenna diode and no large
  diffusion on `fb` or `lp_brk` without a leakage number** — `fb` drives XM1's gate, so a long
  Metal1 track will attract an antenna fix, and that fix is what would spend this budget.
- **`ea_n` — 12.5 nA, binding S6 at -0.597 dB/nA.** It is a diode-connected node, so it looks
  low-impedance, but unbalancing the error amp's mirror is what PSRR is made of. `ea_o1`, the
  other leg, moves PSRR the *other* way (+0.633 dB/nA) — the two are the same mechanism.
- Everything else has 300 nA or more, which no realistic junction has at these areas.

## 6. Matching

MOS mismatch is injected as a dc source in series with one member's gate (**the device sees
`net - dVT`**; the platform's `inject_vsource` is the opposite sign) and as a 1 % `w=` change on
one card. The 1-sigma columns are the PDK's own numbers, not estimates:
`delvto = agauss(0, A_VT/sqrt(m*L*W))` with A_VT = 2.0 mV*um (lv nmos) / 2.5 mV*um (lv pmos), and
`dw_mm` = 4 nm / 5 nm absolute (`sg13g2_moslv_mismatch.lib`); the pair sigma is sqrt(2) x that.
"headroom" = tolerated / 1 sigma. Pattern: < 3 sigma -> common centroid + dummies;
3-6 -> interdigitated + dummies; 6-20 -> same row, same orientation; > 20 -> any.

| class | devices | W/L (um) | linear tol. dVT (mV) | out of box at (mV, first tested pt.) | PDK 1 sigma dVT (mV) | headroom (sigma) | binds | tol. dW (%) | 1 sigma dW (%) | pattern |
|---|---|---|---|---|---|---|---|---|---|---|
| `ea_in_pair` | `XM1` + `XM2` | 9.53/0.5 | 3 | **20** | 1.62 | 1.85 | S1 | 1.99 | 0.0742 | common_centroid+dummies |
| `ea_nmos_load` | `XM3` + `XM4` | 2.95/1 | 3.46 | **20** | 1.65 | 2.1 | S1 | 1.87 | 0.192 | common_centroid+dummies |
| `bias_n_group` | `XMB0` + `XMB1` + `XMS` | 1/1 | 8.92 | - | 2.83 | 3.15 | S5 | 13.4 | 0.566 | interdigitated+dummies |
| `bias_p_group` | `XMBP` + `XMT` + `XM6` | 10/1 | 12.4 | **8** | 1.12 | 7.16 | S8lo | 66.4 | 0.0707 | same_row_same_orientation |
| `fvf_fold_n` | `XMA` + `XMB` | 5.79/0.5 | 29.8 | - | 1.66 | 17.9 | S5 | 297 | 0.0977 | same_row_same_orientation |
| `fvf_fold_p` | `XMCP` + `XMD` | 9.02/0.5 | 31.9 | - | 1.66 | 19.2 | S7 | 81.2 | 0.0784 | same_row_same_orientation |
| `pass_array` | `XMP` | 10/0.13 x19 | - | - | 0.503 | - | - | 40.3 | 0.0707 | any |

| class | devices | unit | tolerated | 1 sigma (%) | headroom (sigma) | binds | pattern |
|---|---|---|---|---|---|---|---|
| `fb_divider` | `XR1`, `XR2` | %dR/R on one arm | 1 | 0.587 | 1.71 | S1 | common_centroid+dummies |
| `mim_feedforward` | `XCFF` | %dC/C | 166 | 1.25 | 133 | S7 | any |
| `mim_miller` | `XCC` | %dC/C | 147 | 0.185 | 794 | S6 | any |
| `bias_resistor` | `XRB` | %dR/R | 20.2 | - | - | S7 | any |
| `mim_cout` | `XCOUT (m=4)` | %dC/C | no bound | 0.0862 | no bound | - | any |
| `mim_cout_unit` | `one XCOUT unit` | %dC/C on 1 of 4 | no bound | 0.172 | no bound | - | any |

**Read this table with the step column.** `bias_p_group` (`XMBP` -> `XMT`) looks catastrophic if
you fit a line through the 10 mV point: S7 there is 235.5 mV, out of the box. It is not a line.
S7 is **flat** from 1 to 7 mV of dVT (104.85 -> 106.65 mV) and **steps to 212.8 mV at 8 mV** —
the tail current has risen enough that the stage-1:stage-2 balance moves the FVF out of its
slewing regime. **Only one sign is dangerous.** The step is on the side that makes `XMT` carry
*more* current than `XMBP`'s ratio dictates (Iq 36.28 -> 36.85 uA across the step); the opposite
sign is free and slightly good — -5 mV gives S7 = 103.68 mV and -10 mV gives 102.59 mV at
Iq 35.62 uA. A systematic layout offset that *weakens* `XMT` costs nothing; one that strengthens
it by 8 mV loses the cell. Two more measurements pin the mechanism: scaling the *whole* bias
(`dvt_XMB1_10m`, Iq 36.28 -> 34.95 uA) leaves S7 at 104.65 mV, and dVT on `XM6` alone *improves*
S7 to 102.84 mV with +2.3 deg of phase margin. **It is the XMT:XM6 ratio, not the bias
magnitude.** `XMBP`(10 um) : `XMT`(10 um) : `XM6`(5.53 um) are one matching group and the
XMT:XM6 leg is not a unit ratio — a note for design as much as for layout (the same shape as
`XMS` at L = 0.95 um against `XMB0` at L = 1.0 um).

**The three that need a common centroid:**

- **`XR1`/`XR2`, the 1:1 divider — 1.71 sigma, the tightest class.** It is the only thing that
  sets Vout against Vref, and 1 % of single-arm dR/R costs 5.87 mV (measured at 0.1/0.3/1/3 %,
  linear throughout), so the quarter margin is spent at 1.00 % of dR/R. A 2000-sample Monte Carlo with the PDK's own `res_typ_mismatch` models
  gives sigma(R2/(R1+R2)) = 0.2934 %, i.e. **sigma(Vout) = 3.52 mV** against a 5.98 mV quarter
  margin. sigma scales as 1/sqrt(area) over 85 -> 680 um, so interdigitation buys nothing against
  the *random* part; it buys the *gradient* part, which is where the 3 mW of XMP sits.
- **`XM1`/`XM2`, the error-amp input pair — 1.85 sigma.** Perfectly linear: 1.99 mV of Vout per
  mV of dVT (2x, the divider ratio) from 1 to 20 mV. dW is 27x looser (0.074 % sigma against a
  1.99 % tolerance), so this pair is a *threshold-voltage* matching problem: common centroid,
  dummies, same orientation, and equal thermal environment.
- **`XM3`/`XM4`, the error-amp NMOS load — 2.10 sigma**, binding S1 at 1.73 mV/mV with PSRR
  (-1.20 dB/mV) close behind. `dvt_XM3_10m` and `dvt_XM4_10m` move Vout by +17.3 and -17.3 mV:
  symmetric, as a 1:1 mirror should be.

The FVF folds (`XMA`/`XMB`, `XMCP`/`XMD`), the bias NMOS group and the pass array are 18 sigma
or looser and need nothing beyond same row / same orientation.

## 7. Devices — currents, voltages, wells

Measured at the operating point of the frozen `dc_op` deck with 0 V ammeters spliced into every
drain (model-agnostic), at no load and at a 10 mA load. Current is into the drain node, so it is
**negative for a PMOS**; `Vds`/`Vgs` are signed for the device type (positive = on).

| device | group | flavour | I no load (uA) | I at 10 mA (uA) | Vds (mV) | Vgs (mV) | Vsb (mV) | bulk / well | Vds at 10 mA (mV) |
|---|---|---|---|---|---|---|---|---|---|
| `XMB0` | bias | lv_nmos | 2.515 | 2.5146 | 366.5 | 366.5 | 0 | vss | 366.5 |
| `XMB1` | bias | lv_nmos | 4.561 | 4.5613 | 1062 | 366.5 | 0 | vss | 1062 |
| `XMBP` | bias | lv_pmos | -4.561 | -4.5613 | 438.1 | 438.1 | 0 | vdd | 438.1 |
| `XMT` | error amp | lv_pmos | -4.566 | -4.5664 | 448.6 | 438.1 | 0 | vdd | 448.6 |
| `XM1` | error amp | lv_pmos | -2.282 | -2.2827 | 765.2 | 451.4 | 449 | vdd | 765.2 |
| `XM2` | error amp | lv_pmos | -2.284 | -2.2836 | 764.3 | 451.4 | 449 | vdd | 764.7 |
| `XM3` | error amp | lv_nmos | 2.282 | 2.2827 | 286.2 | 286.2 | 0 | vss | 286.2 |
| `XM4` | error amp | lv_nmos | 2.284 | 2.2836 | 287.1 | 286.2 | 0 | vss | 286.7 |
| `XM5` | error amp | lv_nmos | 2.646 | 2.6443 | 763.5 | 287.1 | 0 | vss | 776.6 |
| `XM6` | error amp | lv_pmos | -2.646 | -2.6443 | 736.5 | 438.1 | 0 | vdd | 723.4 |
| `XMC` | FVF | lv_pmos | -4.835 | -3.5426 | 921.2 | 436.6 | 300 | vdd | 934.1 |
| `XMA` | FVF | lv_nmos | 4.835 | 3.5426 | 278.9 | 278.9 | 0 | vss | 265.9 |
| `XMB` | FVF | lv_nmos | 8.455 | 6.518 | 1048 | 278.9 | 0 | vss | 1064 |
| `XMCP` | FVF | lv_pmos | -8.455 | -6.518 | 452.3 | 452.3 | 0 | vdd | 435.6 |
| `XMD` | FVF | lv_pmos | -8.155 | -6.8758 | 285.9 | 452.3 | 0 | vdd | 870.6 |
| `XMS` | FVF | lv_nmos | 8.155 | 6.8765 | 1214 | 366.5 | 0 | vss | 629.4 |
| `XMP` | output | lv_pmos | -5.378 | -10004 | 299.9 | 285.9 | 0 | vdd | 300 |
| `XRB` | bias | rhigh | 2.515 | 2.5146 | 1500 | - | 0 | vss | 1500 |
| `XR1` | feedback | rhigh | 0.5434 | 0.54334 | 600 | - | 0 | vss | 600 |
| `XR2` | feedback | rhigh | 0.5434 | 0.54334 | 600 | - | 0 | vss | 600 |

- All nine PMOS have bulk = vdd in the netlist of record. XMC's source is `vout` (Vsb = 300 mV) and XM1/XM2's source is `ea_tail` (Vsb = 449 mV): these are DELIBERATE. Do not give XMC or the input pair its own nwell tied to its source -- that is a design change, not a layout fix.
- Separate nwell islands are therefore for ISOLATION only, all tied to vdd: (a) XMP alone (hot, 10 mA, fast dV/dt); (b) quiet: XMBP/XMT/XM1/XM2/XM6; (c) FVF: XMC/XMCP/XMD.
- All eight NMOS have bulk = vss in the common p-substrate; the rhigh bodies (`bn`) are vss as well. Put a continuous ptap ring around the error amp and a second one between XMP and everything else; the 005 cell uses periodic point taps every 12 um instead.

## 8. Power path — per-net DC current budget

Currents measured (`i_supply` and the XMP ammeter at a 10 mA load); limits from the PDK's own
**`SG13G2_os_process_spec.pdf` section 2.15**, "Maximum Current Densities", 11 years at 105 degC,
scored with `spicexplorer_signoff.current_density.check_current_density`. Measured:
**I(vdd) = 10.0318 mA**, **I(XMP) = 10.0041 mA**,
**0.5265 mA per finger** (m = 19) but
**1.0531 mA per shared diffusion column**, and only
**27.7 uA** on the cell's own `vss` — the bench returns the load
current to the top-level ground, so the 10 mA ground return is a *chip*-level path, not a
cell-level one. If the ground return is routed through this cell, `vss` inherits the `vdd` row.

**As drawn today** (`layout/gen_ldo.py` at `LayoutParams` defaults: `rail_w` 0.8 um, vout bus
0.6 um, `W_M1` = `W_M2` = 0.2 um, `VPAD` 0.38 um so `vstack` places exactly one via per
transition) — worst over-factor **27.8x**:

| net | segment | carries (mA) | drawn | limit (mA) | over |
|---|---|---|---|---|---|
| `vdd` | cell vdd rail (rail_w) | 10.03 | metal1 0.8um | 0.8 | **12.5x** |
| `vout` | pass drain bus / m1h strap bar (one conductor) | 10 | metal1 0.6um | 0.6 | **16.7x** |
| `vout` | vout channel track / pin (W_M1) | 10 | metal1 0.2um | 0.36 | **27.8x** |
| `vout` | vout M1->M2 riser (to_track, W_M2) | 10 | metal2 0.2um | 0.6 | **16.7x** |
| `vout` | vout riser Via1 (vstack, VPAD=0.38) | 10 | via1 x1 | 0.4 | **25x** |
| `vdd` | pass source column (shared, 2 fingers) | 1.053 | metal1 0.2um | 0.36 | **2.92x** |
| `vout` | pass drain column (shared, 2 fingers) | 1.053 | metal1 0.2um | 0.36 | **2.92x** |
| `vout` | pass drain END column (1 finger) | 0.5265 | metal1 0.2um | 0.36 | **1.46x** |
| `vss` | cell vss rail (Iq only) | 0.0277 | metal1 0.8um | 0.8 | 0.035x |

**Why "per column" and not "per finger".** The generator draws `nf` = 19 channels as
`nf + 1` = 20 diffusion columns (`gen_ldo.py`: `cols = [sx + k*pitch for k in range(nf+1)]`,
`S = cols[0::2]`, `D = cols[1::2]`), and every *interior* column is shared by the two channels
either side of it. Per side that is 9 columns at 2 x I_finger = 1.053 mA plus one end column at
0.527 mA (9x2 + 1 = 19 fingers). The Metal1 riser (`m1v`, `W_M1` = 0.2 um) on a shared column is
therefore **2.9x over**, not 1.46x. This is finding **B1** of `review-002` ("~1 mA ... 2.8x"),
which is right; the journal entry's 0.53 mA / 1.5x undercounts by exactly the shared-diffusion
factor of two.

**Minimum width / via count per segment.** The arithmetic minimum is `I / J`:
TopMetal1 **0.67 um** for the output (and
0.67 um for vdd) — below `TM1.a`'s 1.64 um minimum width, so on
TopMetal1 the electromigration requirement is *free* and it is the floorplan (`TM1.b` 1.64 um
space, `TV1.d` 0.42 um enclosure) that costs. Metal1 would need
**10.0 um**, which does not fit the routing channel; Metal5 needs
5.0 um. Vias: **25 Via1** (or Via2/3/4)
for 10 mA at 0.4 mA each, **7 TopVia1** at 1.4 mA each, and one
TopVia2. Per shared S/D column: **1.05 um of Metal1**
(0.2 um is 2.9x over) or 0.53 um of Metal2 reached through
2.6 -> **3 Via1 per column**, and
**3.5 diffusion contacts** — 4 as an integer, which the PDK
device cell's own contact row over a 10 um finger far exceeds (not independently counted).

**The column riser is the one segment a wider wire may not fix.** 1.05 um of Metal1 per shared
column is wider than the S/D column pitch of a 0.13 um-L device, so the designer has three
options, in order of preference: (i) run a **Metal2 (or Metal2+Metal3) plate over the whole
pass-device array**, stitched down to every column, and treat the 0.2 um Metal1 riser as a stub
that only has to reach the plate; (ii) **raise `nf`** until the shared-column current falls
under the 0.36 mA flat allowance for a minimum-width Metal1 riser — that needs
`nf >= 2 x 10.0 mA / 0.36 mA` = **56 fingers** (3.4 um each at the same 190 um total width);
(iii) widen the riser to whatever the pitch allows — but note this buys **nothing** on Metal1:
every width from 0.16 to 0.36 um gets the same flat 0.36 mA allowance, so a riser that stays
inside a ~0.5 um column pitch is still 2.9x over. Do not fall back on a Blech-length argument.

Option (ii) is **not a layout knob**: changing `nf` changes `x_dut_xmp_w`/`x_dut_xmp_m` in
`design.json`, so the certified benches no longer describe the device and LVS against
`w = 10 um, m = 19` fails. It is listed so the trade is visible; taking it means re-running the
003 sizing campaign and re-certifying, which is a design decision, not a layout one.

The same wide-metal argument applies to the `m1h` strap bar that collects the columns: it is the
same conductor as the "pass drain bus" row above and carries the *whole* 10 mA at 0.6 um
(16.7x over).

**What to draw** (>= 1.5x headroom on every segment except the pitch-limited Metal1 column
riser, which only reaches 1.05x and is why the Metal2 plate is the preferred option;
`passed = True`):

| net | segment | carries (mA) | drawn | limit (mA) | over |
|---|---|---|---|---|---|
| `vdd` | vdd strap, TopMetal1 over the stack | 10.03 | topmetal1 2um | 30 | 0.334x |
| `vout` | vout strap, TopMetal1 over the stack | 10 | topmetal1 2um | 30 | 0.333x |
| `vout` | vout M5->TopMetal1 stitch | 10 | topvia1 x12 | 16.8 | 0.595x |
| `vdd` | vdd M5->TopMetal1 stitch | 10.03 | topvia1 x12 | 16.8 | 0.597x |
| `vout` | vout M5 landing pad under the TopVia1 row | 10 | metal5 8um | 16 | 0.625x |
| `vdd` | vdd M5 landing pad | 10.03 | metal5 8um | 16 | 0.627x |
| `vout` | vout M1->M2 stitch | 10 | via1 x40 | 16 | 0.625x |
| `vout` | vout M2->M3 | 10 | via2 x40 | 16 | 0.625x |
| `vout` | vout M3->M4 | 10 | via3 x40 | 16 | 0.625x |
| `vout` | vout M4->M5 | 10 | via4 x40 | 16 | 0.625x |
| `vdd` | vdd M1->M2 stitch (same count as vout) | 10.03 | via1 x40 | 16 | 0.627x |
| `vdd` | pass source column, shared (Metal1) | 1.053 | metal1 1.1um | 1.1 | 0.957x |
| `vout` | pass drain column, shared (Metal1) | 1.053 | metal1 1.1um | 1.1 | 0.957x |
| `vdd` | pass source column, shared (Metal2 plate) | 1.053 | metal2 1um | 2 | 0.527x |
| `vout` | pass drain column, shared (Metal2 plate) | 1.053 | metal2 1um | 2 | 0.527x |
| `vdd` | Via1 per shared column up to the Metal2 plate | 1.053 | via1 x3 | 1.2 | 0.878x |
| `vout` | Via1 per shared column up to the Metal2 plate | 1.053 | via1 x3 | 1.2 | 0.878x |
| `vout` | diffusion contacts per shared column | 1.053 | contact x4 | 1.2 | 0.878x |
| `vss` | cell vss rail, unchanged | 0.0277 | metal1 0.8um | 0.8 | 0.035x |

Three notes for the journal entry `metal-current-density-is-nobodys-check.md`: it generalises
"Metal1 1 mA/um" to all metals — **Metal2-Metal5 are 2 mA/um above 0.3 um and a flat 0.6 mA
between 0.2 and 0.3 um**, so the `vout` M1->M2 riser is 16.7x over rather than 27.8x. And the
0.36 mA / 0.6 mA numbers are *flat totals* in a qualified narrow band, not densities; below
0.16 um (Metal1) / 0.2 um (Metal2-5) the process spec gives no number at all. And its
"0.53 mA per finger, 1.5x" for the pass array is a *per-channel* number: interior diffusion
columns are shared, so the conductor carries 1.05 mA and is 2.9x over, as `review-002` B1 says.

## 9. Structure, pin intent, keep-aparts

**Symmetry axis: vertical, one local axis per matched pair; the cell has NO global differential axis.** The only differential net pair is (fb, vref) at the error-amp inputs and `vref` is driven by an ideal source inside the subckt, so balanced and one-sided injection measure the same thing (c_fbvref_bal_10f == c_fb_vss_10f, S7 103.72 mV / PM 71.311 deg in both). Mirror pairs:
`XM1`/`XM2`, `XM3`/`XM4`, `XMA`/`XMB`, `XMCP`/`XMD`, `XMBP`/`XMT`, `XR1`/`XR2`.

**Pin intent** (the cell of record has three pins — `vdd`, `vout`, `vss`; `vref` and `fb` are
internal today):

| side | pin |
|---|---|
| top | vdd (= vin; TopMetal1 strap over the device stack) |
| bottom | vss (Metal1 rail is enough: the cell carries only Iq on it) |
| right | vout (TopMetal1, beside the pass device; the divider must tap HERE) |
| left | vref (future pin, when a bandgap replaces VREF); fb (test/trim only; keep away from the output bus) |

**Keep apart:**

- XMP dissipates 3.0 mW at 10 mA (0.30 V x 10.0 mA). rhigh tc1 = -2300 ppm/K, and 1 % of single-arm dR/R costs 5.87 mV of Vout, so 1 K of gradient across XR1<->XR2 costs 1.35 mV = 23 % of the S1 quarter-margin. Keep the divider serpentines at the far end from XMP (the 005 floorplan already does) and interdigitate them ABBA.
- XRB sets every branch current from the same tc1: keep it out of XMP's heat too.
- `gate` and `vout` carry the fast edges (gate slews 1.21 -> 0.63 V in ~125 ns). Keep them off `fb`, `lp_brk` and `ea_o1`.

**MIM plate orientation** (bottom plate = Metal5, the plate kpex extracts; top-plate coupling is
not extracted at all, so put the sensitive terminal on top):

- XCFF: bottom plate (Metal5, the plate kpex extracts) on `lp_brk`, not on `fb` -- `fb` has a 28 fF budget and `lp_brk` has none.
- XCOUT: bottom plate on `vss`.
- XCC: bottom plate on `ea_out` (the lower-Z stage-2 side); the C sensitivities of `ea_o1` and `ea_out` are equal to 3 digits, so this is a tie broken by impedance.

## 10. Don't-cares

| axis | explicitly not a constraint |
|---|---|
| capacitance | `vout`, `vdd`, `lp_brk`, `ea_tail`, `nbias`, `pbias`, `ea_n`, `ea_o1`, `ea_out`, `vref`, `vss` |
| series_resistance | `lp_brk`, `gate`, `fb`, `vref`, `vss` |
| leakage | `lp_brk`, `ea_tail`, `x1`, `vout`, `y`, `pbias`, `gate` |
| matching | `XMA/XMB`, `XMCP/XMD`, `XMB0/XMB1`, `XMBP/XM6 (as a pair; the XMBP/XMT leg is NOT)`, `XMP fingers`, `XCOUT unit-to-unit`, `XCC`, `XCFF` |

A net can be a don't-care on one axis and the tightest constraint on another: `gate` has no
series-resistance and no leakage constraint and the smallest capacitance budget in the cell;
`vout` and `vdd` have no capacitance constraint and the two tightest resistance budgets.

Two nets are unmeasurable rather than generous, and are listed as such: `vref` is driven by an
ideal source inside the subckt (`c_vref_vss_10f` reproduces the baseline exactly), and `vss` is
the reference node. When a real bandgap replaces `VREF`, `vref` must be re-measured.

## What I would watch

The one number I would not let out of sight is **28.4 fF on `gate`**. The 005 cell spent it
before anyone wrote a budget, it is 97 % of the quarter-margin allowance, and the failure past
60 fF is a step rather than a slope — there is no graceful degradation to trade against. The
escape is cheap and structural: at these levels `gate` coupled to `vout` costs 10-24x less than
`gate` coupled to a rail, so the gate track wants to run beside the output bus rather than in the
rail channel — with 100 fF as the hard limit there, because the gate-to-vout step was not
bracketed. The second is the divider
tap. Tapping `VLP` at the pass drain turns the whole output metallisation into an S2 problem with
a 0.126 Ohm allowance; tapping at the pin makes the same metal a dropout problem with 1.78 Ohm,
and dropout has 94 mV of margin. That is a floorplan decision worth more than any width.

Third, everything here is **tt / 27 degC**. 003 section 3 already shows S7 failing at ss/-40 and
S5 at ff/125 *before* layout, and the S7 margin at tt/125 is only 21.4 mV — about 55 fF of `gate`
at this coefficient, an extrapolation nobody has measured. Every fF on `gate` is therefore spent
twice. The corner re-run belongs after the layout exists, not before.

Finally, three matching classes (`XR1`/`XR2` at 1.71 sigma, `XM1`/`XM2` at 1.85, `XM3`/`XM4` at
2.10) sit inside 3 sigma of the PDK's own random mismatch. Layout cannot fix the random part —
it can only avoid adding a systematic one. If the S1 window matters at yield, that is a device
sizing conversation, not a layout one, and it should happen before the cell is drawn twice.

## Reproduce

```bash
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2 \
       SPICE_USERINIT_DIR=$PDK_ROOT/ihp-sg13g2/libs.tech/ngspice \
       SX_SCRATCH=$HOME/sx-scratch LDO_JOBS=16 LDO_EXP=005

(cd decks/candidate && sha256sum -c SHA256SUMS)   # the benches were never edited
make runs ARGS="--exp 005 --kind bench"       # every brief_* row of the campaign
```

The campaign driver is `$SX_SCRATCH/ldo-brief/{pert,campaign,analyse,report,emit}.py`:
`pert.build(mutator)` reads each frozen deck **byte for byte**, rewrites only the
`.subckt ldo_ihp_capless ... .ends` block, and hands the 13 decks to `lab.metrics.run_decks`, so
the perturbed runs use the same measurement definitions as the certified scorecard and land in
the same ledger. The operating point is `op.py` (0 V ammeters into every drain, `print all`); the
divider mismatch sigma is `mc/mc_2k.spice` (2000 `mc_source` samples on `res_typ_mismatch`); the
power path is `power_path.py` through `spicexplorer_signoff.current_density`.

**Platform equivalence.** `spicexplorer_signoff.sensitivity` already provides these primitives.
`pert.build` was checked against them on the frozen `dc_op` deck: `inject_caps`,
`inject_resistor(at_devices=...)`, `inject_vsource(pin="g")` and `inject_isource` produce the
same subckt modulo element names, and the `load_regulation` run of the 0.1 Ohm `vout` case is
**numerically identical** (`load_reg = 0.001018`). Two sign conventions differ and are stated
above: the platform injects current *into* the net and puts the source so the device sees
`net + dv`. The only piece the platform lacks for this repo is a `measure()` that runs all 13
frozen decks: that is `lab.metrics.run_decks` over `splice_subckt`, and it is what
`sensitivity.sweep` would take as its callable. **The driver is not durable** — it lives under
`$SX_SCRATCH/ldo-brief/`, which is evidence scratch, not the repo. Under rule 10 this brief only
*proposes*, and does not apply, two procedural changes: adopt `pert.py` + `campaign.py` as
`layout/sensitivity.py` in this repo, or contribute the `run_decks` `measure()` to
`spicexplorer_signoff.sensitivity.sweep` upstream. Until one of those happens, re-running this
campaign means re-writing the splicer.

**`make lint` state.** The repo lints RED on `main` before this brief and after it: two
`scorecard-recompute` rows (neither the reference nor the candidate scorecard is backed by a
signed ledger row) and one `deck-rebuild` row (`decks/reference/noise.spice` no longer rebuilds).
Three failures with the brief present, three without it — this work adds none. The candidate
decks themselves verify: `(cd decks/candidate && sha256sum -c SHA256SUMS)` is clean.

## What was not measured

- **Corners and Monte Carlo.** Every budget is tt/27 degC (rule 9: expensive runs after the cheap
  scorecard). The only statistical number here is the divider ratio sigma.
- **`vref` and `vss` capacitance** — unmeasurable by construction (see section 10).
- **The full net-to-net coupling matrix.** Three pairs were run (`fb`|`vref`, `ea_o1`|`ea_out`,
  `gate`|`vout`); the rest of section 2 is net-to-rail.
- **Per-finger resistance inside `XMP`.** The pass device is one card with `m=19`; splitting it
  into 19 cards with individual drain/source resistances was not done.
- **Junction and gate leakage in absolute terms.** Section 5 gives the budget in nA; converting
  it to a diffusion area needs a PDK leakage number that was not looked up.
- **Self-heating.** The 3.0 mW figure for XMP is `Vds x Id`, not a thermal simulation; the 1.35 mV
  per kelvin of divider gradient uses the model card's `tc1`, not an extracted thermal profile.
