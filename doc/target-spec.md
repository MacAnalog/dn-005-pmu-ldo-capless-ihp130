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

| # | requirement | target | reference baseline | checked by |
|---|---|---|---|---|
| S1 | regulated output at Vin 1.5 V, no load | 1.2 V ± 2 % → in [1.176, 1.224] V | 1.609 V (at Vin 3.3 V; its own 1.6 V target) | `lab.metrics.evaluate` (`dc_op`) |
| S2 | load regulation, 0.1 → 10 mA | ≤ 5 mV | **1.27 mV** (0 → 10 mA) | `load_regulation` |
| S3 | line regulation, Vin 1.4 → 1.65 V at 1 mA | ≤ 5 mV | **4.32 mV** (Vin 2.6 → 3.6 V) | `line_regulation` |
| S4 | dropout at 10 mA | ≤ 200 mV | 170 mV at 1 mA (hv pass device) | `dropout` |
| S5 | quiescent current, no load | ≤ 50 µA | **759 µA** | `dc_op` |
| S6 | PSRR at 1 kHz, 1 mA | ≥ 40 dB | **44.5 dB** (1 µF external Cout) | `psrr` |
| S7 | load-step undershoot, 0.1 → 10 mA | ≤ 150 mV | 1.96 mV (1 → 10 mA into 1 µF; not comparable) | `tran_load_step` |
| S8 | loop phase margin at 1 mA | ≥ 60 deg | **46.4°** (1 mA, 1 µF Cout) | `ac_loopgain` |

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

Bounds are provisional until the literature review (`pdf/INDEX.md`) lands; each row then
cites where it came from.
