# 001 — reference certification: analog-db `ldo_005_buffered_ref` in SG13G2

**Status: CLOSED 2026-09-04. Certified and frozen in `decks/reference/`.**

| | |
|---|---|
| **Paper(s)** | none — this is the carried-forward analog-db reference, not a technique |
| **Hypothesis** | The committed IHP binding of `ldo_005_buffered_ref` runs all ten LDO-class benches through this repo's `lab/` (platform `NGSpice_Wrapper` + analog-db `assemble()`) and reproduces the analog-db scoreboard baseline `67ea759104` (ngspice-45) to the drift tolerances in `lab.metrics.TOL`. Falsified if any bench fails to run or any number moves. |
| **Control** | the frozen deck bytes: `scripts/lint.py::deck_rebuild` proves `lab.dut.Design.deck()` regenerates them; `make check` re-simulates them |
| **Verdict** | **CONFIRMED.** 10/10 benches ran (2.5 s wall, 10 parallel ngspice); every scorecard number equals the analog-db baseline to the printed digits. |

## 1. Result — the numbers every candidate is scored against

Conditions **as committed in analog-db** (not the challenge's): `.lib cornerMOShv.lib mos_tt` /
`res_typ` / `cap_typ`, 27 °C, **Vin = 3.3 V**, `sg13_hv_*` devices, Vout target 1.6 V,
1 mA nominal load, **1 µF external Cout** on every AC/transient bench. Ledger tag
`reference_certify`.

| # | metric | key | unit | **certified** | note |
|---|---|---|---|---|---|
| S1 | regulated output (no load) | `v_out_v` | V | **1.6091** | 1.6 V target of the binding |
| S2 | load regulation 0 → 10 mA | `load_reg_mv` | mV | **1.274** |  |
| S3 | line regulation Vin 2.6 → 3.6 V, 1 mA | `line_reg_mv` | mV | **4.32** |  |
| S4 | dropout at 1 mA | `v_dropout_mv` | mV | **169.7** | level + slope criterion |
| S5 | quiescent current, no load | `i_q_ua` | µA | **758.7** |  |
| S6 | PSRR at 1 kHz, 1 mA, 1 µF | `psrr_1k_db` | dB | **44.53** |  |
| S7 | load-step undershoot 1 → 10 mA (10 ns edge) into 1 µF | `v_undershoot_mv` | mV | **1.957** |  |
| — | load-step recovery to ±1 mV | `t_transient_us` | µs | **0.875** |  |
| S8 | loop phase margin, 1 mA, 1 µF | `pm_loop_deg` | deg | **46.39** | Middlebrook injection at `Vlp` |
| — | DC loop gain | `loopgain_db` | dB | **91.94** |  |
| — | loop UGF | `ugf_loop_khz` | kHz | **569.1** |  |
| — | gain margin | `gm_loop_db` | dB | **41.56** |  |
| — | sensitivity peak Ms | `ms_peak_db` | dB | **4.345** | ≥ 1/(2 sin(PM/2)) = 2.07 dB: consistent |
| — | closed-loop Zout peaking | `zout_peak_db` | dB | **5.88** | proxy only |
| — | integrated output noise 10 Hz–10 MHz | `vn_out_urms` | µVrms | **5038** |  |
| — | line-step deviation 3.1 → 3.5 V | `v_line_pp_mv` | mVpp | **3.449** |  |

Against this repo's box (1.5 V / 1.2 V / capless, `harness.yaml`) the reference fails S1 (it
regulates to 1.6 V), S3 by the literal bound (4.32 mV, but over a 1 V sweep — 4.3 mV/V, i.e.
~1.1 mV over our 0.25 V range, which passes), S5 (759 µA vs ≤ 50 µA) and S8 (46° vs ≥ 60°).
S1 and S5 are the point of the challenge; S8 is the price of its three-stage loop.

## 2. Method — exact commands

```bash
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2
export SPICE_USERINIT_DIR=$PDK_ROOT/ihp-sg13g2/libs.tech/ngspice SX_SCRATCH=$HOME/sx-scratch
uv sync && make doctor
.venv/bin/python -m lab.metrics --certify     # builds decks/reference/*.spice, runs them, writes scorecard.json
make freeze                                    # SHA256SUMS
make check                                     # lint (incl. deck rebuild) + re-simulate the frozen decks, compare
make baseline                                  # print the scorecard from the frozen decks (no compare)
```

Deck provenance: analog-db submodule at the platform's pinned commit (see `decks/reference/build-sheet.md`);
`lab.dut.Design(circuit="ldo_005_buffered_ref", pdk="ihp-sg13g2", corner="tt", sizing={})`.

## 3. What this does and does not certify

- It certifies the **measurement contract** (the ten class benches) and the **lane** (platform
  wrapper, native ngspice-45, PDK pin) on a circuit with a known answer.
- It does **not** certify a yardstick at the challenge's operating point: no analog-db LDO binding
  is at 1.5 V / 1.2 V / capless. Re-basing the reference (lv devices, on-chip Cout) is
  experiment 002 and is expected to move every number; until then S4/S7 bounds come from the
  literature (`doc/target-spec.md`).

## Lessons to graduate

- `doc/journal/reference-is-not-at-the-target-point.md` (ledger tag `reference_certify`)
- `doc/journal/template-gaps-t8.md` (the template gaps hit while instantiating)
