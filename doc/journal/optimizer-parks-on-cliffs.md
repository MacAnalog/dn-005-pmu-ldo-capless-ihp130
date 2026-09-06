# 2026-09-04 — an optimizer's winner can sit on a cliff none of its own metrics can see

KIND: journal entry | type: semantic | status: live

**Observation** (ledger `003_cffsweep_*`, experiment 003 §2). `spicexplorer-optimize` returned
`c_ff_w = 9.415138 µm` for the feed-forward MIM across the top divider resistor. Rounding it to
9.5 µm — a 0.9 % change of the MIM side, 2 % of capacitance — took the 0.1 → 10 mA undershoot
from 107 mV to 201 mV. A sweep put a **cliff between 9.4 and 9.5 µm**: below it S7 is flat at
97–107 mV over 4–9.4 µm, above it S7 is 200–253 mV over 9.5–12 µm.

The optimizer could not have known. Every metric it scored is smooth and monotone straight
through the cliff — phase margin 74.5 → 74.6°, line-step deviation 50.6 → 50.6 mV, quiescent
current unchanged — and S7 itself had 13 mV of slack against the constraint it was given, so the
search was free to spend the knob on the metrics that were still improving and stopped 15 nm from
the edge. The cliff is a change of *mechanism* (the lead zero moves past the loop's own pole and
the step response goes from settling to overshooting-then-settling), and a scalar objective sees
mechanisms only after they have already cost something.

**Rule.** An optimizer's answer is a **point**; a point on a cliff is not a design. Before a
sizing point becomes the design of record, sweep every knob the optimizer moved to a rail or to an
odd-looking interior value across its local neighbourhood, on the spec that knob most affects, and
back the knob off the nearest edge by a stated margin. Deliver the point **plus that sweep** — the
sweep is the evidence that the point is on a plateau, and it costs a handful of single-bench runs.
Here 8 µm was chosen: 19 % of margin to the cliff, for 2 mV of undershoot and 2.1° of phase margin.

**Corollary.** Give the optimizer's own constraints margin against the box (this run used S7
≤ 120 mV against a 150 mV bound) — but margin in the *constraint* does not buy margin in the
*knob*, which is what a cliff eats. They are different quantities and both have to be checked.
