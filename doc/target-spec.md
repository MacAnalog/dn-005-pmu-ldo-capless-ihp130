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
| S1 | regulated output at Vin 1.5 V, no load | 1.2 V ± 2 % → in [1.176, 1.224] V | — | `lab.metrics.evaluate` (`dc_op`) |
| S2 | load regulation, 0.1 → 10 mA | ≤ 5 mV | — | `load_regulation` |
| S3 | line regulation, Vin 1.4 → 1.65 V at 1 mA | ≤ 5 mV | — | `line_regulation` |
| S4 | dropout at 10 mA | ≤ 200 mV | — | `dropout` |
| S5 | quiescent current, no load | ≤ 50 µA | — | `dc_op` |
| S6 | PSRR at 1 kHz, 1 mA | ≥ 40 dB | — | `psrr` |
| S7 | load-step undershoot, 0.1 → 10 mA | ≤ 150 mV | — | `tran_load_step` |
| S8 | loop phase margin at 1 mA | ≥ 60 deg | — | `ac_loopgain` |

Report-only columns (measured on every evaluate, never pass/fail): DC loop gain, loop UGF,
gain margin, sensitivity peak, Zout peaking, load-step recovery time, integrated output noise,
line-transient deviation.

The reference column is filled from `decks/reference/scorecard.json` once
`experiments/001-reference` certifies it (`make check`). Bounds are provisional until the
literature review (`pdf/INDEX.md`) lands; each row will then cite where it came from.
