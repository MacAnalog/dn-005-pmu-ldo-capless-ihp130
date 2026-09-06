# 2026-09-04 — a floorplan is bought, not found: what closing B1 and m3 cost

KIND: journal entry | type: semantic | status: live

**Observation.** The second drawing of `ldo_ihp_capless` (005 §1) closes the four findings
review-002 rejected the first floorplan on. Priced against the first drawing, same sizing, same
benches, same extraction mode:

| bought | price |
|---|---|
| 10 mA path inside the metal limit (B1): TopMetal1 straps, 6 µm Metal2 combs, 48-cut via risers, `xmp_nf_mult = 4` | **+19.6 % area**; `gate` 28.4 → 47.5 fF; S7 +16.9 mV |
| matching (m3): common-centroid / interdigitated rows, 16 tied MOS dummies, 5 closed guard rings | most of the remaining area; `fb` 19.2 → 34.0 fF; S8 −3.7° |
| an LVS reference derived from the certified netlist (M7) and an obstacle map with its own case (M8) | no silicon cost; three build rounds |
| aspect 2.34 : 1 → **1.03 : 1** | the area above, in exchange |

Nothing left the box: S7 keeps 22 mV and S8 keeps 8.8° of margin, and Iq *improved* 2.5 µA.

**The part worth remembering is that the parasitic budgets got worse, and correctly so.** The
layout brief measured `gate` ≤ 29.3 fF and `fb` ≤ 27.9 fF from the pre-layout margins. The drawing
that satisfies the current-density limit spends 47.5 fF and 34.0 fF. That is not a routing failure
to be optimized away — it is the same decision seen from the other side:

- `gate` grew **because** the pass device is now 76 short fingers instead of 19 long ones. That is
  what takes the shared source/drain column from 1.053 mA to 0.263 mA, i.e. it *is* the fix for
  B1, and it makes the gate bar four times longer in x. A budget written before the floorplan
  exists cannot know that the fix for another finding will spend it.
- `fb` grew **because** the cell became square. In a 287 µm row the divider and the input pair were
  neighbours; in a 202 × 208 µm block with three guard-ringed islands they are not.

**The rule this suggests.** A parasitic budget is a *ranking with a scale*, not a bound — it says
which nets to spend last and how much a femtofarad is worth on each, and the brief's own
coefficients then price the overrun (`fb`: 34.0 fF × −0.111 °/fF = −3.77°, measured −3.66°). Treat
an over-budget net as a claim that needs a cause and a margin check, not as a gate. What *is* a
gate is the physical limit: current density is a blocking sign-off stage now, and the hard step at
60–65 fF on `gate` is the number that would actually break the cell.

**Corollary for the next drawing.** The margin is bought back the same way it was spent: the
knob is `xmp_nf_mult`, and dropping it to 3 shortens the gate bar 25 % while the shared column
goes from 0.731× to 0.975× of the Metal1 limit. That is one build, and it is a trade between two
measured quantities — which is the shape every floorplan decision in this cell turned out to have.

**Links.** `experiments/005-layout/README.md` §1 (before/after, the current-density table, every
pre→post delta with its cause); `layout/ldo_ihp_capless/{PLAN.md,REPORT.md}`;
`doc/journal/metal-current-density-is-nobodys-check.md` (the finding this pays off);
`doc/journal/metal1-stub-shorts-are-drc-invisible.md` (the guard the second drawing had to widen
from Metal1 to every layer a router can walk into).
