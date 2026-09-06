# Layout report — `ldo_ihp_capless` (IHP SG13G2), second drawing, round 5

**KIND: REPORT.** The layout of record is the generator `layout/gen_ldo.py` at `LayoutParams()`
defaults, reading its sizing from the certified binding. Plan and assumed approvals:
[`PLAN.md`](PLAN.md). Brief: [`BRIEF.md`](BRIEF.md). Independent reviews this report answers:
[`REVIEW.md`](REVIEW.md) — `review-004` (**PASS with majors**: F3, F16, F1) on top of
`review-003` (FAIL, 3 blockers). Every number below is a verdict this branch produced; where the
previous drawing or the reviewer is quoted it is named as such.

## 0. Changelog

| round | iteration | what changed | verdicts |
|---|---|---|---|
| 3 (`review-002` fixes) | `it09` | the second drawing: TopMetal1 power path, common-centroid rows, closed rings | DRC 0, LVS matched, CC 182 C |
| — | `it10` | the certified deck re-issued on the drawn device set (F19) | Iq 36.28 -> 33.81 uA |
| 4 (`review-003` fixes) | `it11`, `it12` | layer-aware obstacle map + Metal3 gate track (F7/F3), `BOUNDS` walked 40/40 (F2), `pwr_w` 2.0 -> 4.0 (F1), Kelvin `vss` return (F9) | DRC 0, LVS matched, CC 186 C, 18/18 metrics |
| **5 (`review-004` fixes, this report)** | **`it13`** | **the only geometry change is a pin-purpose square under each of the 17 port labels** (F25, PLAN A14) — kpex now emits a `[Pin]` node and anchors **15/15** named ports on the drawn port instead of a proxy. Proved inert: DRC 0, LVS matched, CD 30/30, **40/40 knob endpoints re-walked on `it13` itself**, and the **CC netlist is byte-identical** to `it12`'s, so every number in sections 6–8 is unchanged. Everything else this round is code, measurement or text: **F27** the benches now measure the netlist the extractor named (§5), **F26** the sign-off record carries `mesh_connected` + the anchor census and gates on them, **F24** `signoff.json` merges instead of replacing, **F22** `router.py`/`netlist_ref.py` travel with each snapshot, **F9** the `vss` return is *solved*, not modelled, and two numbers this report printed are corrected (§6.4, §10.4), **F3** reframed (§6.1, PLAN §6b), **F16** answered by `experiments/007-post-layout-corners` — including the control that reproduces the brief's mismatch cliff once the extracted capacitance is deleted — and **the RC row is now measured**: kpex's zero-ohm `[Pin]` ties made ngspice return a non-solution, `postlayout.floor_zero_r()` fixes it, and the stitched RC netlist passes all 13 benches with dropout +30 mV against CC (§5), **F20** §8 gains a *step* column, **F23** the run-dependent RC bench counts are replaced by the node-set statement, **F21** the README M8 row rewritten. | DRC 0, LVS matched, 40/40 endpoints (re-walked on `it13`), CC 186 C / 21 R, RC 186 C / 5 484 R measured (8 583 raw) — **superseded, see round 6**, 13 benches 18/18 metrics on **both** |
| **6 (independent sign-off, `SIGNOFF.md` @ `50442a8`)** | — (no geometry change; verifier re-measure + this reconciliation) | The verifier re-derived every number in rounds 1–5 from raw artefacts and **moved the post-layout row of record from CC to the stitched RC row**: `scorecard_post_rc.json` reproduces on the verifier's own rebuilt GDS and extraction, 3101/3101 zero-Ω `[Pin]` ties contracted (0 left), 15/15 named ports anchored on a pin, and the verifier's own card census is **5482 R** (5461 `Rext_` + 21 `rhigh`), not this report's 5484 — the two-card difference is between an older floored run and the contracted one and changes no verdict. CC is re-labelled the **ideal-metal comparison row**. The verifier also confirms the +30 mV dropout is physical (§5, §6.3) and files the pooled dropout budget as **missed**, not met (§10.7). | RC signed as record: dropout **134.66 mV** / 200 mV (65.3 mV margin), 8/8 spec lines PASS; pooled series-R budget **29.99 mV of a 23.83 mV allowance — 1.26×, MISSED** |

**Verdict.** Current density 30/30 segments (worst 0.836x), **DRC 0**, **LVS matched**, and LVS
matched with DRC 0 at **both ends of all 20 documented knob ranges** (40/40 endpoints), kpex CC
186 C / 21 R, and the cell's own **13 frozen benches on the extracted netlist pass the whole
S1–S8 box, 18/18 metrics — at tt/27**. Outside tt/27, measured this round for the first time
(§10.6, `experiments/007-post-layout-corners`): **S5 fails at ff/125 in the schematic row and the
extracted row alike** (58.37 uA of a 50 uA line) and **S7 leaves the box at 125 C in four of the
five corners post-layout**. Signature at the time this report was written: **none** —
`layout/postlayout.py` logs the post-layout scorecard as one ledger row with `evidence="awaiting"`,
whose signature is the verifier's own re-measure (rule 7), never the designer's. **Superseded by
round 6:** `SIGNOFF.md` has since re-measured both the CC and the stitched RC extraction from raw
artefacts and signed `verify_postlayout_post` and `verify_postlayout_rc`; the RC row is now the
signed post-layout row of record (§5, §10.7). `runs/` is git-ignored and per checkout, so a signed
ledger row does not travel with this commit: re-run `layout/postlayout.py --pex <work>/pex` to
reproduce it locally.

**What is NOT closed — and F3 is not what it looked like.** The brief's **12 fF** `gate` budget
is a **gate-only** number: measured with every other parasitic zeroed it steps between 12 and
13 fF, and the drawn cell's 34.45 fF puts gate-only S7 at 201.7 mV. Swept **in situ** on the full
186-card extraction, however, there is no step and the net carries **+46 fF** before S7 crosses
150 mV — 134 % of what is drawn (§6.1, reproduced from `review-004` F3 to the digit). What the
corner run then shows is that S7's real constraint is **temperature**, not `gate`. Both open
rulings (PLAN §6b) are restated on that basis and neither is decided here.

**Budgets are the re-derived ones.** `BRIEF.md` / `brief.json` at `223373e`, taken on the
re-certified schematic row (S7 margin 34.94 mV). They are materially tighter than the ones the
report before last was written against, and §7 is read against them throughout. One budget row is
now known to be on the wrong quantity and §6.4 says so: `vss_active` should be written on the
common series element, not the worst device.

## 1. Outline, area, aspect

| | first drawing | reviewed drawing | **this drawing** | |
|---|---|---|---|---|
| outline | 287.4 x 122.9 um | 202.50 x 208.55 um | **211.14 x 209.65 um** | |
| aspect | 2.34 : 1 | 1.03 : 1 | **1.01 : 1** | ceiling 2:1 (PLAN A2) |
| bbox area | 35 317 um^2 | 42 231 um^2 | **44 266 um^2** | +4.8 % over the reviewed drawing |
| dummies | none | 16 MOS + 2 rhigh | **16 MOS + 4 rhigh** | XRB gained one at each end (F12) |
| guard rings | periodic point taps | 5 closed rings | **5 closed rings** | unchanged |

**Where the +4.8 % went**, measured by rebuilding this generator with each knob reverted to the
reviewed drawing's value:

| build | area | delta vs record |
|---|---|---|
| record (`pwr_w = 4.0`, `vss_ret_w = 3.0`) | 44 266 um^2 | |
| `pwr_w = 2.0` | 43 637 um^2 | -629 um^2 |
| `vss_ret_w = 0.8` | 43 574 um^2 | -692 um^2 |
| both reverted | 42 740 um^2 | -1 526 um^2 |

The two knobs together are 75 % of the growth and they interact (1 526 > 629 + 692): the right
cell edge is set by `max(x_cout_r + TM1_MIN_SP + pwr_w, ...)` while the left edge is set by
`x_res1 - 2.5 - vss_ret_w`, and the `vss` riser also pushes the XCFF/XCOUT margin. The remaining
509 um^2 (42 740 vs the reviewed 42 231) is the rest of the fix round: the two extra `rhigh`
dummies (F12) and the wider `vdd` contact rows (F4). The `ea_in_pair` / `bias_p_group` swap (F5),
the mirrored column reservation (F6) and the Metal3 gate track (F3) are area-neutral by this
measurement — they do not appear in any of the four builds' outlines.

Render of this drawing:
[`../../experiments/005-layout/figs/ldo_ihp_capless_r3.png`](../../experiments/005-layout/figs/ldo_ihp_capless_r3.png),
and `iterations/it11/layout.png`. **The labelled renders in that directory
(`ldo_ihp_capless_labelled*.png`) still show the reviewed drawing** — they are generated from
`labels.yaml` by a different lane and have not been regenerated here.

## 2. Current density

`spicexplorer_signoff.current_density` over the budget list the **generator emits from its own
drawn geometry** (`gen_ldo.power_budgets`), run by `layout/signoff.py` as a **blocking** stage.
Limits: `SG13G2_os_process_spec.pdf` §2.15. Measured currents: I(vdd) = 10.0318 mA,
I(XMP) = 10.0041 mA, I(vss) = 27.7 uA (brief §8).

**Rows changed because the table now describes what is drawn (review-003 F4).** The Via1 rows
read `x2`, not `x4`: `via_row(n=col_vias, rows=col_vias)` lays `col_vias` cuts out over
`col_vias` rows, i.e. one cut per row, so the count is `col_vias`. The contact row reads `x7`,
counted from the finger width rather than asserted as 4, and there is now a **vdd-side** contact
row as well as a vout-side one. Two rows are new: the two `vss` returns, which are separate paths
now (§6.4).

