# 006 — visual testbenches: every certified deck as a schematic that netlists back to it

**Paper(s):** none
**Hypothesis:** each of the 13 frozen benches can be drawn as a schematic a reviewer can read —
every source, load and probe placed and wired as a component, the cell placed as its own symbol,
and only the simulator directives and the `.control` block left as text — and each drawing can be
*proved* to be the deck that certified the numbers: the same instances, the same connectivity in
the same order, the same values, the same directive text. Falsified if any sheet's netlist differs
from its deck, or if the drawing cannot reproduce the certified measurement.
**Control:** the frozen decks themselves, byte for byte (`decks/candidate/*.spice`, SHA-locked).
Nothing on a sheet is retyped: the bench elements are ingested from the deck and placed by the
generator, and the directive and `.control` text is lifted from the deck verbatim.
**Verdict:** **CONFIRMED.** All **13 of 13** sheets netlist back to their decks with no drift, and
the `ac_loopgain` sheet, simulated from *its own netlist*, returns all **7 of 7** certified measures
to every printed digit — loop gain 49.94548 dB and phase margin 72.41882°, against
`decks/candidate/scorecard.json`.

## 1. What is drawn and what stays text

A bench that is one block of SPICE text inside a frame is a deck with a border, not a schematic. On
each sheet the supply, the load current, the AC stimulus, the load capacitor and the DUT are
**components**, placed and wired by `spicexplorer_netlist2xschem` from the deck's own instance lines.
Only what has no symbol is text: the `.lib`/`.temp`/`.param` directives and the `.control` block,
each lifted verbatim into a `devices/code_shown.sym` block under the drawing. Those blocks are part
of the netlist, so a sheet is not a picture of a bench — it *is* the bench.

The two text blocks sit side by side under the drawing, anchored to the sheet's own extent and the
widest line rather than to typed-in coordinates. The sizing `.param` block is 35 lines on most decks,
and stacking the two made a page three times taller than it was wide.

One **sheet per deck**, not per family. The gate is exact, and the three `ac_loopgain` decks differ
only in their load current, so a single family sheet could not match all three. The table groups the
13 sheets into their 9 measurement families.

## 2. The gate — drawing ≡ certified deck

`build_benches.py::compare_bench` joins the deck and the drawing's netlist through
`spicexplorer_core.spice_engine.NetlistView`, the platform's own parser, and requires all of:

