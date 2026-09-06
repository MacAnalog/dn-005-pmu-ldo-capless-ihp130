# 2026-09-04 — in an FVF output stage, every picofarad at the pass gate is paid at the sink's slew rate

KIND: journal entry | type: semantic | status: live

**Observation** (ledger `003_probe0_defaults` → `003_probe1_2stage_c_x0`, experiment 002 table 2).
A 5 pF "damping" capacitor at the FVF's pass-gate node (the textbook way to give the local loop a
dominant pole) turned the 0.1 → 10 mA / 100 ns undershoot from 65 mV into 553 mV. The waveform
shows why: on a load step the FVF control device turns OFF (its source is the output, which
dropped), so the gate is pulled down by the constant sink alone — I_B / (C_x + C_gate) =
20 µA / 6 pF = 3.3 V/µs (4.5 V/µs measured), and the gate needs 0.36 V of travel. The FVF is fast
only in the pull-UP direction (the control device sources as much current as the droop asks for).

**Rule.** Size the FVF sink for the pull-down slew the step needs — I_B ≥ ΔV_gate · C_gate /
t_edge, with C_gate the pass device's own gate capacitance and nothing else added — and get the
local loop's damping from the control device / sink output resistances (their L), not from a
capacitor at the gate. A feed-forward cap from vout to the gate (`ni2022`'s derivative path)
is the same capacitance seen from the sink and hurt here too (65 → 90 → 119 mV for 0/1/3 pF).

**Corollary for layout.** Keep the pass-gate net short and away from wide metal: parasitic C
on that net is a transient penalty, so it is the first net on the layout brief.