| net | segment | carries (mA) | drawn | limit (mA) | used/allowed |
|---|---|---|---|---|---|
| `vdd` | pass source column Metal1 riser (shared) | 0.263 | metal1 0.31 um | 0.36 | 0.731x |
| `vout` | pass drain column Metal1 riser (shared) | 0.263 | metal1 0.31 um | 0.36 | 0.731x |
| `vdd` | pass source column Via1 (shared) | 0.263 | via1 x2 | 0.80 | 0.329x |
| `vout` | pass drain column Via1 (shared) | 0.263 | via1 x2 | 0.80 | 0.329x |
| `vdd` | pass source column Metal2 finger | 0.263 | metal2 0.31 um | 0.62 | 0.425x |
| `vout` | pass drain column Metal2 finger | 0.263 | metal2 0.31 um | 0.62 | 0.425x |
| `vdd` | pass source Metal2 comb spine | 10.032 | metal2 6.0 um | 12.00 | 0.836x |
| `vout` | pass drain Metal2 comb spine | 10.004 | metal2 6.0 um | 12.00 | 0.834x |
| `vout` | pass drain diffusion contacts (shared column) | 0.263 | cnt x7 | 2.10 | 0.125x |
| `vdd` | pass source diffusion contacts (shared column) | 0.263 | cnt x7 | 2.10 | 0.125x |
| `vdd` | vdd riser Metal2->Metal3 | 10.032 | via2 x48 | 19.20 | 0.522x |
| `vdd` | vdd riser Metal3->Metal4 | 10.032 | via3 x48 | 19.20 | 0.522x |
| `vdd` | vdd riser Metal4->Metal5 | 10.032 | via4 x48 | 19.20 | 0.522x |
| `vdd` | vdd Metal5->TopMetal1 stitch | 10.032 | topvia1 x12 | 16.80 | 0.597x |
| `vdd` | vdd riser Metal3 pad | 10.032 | metal3 6.0 um | 12.00 | 0.836x |
| `vdd` | vdd riser Metal4 pad | 10.032 | metal4 6.0 um | 12.00 | 0.836x |
| `vdd` | vdd riser Metal5 pad | 10.032 | metal5 6.0 um | 12.00 | 0.836x |
| `vout` | vout riser Metal2->Metal3 | 10.004 | via2 x48 | 19.20 | 0.521x |
| `vout` | vout riser Metal3->Metal4 | 10.004 | via3 x48 | 19.20 | 0.521x |
| `vout` | vout riser Metal4->Metal5 | 10.004 | via4 x48 | 19.20 | 0.521x |
| `vout` | vout Metal5->TopMetal1 stitch | 10.004 | topvia1 x12 | 16.80 | 0.596x |
| `vout` | vout riser Metal3 pad | 10.004 | metal3 6.0 um | 12.00 | 0.834x |
| `vout` | vout riser Metal4 pad | 10.004 | metal4 6.0 um | 12.00 | 0.834x |
| `vout` | vout riser Metal5 pad | 10.004 | metal5 6.0 um | 12.00 | 0.834x |
| `vdd` | cell Metal1 vdd rail (row-B sources + XRB, Iq only) | 0.037 | metal1 0.8 um | 0.80 | 0.046x |
| `vss` | cell Metal1 vss rail (Iq only) | 0.028 | metal1 0.8 um | 0.80 | 0.035x |
| `vss` | vss active-device return: left edge riser (Iq only) | 0.028 | metal1 3.0 um | 3.00 | 0.009x |
| `vss` | vss XCOUT bottom-plate return: bottom rail (displacement current) | 0.028 | metal1 3.0 um | 3.00 | 0.009x |
| `vdd` | vdd TopMetal1 strap (top edge) | 10.032 | topmetal1 4.0 um | 60.00 | 0.167x |
| `vout` | vout TopMetal1 strap (right edge + XCOUT bus) | 10.004 | topmetal1 4.0 um | 60.00 | 0.167x |

**Worst 0.836x**, unchanged — the worst segment is the Metal2 comb spine, and neither `pwr_w` nor
the via-count corrections touch it. The TopMetal1 straps drop from 0.334x to 0.167x because they
are twice as wide (F1); that is not why they were widened (see §6.3).

## 3. DRC

| | |
|---|---|
| engine | KLayout 0.30.5, IHP SG13G2 runset, `sg13g2_maximal` |
| flags | `--no_density` (PLAN A7: fill is a chip-assembly step and distorts the PEX of a bare cell) |
| result | **0 violations**, no waivers |
| every documented knob endpoint | **0 violations**, 40/40 (§4) |
| gate | **blocking** — `layout/signoff.py` stops the run and writes no scorecard (F2) |

**"0 violations" is conditional on the density/fill tables being off**; that is the only rule group
switched off and nothing else is waived. The waived set, from `review-002` m1, is 12 rules:
`AFil.g`, `AFil.g2`, `GFil.g`, `M1.j`–`M4.j`, `M1Fil.h`–`M4Fil.h`, `TM2.c` (F18: the list is
carried here so a reader can compare it between drawings; this round did not re-run `--density`,
so whether the *set* grew with the new floorplan is still unverified — §10).

## 4. LVS, and the knob ranges

Both sizing points were re-run against **this** generator and **this** reference this round
(a routing bug is latent in the floorplan and only some sizings expose it):

| | this drawing (record sizing) | 002 hand sizing |
|---|---|---|
| reference | `lower(certified netlist) + declared dummies` | same |
| flags | `--combine_devices` | `--combine_devices` |
| DRC | **0** | **0** |
| result | **matched** | **matched** |
| gate | **blocking** — a build whose LVS does not match is a FAIL, never a scorecard (F2) | |

**The reference is derived, not typed.** `layout/netlist_ref.py` parses
`circuits/ldo_ihp_capless/pdk/ihp-sg13g2/netlist.spice` — which, since the re-certification
(`iterations/it10`), *is* the drawn device set — substitutes the sizing values, lowers the `X`
subcircuit calls to the primitive cards the deck reads, and drops `rhigh`'s poly-body node. The
only thing the reference adds is the layout's **dummy devices**, and the emitter asserts every
added card has all four terminals on one rail.

### 4.1 Every documented range, walked (review-003 F2)

`layout/signoff.py --stages bounds` builds the cell at **both ends of every `BOUNDS` row**, then
current-density-checks, DRC-checks and LVS-checks each one, two KLayout jobs at a time, and fails
if any endpoint is not clean. The previous table was never walked and five of ten values the
reviewer tried produced a cell that was not the certified circuit.

**40 / 40 endpoints clean** (20 knobs x 2 ends), each `built + DRC 0 + LVS matched + current density within limit`:

| knob | low | area | high | area | DRC | LVS | worst J |
|---|---|---|---|---|---|---|---|
| `blk_gap` | 4.0 | 43 428 | 15.0 | 48 134 | 0 | matched | 0.836x |
| `ch_margin` | 0.8 | 44 223 | 2.0 | 44 730 | 0 | matched | 0.836x |
| `col_vias` | 1 | 44 175 | 4 | 44 447 | 0 | matched | 0.836x |
| `dev_gap` | 3.0 | 44 266 | 6.0 | 49 704 | 0 | matched | 0.836x |
| `gpad` | 0.34 | 44 215 | 0.6 | 44 297 | 0 | matched | 0.836x |
| `grp_gap` | 0.0 | 44 266 | 8.0 | 44 266 | 0 | matched | 0.836x |
| `isl_gap` | 1.3 | 44 266 | 6.0 | 44 266 | 0 | matched | 0.836x |
| `mim_gap` | 2.5 | 43 846 | 8.0 | 48 573 | 0 | matched | 0.836x |
| `n_dummy` | 1 | 44 266 | 2 | 45 708 | 0 | matched | 0.836x |
| `pwr_band_w` | 5.1 | 43 885 | 12.0 | 46 799 | 0 | matched | 0.984x |
| `pwr_riser_vias` | 28 | 44 266 | 72 | 44 266 | 0 | matched | 0.896x |
| `pwr_stitch` | 8 | 44 266 | 24 | 44 266 | 0 | matched | 0.896x |
| `pwr_w` | 1.64 | 43 561 | 8.0 | 46 781 | 0 | matched | 0.836x |
| `rail_gap` | 1.4 | 44 181 | 2.5 | 44 646 | 0 | matched | 0.836x |
| `rail_w` | 0.5 | 44 234 | 1.4 | 44 329 | 0 | matched | 0.836x |
| `res_pitch` | 1.9 | 44 266 | 3.0 | 46 362 | 0 | matched | 0.836x |
| `ring_gap` | 0.6 | 43 928 | 3.0 | 44 941 | 0 | matched | 0.836x |
| `ring_w` | 0.5 | 44 181 | 1.5 | 45 026 | 0 | matched | 0.836x |
| `track_pitch` | 0.65 | 44 139 | 1.2 | 45 532 | 0 | matched | 0.836x |
| `vss_ret_w` | 0.8 | 43 574 | 6.0 | 45 638 | 0 | matched | 0.836x |

Area is the endpoint's own bbox, so the table doubles as the knob's area sensitivity: `dev_gap` (+5 438 um^2 across its range) and `blk_gap` (+4 706 um^2) are the only two that cost real silicon; every other knob moves the outline by under 1 %. Worst current-density ratio never leaves the limit: `pwr_band_w = 5.1 um` is the tightest at 0.984x, which is why 5.1 and not 5.0 is the floor.

**The bounds are derived from this walk, not asserted.** Against `iterations/it10/gen.py`, four rounds of walking moved five rows and changed the knob set (`diff` of the two `BOUNDS` dicts):

| row | it10 | record | why |
|---|---|---|---|
| `rail_w` | (0.5, **2.0**) | (0.5, **1.4**) | 2.0 leaves no free Metal2 column for `vout`; 1.6 does not build; 1.5 gives one M1.b |
| `col_vias` | (1, **2**) | (1, **4**) | raised: the drain via pad reached into the gate bar at 4, fixed by deriving `gate_gap_P` from `gpad` |
| `pwr_w` | (1.64, **6.0**) | (1.64, **8.0**) | raised, after the right cell edge was made to follow `pwr_w` through `pwr_extra` |
| `res_pitch` | (**1.8**, **4.0**) | (**1.9**, **3.0**) | both ends were LVS mismatches; 3.0 also exposed the dead `x_pass_r` |
| `n_dummy` | (**0**, 2) | (**1**, 2) | 0 dummies is not a floorplan this cell may draw |
| `tap_pitch` | (6.0, 18.0) | *deleted* | the knob had no effect after the rings closed |
| `gpad`, `vss_ret_w` | *absent* | (0.34, 0.6), (0.8, 6.0) | new knobs (F3, F9) |

A `LayoutParams` field with no `BOUNDS` row is an `AssertionError` at import, so the two can no longer drift.

Four of the reviewer's eight failing endpoints were **generator bugs and are fixed**; three ranges
were **narrowed** because the limit is geometric and the knob has somewhere else to go; one
(`vss_ret_w`, new) was fixed by the same edge-placement change as `pwr_w`. PLAN §5 carries the
per-knob reasons. `gen_ldo.py` now also asserts at import that `BOUNDS` and `LayoutParams` name
the same knobs, so a dead search dimension (`tap_pitch`, F11) or an undocumented one (`isl_gap`)
fails the build rather than the review.

## 5. PEX

**Superseded by round 6.** `SIGNOFF.md` moved the post-layout row of record from CC to the
stitched RC row (its own re-extraction, re-measured from raw artefacts) — see the note after this
table. The row below is left as this report measured it; read "row of record" in the CC line as
historical.

