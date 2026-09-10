# Benches

KIND: REFERENCE (what certifies what)

**Reference-first policy.** Fast metrics (`ldo.metrics.evaluate`) iterate; the frozen
definitions certify. A number that has not passed through them is a claim.

**The measurement definitions are the analog-db LDO class testbench templates**, at
`examples/analog-db/_shared/classes/ldo/testbench-templates/*.spice`, with the canonical
vocabulary in `metrics.yaml`.

- **One deck per bench.** `ldo.dut.Design.deck(bench)` renders a template through analog-db's own
  `assemble()` — class template + the circuit's lowered netlist + the sizing point.
- **Fast and frozen run the same definition**, which is why the fast scorecard and the frozen
  reference are comparable at all.
- **Scalars come out of the log.** Every deck ends with `print <measures>`; `ldo.sim.run` parses
  those scalars out of the ngspice log.

| bench (analog-db template) | what it measures | ngspice measure → spec key (scale) |
|---|---|---|
| `dc_op` | quiescent current, regulated output, no load | `i_supply` → `i_q_ua` (×1e6); `vout_dc` → `v_out_v` |
| `load_regulation` | DC load sweep ΔVout (volts) | `load_reg` → `load_reg_mv` (×1e3) |
| `line_regulation` | DC Vin sweep ΔVout at fixed load | `line_reg` → `line_reg_mv` (×1e3) |
| `dropout` | smallest Vin − Vout that still regulates (level + slope criterion) | `v_dropout` → `v_dropout_mv` (×1e3) |
| `psrr` | closed-loop supply rejection at `FMEAS` | `psrr_vdd_db` → `psrr_1k_db` |
| `tran_load_step` | undershoot + recovery on a fast load step | `v_undershoot` → `v_undershoot_mv` (×1e3); `t_transient` → `t_transient_us` (×1e6) |
| `ac_loopgain` | TRUE loop gain / UGF / PM / GM by voltage injection at the DUT's 0 V `Vlp` marker | `pm_loop` → `pm_loop_deg`; `loopgain_db`; `ugf_loop` → `ugf_loop_khz` (×1e-3); `gm_loop_db`; `ms_peak` → `ms_peak_db` |
| `loop_stability` | closed-loop Zout peaking (stability proxy, port-only) | `zout_peak_db` |
| `noise` | integrated closed-loop output noise over the band | `vn_out_rms` → `vn_out_urms` (×1e6). The template's `vn_out_rms` **is** ngspice's `onoise_total`: already V rms, no square root (analog-db PR #68 removed the extra `sqrt` this repo certified against until 2026-09-04) |
| `tran_line_step` | p2p output deviation on a supply step | `v_line_pp` → `v_line_pp_mv` (×1e3) |

## Bench conditions

**They come from the circuit's own binding, not from this file.** VDD, ILOAD, COUT, sweep limits
and step edges are read from `analyses/<bench>.yaml` and `datasheet.yaml` `default_conditions`,
exactly as analog-db binds them.

| what runs | conditions |
|---|---|
| the reference, certified as committed (`experiments/001-reference`) | 3.3 V, 1.6 V, 1 µF external Cout |
| candidates for this challenge, from their own analog-db circuit binding | 1.5 V, 1.2 V, on-chip Cout |

## What sign-off runs that the fast scorecard does not

- **PM at 0.1 mA and 10 mA** (the fast scorecard measures 1 mA only).
- **PSRR at 1 MHz** (`FMEAS=1meg`).
- **The five MOS corners × −40/27/125 °C.**
