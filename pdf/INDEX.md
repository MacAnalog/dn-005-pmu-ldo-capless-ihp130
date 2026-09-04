# Papers

KIND: REFERENCE (agent entry point for paper retrieval; data rows start with a backticked handle)

No PDF is vendored: every row links an open-access source (or the publisher's abstract page
when that is all that could be read — those rows are marked **unverified: abstract only** and
their numbers must not be cited as facts). Technology nodes are named as "N nm CMOS" only.

| handle | file | content / innovation | usable here for | status |
|---|---|---|---|---|
| `engur2023-dualrange-fvf` | [arXiv:2310.18998](https://arxiv.org/abs/2310.18998) (open) | Capacitor-less analog LDO, 65 nm LP CMOS, **Vin 1.5 V / Vout 1.2 V** (our point). FVF + super-source-follower buffer, two loops, on-chip Cc = 40 pF, on-chip load cap 160 pF. Dual-range bias switching: **Iq 3 µA (0–500 µA load) / 50–110 µA (5–15 mA)**; 0→15 mA in 80 ns → **undershoot 100 mV, overshoot 60 mV**, settles < 500 ns, response time 1.07 ns; PSR **≥ 40 dB to 10 kHz, > 32 dB to 10 MHz**; FoM **0.21 ps** (unit consistent with the Hazucha FoM; the paper defines it in its Table I, which was not read). Measured silicon. | S1/S5/S6/S7 anchors at exactly our Vin/Vout; the FVF + SSF buffer and the mode-switched bias as candidate techniques | read (full text) |
| `ni2022-ocl-slewrate` | [doi:10.3390/mi13101594](https://doi.org/10.3390/mi13101594) (open, Micromachines) | Output-capacitorless LDO, 40 nm, Vin ≥ 1.1 V / Vout 0.9 V, 0–100 mA, **Iq 30 µA**, on-chip Cout 8.6 pF; transient current-boost through the compensation caps (slew-rate enhancement) + push-pull output; 0→100 mA in 100 ns → **23.5 mV undershoot** (CL 100 pF); PSRR −70 dB at 10 kHz; **PM ≥ 74.1° worst case**; dropout 200 mV; FoM 7.05 µV (K·ΔVout·Iq/ΔIload). **Simulation only.** | S4 (200 mV) and S8 (PM) anchors; the transient current-boost as a technique | read (full text) |
| `zhang2023-220na-capless` | [doi:10.3390/mi14050998](https://doi.org/10.3390/mi14050998) (open, Micromachines) | Capacitor-less LDO, 180 nm, Vin 0.6 V / Vout 0.5 V, 10 µA–10 mA, **Iq 220 nA**, current efficiency 99.958 %; adaptive power transistors (2↔3-stage) + bulk modulation + bounded adaptive bias; 1 µs edge → 140 mV undershoot (1 ns edge → 230 mV overshoot); load reg 0.0059 mV/mA, line reg 0.49 mV/V; PSRR −51.4 dB DC–50 kHz; PM ≥ 45°; **dropout 100 mV at 10 mA**; FoM 0.0506 ps. **Simulation only.** | S4 anchor (100 mV at 10 mA is reachable); adaptive biasing with bounds as a technique | read (full text) |
| `perez2018-cbbc-ldo` | [doi:10.3390/s18051405](https://doi.org/10.3390/s18051405) (open, Sensors) | LDO with 100 pF on-chip Cout, 180 nm, Vin 1.94–3.6 V / Vout 1.8 V, 1 µA–50 mA, **Iq 7.45 µA**; dynamic current-bias boosting (quasi-floating-gate under/overshoot detectors); 0.5 µs edge → ~400 mV / ~480 mV; load reg −0.82 mV/mA, line reg 0.081 mV/V; **PSRR −48 dB at 1 kHz**; PM 89.6°; dropout 140 mV at 50 mA; FoM2 = Tsettle·Iq/Imax = 0.37 ns. Measured silicon. | S6 anchor at 1 kHz with an on-chip 100 pF Cout (our C1 constraint); the CBBC as a technique | read (full text) |
| `ieee9180856-adaptive-fb` | [IEEE Xplore 9180856](https://ieeexplore.ieee.org/document/9180856/), IEEE conference 2020 (ADS record 2020scas.conf..487Y); DOI not read | Capacitor-less LDO, **130 nm CMOS**, adaptively biased power transistors + load-aware (dynamically biased) feedback resistor; Vin 1.92–3.6 V / Vout 1.87 V, 0–100 mA; **Iq 0.7 µA**; 0→100 mA in 1 µs → 76 mV undershoot / 198 mV overshoot, no decoupling; load reg 0.00136 mV/mA, line reg 0.078 mV/V. | the 130 nm existence proof for sub-µA Iq with mV-class regulation; the load-aware divider as a technique | **unverified: abstract only** (numbers from the search abstract; the Xplore page itself could not be read) |
| `bu2018-200ps-ocl` | [doi:10.1109/TPEL.2017.2711017](https://doi.org/10.1109/TPEL.2017.2711017) | Output-capacitorless LDO, **130 nm CMOS**, enhanced multipath nested-Miller compensation with embedded feed-forward; UGB > 100 MHz at every load up to 25 mA; **Iq 112 µA**; 200 ps response time for a 300 ps edge. Measured silicon. | what the 130 nm node buys in bandwidth when Iq is not the constraint — the S7 ceiling reference | **unverified: abstract only** |

## Figures of merit used in this repo

- **Hazucha transient FoM** (Hazucha et al., JSSC 2005): `FoM = T_R · I_Q / I_max` with
  `T_R = C_out · ΔV_out / I_max` — the response time a capacitor-based estimate gives, scaled
  by the current-efficiency penalty. Lower is better. `engur2023` reports 0.21 ps, `zhang2023`
  0.0506 ps, `perez2018` 0.37 ns (their Tsettle variant). Our box implies
  `T_R = 100 pF · 150 mV / 10 mA = 1.5 ns` and `FoM = 1.5 ns · 50 µA / 10 mA = 7.5 ps` at the
  bound — report-only, not a spec line.
- **Current efficiency** `η_I = I_max / (I_max + I_Q)`: 99.5 % at our bound (10 mA, 50 µA);
  `zhang2023` 99.958 %.
- **PSRR at 1 kHz and 1 MHz** with the paper's own Cout stated beside the number; our S6 is at
  1 kHz with ≤ 100 pF on chip, 1 MHz is report-only (`psrr_1m_db`).

## Technique briefs (one line each; the `paper-analyst` agent expands one into a falsifiable brief)

- **FVF / buffered FVF** (`engur2023`, `bu2018`): the pass device is the FVF's shunt element,
  the fast local loop gives a low output impedance without an output cap; a super-source-
  follower or level-shift buffer drives the big gate. Cost: headroom (one Vgs + Vds inside 1.5 V).
- **Adaptive biasing** (`zhang2023`, `ieee9180856-adaptive-fb`, `perez2018`): bias current follows the load
  (sensed copy of the pass current or an under/overshoot detector), so Iq is set by the light-load
  point while slew is bought at heavy load. Cost: stability across the bias range (PM at 0.1 mA).
- **Transient current boost through the compensation cap** (`ni2022`): a derivative path from
  Vout into the gate driver. Cost: overshoot symmetry, noise coupling.
- **Load-aware feedback divider** (`ieee9180856-adaptive-fb`): the divider's bias moves with Vout error to
  speed the loop without standing current.
- **Digital assist** (not in this table yet): a comparator-driven coarse loop beside the analog
  fine loop; out of scope until the analog box is met.
