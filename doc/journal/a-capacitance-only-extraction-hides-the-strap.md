# 2026-09-05 — a capacitance-only extraction hides the strap

KIND: journal entry | type: semantic | status: live

**Observation.** The layout brief's pooled dropout rule for `ldo_ihp_capless`,
`10.34 × R(vdd) + 8.65 × R(vout) ≤ 23.83 mV` (a quarter of the S4 margin), was scored twice
against the same drawn cell and passed once, then failed:

| where the resistance came from | `R(vdd)` | `R(vout)` | pooled dropout cost | verdict |
|---|---|---|---|---|
| hand model, two straps only (pin → riser), single lumped elements | 0.598 Ω | 0.556 Ω | 10.98 mV | **met**, 46 % of the pool |
| stitched RC mesh, the drawn metal end to end (`SIGNOFF.md` §3.4, round 6) | ~1.57 Ω | ~1.52 Ω | **29.99 mV** | **missed, 1.26×** |

The capacitance-only (CC) extraction that was carried as the post-layout row of record through
five rounds cannot see this at all — it zeroes every wire resistance by construction, so its
dropout (104.671 mV) is the schematic number, unchanged to the printed digit. Only the stitched
RC mesh, now the post-layout row of record, measures the drawn `vdd`/`vout` metal's own IR drop:
+29.99 mV at 10 mA, i.e. **3.00 Ω** pooled. Each net's *individual* series-R budget is still met
(`R(vdd)` 1.57 Ω of a 2.31 Ω allowance, `R(vout)` 1.52 Ω of 2.76 Ω) — it is the **shared pool**
the two nets draw on together that is not.

**Why the hand model missed it, and by how much.** The hand model counts exactly the two straps
between each pin and its riser — the piece a designer can point at and solve by hand. The mesh
also carries the risers themselves, the via stacks between metal levels, the 39 parallel
pass-device column feeds and the source/drain contact rails: everything the hand model treats as
"free" because it *does* divide by the column count and was assumed negligible per column. It
does not divide cleanly at the top: the coordinator's decomposition of the measured 3.00 Ω
(quoted in `REPORT.md` §6.3, not re-derived there) puts **85 %** of it in two elements that are
shared across all 39 columns and do not shrink with parallelism — the **TopMetal1 strap**
(0.59 Ω) and the **Via2–TopVia1 stack** (0.75 Ω) — plus 4 % contacts. A hand model built by
solving "the strap" as one lumped resistor already had the right shape; what it missed is that
the strap and via stack are shared elements sitting *above* the point where the current spreads
into parallel columns, so widening the per-column risers (which the current-density sign-off
already sized correctly, §2) does nothing for this budget, and the hand model's own per-net
totals (0.598 / 0.556 Ω) were never wrong for what they counted — they simply did not count the
shared elements the mesh does.

**The rule this suggests.** A capacitance-only extraction is not a conservative stand-in for a
full RC one on a resistance-sensitive spec: it does not under-report the resistive term, it
reports **zero** of it, so a dropout/IR-drop budget scored on CC alone is untested, not merely
optimistic. And a per-net hand model of series resistance is only as complete as the elements it
was told to include — a model built from "the two obvious straps" will miss whatever sits above
the point where per-column parallelism starts, because that is exactly the point a hand model
usually stops counting columns and starts counting one lumped path. The fix, when this binds, is
architectural (widen the shared strap, multiply the shared via array), not a per-column change.

**Corollary for the next redraw.** Any fix to the strap or via stack changes metal that sits at or
near the `ea_o1` net, whose 64 fF of drawn-by-accident capacitance is what the mismatch box edges
in `SIGNOFF.md` §4 (9.109 σ / 17.889 σ, PLAN §6b ruling 1/2) currently rest on. A redraw that
closes this budget must re-bisect those edges rather than assume they survive unchanged — the two
findings are coupled through the same piece of metal.

**Links.** `layout/ldo_ihp_capless/SIGNOFF.md` §3.3–§3.4 (the measurement and the budget-miss
finding); `layout/ldo_ihp_capless/REPORT.md` §6.3 (the hand model and its round-6 addendum);
`layout/ldo_ihp_capless/PLAN.md` §6b (A15, and the ruling-1/2 coupling); does not supersede any
earlier entry — the CC-vs-RC gap was disclosed as a difference from round 3 onward
(`REPORT.md` §5), but which side of the dropout budget it landed on was not measured until round 6.
