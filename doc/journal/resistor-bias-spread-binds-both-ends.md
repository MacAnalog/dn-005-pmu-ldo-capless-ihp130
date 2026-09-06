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

**Correction, 2026-09-04 (review-002 M6).** The first two sentences of that last clause survive
re-measurement; the word *proportionally* does not. Sweeping the bias resistor rather than
reading the two published corners shows S7 against bias current is a **step**:

| ss / −40 °C, Iq (µA) | 30.9 | 28.8 | 27.8 | 26.8 | 25.6 |
|---|---|---|---|---|---|
| S7 (mV) | 83.8 | 88.3 | **309.8** | 301.3 | 310.8 |
| recovery (µs) | 0.143 | 0.203 | **1.33** | 1.30 | 1.27 |

3.5× of undershoot for 3.4 % of current, with the recovery time stepping by 6× alongside it. Below
the threshold the loop still catches the step; above it the gate sink cannot slew the pass gate
inside the 100 ns edge and the output falls until the outer loop recovers it. That is a change of
mechanism, not a degradation of one — the same signature as the `c_ff_w` cliff, and it means a
two-point corner table cannot tell you where the edge is.

Two further corrections from the same sweep:

* **Total Iq is a misleading proxy.** Slow transistors at −40 °C *lower* Iq by 15 % and *improve*
  S7, 105 → 84 mV. Decoupling the bundles (transistor / resistor / capacitor corner separately)
  shows the resistor corner alone reproduces both failures and neither of the others reproduces
  either. It is the bias-BRANCH current that sets S7.
* **The named fix does not relax both ends at once.** See below.

**Rule.** When one corner fails a *current* spec and another fails a *slew or settling* spec, read
the Iq column across corners **before** touching any sizing. If the spread is large, the two
failures pull the same bias knob in opposite directions and **no static value of it passes both** —
this is a bias-architecture problem, not a sizing problem, and more optimizer budget will not find
a point that does not exist. The tell is that the specs which do not depend on bias *magnitude*
(here S1–S4, S6, and all three phase-margin columns) hold comfortably at every corner.

**Fix, when it is in scope — and what it costs.** A supply-independent reference collapses the
spread, but *pinning the spread does not by itself pass the box*: held at the design's own 36.3 µA
it still fails S7 at ff/125 °C.

| ff / 125 °C, Iq (µA) | 61.9 | 58.1 | 52.7 | 48.3 | 44.7 | 40.9 | 35.9 |
|---|---|---|---|---|---|---|---|
| S7 (mV) | 109.8 | 115.2 | 123.2 | 130.6 | 139.1 | 148.4 | **165.2** |

The window that clears S7 at ff/125 and S5 at ≤ 50 µA is **Iq ≈ 41–50 µA**. So the exit path
trades most of the margin the 36.28 µA headline is built on: **the corner-robust headline is
41–50 µA.** Note also that a constant-*gm* / beta-multiplier reference is the wrong prescription
in kind — it holds transconductance constant, while the quantity that sets the pass-gate slew is
a current, and a beta-multiplier current still tracks the resistor and the mobility. What is
wanted is a current reference that is flat in PVT, and the nominal has to be chosen inside the
window above rather than inherited from the pre-corner optimum.

**Rule, restated.** Before naming a bias architecture as the exit path, sweep the bias knob at
both binding corners and state the *window*, not just the direction. `r_bias_l` sits ~11 % from a
step; `optimizer-parks-on-cliffs.md` already requires that sweep for any knob at an odd interior
value, and this entry originally did not do it. Sizing the two ends against each other with a
resistor-referenced bias remains the thing not to spend time on.
