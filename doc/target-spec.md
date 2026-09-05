# Target spec — the design challenge

**KIND: SPEC.** The acceptance box every experiment is judged against. Its machine twin is
`spec:` in `harness.yaml`; every bound below appears there verbatim and vice versa (`make lint`).

## The challenge

> Design a **capless, low-quiescent-current LDO** in IHP SG13G2 on the thin-oxide 1.5 V
> devices that **matches the certified reference's load regulation, line regulation and
> 1 kHz PSRR at ≤ 50 µA quiescent current** — without giving back phase margin, dropout or
> load-step undershoot, and with the output capacitor **on chip**.

## Conditions

| | |
|---|---|
| PDK | IHP SG13G2, open source; pinned in `doc/environment.md` |
| devices | `sg13_lv_nmos` / `sg13_lv_pmos` (thin oxide, 1.5 V family — the PDK registry's nominal LV rail, `_shared/pdk/ihp-sg13g2.yaml`); passives `rppd`/`rhigh`, `cap_cmim` |
| corner | `mos_tt` / `res_typ` / `cap_typ`, 27 °C — the box is judged here; sign-off runs the five MOS corners and −40/125 °C |
| supply | **Vin = 1.5 V nominal**; line range 1.4 → 1.65 V |
| output | **Vout = 1.2 V**; load 0.1 → 10 mA; Cout **on chip only**, ≤ 100 pF |

## The box

| # | requirement | target | reference baseline | checked by | where the bound comes from |
|---|---|---|---|---|---|
| S1 | regulated output at Vin 1.5 V, no load | 1.2 V ± 2 % → in [1.176, 1.224] V | 1.609 V (at Vin 3.3 V; its own 1.6 V target) | `ldo.metrics.evaluate` (`dc_op`) | `engur2023-dualrange-fvf` runs at exactly 1.5 V → 1.2 V; ±2 % is the reference's own regulation error (S2+S3) doubled |
| S2 | load regulation, 0.1 → 10 mA | ≤ 5 mV | **1.27 mV** (0 → 10 mA) | `load_regulation` | match the reference (1.27 mV over 0 → 10 mA) with margin; `perez2018` −0.82 mV/mA and `ieee9180856-adaptive-fb` 0.0014 mV/mA bracket it |
| S3 | line regulation, Vin 1.4 → 1.65 V at 1 mA | ≤ 2 mV | **4.32 mV** (Vin 2.6 → 3.6 V) | `line_regulation` | reference 4.32 mV/V → 1.1 mV over our 0.25 V range; literature 0.08–0.49 mV/V (`perez2018`, `zhang2023`) |
| S4 | dropout at 10 mA | ≤ 200 mV | 170 mV at 1 mA (hv pass device) | `dropout` | `ni2022` 200 mV, `zhang2023` 100 mV at 10 mA, `perez2018` 140 mV at 50 mA; the reference's hv number does not transfer |
| S5 | quiescent current, no load | ≤ 50 µA | **759 µA** | `dc_op` | an order of magnitude below the reference (759 µA); `engur2023` 50 µA high-current mode, `ni2022` 30 µA, `perez2018` 7.45 µA |
| S6 | PSRR at 1 kHz, 1 mA | ≥ 40 dB | **44.5 dB** (1 µF external Cout) | `psrr` | reference 44.5 dB with 1 µF; `perez2018` 48 dB at 1 kHz with 100 pF on chip; `engur2023` ≥ 40 dB to 10 kHz |
| S7 | load-step undershoot, 0.1 → 10 mA | ≤ 150 mV | 1.96 mV (1 → 10 mA into 1 µF; not comparable) | `tran_load_step` | `engur2023` 100 mV for 0 → 15 mA in 80 ns at 1.5/1.2 V; `zhang2023` 140 mV; the bench edge for candidates is 100 ns |
| S8 | loop phase margin at 1 mA | ≥ 60 deg | **46.4°** (1 mA, 1 µF Cout) | `ac_loopgain` | `ni2022` ≥ 74°, `perez2018` 89.6°; the reference's 46° is what a three-stage loop costs and is the thing not to give back |

Report-only columns (measured on every evaluate, never pass/fail): DC loop gain, loop UGF,
gain margin, sensitivity peak, Zout peaking, load-step recovery time, integrated output noise,
line-transient deviation.

**Reference baseline** = analog-db `ldo_005_buffered_ref`, IHP tt, 27 °C, certified in
`experiments/001-reference` on the frozen decks (`decks/reference/scorecard.json`, `make check`
re-measures it). It was certified **at its committed operating point — 3.3 V thick-oxide
devices, Vout 1.6 V, 1 mA nominal, 1 µF external Cout** — because no analog-db LDO binding
operates at this challenge's conditions. Only S2, S3, S5, S6 and S8 are quotable yardsticks;
S4 and S7 depend on the pass device family and the output capacitor and are set from the
literature instead. Full certified scorecard: `experiments/001-reference/README.md`.

Report-only from the same certification: DC loop gain 91.9 dB, UGF 569 kHz,
gain margin 41.6 dB, Ms 4.34 dB, Zout peaking 5.88 dB, recovery
0.87 µs, output noise 5.04 mVrms (10 Hz–10 MHz), line-step 3.45 mVpp.

Every bound cites its origin in the last column (handles are `pdf/INDEX.md` rows; two of them
are abstract-only and are used for bracketing, never as the sole source of a bound). Derived,
report-only: Hazucha FoM at the bound 7.5 ps (100 pF · 150 mV / 10 mA · 50 µA / 10 mA),
current efficiency 99.5 % at 10 mA.