| mode | halo | netlist measured | C | R | mesh | benches |
|---|---|---|---|---|---|---|
| **CC** — **the ideal-metal comparison row** (was called "the row of record" here; superseded, see round 6 above) | tech default, SG13G2 8 um sidewall | `…_k25d_pex_netlist.spice` (there is no other) | 186 | 21 | n/a | 13/13 ran, **0 spec violations** |
| **RC** — **the post-layout row of record** (moved here in round 6; measured once in this round) | same | **`…_k25d_pex_netlist_stitched.spice`** | 186 | 8 583 raw → **5 484 measured** by this report (5 463 `Rext` + 21 device; the stitcher collapses 3 099 zero-ohm merge cards, and §5 item 3 floors the 2 it leaves) — **the verifier's independent re-extraction counts 5482 R (5461 `Rext_` + 21 `rhigh`) after contracting all 3101 zero-ohm ties instead of flooring 2 of them; this report's 5484 is superseded, not wrong — it is the floored count, one card different from the contracted one** | **connected**: 220/243 device pins, **0 open nets**, 19 stub nets, 15/15 named ports anchored on a `[Pin]` node | 13/13 ran, **0 spec violations** |

**Which file is measured is now a decision, not a glob** (review-004 F27). kpex writes the raw
netlist *and*, for RC, a stitched one — and `PexResult.netlist_path` names the stitched one. The
old `rglob("*_pex_netlist.spice")` does not match the stitched name, so with both present it found
exactly one file, reported no ambiguity, and measured the **raw** netlist: an RC scorecard from
that path is the artefact whose mesh is not in the circuit. `select_pex_netlist()` now takes the
path from the PEX stage's own record, prefers the stitched half of an RC pair (with a printed
note), and stops on a real ambiguity; five cases in `layout/test_builder.py` pin it, and they were
written failing.

**The RC mesh is joined and its values are still not usable here.** review-003's finding — the
mesh was an electrical island, zero device pins on it — is **fixed upstream**
(`spicexplorer-platform @d708816`, `@b61f6c7`, `@9df117b`) and the fix is visible in the record
above. Two things followed from this round's own runs:

1. **The port anchors were wrong and are now right, because of a change to the drawing.** kpex
   emits a `[Pin]` node only when a label sits inside a polygon on the layer's **pin purpose**;
   the cell drew labels only, so the stitcher anchored every port on a node it picked (review-004
   F25 measured the proxy ~100 um from the drawn port). PLAN A14 adds a 0.2 um square on
   `<metal>/2` under all 17 labels, and the anchor census goes from 0 to **15 of 15 named ports on
   `pin`** (the 18 remaining proxies are anonymous `$NN` divider nets). It is geometry only, and
   that is proved rather than asserted: DRC 0, LVS matched, current density 30/30 worst 0.836x
   unchanged, and the **CC extracted netlist is byte-identical** to the one the record scorecard
   was made from — 418 of 418 lines, zero differences. Nothing in sections 6-8 moves.
