# Layout report — `ldo_ihp_capless` (IHP SG13G2), second drawing, fix round

**KIND: REPORT.** The layout of record is the generator `layout/gen_ldo.py` at `LayoutParams()`
defaults, reading its sizing from the certified binding. Plan and assumed approvals:
[`PLAN.md`](PLAN.md). Brief: [`BRIEF.md`](BRIEF.md). Independent review this round answers:
[`REVIEW.md`](REVIEW.md) (`review-003`, FAIL — 3 blockers, 7 majors, 5 minors). Every number below
is a verdict this branch produced; where the previous drawing is quoted it is named as such.

**Verdict.** Current density 30/30 segments (worst 0.836x), **DRC 0**, **LVS matched**, and LVS
matched with DRC 0 at **both ends of all 20 documented knob ranges** (40/40 endpoints), kpex CC
186 C / 21 R, and the cell's own **13 frozen benches on the extracted netlist pass the whole
S1–S8 box, 18/18 metrics**. Signature: **none** — `layout/postlayout.py` logs the post-layout
scorecard as one ledger row with `evidence="awaiting"`, whose signature is the verifier's own
re-measure (rule 7), never the designer's. `runs/` is git-ignored and per checkout, so that row
does not travel with this commit: re-run `layout/postlayout.py --pex <work>/pex` to reproduce it.

**What is NOT closed.** F3's numeric objective, and it is now shown to be unreachable by layout.
The re-derived brief budgets **12 fF** of `gate` to-rail capacitance with a measured step between
12 and 13 fF; the drawn cell is **34.45 fF** and gate-only parasitics put S7 at **201.7 mV**
against a 150 mV line. §6.1 measures both remaining levers: the whole Metal3 gate track is worth
**3.0 fF** (so a `vout` shield under it recovers 13 % of the shortfall) and the pass array's own
gate structure costs **3.9 fF per unit finger multiple**, extrapolating to a ~18.8 fF floor at a
finger count the current-density limit already forbids. It is reported, priced, and filed as an
owner ruling (PLAN §6b) — no EA-path recovery is credited, per brief §3b.

**Budgets are the re-derived ones.** `BRIEF.md` / `brief.json` at `223373e`, taken on the
re-certified schematic row (S7 margin 34.94 mV). They are materially tighter than the ones the
previous report was written against, and §7 is read against them throughout.

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

| mode | halo | C | R | benches |
|---|---|---|---|---|
| **CC** (the reported row) | tech default, SG13G2 8 um sidewall | 186 | 21 | 13/13 ran, **0 spec violations** |
| **RC** (once, for this report) | same | 186 | 8 569 | 8/13 ran, 7 violations — see below |

**The RC row is not a measurement of wire resistance, and this is now proved rather than
suspected** (review-003 F1). Measured on the raw kpex netlist of *this* drawing: 8 548 `Rext_`
cards sit on a 6 217-node mesh whose node names are `<net>.$i.j`; the intersection of that mesh
with the **33 device-terminal nodes is empty**, and with the 34 `Cext_` nodes is empty. All 33
mesh prefixes *are* real nets, so the join exists in the node name and nowhere else. Consequences,
measured: five of thirteen benches abort with `singular matrix`, and the transient benches that do
run reproduce the CC row exactly (undershoot 127.558 mV, recovery 0.1901 us, line step 55.73 mV) —
because there is no R in the circuit to change them.

This is a kpex 0.3.12 defect, not a translation defect: it was measured on the file kpex wrote,
before `layout/postlayout.py` touches it, and no kpex flag controls it (`--magic_short` /
`--magic_mode` are magic-engine options). The write-up with the argv, the raw cards and a ten-line
reproduction is at `$SX_SCRATCH/ldo-review/pex_rc_defect.md` for routing to the platform.
**Because RC measures no resistance, the series-R numbers in this report are a hand model from the
drawn geometry (§6.3), not zero and not an extraction.**

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

The extractor measures no wire resistance (§5), so this is a hand model from the drawn geometry:
TopMetal1 sheet resistance 18 mOhm/sq, Metal1 110 mOhm/sq
(`libs.tech/magic/ihp-sg13g2-extract.tech`), lengths read pin-label-to-riser out of the builder.

**`vdd` and `vout` share one dropout pool** (re-derived brief §4a):
**10.34 x R(vdd) + 8.64 x R(vout) <= 23.83 mV**, i.e. 25 % of the 95.3 mV dropout margin.

