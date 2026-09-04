# 2026-09-04 — a resistor-referenced bias makes one corner fail on current and the other on slew

KIND: journal entry | type: semantic | status: live

**Observation** (ledger `003_record_<corner>_<T>C`, experiment 003 §3). The design of record
passes the whole box at tt/27 °C and at 12 of 15 corners. The three failures are **S5 (Iq) at
ff/125 °C, 61.9 µA against 50** and **S7 (undershoot) at ss/−40 °C and ss/27 °C, 311 and 255 mV
against 150**. They look like two unrelated problems and are one.

The bias is resistor-referenced: `I_ref = (VDD − Vgs(XMB0)) / R(r_bias_l)`, and `rhigh`'s sheet
resistance moves from `res_wcs` to `res_bcs` across the corner bundles. Every branch current
therefore scales with the corner, and the quiescent-current column shows it directly: **25.6 µA at
ss/−40 to 61.9 µA at ff/125, a 2.4× spread** on a 36.3 µA nominal. At the fast/hot end there is
24 % too much current and S5 fails. At the slow/cold end there is 30 % too little — including in
the FVF gate sink, whose I_B/C_gate sets the pass-gate pull-down slew — so the gate slews
proportionally slower and S7 fails by 2×.

**Rule.** When one corner fails a *current* spec and another fails a *slew or settling* spec, read
the Iq column across corners **before** touching any sizing. If the spread is large, the two
failures pull the same bias knob in opposite directions and **no static value of it passes both** —
this is a bias-architecture problem, not a sizing problem, and more optimizer budget will not find
a point that does not exist. The tell is that the specs which do not depend on bias *magnitude*
(here S1–S4, S6, and all three phase-margin columns) hold comfortably at every corner.

**Fix, when it is in scope.** A PVT-stable reference — constant-gm / beta-multiplier, or a bounded
adaptive bias (`zhang2023`) — collapses the spread and relaxes both ends at once. Sizing the two
ends against each other is the thing not to spend time on.
