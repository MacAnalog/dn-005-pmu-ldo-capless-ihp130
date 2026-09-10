# Experiment log

**KIND: TODO/log.** One row per `experiments/NNN-*` directory, newest last. Details live in
each experiment's README; keep the verdict column honest the moment one lands.

| # | technique | paper(s) | verdict |
|---|---|---|---|
| 001-reference | reference certification (analog-db ldo_005, IHP tt, committed 3.3 V point) | none | CONFIRMED — 10/10 benches, equals the analog-db baseline |
| 002-literature | topology pick: FVF output stage + two-stage error amp (structural A/B at tt, then corners) | engur2023-dualrange-fvf, ni2022-ocl-slewrate, zhang2023-220na-capless, perez2018-cbbc-ldo | PARTLY FALSIFIED then CONFIRMED — the double-mirror FVF fold regulates at every corner tried |
| 003-sizing | gm/ID start -> `spicexplorer-optimize` (NGOpt, 120 trials, Iq objective, S1-S8 + PM at 0.1/1/10 mA as constraints), rounding to the layout grid, five MOS corners x -40/27/125 C | none | PARTLY CONFIRMED — whole box PASS at tt/27 and at 12/15 corners; the <= 35 uA target missed by 1.28 uA |
| 004-schematic | xschem schematic of record — a five-block HIERARCHY plus the flat sheet as control, netlisted back, spliced flat and compared with `spicexplorer_circuitgraph` (topology), a per-device parameter assertion (sizes, review M3) and a block-coverage assertion (structure) | none | CONFIRMED at the recertified cell (`bf3a4f8`) — the drawing IS the certified netlist, devices and sizes |
| 005-layout | parameterized gdsfactory generator -> GDS -> KLayout DRC/LVS -> kpex 2.5D PEX -> the cell's own frozen benches on the extracted netlist | none | CONFIRMED — DRC 0 violations, LVS matched, PEX 121 C / 10 R, and the extracted cell passes all of S1-S8 |
| 006-visual-benches | every certified deck drawn as a testbench schematic — sources, loads and the DUT symbol placed and wired, directives and `.control` lifted verbatim into text blocks — then netlisted back and compared with the deck instance by instance | none | CONFIRMED at the recertified decks (`bf3a4f8`) — 13 of 13 sheets netlist back with no drift |
| 007-post-layout-corners | the extracted cell outside tt/27: 5 MOS corner bundles x -40/27/125 C on the CC extraction with the schematic row as the control, plus sigma-injection on the two sub-sigma matching classes | none | FALSIFIED (the hypothesis was "parasitics do not change the corner verdict") — they change it in both directions |

## What each experiment measured

**001-reference.** load_reg 1.27 mV, i_q 759 µA, PSRR 44.5 dB, PM 46.4°.

**002-literature.** Plain FVF passes the box at tt/27 but cannot turn the pass device off at
ff/hot (v_out 1.37 V at ff/125); SF/SSF buffer rings; the double-mirror FVF fold regulates at
every corner tried. Fold at hand sizes, tt/27: v_out 1.195, i_q 53.8 µA, undershoot 74 mV,
PM 60.1°, PSRR 57.1 dB; ff/125: v_out 1.190.

**003-sizing.** Iq cut 50.17 -> 36.28 uA (-27.7 %), whole box PASS at tt/27 and at 12/15 corners.
The <= 35 uA target was missed by 1.28 uA, and the corner clause was falsified in the wrong place
— S7 at ss/-40 and S5 at ff/125, never S8. Design of record tt/27: v_out 1.200, i_q 36.28 uA,
load_reg 0.028 mV, line_reg 0.059 mV, dropout 106 mV, PSRR 70.0 dB, undershoot 105 mV,
PM 72.4/72.4/72.3 deg; corner Iq spread 25.6-61.9 uA.

**004-schematic.** **50 vs 50** components + 33 nets under a wiring-preserving isomorphism,
nothing skipped, and **239 of 239** parameter rows green; the flat drawing returns the same two
verdicts. The recertification renamed every segmented device, which silently collapsed the
hierarchy from 5 blocks to 2 with both gates still green — the block-coverage assertion is the
answer. Six generator changes were needed, were proposed as a diff rather than worked around, and
have landed in the platform (`33850e1`); the build now calls the generator's own APIs and only
asserts they are present. The newest was a child sheet whose trunk wire CROSSES a pin without a
junction.

**005-layout.** 35 317 um2 (287.4 x 122.9 um). Pre -> post: undershoot 104.8 -> 113.9 mV,
PM 72.42 -> 71.74 deg, i_q 36.28 -> 36.20 uA, 28.4 fF on the pass gate.

**006-visual-benches.** The `ac_loopgain` sheet reproduces all 7 certified measures from its own
netlist: loop gain 50.22434 dB and PM 72.5064° from the drawing, equal to
`decks/candidate/scorecard.json` at every printed digit. The value half of the gate caught a live
emitter defect that truncated `pulse(0.1m 10m 1u 100n 100n 10u 20u)` in 2 sheets and, on the
recertified cell, the pass device's own `w`/`m` on the stock generator's sheet, while every
topology check passed.

**007-post-layout-corners.** S5 fails at ff/125 in BOTH rows (58.37 uA of 50). S7 leaves the box
at 125 C in 4 of 5 corners post-layout (152-171 mV) where only ss/125 does pre-layout; at -40 C
the parasitics RESCUE S7 (schematic 269-302 mV, extracted 106-116 mV) and one net does it —
`ea_o1` alone is worth 289 -> 89 mV. S8 never binds (worst 67.61 deg at ff/125). The mismatch box
edges are +15.0 mV (9.1 sigma, S1) and +20.0 mV (17.9 sigma, S7), and the control shows why the
brief's cliff does not reproduce — delete the extracted C and +2.0 mV puts S7 at 198.0 mV again,
`ea_o1` alone removes it. The two sub-sigma classes cost no yield at tt/27.