2. **The stitched netlist did not regulate, and the cause is two zero-ohm cards.** The first
   scoring of it, tt/27, ran 13/13 benches to convergence — no singular matrix, no gmin stepping
   — and reported `v_out` **1.4999 V** against 1.1995, `i_q` **12.66 uA**, `psrr_1k` **-0.042 dB**.
   That looked like a topology break in the spliced block. It is not; it is arithmetic, and the
   evidence is the feedback divider, sixteen **identical** 126 kOhm `rhigh` segments in series
   from `vout` to `vss`:

   | | drop per segment, top eight | drop per segment, bottom eight | `fb` |
   |---|---|---|---|
   | as translated | 186.25 mV | 1.248 mV | 9.99 mV |
   | required by the network | equal | equal | `vout`/2 |

   A series chain of identical linear elements cannot do that: the reported point violates KCL at
   `fb` by ~1.5 uA with no card able to carry it (the `fb` mesh terminates on two MOS gates and
   capacitors, and all 44 of its nodes sit within 1 nV of each other). It survives replacing the
   `rhigh` subcircuits with ideal linear resistors, survives SPARSE **and** KLU, and survives a
   `.nodeset` seeded from the correct solution — so it is not a convergence basin either. What
   causes it: kpex writes a **zero-ohm resistor** where it means "these two nodes are one".
   The raw RC netlist has **3 101** of them; the platform's stitcher collapses 3 099 and leaves
   **two** — the `[Pin]` anchors `Rext_971 fb fb.$24.18 0 R` and `Rext_7135 vref vref.$0.18 0 R`.
   ngspice does not merge: it clamps each to **1e-12 ohm** and puts a 1e12 S entry into a matrix
   whose signal entries are ~1e-5 S, and the direct solve then returns a non-solution, quietly.
   Give those two cards a finite value and the same netlist regulates:

   | the two ties at | `v_out` | `i_q` | `fb` |
   |---|---|---|---|
   | 0 (ngspice: 1e-12 ohm) | 1.4999 V | 12.66 uA | 9.99 mV |
   | 1e-3 ohm | **1.1995 V** | 33.77 uA | **599.7 mV** |
   | 1e-6 ohm | 1.1995 V | 33.77 uA | 599.7 mV |

   `postlayout.floor_zero_r()` therefore floors any zero-valued `Rext_` card at **1 mOhm** — a
   millionth of the mesh's own smallest segment, worth a nanovolt — and leaves every device
   resistor alone; the case is in `layout/test_builder.py`. It is a no-op on CC (a CC netlist has
   no `Rext_` cards at all, and re-translating the CC extraction reproduces the committed
   `asbuilt/core_pex.sp` line for line apart from kpex's date stamp), so **no number in sections
   6–8 or in `experiments/007` moves.** The RC row was measured twice: once before the floor
   (above) and once after (below).

3. **The RC row, measured.** Scored once at tt/27 on the floored stitched netlist, 13/13 benches,
   **0 spec violations** — the whole S1–S8 box passes on the extraction that carries the drawn
   metal's resistance. Against the CC row of record:

   | metric | CC (record) | RC (stitched) | delta | spec |
   |---|---|---|---|---|
   | `v_out_v` | 1.199499 | 1.199498 | −1 uV | S1 1.176–1.224 V |
   | `i_q_ua` | 33.81 | 33.77 | −0.04 uA | S5 ≤ 50 |
   | `load_reg_mv` | 0.026 | 0.027 | +0.001 | S2 ≤ 5 |
   | `line_reg_mv` | 0.056 | 0.056 | 0 | S3 ≤ 2 |
   | **`v_dropout_mv`** | **104.7** | **134.7** | **+30.0 (+28.7 %)** | S4 ≤ 200 |
   | `psrr_1k_db` | 70.09 | 70.06 | −0.03 | S6 ≥ 40 |
   | `v_undershoot_mv` | 127.6 | 129.5 | +2.0 | S7 ≤ 150 |
   | `pm_loop_deg` | 69.30 | 69.33 | +0.03 | S8 ≥ 60 |
   | `ugf_loop_khz` | 777.3 | 775.5 | −1.8 | — |
   | `ms_peak_db` | 10.32 | 8.59 | −1.73 | — |
   | `v_line_pp_mv` | 55.72 | 56.41 | +0.7 | — |

   Everything except dropout is inside the noise of the CC row. **Dropout is not**: +30 mV is the
   IR drop of the drawn `vdd`→pass→`vout` metal at 10 mA, which a CC extraction cannot see, and it
   is larger than any budget in section 7. At the time of this report the **record row stayed
   CC** and the difference was reported, not adopted — S4's margin is 95.3 mV on the CC row and
   65.3 mV on the RC row, both passing, and which row is the row of record was left to the
   coordinator. `scorecard_post_rc.json` carries the RC row verbatim.

   **Round 6 (superseding the paragraph above).** The coordinator's round-3 platform result and
   the independent `SIGNOFF.md` pass both moved the record: **the post-layout row of record is
   now the stitched RC row**, re-measured by the verifier on its own rebuilt GDS and extraction —
   3101/3101 zero-ohm `[Pin]` ties contracted (0 left), 15/15 named ports anchored on a pin, 13/13
   benches reproduce `scorecard_post_rc.json` to 1e-9 relative on every spec metric, 8/8 spec
   lines PASS. CC is now the **ideal-metal comparison row** — the same layout with every wire
   resistance set to zero, kept because it is the only row that isolates the extracted
   capacitance from the extracted resistance. The +30 mV is confirmed physical, not an artefact
   of the extraction (§6.3), and the brief's pooled dropout budget is **missed**, not met, at the
   record row (§10.7).

**Series resistance now has two independent numbers, and they agree where they overlap.** §6.3 and
§6.4 solve the drawn metal by hand (`layout/rail_solve.py`); the RC row measures it in circuit.
The one place they can be compared is PSRR: the hand solve puts the `vss` return at 4.743 Ohm and
predicts 67.33 dB, while the RC mesh — which distributes the same metal instead of lumping it in
series with everything — gives **70.06 dB**, i.e. the lumped model is the pessimistic bound it was
meant to be, and the mesh number supersedes it. The earlier write-up of the
island defect, with argv and a ten-line reproduction, is at `$SX_SCRATCH/ldo-review/
pex_rc_defect.md`; the counts it quotes for "how many benches abort" should not be re-quoted —
they were artefacts of an ill-conditioned matrix and differed run to run (review-004 F23: the
reviewer got 4/13 where this report said 8/13). The deterministic statement is the node-set one:
before the platform fix, `mesh nodes ∩ device pins = ∅`; after it, 220 of 243.

**Extraction blind spots, stated not discovered.** The MIM capacitors are stripped from the GDS
before kpex (it cannot read `cap_cmim`) and spliced back as schematic devices, so **Metal5
bottom-plate coupling to the neighbourhood is extracted and top-plate coupling is not**;
n-well-to-substrate junction capacitance is in neither the extractor nor the model cards; couplings
wider than the 8 um tech sidewall halo are dropped; there is no inductance.

**Where kpex's stray file goes — traced to the line.** kpex drives its own KLayout LVS pass and
never passes `-rd target_netlist=` to the runset (`klayout_pex/klayout/lvs_runner.py:49-69`,
`kpex_cli.py:837-844`), so `sg13g2.lvs` takes its `else` branch:

```ruby
layout_dir   = Pathname.new(RBA::CellView.active.filename).parent.realpath   # sg13g2.lvs:232
netlist_path = layout_dir.join("#{source.cell_name}_extracted.cir")
```

The destination is whatever `RBA::CellView.active.filename` resolves to, and it has **two
behaviours**, both observed:

| `CellView.active.filename` | `Pathname(...).parent.realpath` | observed |
|---|---|---|
| the loaded input GDS (normal) | the GDS's directory | `$SX_SCRATCH/ldo-fix/wf/ldo_ihp_capless_extracted.cir`, beside `ldo_ihp_capless_pex.gds` (`-rd input=` in the kpex LVS log names that path) |
| `""` (no active view) | **the parent of the process cwd** — `Pathname.new("").parent` is `..`, not `.` | the single `ldo_ihp_capless_extracted.cir` one level above this repo (mtime 2026-09-05 00:40), written when the PEX stage still ran with the repo as its cwd |

No kpex flag suppresses either. Our containment is that the PEX stage now runs with the run
directory as its cwd **and** hands kpex a GDS that lives in it, so both branches land under
`$SX_SCRATCH`. It has not recurred in the ~12 kpex runs of this round. The review-round file is
left in place for the coordinator. Our own `spicexplorer_signoff.lvs` path was never affected —
the PDK's `run_lvs.py` sets `target_netlist`, so the deck takes the `if` branch and writes into
the LVS run directory (`wf/lvs/ldo_ihp_capless_extracted.cir`). The platform-side fix, if wanted,
is the same one line in `spicexplorer_signoff.pex`: pass `-rd target_netlist=<run_dir>/…` through
to the runset.

## 6. Pre- vs post-layout scorecard, and where each delta comes from

The cell's own 13 frozen benches, all rows simulated through the frozen path
(`ldo.sim.run` + `ldo.metrics.promote`), `layout/postlayout.py`. **The third column the previous
report needed is gone**: since `iterations/it10` the certified deck *is* the drawn device set, so
"pre-layout" and "the drawn geometry with no parasitics" are the same row — verified, not assumed
(`postlayout.py --no-c` reproduces the pre-layout row to the printed digits on every spec metric;
the three no-spec columns move within one resolution step — `gm_loop` 6.134 vs 6.133,
`ms_peak` 7.805 vs 7.813, `v_line_pp` 51.44 vs 51.45 — which is the re-inserted `VSUBSTIE`
branch, not a parasitic).

| metric | pre-layout (certified) | post-layout (extracted) | delta |
|---|---|---|---|
| `v_out_v` | 1.1995 | **1.1995** | 0 |
| `i_q_ua` | 33.8054 | **33.8054** | 0 |
| `load_reg_mv` | 0.026 | **0.026** | 0 |
| `line_reg_mv` | 0.056 | **0.056** | 0 |
| `v_dropout_mv` | 104.671 | **104.671** | 0 |
| `psrr_1k_db` | 70.007 | **70.093** | +0.086 |
| `v_undershoot_mv` | 115.057 | **127.558** | **+12.50** |
| `pm_loop_deg` | 72.506 | **69.301** | **-3.21** |
| `pm_loop_lo_deg` | 72.473 | **69.270** | -3.20 |
| `pm_loop_hi_deg` | 72.418 | **69.186** | -3.23 |
| `loopgain_db` | 50.224 | **50.224** | 0 |
| `ugf_loop_khz` | 801.5 | **777.3** | -24.2 |
| `gm_loop_db` | 6.133 | **7.721** | +1.59 |
| `ms_peak_db` | 7.813 | **10.319** | +2.51 |
| `psrr_1m_db` | 15.144 | **14.318** | -0.83 |
| `t_transient_us` | 0.15625 | **0.19011** | +0.0339 |
| `vn_out_urms` | 372.9 | **361.8** | -11.1 |
| `v_line_pp_mv` | 51.45 | **55.72** | +4.28 |
| **spec box** | [1.176,1.224] / <=50 / <=5 / <=2 / <=200 / >=40 / <=150 / >=60 (x3) | **0 violations** | |

Bench resolutions (brief §1): `v_out_v` 2e-6, `load_reg`/`line_reg`/`i_q` 0.001, `v_dropout` 2,
`psrr_1k` 0.001, `v_undershoot` 0.005, `pm_loop` 0.03.

**Every delta above the noise floor, with the parasitic that causes it — each verified by a
what-if** (`layout/postlayout.py --keep-c/--drop-c/--no-c`, which deletes only `Cext_` cards, runs
the same frozen benches, and writes to its own directory so it can never overwrite the record):

| what-if | S7 undershoot (mV) | PM (deg) | reads |
|---|---|---|---|
| no extracted C | 115.06 | 72.51 | = the pre-layout row on every spec metric |
| **all** extracted C (the post-layout row) | **127.56** | **69.30** | |
| `gate` C only | **201.72** | 72.48 | over the 150 mV line on its own |
| everything except `gate` | 110.03 | 69.31 | *better* than pre-layout |
| `fb` C only | 110.90 | **70.22** | PM: -2.29 deg |
| `lp_brk` C only | 116.32 | 72.86 | +0.35 deg |

- **`v_undershoot_mv` +12.5 mV.** The cause is `gate`, and the recovery is real but not a credit:
  `gate` alone is 201.7 mV, and the other nets bring it back to 127.6. Adding one net at a time
  recovers ~75–90 mV each and all of them together recover barely more than any one — a saturating
  mechanism on the `ea_o1 -> ea_out -> gate` path, which brief §3 n4 forbids as a linear per-fF
  credit. So this report claims **no** credit for it and states the gate-only number as the one to
  design against. S7 keeps 22.4 mV of margin as drawn.
- **`pm_loop_deg` -3.21 deg.** `fb` alone accounts for **-2.29 deg** of it, and `fb`'s to-rail C
  is 21.20 fF at the brief's -0.111 deg/fF = -2.35 deg — agreement to 0.06 deg. The remaining
  -0.9 deg is `ea_o1` (43.9 fF to rail on the Miller node). Against the reviewed drawing this is a
  **+0.54 deg improvement**, and it is F5: the `fb` track went from 107.15 um to 79.57 um when
  `ea_in_pair` became the first group of row B.
- **`ugf_loop_khz` -24.2 kHz**, **`gm_loop_db` +1.59**, **`ms_peak_db` +2.51** — the same added
  phase lag on the Miller node; no spec line on any of the three.
- **`t_transient_us` +0.034 us** — the recovery of the same `gate` slew as the undershoot.
- **`psrr_1k_db` +0.086**, **`psrr_1m_db` -0.83**, **`v_line_pp_mv` +4.28**, **`vn_out_urms`
  -11.1 uVrms** — high-frequency and noise columns, no spec line; the first is inside one
  resolution step.
- **Everything else is exactly zero**: DC operating point, Iq, dropout, both regulation lines and
  the loop gain are unchanged to the last digit the benches print, because the certified deck now
  carries the drawn device set.

### 6.1 F3 — the gate objective, and why neither routing nor a legal sizing reaches it

The re-derived brief (§2, §3, §3b) tightens the target: **12 fF to a rail**, with a measured step
between 12 and 13 fF (S7 120.97 -> 178.52 mV), and re-brackets the escape route — capacitance to
`vout` costs +0.0197 mV/fF against +0.507 mV/fF to a rail, **26x cheaper**, with its own step at
40-45 fF. The gate budget is stated **gate-only** and the EA-path recovery is explicitly excluded,
so this report banks none of it.

**The drawn cell, measured (kpex CC, tech-default halo):**

| | reviewed drawing | **this drawing** | budget |
|---|---|---|---|
| `gate` total C | 47.49 fF | **44.50 fF** | - |
| `gate` **to-rail** (VSUBS + vdd + vss) | 34.5 fF | **34.45 fF** | **12 fF** -> **2.87x, past the 13 fF step** |
| of which to `VSUBS` | - | 29.00 fF | |
| of which to `vdd` / `vss` | - | 5.13 / 0.32 fF | |
| `gate` to `vout` (the escape route) | 10.9 fF | **8.91 fF** | 40 fF -> 0.22x |
| **gate-only S7** | 204.50 mV | **201.72 mV** | <= 150 mV -> **OUT by 51.7 mV** |

**How much routing can still buy — measured, not estimated.** Two experiments:

1. **The whole gate track is worth 3.0 fF.** `dev_gap` 3.2 -> 6.0 um (a bounds-verified endpoint)
   lengthens the Metal3 `gate` track from 50.77 to 59.17 um and moves `gate` to-rail from 34.45 to
   **34.95 fF** — **0.060 fF/um**. At that slope the entire 50.77 um track carries ~3.0 fF, so a
   perfect `vout` shield under it can move at most 3.0 fF into the 26x-cheaper column: 34.45 ->
   ~31.4 fF, still **2.6x** the budget. That is **13 % of the 22.5 fF shortfall.**
2. **The rest is the pass array's own gate structure, and it is a sizing knob.** Building at
   `x_dut_xmp_nf_mult` = 2 (half the fingers, same total W) gives `gate` 33.70 fF total /
   **26.63 fF to-rail** — **3.9 fF of to-rail per unit finger multiple**, extrapolating to a floor
   of ~18.8 fF as nf_mult -> 0. And nf_mult = 2 is already **1.46x over the Metal1 current-density
   limit** on the shared S/D column, so it is not available. Independently, taking `gpad` from 0.5
   to 0.34 removes 32 % of the gate bar's Metal1 and poly *area* and buys **0.30 fF of 34.45** —
   the term is the bar's edges and the 76 poly tabs that run from it to the fingers, not its area.

**What a Metal3-over-Metal2-shield stack would cost.** The shield has to sit between the gate
track and the substrate and be tied to `vout`. Metal2 at the gate track's y is not available — the
channel's Metal2 columns cross that y on their way from row B to their own tracks — so the
workable stack is **gate on Metal4 over a `vout` Metal3 shield**, ~51 x 1 um of Metal3 plus a
Via1-3 stack from the `vout` channel track. Cost: no area (it is over the existing channel), about
+3 fF on `gate`-to-`vout` (8.91 -> ~12 fF against a 40 fF limit, so it fits), one more crossing
class for the router to get right, and one more layer in the gate's via stack. Benefit: **3.0 fF
of 22.5**. It is not built, because 13 % of a shortfall is not a fix and the router risk is real.

**Status: NOT FIXED, and it is not fixable by layout.** 12 fF to-rail is out of reach at every
legal value of `x_dut_xmp_nf_mult` and with the best shield the stack allows. This is a
spec/topology conflict, filed as **PLAN §6b open ruling 1** for the owner: a smaller pass device,
a different output stage, a deliberate certified capacitor on `ea_o1` (brief §3b measures the EA
recovery as real but says it must be a *design* decision, not a routing accident), or a wider S7
line. What the layout does do is spend the escape route it has: the `gate` track is the top
channel track, immediately under the `vout` bus, and 8.91 fF of the 44.50 is on the 26x-cheaper
column.

### 6.2 F8 — where the divider senses

`lp_brk` is the divider's top terminal *and* the loop-break port: the certified netlist closes it
with `VLP lp_brk vout dc 0`, which the loop-gain bench drives. The cell therefore cannot merge
`lp_brk` into `vout` without deleting a pin the benches use. What the layout decides is **where
the external short lands**, and brief §4 makes that a 14x budget difference (0.126 Ohm at the pass
drain, 1.78 Ohm at the pin) worth ~10 mV of load regulation against a 5.0 mV line.

Drawn: the `lp_brk` track is escaped to the **right cell edge, beside the `vout` pin**, and
labelled there. The GDS now says which tap the cell offers; PLAN A12 records it as an interface
contract. The cost is measured: `lp_brk` C rose to 37.9 fF total / 24.3 fF to rail (it has no
budget), the run is the track's own 0.2 um Metal1 (~104 Ohm, a **static** 0.13 mV offset at the
divider's 1.2 uA, not a load-dependent term), and the `lp_brk`-only what-if moves PM by +0.35 deg
and S7 by +1.3 mV.

### 6.3 Series resistance — the hand model, scored against the brief's own pool

This is a hand model from the drawn geometry, written before the RC row existed and kept because
it is the only *per-net* breakdown; the RC row now measures the same thing end to end (§5) and the
two are reconciled at the end of this section. Sheet resistances:
TopMetal1 sheet resistance 18 mOhm/sq, Metal1 110 mOhm/sq
(`libs.tech/magic/ihp-sg13g2-extract.tech`), lengths read pin-label-to-riser out of the builder.

**`vdd` and `vout` share one dropout pool** (re-derived brief §4a):
**10.34 x R(vdd) + 8.64 x R(vout) <= 23.83 mV**, i.e. 25 % of the 95.3 mV dropout margin.

| net | path | length | at `pwr_w` = 2.0 (reviewed) | at `pwr_w` = 4.0 (**drawn**) | own budget |
|---|---|---|---|---|---|
| `vdd` | top-edge strap, pin at x = -65.5 to riser at x = 67.4 | 132.9 um | 1.196 Ohm | **0.598 Ohm** | 2.31 Ohm |
| `vout` | riser at (67.4, 55.3) to pin at (133.6, 0) | 123.6 um | 1.112 Ohm | **0.556 Ohm** | 2.76 Ohm |
| | **pooled dropout cost** | | 21.98 mV (**92 %** of the pool) | **10.98 mV (46 %)** | <= 23.83 mV |

**The CC scorecard column does not contain that 10.98 mV**, which is the reason it is not
reported as zero. The brief's own splice of the `pwr_w` = 2.0 hand model into the frozen benches
measures **+20.04 mV** of dropout (84 % of the pool); halving both resistances halves it. Hand
model: measured CC dropout 104.7 mV + 11.0 mV = **115.7 mV** against a 200 mV line.

**The RC row measures 134.7 mV** (§5), i.e. **+30.0 mV**, 2.7x the hand model's 11.0. The hand
model counts only the two straps between pin and riser; the mesh also carries the risers
themselves, the via stacks, the 39 pass-device column feeds and the source/drain contact rails —
the parts of the path this section never modelled. The hand model is therefore a **lower** bound
on the dropout term, not an estimate, and §7's `vdd`/`vout` budget rows should be read that way.

**Round 6 — the +30 mV is physical, and the platform's investigation names where it lives.**
`SIGNOFF.md` re-measured the record row at **134.663 mV** (**+29.99 mV** over CC's 104.671) and
established, from its own re-extraction, that no zero-ohm card or floor is behind it: the RC mesh
now has zero zero-ohm ties (all 3101 contracted), and the CC row — same layout, same capacitance,
no wire resistance — sits 29.99 mV lower, so the whole delta is series resistance. At the 10 mA
dropout point that is **29.99 mV / 10 mA = 3.00 Ω** of pooled `vdd` + `vout` metal — the size of a
real strap-and-via stack, not a numerical residue. The coordinator's round-3 decomposition of that
3.00 Ω, **quoted here and not re-derived by this report**: **15.67 mV** from `vdd` → the 39 pass
sources plus **15.21 mV** from the drains → `vout` (= 30.88 mV ≈ 10 mA × 3.088 Ω), **85 %** of it
the shared **TopMetal1 strap** (0.59 Ω) and the **Via2–TopVia1 stack** (0.75 Ω) — neither of which
divides by the 39 parallel columns the hand model above assumes — **contacts 4 %**, and the two
former zero-ohm cards worth 0.00 mV.

**The pooled dropout budget is MISSED, not met, at the record row.** `brief.json`'s
`dropout_pool` rule, `10.34 × R(vdd) + 8.65 × R(vout) ≤ 23.83 mV` (a quarter of the S4 margin), is
scored against the RC measurement at **29.99 mV — 1.26× the 23.83 mV allowance** (the brief's own
linear form, fed the coordinator's 1.567/1.521 Ω split, gives 29.35 mV, 1.23× — both readings
miss). Each **individual** net's series-R budget is still met (`R(vdd)` 1.57 Ω of a 2.31 Ω
allowance, `R(vout)` 1.52 Ω of 2.76 Ω); it is the **shared pool** they both draw on that is
over. S4 itself is not at risk — 134.66 mV against 200 mV is 65.3 mV of margin, 33 % — this is a
design-discipline budget miss, not a spec failure, filed as an open finding in §10.7 with its fix
path: widen the shared TopMetal1 strap and/or the Via2–TopVia1 stack, the two elements that do not
divide by the column count. Any redraw that changes those elements also changes the extracted
capacitance at `ea_o1` (currently 64 fF), which is what the mismatch box edges in §8/§4 of
`SIGNOFF.md` rest on — a redraw here must re-bisect those edges, not just re-check S4.

The brief also settles F8 as a measurement rather than an estimate: with the divider sensing at
the **pass drain** the same metal gives **S2 = 10.22 mV against a 5 mV spec — out of the box** —
and it is allowed only 0.126 Ohm there, 22x less than at the pin. The cell draws the tap at the
pin (§6.2).

### 6.4 F9 — the `vss` cliff is shared impedance, and the fix is a connection

The reviewer's severity was right and the mechanism was not. The re-derived brief §4a splits the
injection and settles it:

| what is behind the R | 32 Ohm gives | reads |
|---|---|---|
| the whole cell (active devices **and** XCOUT's plate) | S7 **218.06 mV — OUT**, PSRR 62.04 dB | a hard step between 11 and 12 Ohm |
| the **active devices only** (XCOUT returned to the pin) | S7 **115.50 mV**, +0.44 mV | no step at all; PSRR binds at **16 Ohm** |
| **XCOUT's bottom plate only** | S7 **103.20 mV** — *better* than baseline | textbook ESR-zero damping |

So the cliff needs both halves behind one R: Cout's load-step displacement current develops a
ground bounce the FVF's sources and the EA read as a reference step. Static arithmetic agrees —
26 uA through 11 Ohm is 0.4 mV, which cannot move a 115 mV undershoot.

**Drawn (PLAN A10).** The `vss` **pin is the foot of a single left-edge riser**,
`vss_ret_w = 3.0 um` wide and 134.0 um long. The active devices reach that pin down that riser
alone; XCOUT's four bottom plates reach **the same pin** along the bottom rail on their own
`vss_ret_w`-wide straps. The second (right-edge) riser of the first fix round is **deleted on
purpose**: it would have run the active current the length of the bottom rail, which is the cap's
return — putting back exactly the shared impedance the cliff is made of.

**The numbers below are solved, not modelled — and the two this report printed last round were
wrong** (review-004 F9). `layout/rail_solve.py` rasterizes the drawn Metal1 at 0.1 um, keeps the
4-connected component that touches the `vss` pin, and solves the resistor grid at the PDK's
110 mOhm/sq with a terminal contracted to the drawn face rather than a point; it lands on an
analytic 9.9 x 1 um bar to **0.00 %** (`--selftest`). The reviewer's independent Laplace solve is
in the last column:

| path | drawn | **solved** | reviewer | budget |
|---|---|---|---|---|
| active devices -> pin, common series element (the riser) | 134.0 um of 3.0 um Metal1 | **4.74 Ohm** | 4.84 | 16.48 Ohm (S6, active-only) |
| worst device (`XMS`b, x = 90.9-95.7) | + the cell rail | **20.56 Ohm** | 20.88 | 16.48 Ohm — **1.25x, OVER** |
| nearest device (x = 0.5) | + a short rail run | **14.40 Ohm** | 14.3 | — |
| XCOUT plates -> pin (the cap's own ESR) | bottom rail, 3.0 um, 71-198 um | 2.6-7.3 Ohm (hand) | — | no bound (more is mildly *better* for S7) |
| shared between the two | the pin | **~0 Ohm** | — | the 11 Ohm cliff does not apply |

**What this report got wrong, and why.** The 14.3 Ohm printed last round credited the row-A ptap
ring over the whole 170 um of the return. The ring spans only **x = -3.4 .. 105.6**; from the
riser top the return runs 66.6 um of *bare* 0.8 um rail before it. 14.3 Ohm is the solve for a
device at the **near** end of the row, not the far end — my own solver now returns 14.40 Ohm for
exactly that device, which is how the error is identified rather than merely conceded. §10.4's
"`rail_w` 1.2 -> ~12.7 Ohm" has the same origin: rebuilt and solved, `rail_w` = 1.2 gives
**16.22 Ohm** and `rail_w` = 1.4 gives **14.89 Ohm** (reviewer: ~16.6 and 15.13).

**But the per-device spread is not the quantity the metric follows**, and that is the reviewer's
finding, reproduced here rather than accepted. The CC extraction carries no wire resistance at
all, so the committed `psrr_1k` = **70.093 dB is measured with an ideal ground return**.
`layout/postlayout.py --vss-r <Ohm>` puts the drawn return in circuit (every card inside the block
moved to an internal `vss_ret`, XCOUT excepted — it has its own strap to the pin — and one
resistor to the pin), and runs the same frozen benches:

| in-circuit model | `psrr_1k` | S7 | box |
|---|---|---|---|
| ideal return (the committed row) | 70.093 dB | 127.560 mV | PASS |
| **the solved common element, 4.74 Ohm** | **67.329 dB** (-2.76) | 127.582 mV | PASS, 27 dB of margin |
| a pessimistic lump: the *worst* device R, 20.56 Ohm, on everything | 61.051 dB (-9.04) | 127.656 mV | PASS |
| **the extracted RC mesh** (§5, measured, not modelled) | **70.06 dB** (-0.03) | 129.5 mV | PASS |

The reviewer's own figure for the middle row is 67.316 dB (they model the per-device spread
explicitly; I lump it), i.e. the two methods agree to 0.013 dB. **The last row supersedes both**:
the RC mesh distributes the same metal along the return instead of putting all of it in series
with everything the block contains, and it costs 0.03 dB, not 2.76. The lumped rows are what they
were built to be — a bound — and the bound is loose by ~2.7 dB. F9's severity survives the mesh
only as an accounting correction. **So F9's deliverable is a corrected budget, not a redrawn
cell**: the quantity to budget is the **common series element**,
4.74 Ohm against 16.48, **0.29x** — and the "worst active device" row should come out of the
brief, because the entire drawn per-device spread is worth about **+0.04 dB** of PSRR. `rail_w`
0.8 -> 1.4 is measured (bounds endpoint, DRC 0, LVS matched, CD 0.836x) and buys ~1 dB; the
better lever for the quantity that matters would be `vss_ret_w`, which acts on the common
element. Neither is drawn: S6 has 27 dB of margin.

## 7. Per-net parasitic budget (re-derived brief §2, kpex CC, tech-default 8 um halo)

**One accounting convention, stated (review-003 F10).** The brief's coefficients are **to-rail**
coefficients, so the budget column is read against to-rail capacitance for every net; raw totals
sit beside it. **Every net is listed** — the previous table truncated at the top twelve, which is
why `x1` and `y` read "< 17.7" when they are a fifth of their budgets.

Budgets are the re-derived ones (BRIEF.md @ `223373e`), taken on the re-certified schematic row
whose S7 margin is 34.94 mV. They are materially tighter than the ones the previous report used.

| net | budget (fF, to-rail) | hard limit | reviewed drawing (total) | this drawing (total) | this drawing (to-rail) | used/allowed |
|---|---|---|---|---|---|---|
| `gate` | **12** | **step 12->13 fF** | 47.49 | 44.50 | **34.45** | **2.87x — OVER, §6.1** |
| `gate` -> `vout` (the escape route) | 40 | step 40-45 fF | 10.9 | 8.91 | - | 0.22x |
| `fb` | 27.1 | - | 33.97 | 31.90 | **21.20** | **0.78x** |
| `x1` | 28.3 | step 30-40 fF | 11.28 | 11.38 | 6.91 | 0.24x |
| `y` | 39.4 | step 50-60 fF | 11.50 | 11.62 | 8.34 | 0.21x |
| `ea_n` | 90.7 | - | 17.7 | 17.99 | 10.03 | 0.11x |
| `ea_tail` | no bound (6.2 pF) | - | 19.4 | 18.02 | 6.68 | - |
| `pbias` | no bound (8.7 pF) | - | 25.8 | 22.19 | 13.95 | - |
| `ea_o1` | no bound | - | 64.91 | 64.11 | 43.92 | - |
| `ea_out` | no bound | - | 26.44 | 26.63 | 16.72 | - |
| `lp_brk` | no bound | - | 18.2 | 37.93 | 24.26 | - |
| `nbias` | no bound | - | 31.4 | 30.35 | 20.24 | - |
| `vref` | no bound | - | - | 5.98 | 3.22 | - |
| `vout` | no bound | - | 82.67 | 109.17 | 96.73 | - |
| `vdd` | no bound | - | 159.16 | 163.26 | 127.22 | - |

**One coupling budget is new and is the second-tightest ratio in the cell: `fb` <-> `lp_brk`
<= 6 fF.** Brief §3 measures 2 % of the 0.1 pF feedforward capacitor as the S7 cliff reached
through `XCFF`'s value — 6 fF in box, 8 fF out (S7 115.6 -> 194.1 mV). The extraction reports
**4.23 fF** (`Cext_127`), i.e. **0.71x of budget and 1.9x below the step**. It is in box and it is
not comfortable: the two tracks sit 1.4 um apart in the channel with only `vref` between them, and
`lp_brk` now runs the full cell width (§6.2). The named lever, if the corner run needs it, is the
`TRACKS` order — moving `lp_brk` from slot 3 to slot 9 puts 5.6 um between them instead of 1.4 —
and it is a one-line change with its own build.

**One net is over budget: `gate`, at 2.87x**, and §6.1 is the measurement of why neither routing
nor a legal sizing reaches 12 fF. Everything else is inside, most of it by 4-10x. Three notes:

- **`fb` is 0.78x**, not the 1.22x the previous report showed. Two thirds of that is the correct
  (to-rail) accounting and one third is F5: the track went from 107.15 um to 79.57 um.
- **`lp_brk` doubled, deliberately** (§6.2) and has no capacitance budget; what it buys is the
  22x looser series-R budget on `vout`.
- **`vout` grew 26 fF** because the TopMetal1 strap is twice as wide — the trade F1 asks for, and
  §6.3 prices it at 11 mV of dropout saved.

## 8. Matching — what was drawn, per class, with the achieved sigma-multiple

**Every row's headroom is now `tolerated / 1 sigma`, and the step has its own column**
(review-004 F20). The `bias_n_group` row printed *6 mV* under a heading that said *tolerated*:
6 / 2.43 = 2.47, not the 2.06 beside it. 6 mV is the **step**; `brief.json` tolerates **5.0 mV**,
and 5.0 / 2.4318 = 2.056. Every other row closed; that was the one a reader would check. The
values below are read out of `brief.json`, not retyped.

The re-derived brief prices every class in **sigma of the PDK's own random mismatch**
(`sg13g2_moslv_mismatch.lib`, A_VT = 2.0 / 2.5 mV*um, dw 4 / 5 nm), computed per member from its
own W·L·m. Layout removes the **systematic** part — gradient, orientation, neighbourhood, etch,
and the routing asymmetry §8.1 measures. It removes **none** of the random part, so a class whose
tolerated mismatch is below one sigma cannot be fixed by drawing it better. Two are.

| class | tolerated | step | 1 sigma | **headroom (sigma)** | brief's pattern | drawn | systematic part removed? |
|---|---|---|---|---|---|---|---|
| `ea_nmos_load` `XM3`,`XM4` | 1.0 mV dVT | 2.0 mV | 1.6468 mV | **0.61** | common_centroid+dummies | **A B B A**, one x-centroid, tied dummies both ends, **routing XOR 0.000-0.003 um^2, 2 vs 2 Via1** | yes, fully |
| `bias_p_group` `XMBP`,`XMT`,`XM6` | 1.2 mV dVT | 1.5 mV | 1.118 mV | **1.07** | common_centroid+dummies | **same row, same orientation**, `XMT` **between** `XMBP` and `XM6`, dummies sized to their own neighbour | **partly — see below** |
| `fb_divider` `XR1`,`XR2` | 0.989 % dR/R | — | 0.5745 % | 1.72 | common_centroid+dummies | **[A B B A] x4** = 16 segments, both centroids at the block centre, tied dummy segment each end | yes, fully |
| `ea_in_pair` `XM1`,`XM2` | 2.9477 mV dVT | — | 1.6197 mV | 1.82 | common_centroid+dummies | **A B B A**, first group of row B, **routing XOR 0.000-0.011 um^2, 3 vs 3 Via1** | yes, fully |
| `bias_n_group` `XMB0`,`XMB1`,`XMS` | **5.0 mV dVT** | 6.0 mV | 2.4318 mV | **2.06** | common_centroid+dummies | **S B1 B0 \| B0 B1 S**, one centroid for all three, dummies both ends, **XOR 0.000-0.001 um^2** | yes, fully |
| `mim_feedforward` `XCFF` | 6 % dC/C | step | 1.25 % | 4.8 | interdigitated+dummies | one certified 8 x 8 um unit; the *coupling* form of the same cliff is §7's `fb`<->`lp_brk` at 0.71x | n/a — single device |
| `fb_divider_segment` `XR2_1` | 7.9175 % dR/R | — | 1.625 % | 4.87 | interdigitated+dummies | the ABBA comb interdigitates the segments | yes |
| `bias_resistor` `XRB` | 6 % dR/R | step | - | - | any | own `res_pitch`, tied `rhigh` dummy each end (F12) | yes |
| `fvf_fold_p` `XMCP`,`XMD` | 20.78 mV | — | 1.6648 mV | 12.5 | same_row_same_orientation | adjacent, same orientation, dummies at the group ends | yes |
| `fvf_fold_n` `XMA`,`XMB` | 40.59 mV | — | 1.6623 mV | 24.4 | any | adjacent, same orientation, dummies at the group ends | yes |
| `mim_miller` `XCC` | 134.8 % | — | 0.1852 % | 728 | any | one certified unit, same orientation, one plate side | n/a |
| `pass_array` `XMP` | - | — | 0.503 mV | 125 | any | 76 shared-diffusion fingers, own n-well island, own n-tap ring, own p-substrate ring | n/a |
| `mim_cout` `XCOUT` | no bound | — | 0.0862 % | no bound | any | 2 x 2 common-centroid array of the certified 58 um unit about a central TopMetal1 spine | yes |

**`bias_p_group` is the one class drawn below its brief pattern, and the reason is the netlist.**
The brief now asks for common_centroid+dummies at 1.07 sigma; the group is three *different*
cards (`XMBP` 10 um, `XMT` 10 um, `XM6` 5.53 um) and a common centroid of three unequal devices
needs each split about one axis — which is a **certified-netlist edit**, i.e. a sizing change, not
a layout liberty (that is exactly what `bias_n_group` got in the re-certification, and why it can
be a centroid). What the layout does instead is exploit the brief's own asymmetry: only the sign
that **strengthens `XMT`** relative to `XMBP` is dangerous (S7 steps at +1.5 mV; -5 mV and -10 mV
both *improve* S7), so `XMT` is placed **between** `XMBP` and `XM6`, where a linear gradient
weakens it. Filed as PLAN §6b open ruling 2.

**`ea_nmos_load` at 0.61 sigma is the tightest class in the cell and the most sensitive to
routing.** Brief §6b measures a half-only offset on `XM3A` at **+102.6 mV of S7** — three quarters
of the whole-class step, from an asymmetry between the two halves of one member. That is precisely
what F6 was about, and it is why §8.1's XOR result matters more here than anywhere else: this
class draws at **0.000-0.003 um^2** of XOR with equal via counts.

### 8.1 Routing symmetry, measured (review-003 F6)

Every common-centroid group now **reserves a mirrored column pair per member before the general
allocator runs**: for each partner pair the two halves' terminals are offered the *same* offset
from their own device edge, and the pair is claimed in the obstacle map so an inner member cannot
take it. Measured by the reviewer's own test — translate one half's window onto the other and XOR
Metal1 + Metal2 + Via1 + Metal3:

| pair | reviewed drawing | this drawing (device window, +1.2 um) | Via1 |
|---|---|---|---|
| `ea_in_pair` XM1a/XM1b | XOR 3.69 of 5.71 um^2 (64.7 %) | **0.000 um^2 (0.0 %)** | 3 vs 3 |
| `ea_in_pair` XM2a/XM2b | XOR 2.54 of 7.74 um^2 (32.8 %), 4 vs 3 Via1 | **0.011 um^2 (0.1 %)** | 3 vs 3 |
| `ea_nmos_load` XM3a/XM3b | 0.000 um^2 | **0.003 um^2 (0.0 %)** | 2 vs 2 |
| `ea_nmos_load` XM4a/XM4b | 0.000 um^2 | **0.000 um^2 (0.0 %)** | 2 vs 2 |
| `bias_n_group` XMSa/XMSb | not measured | **0.000 um^2** | 2 vs 2 |
| `bias_n_group` XMB1a/XMB1b | not measured | **0.001 um^2** | 2 vs 2 |
| `bias_n_group` XMB0a/XMB0b | not measured | **0.001 um^2** | 2 vs 2 |

At the reviewer's wider window (+2.6 um) `ea_in_pair` reads 5.6 % and 2.4 %: the residual is a
**neighbour's** column entering the translated window at its boundary, not the pair's own routing
— the placement is mirror-symmetric while the test translates, so the two windows do not contain
the same neighbours. The pairs' own routes are identical.

### 8.2 Deviations from the plan and the brief, still recorded

1. **No MIM dummy ring** (PLAN A3), for the arithmetic and headroom reasons given there.
2. **The MIM plate assignment follows the certified card, not brief §9** — `cap_cmim` is polarised
   in the LVS deck and swapping the plates moves the bottom-plate parasitic to the other node, i.e.
   it is a certified-netlist edit. `REVIEW.md` F15 measures the swap at ~ +0.3 deg for a re-freeze;
   filed in §10, not done here.
3. **`bias_p_group` is same-row, not common-centroid** — see above; a netlist change.

## 9. Iterations

| it | what changed / what it fixed | DRC | LVS | PEX | area µm² | files |
|---|---|---|---|---|---|---|
| it01 | floorplan rebuilt: TopMetal1 power path, CC/interdigitated rows w/ dummies, closed rings -> DRC 118 (M2.c1 x77) | 118 (M2.c1 ×77, Cnt.b ×14, M1.b ×8, OffGrid.EXTBlock ×6) | — | — | 42395 | [gen](it01/gen.py) [png](it01/layout.png) |
| it02 | M2.c1 x77: comb Via1 stack overhung the 0.31 um Metal2 finger -> endcap enclosure; own guard ring; dummy blanket | **0** | MISMATCH | — | 42231 | [gen](it02/gen.py) [png](it02/layout.png) [diff_from_it01](diff_it01_it02.png) |
| it03 | gate merged into vout at the comb spine; XR2 split 212/85/42 by a stub walking the port row -> Metal3 escape + claimed pads | 129 (V1.b ×128, V1.a ×1) | MISMATCH | — | 42231 | [gen](it03/gen.py) [png](it03/layout.png) [diff_from_it02](diff_it02_it03.png) |
| it04 | V1.b x128: MIM pad + to_track both stacked Via1 at one point; vout split at the climb landing; XR2 links -> Metal3 | 3 (M2.b ×2, V1.a ×1) | MISMATCH | — | 42231 | [gen](it04/gen.py) [png](it04/layout.png) [diff_from_it03](diff_it03_it04.png) |
| it05 | CFF/CC plates swapped vs the certified card: cap_cmim is polarised, nodes[0] is the top plate -> read the assignment from the netlist | 6 (M1.b ×2, M2.b ×2, V1.a ×1, V1.b ×1) | match | — | 42231 | [gen](it05/gen.py) [png](it05/layout.png) [diff_from_it04](diff_it04_it05.png) |
| it06 | LVS matched; last 6 DRC are one cause: a shifted column 0.95 um from a 1.3 um MIM pad -> push it 1.4 um clear | 6 (M2.b ×3, V1.b ×2, M2.e ×1) | match | — | 42231 | [gen](it06/gen.py) [png](it06/layout.png) [diff_from_it05](diff_it05_it06.png) |
| it07 | MIM plate pads now claimed in the obstacle map and routed from a 2 um Metal1 escape arm, not from the pad itself | **0** | MISMATCH | — | 42231 | [gen](it07/gen.py) [png](it07/layout.png) [diff_from_it06](diff_it06_it07.png) |
| it08 | escape arms ran outward into the left-edge vss strap and shorted ea_o1/fb/vss -> route them inward under the plate | **0** | match | — | 42231 | [gen](it08/gen.py) [png](it08/layout.png) [diff_from_it07](diff_it07_it08.png) |
| it09 | layout of record: DRC 0, LVS matched at both sizing points, current density 27/27, kpex CC 182C/21R, 13/13 benches PASS | **0** | match | CC 182C/21R | 42231 | [gen](it09/gen.py) [png](it09/layout.png) [diff_from_it08](diff_it08_it09.png) |
| it10 | certified deck re-issued on the drawn device set (F19): Iq 36.28->33.81 uA, S7 104.8->115.1 mV | **0** | match | — | 42231 | [gen](it10/gen.py) [png](it10/layout.png) [diff_from_it09](diff_it09_it10.png) |
| it11 | Metal2 comb registered per-layer + gate track on Metal3 + ea_in_pair leftmost: DRC 0, LVS matched, PM 68.76->69.30 | **0** | match | CC 186C/21R | 44266 | [gen](it11/gen.py) [png](it11/layout.png) [diff_from_it10](diff_it10_it11.png) |
| it12 | vss cliff is shared impedance, not width: XCOUT gets its own strap to the pin, right riser deleted -> return 4.9 ohm, 40/40 endpoints clean | **0** | match | CC 186C/21R | 44266 | [gen](it12/gen.py) [png](it12/layout.png) [diff_from_it11](diff_it11_it12.png) |
| it13 | port labels were not pins: 0.2 um pin-purpose square under all 17 -> kpex anchors 15/15 ports on [Pin], CC netlist byte-identical | **0** | match | CC 186C/21R | 44266 | [gen](it13/gen.py) [png](it13/layout.png) [diff_from_it12](diff_it12_it13.png) |

Every round is `build -> current density -> DRC -> LVS`, snapshotted before the generator was
touched again; `it09` was the reviewed drawing, `it10` the re-certification (recorded here because
it was committed without a snapshot), `it11` the fix round against the review, `it12` the
second round after the brief was re-derived, and `it13` the pin-purpose round (§5). `it11` -> `it12` **does** move the GDS
(`a66d15b5...` -> `c8d92a2f...`): the diff picture boxes two changed regions, 858.3 um^2 on
Metal1 (layer 8/0) — the right-edge `vss` riser deleted, and the XCOUT bottom-plate drops widened
0.6 -> 3.0 um to the pin. The two generator fixes that came out of the bounds walk (the XRB
segment-end claim and `x_cout0`) are byte-identical at the record sizing and only show at other
knob values. What does *not* move is the pre/post scorecard: `it12` is a change of return-path
*resistance*, and the CC extraction carries no resistance, so its benefit is a hand-model number
(section 7) and not a simulated one. That is the honest reading of a return-path fix under this
extractor. Five dead ends are worth carrying
forward, three of them new:

**A power comb is an obstacle even when nothing "routed" it.** The Metal1 obstacle map of the
first drawing and the Metal3 bypass of the second were both patches on the same hole: the pass
array's Metal2 comb is drawn by the *power path*, with `rect`/`h`, and was never entered in the
map, so `column_free` could not see it. The structural fix is that the map is **layer-aware** and
`claim_box()` records any drawn rectangle, so the comb is an obstacle to Metal2 and simply is not
on Metal3's layer — which is what let the hard-coded `to_track_m3` for `gate` be deleted rather
than generalised. `layout/test_builder.py` carries the case that fails without it.

**Same net is not the same column.** Two `ea_n` columns 0.38 um apart merge into one legal Metal2
polygon — and put their Via1 cuts 0.19 um apart, which is V1.b. The obstacle map skipped same-net
comparisons entirely, so the mirrored-column reservation walked straight into it on its first
build. The pad pitch is a *geometric* rule and now applies to a net's own columns too, coincident
or a full pitch away.

**Retrofitting a width into a finished floorplan does not work — twice in one round.** `vss_ret_w`
0.8 -> 3.0 put the left riser on top of the XCFF bottom-plate pad and LVS returned
`ea_o1 | fb | vss`; `pwr_w` 2.0 -> 4.0 put the right-edge `vout` strap 0.76 um from the XCOUT top
plate (TM1.b 1.64) and 0.40 um from the MIM (MIM.e 0.60). Both are fixed the same way: the cell
edges are **placed from the widths**, not from a constant margin.

**A finding can have the right severity and the wrong mechanism.** F9 read the `vss` return as a
32 Ohm rail and asked for width; the re-derived brief's split injection shows 32 Ohm on the active
devices alone is worth +0.44 mV and on XCOUT's plate alone is an *improvement*, and that the cliff
only exists when both are behind one R. The first fix (two wide risers) was therefore the wrong
shape — it lowered the number the finding named while keeping the sharing that causes the cliff.
The second fix deletes a riser.

**A dead variable is a bug waiting for a knob to move.** `x_pass_r` — the right edge of the
passive column — was computed and never used, and the XCOUT array started at a fixed x = 1.0 um.
At `res_pitch` = 3.0 the XRB block slid under the array and XCOUT's bottom-plate drop went down
through it. The range walk found it; nothing at the record sizing ever would have.

**`ihp.cells.guard_ring` is not DRC-clean** at its corners (Cnt.b), measured on a standalone ring
at seven width/spacing combinations; `Builder.ring` draws the ring instead.

## 10. What stays open

1. **No independent review of this round.** `layout-reviewer` has not rebuilt or re-measured it.
   The post-layout row is logged `evidence="awaiting"`.
2. **F3 is reframed, not closed** (§6.1, PLAN §6b ruling 1, review-004 F3). The 12 fF budget is
   a *gate-only* number; swept in situ on the full extraction the net takes **+46 fF** before S7
   crosses 150 mV, at 0.455 mV/fF with no step — 134 % of what the cell draws. The open question
   is therefore not the drawn `gate` capacitance but whether to **certify the error-amp-path
   capacitance the margin already depends on**. Owner's call, and it should wait for 007's corner
   row, which shows S7 leaving the box at 125 C in four of five corners for reasons that have
   nothing to do with `gate`.
3. **Two matching classes have sub-sigma budgets** (§8, PLAN §6b ruling 2): `ea_nmos_load` at
   0.61 sigma and `bias_p_group` at 1.07 sigma of the PDK's random mismatch. The layout removes
   the systematic part in full for the first and partly for the second; nothing drawable removes
   the random part. **On the drawn cell the budgets do not bind**: 007 §4 bisects the box edge at
   +15.0 mV (9.1 sigma) and +20.0 mV (17.9 sigma), and its control shows the brief's cliff is real
   but is removed by the extracted `ea_o1` capacitance — which is ruling 1's subject, so the two
   rulings are one decision. `bias_p_group` cannot even be a common centroid without splitting its three
   cards in the certified netlist.
4. **The `vss` per-device return is over its budget and the budget is on the wrong quantity**
   (§6.4, review-004 F9). Solved: worst device **20.56 Ohm** of a 16.48 Ohm per-device budget
   (1.25x), common series element **4.74 Ohm** of the same 16.48 (0.29x). In circuit the whole
   per-device spread is worth **+0.04 dB** of a 27 dB PSRR margin, so the deliverable is a
   corrected brief row — budget the common element, drop the "worst active device" row — not a
   redrawn cell. `rail_w` 1.2 / 1.4 are rebuilt and solved at 16.22 / 14.89 Ohm if it ever binds.
5. **`fb` <-> `lp_brk` is 0.71x of a 6 fF coupling budget** with the step at 8 fF (§7). The named
   lever is the `TRACKS` order.
6. **Corners are now measured; the Monte Carlo is not** (`experiments/007-post-layout-corners`,
   review-004 F16). The extracted cell is scored over 5 MOS corner bundles x -40/27/125 C with
   the schematic row as the control: **S5 fails at ff/125 in both rows** (58.37 uA of a 50 uA
   line — a schematic-level corner failure, not a layout one) and **S7 leaves the box at 125 C in
   four of the five corners post-layout** (152-171 mV), where pre-layout only ss/125 does. The
   two sub-sigma matching classes are priced by injection with a measured out-of-box threshold
   (§8, 007 §4). What is still missing is the distribution itself: selecting the PDK's
   `*_mismatch.lib` sections needs an edit to the certified `corners.yaml`, which belongs to the
   schematic lane. The old text of this item read "everything here is tt / 27 C"; 003 §3
   shows S5 and S7 binding at corners *before* layout, and the re-certification moved Iq to
   33.81 uA — `REVIEW.md` F16 is right that ss/-40 is what decides this drawing.
7. **The RC row is measured, and it moves dropout by +30 mV** (§5). The stitched RC netlist
   passes all 13 benches once kpex's two zero-ohm `[Pin]` ties are given a finite value
   (`postlayout.floor_zero_r()`), and its only material difference from the CC row of record is
   **S4 dropout 104.7 -> 134.7 mV** — the drawn `vdd`/`vout` IR drop at 10 mA, which no CC
   extraction can see. **CLOSED (round 6).** `SIGNOFF.md` re-verified this independently on its
   own rebuilt GDS: the +30 mV is physical (§6.3), and the coordinator has since ruled that the
   **post-layout row of record is the stitched RC row**, not CC — CC is re-labelled the
   ideal-metal comparison row. §6.3's hand model (+11.0 mV) reads as a *lower* bound on the same
   quantity, and §6.4's lumped `vss` return (-2.76 dB of PSRR) is loose by 2.7 dB against the
   mesh's -0.03 dB. **Open item for the platform, also CLOSED**: kpex emitting 3 101 zero-ohm
   cards where the stitcher leaves 2 unmerged is fixed upstream
   (`spicexplorer-platform` `feat/harness-spec-v2` @ `6c07a02`) and re-verified by `SIGNOFF.md`
   §3.1 — all 3101 are now contracted, 0 zero-ohm cards remain, and the stitched file simulates as
   written with no floor needed.
8. **New open finding — the pooled dropout series-R budget is missed at the record row** (round 6,
   `SIGNOFF.md` §3.4, and §6.3 above). `brief.json`'s pooled rule (`10.34 × R(vdd) + 8.65 ×
   R(vout) ≤ 23.83 mV`, a quarter of the S4 margin) reads **29.99 mV at the RC record — 1.26× the
   allowance** — while each net's *individual* budget is still met and S4 itself passes with 65.3
   mV of margin (134.66 / 200 mV). The miss is in the shared **TopMetal1 strap** (0.59 Ω) and the
   **Via2–TopVia1 stack** (0.75 Ω), 85 % of the pooled 3.00 Ω, neither of which divides by the 39
   parallel pass-device columns. **Fix path**: widen the shared strap and/or multiply the via
   array — a designer action, not a re-measurement. **Caution for whoever redraws it**: both fixes
   touch metal that sits over/near `ea_o1`, whose 64 fF of drawn-by-accident capacitance is what
   the mismatch box edges in `SIGNOFF.md` §4 (9.109 σ / 17.889 σ) and PLAN §6b ruling 1 rest on —
   a redraw here must **re-bisect** those edges, not assume they hold.
9. **`--density` was not re-run**, so whether the 12-rule waived set grew with the new floorplan is
   unverified (F18).
10. **The MIM plate swap (F15) is not done.** It is a certified-netlist edit and a re-freeze worth
   ~ +0.3 deg by the reviewer's hand model.
11. **The labelled renders are stale** (§1) — `labels.yaml` and `experiments/005-layout/figs`
    belong to another lane and were deliberately not touched.
12. **Density/fill and sealring remain out of scope** (PLAN A7), so DRC 0 is conditional.

## Summary

**What was done.** Two rounds of fixes against `review-003`, the second re-scored on the
re-derived brief. **F7**: the obstacle map is layer-aware and records any drawn rectangle, so the
pass array's Metal2 comb is finally an obstacle — that closes the `gate | vout` short class at
`col_vias` 3 and 4 and removes the hard-coded Metal3 hop, with a regression case that fails
without it. **F2**: DRC and LVS now block, and a new `bounds` stage walks both ends of all 20
documented ranges — 40/40 build, DRC 0, LVS matched, current density pass; four endpoints were
generator bugs and are fixed, three ranges are narrowed with the geometric reason recorded.
**F1**: `pwr_w` 2.0 -> 4.0 halves both strap resistances, and the hand model is scored against the
brief's pooled rule at 10.98 mV of 23.83 (46 %, from 92 %); the RC defect is proved on the raw
kpex netlist and written up for the platform. **F3**: the routing lever is spent and measured, and
the objective is shown unreachable by layout — reported, not credited. **F5**: `fb` 107.15 ->
79.57 um, PM 68.76 -> 69.30 deg. **F6**: the two halves of every common-centroid pair are drawn
identically (XOR 0.000-0.011 um^2, equal via counts). **F9**: the mechanism turned out to be
shared impedance, not rail width, so the fix is a **Kelvin cap return** — XCOUT's plates and the
active devices meet only at the pin, and the second riser of the first attempt is deleted because
it would put the sharing back. **F4, F8, F10-F14** as listed. Post-layout 18/18 PASS, 0 spec
violations.

A third round then answered `review-004`. The only geometry change is `it13`'s pin-purpose square
under each of the 17 port labels (**F25**), which moves kpex from 0 `[Pin]` nodes to 15/15 named
ports anchored on the drawn port while the CC netlist stays byte-identical; 40/40 knob endpoints
were re-walked on `it13` itself. **F27/F26/F24/F22** are provenance: the benches now measure the
netlist the extractor named, the sign-off record carries the mesh verdict and gates on it, and
each snapshot carries `router.py`/`netlist_ref.py`. **F9** is re-solved rather than modelled
(`layout/rail_solve.py`, 0.00 % on its self-test) and two printed numbers are corrected. **F16**
is `experiments/007-post-layout-corners`: 30 corner rows, 12 injection rows, a bisection to the
box edge and a cap-set control. And the RC lane finally measures: kpex's zero-ohm `[Pin]` ties
made ngspice return a non-solution — provable on a sixteen-segment resistive divider that reported
149:1 asymmetry between identical halves — and with `floor_zero_r()` the stitched RC netlist
passes all 13 benches, differing from the CC row of record only in dropout, by +30 mV (§5).

**Assumptions.** PLAN §0 lists thirteen; four are new across these two rounds and each is named
there: A10 the Kelvin `vss` return and its `vss_ret_w` knob, A11 the pass gate's Metal3 track,
A12 `lp_brk` kept as a pin and escaped to the output-pin edge, A13 `gpad`/`isl_gap` promoted to
knobs and `tap_pitch` deleted. Two **open rulings** are filed in PLAN §6b rather than decided: the
12 fF gate budget and the sub-sigma mismatch budgets.

**Errors / setbacks / gotchas.** §9. Five that generalise. **A netlist that converges is not a
netlist that solved**: the stitched RC row read `v_out` = 1.4999 V through 13 clean benches with
no warning, and the giveaway was not the simulator but the circuit — sixteen identical series
resistors reporting unequal drops, which is arithmetically impossible. Two zero-ohm cards in
5 463 were enough. Check a known-value subnetwork before believing an extracted operating point,
and be suspicious of any extractor that writes 0 where it means "merge". Then the four from the
earlier rounds: a power comb drawn by something other
than the router is still an obstacle, and a map that only knows what it routed is half a guard;
two columns of one net are not one column, because the via pads are geometry; a width retrofitted
into a finished floorplan lands on whatever was there — twice in one round, once as an invisible
short and once as TopMetal1 spacing; and a return-path finding can have the right severity and the
wrong mechanism, so the fix (a connection) is nothing like the fix the finding proposed (a width).

**Next steps.** An independent `layout-reviewer` pass on this drawing. The two owner rulings in
PLAN §6b, which 007 has now turned into **one** decision — certify the `ea_o1` capacitance the
cell's cold-corner margin and its mismatch margin both rest on, or accept that both move with the
floorplan. The Monte Carlo, which needs the schematic lane to
add the PDK's mismatch sections to `corners.yaml`. Widen the shared TopMetal1 strap and/or the
Via2–TopVia1 stack to close the pooled dropout budget miss (§10 item 8), and re-bisect the
mismatch box edges afterward since they rest on `ea_o1`'s drawn-by-accident capacitance.

**Round 6 addendum (independent sign-off, `SIGNOFF.md` @ `50442a8`).** Both open items above that
were pending a coordinator/platform call are now resolved: the platform's zero-ohm `[Pin]` fix is
verified upstream and the record row question is decided — **the post-layout row of record is now
the stitched RC row**, not CC, re-measured end to end by the verifier on its own rebuilt GDS
(3101/3101 zero-ohm ties contracted, 15/15 ports on a pin, dropout **134.66 mV** of a 200 mV bound,
8/8 spec lines PASS). What that reopens is new, not closed: the brief's pooled dropout series-R
budget is **missed** at the record row (29.99 mV of a 23.83 mV allowance, 1.26×) even though S4
itself passes with 65.3 mV of margin — filed above as item 8, with the strap/via fix path and the
re-bisection caveat. CC is retained as the ideal-metal comparison row. The verifier's mismatch
re-measure also confirms the designer's box-edge numbers for the row of record (9.109 σ /
17.889 σ) while agreeing the reviewer's 0.61/1.07 σ and 11 %/9 % are correct readings of
`brief.json`'s own `headroom_sigma` fields and one-sided tails for the **schematic**-priced
circuit, not the as-built one (`SIGNOFF.md` §4.3) — see PLAN §6b for the reconciled ruling text.
