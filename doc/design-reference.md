# Design reference

KIND: REFERENCE (curated semantic facts; the pack carries the constraints section in full)

## Device map

The reference `ldo_005_buffered_ref` (analog-db, IHP binding): a two-stage reference buffer
(`XMRA_*`, Miller `RRAZ`/`CRAC`) gains an ideal 0.8 V `VREF` up through `R1`/`R2` to 1.6 V,
an RC (`R_LPF`/`C_LPF`) filters it, and a two-stage error amplifier (`XMEA_*`, Miller
`REAZ`/`CEAC`) drives the PMOS pass device `XMP` (w×m); `R3` bleeds the output, `C1` is the
on-die 10 pF. All MOS are `sg13_hv_*` (3.3 V family). The 0 V source `VLP lp_brk vout` is the
loop-break marker the `ac_loopgain` bench turns into a generator. Sizing knobs and their
defaults: `circuits/ldo_005_buffered_ref/pdk/ihp-sg13g2/sizing.yaml`; a `lab.dut.Design`
is that circuit id + a dict of knob overrides.

## Validated model

None yet. The first experiment after certification should fit the DC loop gain → load
regulation relation (ΔVout ≈ ΔIload·Rout_ol/(1+T0)) against the certified numbers.

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
4. **Phase margin is measured with the true loop bench** (`ac_loopgain`, Middlebrook injection
   at `Vlp`), not the Zout-peaking proxy: the proxy read 0 dB on a revision of the reference
   that had no loop gain at all (analog-db `datasheet.yaml`, `pm_loop_deg` note).