- **the same top-level instances**, compared case-insensitively (the parser upper-cases references,
  so the deck's `Vdd`/`Iload`/`CLoad` meet `VDD`/`ILOAD`/`CLOAD`); an instance on one side only is
  its own finding;
- **each instance's nets equal in order** — which makes `XDUT vdd vout vss` a real check of the
  cell's port order, not just of its connections;
- **each instance's value and parameters equal**, as numbers once the deck's `.param` bindings and
  the SI suffixes are resolved, and as whitespace-normalised text otherwise (`dc 1m` against `1m`,
  `pulse(...)` against `pulse(...)`); only `m` may be defaulted to 1, because the generic symbol
  writes it unconditionally;
- **the directive and `.control` text equal line by line**, whitespace-normalised, in order.

The DUT's own body is *not* re-proved here: it is a hierarchy on the sheet and flat in the deck, and
[004](../004-schematic/README.md) is where that comparison is made (25 components, 15 nets, 114
parameter rows). What 006 adds is everything around it.

| family | deck | sheet | figure | compared | gate |
|---|---|---|---|---|---|
| operating point | `dc_op` | `dc_op_tb.sch` | `figs/dc_op_tb.png` | 3 instances, 7 nets, 6 values, 46 text lines | **PASS** |
| load regulation | `load_regulation` | `load_regulation_tb.sch` | `figs/load_regulation_tb.png` | 4 instances, 9 nets, 8 values, 47 text lines | **PASS** |
| line regulation | `line_regulation` | `line_regulation_tb.sch` | `figs/line_regulation_tb.png` | 4 instances, 9 nets, 8 values, 46 text lines | **PASS** |
| dropout | `dropout` | `dropout_tb.sch` | `figs/dropout_tb.png` | 4 instances, 9 nets, 8 values, 69 text lines | **PASS** |
| loop gain / phase margin (Middlebrook) | `ac_loopgain` | `ac_loopgain_tb.sch` | `figs/ac_loopgain_tb.png` | 5 instances, 11 nets, 11 values, 57 text lines | **PASS** |
| loop gain / phase margin (Middlebrook) | `ac_loopgain_lo` | `ac_loopgain_lo_tb.sch` | `figs/ac_loopgain_lo_tb.png` | 5 instances, 11 nets, 11 values, 57 text lines | **PASS** |
| loop gain / phase margin (Middlebrook) | `ac_loopgain_hi` | `ac_loopgain_hi_tb.sch` | `figs/ac_loopgain_hi_tb.png` | 5 instances, 11 nets, 11 values, 57 text lines | **PASS** |
| closed-loop output impedance | `loop_stability` | `loop_stability_tb.sch` | `figs/loop_stability_tb.png` | 6 instances, 13 nets, 13 values, 47 text lines | **PASS** |
| PSRR | `psrr` | `psrr_tb.sch` | `figs/psrr_tb.png` | 5 instances, 11 nets, 11 values, 46 text lines | **PASS** |
| PSRR | `psrr_1m` | `psrr_1m_tb.sch` | `figs/psrr_1m_tb.png` | 5 instances, 11 nets, 11 values, 46 text lines | **PASS** |
| output noise | `noise` | `noise_tb.sch` | `figs/noise_tb.png` | 5 instances, 11 nets, 11 values, 45 text lines | **PASS** |
| load-step transient | `tran_load_step` | `tran_load_step_tb.sch` | `figs/tran_load_step_tb.png` | 5 instances, 11 nets, 11 values, 50 text lines | **PASS** |
| line-step transient | `tran_line_step` | `tran_line_step_tb.sch` | `figs/tran_line_step_tb.png` | 5 instances, 11 nets, 11 values, 46 text lines | **PASS** |

**The gate bit, on its first full run.** Two sheets failed it: the drawing's netlist carried
`ILOAD vout 0 …00n 10u 20u)` where the deck has
`Iload vout 0 pulse(0.1m 10m 1u 100n 100n 10u 20u)`. The cause was in the emitter, which abbreviated
any attribute value over 24 characters to its tail and wrote that into the instance's `value=` — the
attribute xschem netlists. Sizing symbols are short enough that it had never shown; a transient
stimulus is not. Every topology check passed on those two sheets. The fix is proposal **P4**
(`$SX_SCRATCH/ldo-schematic/platform-proposal/`), applied here as a guarded patch.

## 3. The drawing reproduces the number

The gate above compares text. The last step runs the drawing:
`ldo.metrics.run_decks` is handed the netlist xschem wrote out of `ac_loopgain_tb.sch` — not a deck,
not a rebuild — and its measures are compared with `decks/candidate/scorecard.json`'s own
`bench_measures` for that bench.

| measure | certified | from the drawing |
|---|---|---|
| `loopgain_db` | 49.94548 | 49.94548 |
| `pm_loop` | 72.41882 | 72.41882 |
| `ugf_loop` | 836501.2 | 836501.2 |
| `gm_at_180` | −6.426522 | −6.426522 |
| `gm_loop_db` | 6.426522 | 6.426522 |
| `ms_peak` | 7.149795 | 7.149795 |
| `tloop_ph_dc` | 179.9755 | 179.9755 |

All seven agree at every printed digit. The Middlebrook injection is what makes this a real check of
the hierarchy: `.control` reaches into the cell as `@v.xdut.vlp[acmag]` and reads `v(xdut.lp_brk)`,
so the drawing would return nothing at all if the loop-break marker had been drawn inside a block
rather than at the cell level.

## 4. Artefacts

| file | what it is |
|---|---|
| `circuits/ldo_ihp_capless/xschem/<bench>_tb.sch` | the 13 bench sheets, beside the cell symbol they instantiate |
| `figs/<bench>_tb.png` | one render per sheet |
| `build_benches.py` | the deck split, the drawing, the comparison, the reproduction |
| `out/<bench>_tb.spice` | the netlist xschem writes out of each sheet |
| `out/benches.json` | every gate's counts and findings, xschem's log, the reproduction table |

Reproduce: `LDO_EXP=006 uv run --no-sync python experiments/006-visual-benches/build_benches.py`.
Run [004](../004-schematic/README.md) first — the sheets instantiate the cell symbol and the block
hierarchy it builds. The step is an assertion: any drift on any sheet, a missing figure, or a
reproduction that moves a digit exits non-zero.

## Lessons to graduate

- (`006`) A schematic that a netlist round trip proves *topologically* correct can still carry a
  corrupted value, because a topology check never looks at one. Comparing the drawing's netlist with
  the deck value by value is what caught a stimulus that had been silently truncated to its last 24
  characters. Journal: `doc/journal/a-display-shortening-reached-the-netlist.md`.
- (`006`) A bench drawing has to carry its own directives and `.control` to be a bench at all. Lift
  them verbatim from the certified deck into a `code_shown` block rather than retyping them, and
  compare them back — then the drawing cannot drift from the bench of record either.
