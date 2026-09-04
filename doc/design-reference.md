# Design reference

KIND: REFERENCE (curated semantic facts; the pack carries the constraints section in full)

## Topology of record — `ldo_ihp_capless`

A **double-mirror flipped-voltage-follower (FVF)** output stage under a slow, high-gain outer
loop, in `sg13_lv_*` at 1.5 V. Chosen in experiment 002, sized in 003, drawn in 005.

- **Output stage.** Pass PMOS `XMP` (19 fingers x 10 um, L 0.13 um). Control PMOS `XMC` whose
  source IS `vout` — the fast local loop. `XMC`'s drain current is folded to the pass gate as a
  **pull-up** through an NMOS 1:1 mirror (`XMA`/`XMB`) and then a PMOS 1:1 mirror (`XMCP`/`XMD`);
  the constant sink `XMS` pulls the gate down. The fold is what lets the gate reach `vdd - Vsd,sat`
  so the pass device turns fully **off** at hot/fast corners — a plain FVF caps the gate at `vout`
  and leaks 80-470 uA there (`journal/plain-fvf-gate-ceiling.md`). Each mirror node is a diode,
  i.e. low impedance, so the fold adds no high-impedance pole where a source-follower buffer did.
- **Outer loop.** Two-stage error amplifier: PMOS-input 5T OTA (`XMT`/`XM1`/`XM2`/`XM3`/`XM4`)
  then an NMOS common source under a PMOS current source (`XM5`/`XM6`), Miller cap `XCC` across
  stage 2 (dominant pole at `ea_o1`). It sets DC accuracy, PSRR and load/line regulation; the FVF
  sets the transient.
- **Feedback.** 1:1 `rhigh` divider `XR1`/`XR2` (340 um each) sensed through the 0 V loop-break
  marker `VLP`, with a 0.1 pF MIM `XCFF` across the top resistor cancelling the divider-node pole
  the resistors' own substrate capacitance makes.
- **Bias.** Resistor-referenced: `XRB` + NMOS diode `XMB0`, mirrored to the sink and, via the PMOS
  diode `XMBP`, to the error-amp tail. No ideal current sources. **This is the design's binding
  limitation** — see the constraint list below.
- **Output capacitor.** `XCOUT`, 4 x 5 pF MIM units on chip (21 pF total incl. the bench's 1 pF),
  well under the 100 pF bound: 002 showed the transient is loop-speed-limited, not charge-limited.

Sizing knobs and their defaults ARE the design of record:
`circuits/ldo_ihp_capless/pdk/ihp-sg13g2/sizing.yaml`, so a bare `lab.dut.CANDIDATE` renders it.
Certified into `decks/candidate/` with `SHA256SUMS`. Schematic of record:
`experiments/004-schematic/`. Layout generator: `layout/gen_ldo.py`.

## Device map — the reference

The reference `ldo_005_buffered_ref` (analog-db, IHP binding): a two-stage reference buffer
(`XMRA_*`, Miller `RRAZ`/`CRAC`) gains an ideal 0.8 V `VREF` up through `R1`/`R2` to 1.6 V,
an RC (`R_LPF`/`C_LPF`) filters it, and a two-stage error amplifier (`XMEA_*`, Miller
`REAZ`/`CEAC`) drives the PMOS pass device `XMP` (w×m); `R3` bleeds the output, `C1` is the
on-die 10 pF. All MOS are `sg13_hv_*` (3.3 V family). The 0 V source `VLP lp_brk vout` is the
loop-break marker the `ac_loopgain` bench turns into a generator. Sizing knobs and their
defaults: `circuits/ldo_005_buffered_ref/pdk/ihp-sg13g2/sizing.yaml`; a `lab.dut.Design`
is that circuit id + a dict of knob overrides.

## Validated model

**Loop-gain → load regulation.** ΔVout ≈ ΔIload·Rout_ol/(1+T0). The record measures
loop gain 49.95 dB (T0 = 314) and load regulation 0.028 mV over 0.1 → 10 mA, i.e. an effective
closed-loop output resistance of 2.8 mΩ and Rout_ol ≈ 0.88 Ω — the pass device's own 1/gm at
10 mA, as the relation predicts. The relation also holds across the corner table: load regulation
tracks 1/(1+T0) (0.017 mV at loop gain 52.6 dB, 0.056 mV at 45.9 dB).

**Pass-gate capacitance → undershoot.** From `journal/fvf-gate-cap-is-slew.md`, the pull-down
slew is I_B/C_gate. The layout adds 28.4 fF to a ~1 pF gate (+3 %) and S7 moves 104.8 → 113.9 mV
(+8.7 %) with recovery 0.125 → 0.150 µs (experiment 005 §1) — the predicted direction, and the
right order of magnitude given the FVF is pull-down-slew-limited on the falling edge only.

## Facts that constrain every candidate

1. **Cout is on chip: ≤ 100 pF total at the output node.** The reference's benches hang a 1 µF
   external capacitor on `vout`; a candidate may not. This moves the dominant pole inside the
   loop and is the whole difficulty of the capless class (provenance: `harness.yaml` goal;
   the reference's `analyses/*.yaml` bind `COUT: 1u`).
2. **Thin-oxide devices at 1.5 V.** `sg13_lv_*` are the 1.5 V family in the PDK registry
   (`_shared/pdk/ihp-sg13g2.yaml: supply.default: 1.5`); the reference is hv at 3.3 V, so
   none of its sizing carries over, only its structure and its benches.
3. **Quiescent current ≤ 50 µA is measured at no load** (`dc_op`, `i_supply`) — a bleeder or a
   minimum-load device counts against it.
4. **The bias sets the corner spread, and it binds at both ends.** The resistor-referenced bias
   makes every branch current scale with `rhigh`'s sheet resistance: Iq runs 25.6 µA at ss/−40 °C
   to 61.9 µA at ff/125 °C, a 2.4× spread on a 36.3 µA nominal. S5 therefore fails at ff/125 and
   S7 (which is set by the same current through the gate sink's slew) fails at ss/−40 — the two
   pull `r_bias_l` in opposite directions, so no static value passes both. A PVT-stable reference
   (constant-gm / beta-multiplier, or `zhang2023`'s bounded adaptive bias) is the named next
   increment; provenance: `experiments/003-sizing/README.md` §3,
   `journal/resistor-bias-spread-binds-both-ends.md`.
5. **Phase margin is measured with the true loop bench** (`ac_loopgain`, Middlebrook injection
   at `Vlp`), not the Zout-peaking proxy: the proxy read 0 dB on a revision of the reference
   that had no loop gain at all (analog-db `datasheet.yaml`, `pm_loop_deg` note).
