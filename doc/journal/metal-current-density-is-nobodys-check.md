# 2026-09-04 — the 10 mA path was 12–28× over the metal limit, and both sign-off stages passed it

KIND: journal entry | type: semantic | status: live

**Observation** (review-002-capless-ldo B1). The cell of record is DRC-clean and LVS-matched, and
its whole 10 mA load path is drawn on near-minimum Metal1. Against the process limits — Metal1
**1 mA/µm** above 0.36 µm width, **0.36 mA total** between 0.16 and 0.36 µm, **0.4 mA per Via1**:

| where | drawn | carries | limit | over by |
|---|---|---|---|---|
| vdd rail (`rail_w`) | 0.8 µm Metal1 | 10 mA | 0.8 mA | **12.5×** |
| vout drain bus | 0.6 µm Metal1 | 10 mA | 0.6 mA | **16.7×** |
| pass-device S/D column drop | 0.2 µm Metal1 | ≈0.53 mA (10 mA / 19 fingers) | 0.36 mA | **1.5×** |
| **vout pin** | 0.2 µm track, one Via1 each end | 10 mA | 0.36 mA / 0.4 mA | **25–28×** |

**Why nothing caught it.** Electromigration is not a rule-deck check — the rule deck checks
geometry, and every one of these shapes is geometrically legal. It is not a connectivity check
either: LVS compares devices and nets, and a 0.2 µm wire is the same net as a 20 µm wire. And it
is not visible in simulation, because the extracted netlist models the wire's *resistance*, which
at these lengths is milliohms and moves no metric in the box. So a cell can pass DRC, LVS, PEX and
all thirteen benches and still not be manufacturable at its rated load. **A sign-off chain that
has no current-density stage cannot report this, and silence from it is not evidence.**

**Rule.** Current density is a *design* obligation, not a check you can inherit. For every net,
write down the current it carries before drawing it, and size metal and via count from the
process's per-µm and per-via numbers. The nets that matter are few — supply, ground, output —
and the arithmetic is one line each.

**What a fix costs here, measured.** Widening in place does not work, and the attempt is recorded
so the next person does not repeat it. Setting `rail_w` 0.8 → 3.0 µm and the `vout` channel track
to the same width gives **117 Metal1 width/spacing violations** (`M1.a`, `M1.b`): the rails were
placed with `rail_gap` 1.6 µm, sized for a 0.8 µm rail, and the routing channel has a 0.7 µm track
pitch, so a 3 µm conductor does not fit in either. Reverting those two and keeping only the
per-finger bar widening (0.2 → 0.6 µm) and a 3×3 Via1 array on the output drop still leaves **79**.
The conclusion is structural: **the power path needs upper metal and a floorplan that reserves
room for it** — TopMetal1 carries 15 mA/µm, so 10 mA fits in under a micron there — and that is a
floorplan change (track plan, pin frame, stitch pitch), not a parameter change. `LayoutParams`
should grow `pwr_w` / `pwr_stitch` knobs and `build()` should place the straps over the transistor
stack, where nothing but the MIM top plates uses TopMetal1.

**Correction (2026-09-04)** — three numbers above, from the measured layout brief
(`layout/ldo_ihp_capless/BRIEF.md` §8, which derives every limit from the process spec per net):

1. The entry generalises "Metal1 **1 mA/µm**" to all metals. **Metal2–Metal5 carry 2 mA/µm above
   0.3 µm**, with a flat 0.6 mA total between 0.2 and 0.3 µm — so the `vout` Metal1→Metal2 riser
   is **16.7×** over, not 27.8×. (Metal1's own 1 mA/µm above 0.36 µm and 0.36 mA flat between
   0.16 and 0.36 µm stand, as do the 12.5× / 16.7× / 25× rows in the table.) Note also that the
   0.36 mA and 0.6 mA figures are **flat totals in a qualified narrow band, not densities**;
   below 0.16 µm (Metal1) / 0.2 µm (Metal2–5) the process spec gives no number at all.
2. "pass-device S/D column drop … ≈0.53 mA (10 mA / 19 fingers) … **1.5×**" is a *per-channel*
   number. Interior diffusion columns are **shared** by two fingers, so the conductor that is
   actually drawn carries **1.053 mA** and is **2.92×** over 0.36 mA. Only the two end columns
   serve one finger each (0.53 mA, 1.46×). The row should read per shared column, not per finger.
3. "TopMetal1 carries 15 mA/µm, so 10 mA fits in **under a micron** there" is true of the current
   limit and false of what can be drawn: **TM1.a makes 1.64 µm the drawable minimum TopMetal1
   width** (and 1.64 µm the minimum space). A TopMetal1 power strap is at least 1.64 µm wide by
   rule, which is what the floorplan has to reserve — the conclusion of the paragraph is
   unchanged, only its arithmetic.

The headline "12–28× over" and the structural conclusion (upper metal plus floorplan room, not a
parameter change) both stand.

**Also.** `layout/signoff.py`'s `drc()` put `DrcViolation` objects straight into `json.dumps`. That
line only ever runs when the violation list is non-empty, so a cell that had always been clean hid
the crash until this attempt produced the first real violation. An error path that runs only on
failure is untested by every passing run.
