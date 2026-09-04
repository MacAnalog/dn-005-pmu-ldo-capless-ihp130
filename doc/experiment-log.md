# Experiment log

**KIND: TODO/log.** One row per `experiments/NNN-*` directory, newest last. Details live in
each experiment's README; keep the verdict column honest the moment one lands.

| # | technique | paper(s) | verdict | headline metric |
|---|---|---|---|---|
| 001-reference | reference certification (analog-db ldo_005, IHP tt, committed 3.3 V point) | none | CONFIRMED — 10/10 benches, equals the analog-db baseline | load_reg 1.27 mV, i_q 759 µA, PSRR 44.5 dB, PM 46.4° |
| 002-literature | topology pick: FVF output stage + two-stage error amp (structural A/B at tt, then corners) | engur2023-dualrange-fvf, ni2022-ocl-slewrate, zhang2023-220na-capless, perez2018-cbbc-ldo | PARTLY FALSIFIED then CONFIRMED — plain FVF passes the box at tt/27 but cannot turn the pass device off at ff/hot (v_out 1.37 V at ff/125); SF/SSF buffer rings; double-mirror FVF fold regulates at every corner tried | fold at hand sizes, tt/27: v_out 1.195, i_q 53.8 µA, undershoot 74 mV, PM 60.1°, PSRR 57.1 dB; ff/125: v_out 1.190 |