| net | path | length | at `pwr_w` = 2.0 (reviewed) | at `pwr_w` = 4.0 (**drawn**) | own budget |
|---|---|---|---|---|---|
| `vdd` | top-edge strap, pin at x = -65.5 to riser at x = 67.4 | 132.9 um | 1.196 Ohm | **0.598 Ohm** | 2.31 Ohm |
| `vout` | riser at (67.4, 55.3) to pin at (133.6, 0) | 123.6 um | 1.112 Ohm | **0.556 Ohm** | 2.76 Ohm |
| | **pooled dropout cost** | | 21.98 mV (**92 %** of the pool) | **10.98 mV (46 %)** | <= 23.83 mV |

**Neither scorecard column contains that 10.98 mV**, in either PEX mode, and this line is the
reason it is not reported as zero. The brief's own splice of the `pwr_w` = 2.0 hand model into the
frozen benches measures **+20.04 mV** of dropout (84 % of the pool); halving both resistances
halves it. Measured dropout 104.7 mV + 11.0 mV = 115.7 mV against a 200 mV line.

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

| path | drawn | hand model | budget |
|---|---|---|---|
| active devices -> pin, common series element (the riser) | 134.0 um of 3.0 um Metal1 | **4.91 Ohm** | 16 Ohm (S6, active-only) |
| worst-case device (bias group at x = 100) incl. the cell rail | + 170 um of 0.8 um rail in parallel with the ptap ring's two 0.6 um segments | **14.3 Ohm** | 16 Ohm — **89 % spent** |
| XCOUT plates -> pin (the cap's own ESR) | bottom rail, 3.0 um, 71-198 um | 2.6-7.3 Ohm | no bound (more is mildly *better* for S7) |
| shared between the two | the pin | **~0 Ohm** | the 11 Ohm cliff does not apply |

**None of this shows in either scorecard column**, because the CC extraction carries no R and the
RC mesh is electrically absent (§5) — the evidence is the brief's own injection sweep plus the
geometry. If the corner run needs the 89 %, `rail_w` 0.8 -> 1.2 (inside the walked range) takes
the worst-device figure to ~12.7 Ohm.

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

The re-derived brief prices every class in **sigma of the PDK's own random mismatch**
(`sg13g2_moslv_mismatch.lib`, A_VT = 2.0 / 2.5 mV*um, dw 4 / 5 nm), computed per member from its
own W·L·m. Layout removes the **systematic** part — gradient, orientation, neighbourhood, etch,
and the routing asymmetry §8.1 measures. It removes **none** of the random part, so a class whose
tolerated mismatch is below one sigma cannot be fixed by drawing it better. Two are.

| class | tolerated | 1 sigma | **headroom (sigma)** | brief's pattern | drawn | systematic part removed? |
|---|---|---|---|---|---|---|
| `ea_nmos_load` `XM3`,`XM4` | 1.0 mV dVT (step) | 1.65 mV | **0.61** | common_centroid+dummies | **A B B A**, one x-centroid, tied dummies both ends, **routing XOR 0.000-0.003 um^2, 2 vs 2 Via1** | yes, fully |
| `bias_p_group` `XMBP`,`XMT`,`XM6` | 1.2 mV dVT (step) | 1.12 mV | **1.07** | common_centroid+dummies | **same row, same orientation**, `XMT` **between** `XMBP` and `XM6`, dummies sized to their own neighbour | **partly — see below** |
| `fb_divider` `XR1`,`XR2` | 0.989 % dR/R | 0.575 % | 1.72 | common_centroid+dummies | **[A B B A] x4** = 16 segments, both centroids at the block centre, tied dummy segment each end | yes, fully |
| `ea_in_pair` `XM1`,`XM2` | 2.95 mV dVT | 1.62 mV | 1.82 | common_centroid+dummies | **A B B A**, first group of row B, **routing XOR 0.000-0.011 um^2, 3 vs 3 Via1** | yes, fully |
| `bias_n_group` `XMB0`,`XMB1`,`XMS` | 6 mV dVT (step) | 2.43 mV | 2.06 | common_centroid+dummies | **S B1 B0 \| B0 B1 S**, one centroid for all three, dummies both ends, **XOR 0.000-0.001 um^2** | yes, fully |
| `mim_feedforward` `XCFF` | 6 % dC/C (step) | 1.25 % | 4.8 | interdigitated+dummies | one certified 8 x 8 um unit; the *coupling* form of the same cliff is §7's `fb`<->`lp_brk` at 0.71x | n/a — single device |
| `fb_divider_segment` `XR2_1` | 7.92 % dR/R | 1.62 % | 4.87 | interdigitated+dummies | the ABBA comb interdigitates the segments | yes |
| `bias_resistor` `XRB` | 6 % dR/R (step) | - | - | any | own `res_pitch`, tied `rhigh` dummy each end (F12) | yes |
| `fvf_fold_p` `XMCP`,`XMD` | 20.8 mV | 1.66 mV | 12.5 | same_row_same_orientation | adjacent, same orientation, dummies at the group ends | yes |
| `fvf_fold_n` `XMA`,`XMB` | 40.6 mV | 1.66 mV | 24.4 | any | adjacent, same orientation, dummies at the group ends | yes |
| `mim_miller` `XCC` | 135 % | 0.185 % | 728 | any | one certified unit, same orientation, one plate side | n/a |
| `pass_array` `XMP` | - | 0.503 mV | 125 | any | 76 shared-diffusion fingers, own n-well island, own n-tap ring, own p-substrate ring | n/a |
| `mim_cout` `XCOUT` | no bound | 0.086 % | no bound | any | 2 x 2 common-centroid array of the certified 58 um unit about a central TopMetal1 spine | yes |

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

Every round is `build -> current density -> DRC -> LVS`, snapshotted before the generator was
touched again; `it09` was the reviewed drawing, `it10` the re-certification (recorded here because
it was committed without a snapshot), `it11` the fix round against the review, and `it12` the
second round after the brief was re-derived. `it11` -> `it12` **does** move the GDS
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
2. **F3 is not closed and is not closeable by layout** (§6.1, PLAN §6b ruling 1). `gate` to-rail
   is 34.45 fF against a 12 fF budget with a step at 13; the best shield the metal stack allows
   recovers 3.0 fF and the smallest legal finger count leaves ~18.8 fF. Owner's call: a smaller
   pass device, a different output stage, a certified capacitor on `ea_o1` (brief §3b), or a wider
   S7 line.
3. **Two matching classes have sub-sigma budgets** (§8, PLAN §6b ruling 2): `ea_nmos_load` at
   0.61 sigma and `bias_p_group` at 1.07 sigma of the PDK's random mismatch. The layout removes
   the systematic part in full for the first and partly for the second; nothing drawable removes
   the random part. `bias_p_group` cannot even be a common centroid without splitting its three
   cards in the certified netlist.
4. **The `vss` active-return hand model is 89 % spent** (14.3 Ohm of a 16 Ohm budget, §6.4).
   `rail_w` 0.8 -> 1.2 — inside the walked range — takes it to ~12.7 Ohm, at the cost of a
   slightly taller cell and a re-walk of the ranges.
5. **`fb` <-> `lp_brk` is 0.71x of a 6 fF coupling budget** with the step at 8 fF (§7). The named
   lever is the `TRACKS` order.
6. **Corners and Monte Carlo are not re-run post-layout.** Everything here is tt / 27 C. 003 §3
   shows S5 and S7 binding at corners *before* layout, and the re-certification moved Iq to
   33.81 uA — `REVIEW.md` F16 is right that ss/-40 is what decides this drawing.
7. **RC-mode benches do not converge, and RC measures no resistance** (§5). The defect is written
   up for the platform; a `.nodeset` would only make an R-free netlist converge. Every series-R
   number in this report is therefore a hand model.
8. **`--density` was not re-run**, so whether the 12-rule waived set grew with the new floorplan is
   unverified (F18).
9. **The MIM plate swap (F15) is not done.** It is a certified-netlist edit and a re-freeze worth
   ~ +0.3 deg by the reviewer's hand model.
10. **The labelled renders are stale** (§1) — `labels.yaml` and `experiments/005-layout/figs`
    belong to another lane and were deliberately not touched.
11. **Density/fill and sealring remain out of scope** (PLAN A7), so DRC 0 is conditional.

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

**Assumptions.** PLAN §0 lists thirteen; four are new across these two rounds and each is named
there: A10 the Kelvin `vss` return and its `vss_ret_w` knob, A11 the pass gate's Metal3 track,
A12 `lp_brk` kept as a pin and escaped to the output-pin edge, A13 `gpad`/`isl_gap` promoted to
knobs and `tap_pitch` deleted. Two **open rulings** are filed in PLAN §6b rather than decided: the
12 fF gate budget and the sub-sigma mismatch budgets.

**Errors / setbacks / gotchas.** §9. Four that generalise: a power comb drawn by something other
than the router is still an obstacle, and a map that only knows what it routed is half a guard;
two columns of one net are not one column, because the via pads are geometry; a width retrofitted
into a finished floorplan lands on whatever was there — twice in one round, once as an invisible
short and once as TopMetal1 spacing; and a return-path finding can have the right severity and the
wrong mechanism, so the fix (a connection) is nothing like the fix the finding proposed (a width).

**Next steps.** An independent `layout-reviewer` pass on this drawing; the two owner rulings in
PLAN §6b; then the post-layout corner + Monte-Carlo run, which is where the +12.5 mV of undershoot
and the 33.81 uA of Iq will be paid for.
