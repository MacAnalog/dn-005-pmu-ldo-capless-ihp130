# 004 — schematic of record: the drawing that provably IS the certified netlist

**Paper(s):** none
**Hypothesis:** the certified cell can be drawn as a hierarchy a reviewer can read — a top sheet of
five functional blocks in signal order, one child sheet per block — and the drawing can be *proved*
to be the certified netlist: the same devices and wiring under `spicexplorer_circuitgraph`, and the
same sizes under a per-device parameter assertion. Falsified if the round trip loses or invents a
device, if the equivalence check cannot be made non-vacuous, or if any parameter drifts.
**Control:** the certified deck itself, byte for byte (`decks/candidate/dc_op.spice`, SHA-locked) —
never a rebuild. The flat drawing is built beside the hierarchy from the same deck and put through
the same two gates, so a difference between them would be visible.
**Verdict:** **CONFIRMED**, re-gated against the **recertified** cell (`bf3a4f8`, "the certified deck
is the drawn device set": segmented `XR1_1..8`/`XR2_1..8`/`XRB_1..5`, half-width `…A`/`…B` device
pairs, the pass device as `x_dut_xmp_nf_mult` fingers). The hierarchy is that cell: **50 of 50
components and 33 nets** matched under a wiring-preserving isomorphism, nothing skipped, and **239 of
239 parameter rows** green over the 50 devices, including the 0.6 V reference by name. The flat
drawing returns the same two verdicts. Both `w`/`l` gaps and the 3 V reference this experiment
reported in its first round were emitter defects and are fixed upstream
(`spicexplorer-platform @1775a67`).

## 1. The hierarchy

`circuits/ldo_ihp_capless/xschem/ldo_ihp_capless.blocks.json` names the blocks — the
`spicexplorer/xschem-block-annotations@1` contract, hand-authored from `doc/design-reference.md`.
`circuitgraph.find_subcircuits` was run first and does detect the mirrors, but its matches straddle
the functional boundaries (the `XMA`/`XMB` fold mirror and the `XMCP`/`XMD` mirror are found as
pairs, not as one output stage), so the hand decomposition is the one drawn and the detector is not
used here.

| block | devices | what it is | boundary nets |
|---|---|---|---|
| `bias_ref` | `XRB_1..5` `XMB0A/B` `XMB1A/B` `XMBP` (10) | resistor-referenced bias | `nbias` `pbias` `vdd` `vss` |
| `ea_stage1` | `XMT` `XM1A/B` `XM2A/B` `XM3A/B` `XM4A/B` (9) | 5T OTA, PMOS input | `vref` `fb` `ea_o1` `pbias` `vdd` `vss` |
| `ea_stage2` | `XM5` `XM6` `XCC` (3) | NMOS common source + Miller cap | `ea_o1` `ea_out` `pbias` `vdd` `vss` |
| `fvf_output` | `XMC` `XMA` `XMB` `XMCP` `XMD` `XMSA/B` `XMP` (8) | FVF double-mirror output stage | `ea_out` `vout` `nbias` `vdd` `vss` |
| `fb_divider` | `XR1_1..8` `XR2_1..8` `XCFF` (17) | 1:1 divider + feed-forward cap | `lp_brk` `fb` `vss` |

Three devices stay at the cell level and are drawn on the top sheet: `VREF`, the loop-break marker
`VLP`, and the output capacitor `XCOUT`. `VLP` staying at the top level is a **requirement, not a
preference**: the three `ac_loopgain` decks reach it as `@v.xdut.vlp[acmag]` and read
`v(xdut.lp_brk)`, so moving it into `fb_divider` would rename both paths to `xdut.xfb_divider.*` and
break the benches that measure phase margin. The Miller cap `XCC` is folded into `ea_stage2` rather
than left loose because the hierarchy generator does not make a subcircuit of a single device, and a
one-capacitor block would be noise on the sheet.

## 2. Drawing ≡ netlist (topology and sizes)

The chain is: frozen deck → hierarchy → **xschem netlists the drawing back out** → the block
subcircuits are spliced back inline → `circuitgraph.compare_netlists`, then the parameter assertion.
A `.sch` is a drawing file, so it is never handed to circuitgraph; the thing compared is what the
drawing *means*. The splice (`sch_support.flatten_hierarchy`) uses only the platform's netlist
parser: a leaf line's net tokens are identified by position from the parser's own node count for
that device, formals are mapped to actuals through the block instance, and **leaf instance names are
preserved** (`XM1` stays `XM1`), which is what lets the parameter assertion join the two netlists
device by device. It refuses to run if two blocks share a leaf name or an internal net name.

| drawing | components | nets | vacuous | parameter rows |
|---|---|---|---|---|
| `ldo_ihp_capless.sch` (hierarchy, 5 blocks) | **50 vs 50** | **33** | no | **239 / 239** |
| `ldo_ihp_capless_flat.sch` (one sheet) | **50 vs 50** | **33** | no | **239 / 239** |

The net count is also the check that all **21** `rhigh` resistors kept their substrate terminal: the
PDK symbol carries it on a `body=` attribute rather than a pin, and a split `vss` would show up here
as an extra net. A block's own internal nets are qualified with the block instance when the sheets
are spliced (`xbias_ref.n_rb_1`), because two children auto-name an unlabelled node the same
`net1`; the count is unchanged by the renaming, and a collision that is NOT local is still a
failure.

**A third assertion: block coverage.** The blocks are named by device, so a recertification that
renames devices (`XR1` → `XR1_1..8`) silently empties a block — `BlockAnnotationSet.load` drops what
it cannot find, and the topology gate still passes on the collapsed drawing, because equivalence
measures the netlist and not the readability. Measured, before the fix: **2** blocks formed of 5,
gate green at 50/50 and 239/239. The build now asserts that every annotated device exists, that
every device is either in a block or one of the three declared loose ones, and that as many blocks
formed as were declared.

The parameter assertion is what an isomorphism cannot do. It joins the two netlists device by device
through `spicexplorer_core.spice_engine.NetlistView` — the platform's own parser, never a new one —
and compares every parameter **by number**: each token is resolved against the deck's `.param`
bindings (the drawing carries the sizing symbolically, which is the point of it) and normalised
through `spicexplorer_core.eng.parse_value`, so `c_out_w` and `58u` and `5.8e-05` are one value.

- A device present on one side only is its own finding, so a lost device cannot hide inside the join.
- A model or subckt name is compared as a case-insensitive string, not semantically: the check would
  not notice a symbol that renamed a device to an equivalent model.
- **`w` and `l` may never be defaulted.** An absent size is a failure, not a device at its model
  default — a `cap_cmim` with no size is 7 µm × 7 µm ≈ 74 fF, which is exactly the drift being
  looked for. Only no-ops default: `m`/`ng`/`nf` → 1 and the poly resistor's bend count `b` → 0.
- `VREF` gets its own named check against `vref_val` (0.6 V, `pdk/ihp-sg13g2/sizing.yaml`,
  `min == max`), so a wrong reference can never be reported as just one more parameter row. It reads
  0.6 V drawn against 0.6 V certified.

An expression-valued parameter (`w={x_dut_xm1_w/2}`, `l={r_fb_l/8}`) is compared as **normalised
text**, not evaluated: `spicexplorer_core.eng.parse_value` resolves a symbol against the deck's
bindings but does not do arithmetic, so for these rows the assertion proves the drawing carries the
deck's expression verbatim rather than proving the two numbers agree. It is the weaker half of the
gate and is stated as such.

**Both gates bite.** Run against the drawing committed at `6bd5aba` — a sheet of an older topology —
the same command reports `equivalent: false, components_matched: 0, vacuous: true` and names the
devices of that revision the certified cell does not have. The value half of the same machinery
catches live silent corruption twice over: the stock emitter abbreviates any attribute over 24
characters and writes the abbreviation into the netlist, which truncated a `pulse(...)` stimulus on
two bench sheets in [006](../006-visual-benches/README.md), and on **this** cell truncates the pass
device's own size — the unpatched generator's sheet netlists `XMP` with
`w='…xmp_nf_mult}' m='…xmp_nf_mult}'` against a certified
`w={x_dut_xmp_w/x_dut_xmp_nf_mult} m={x_dut_xmp_m*x_dut_xmp_nf_mult}`, while its topology check
passes at 50/50. That run is kept as a report-only control (`out/unpatched/`,
`unpatched_cli_control` in `out/schematic.json`): the drawing of record is built in-process with the
shims, and the stock generator's own sheet is measured beside it as the evidence for P4.

```
uv run --no-sync python experiments/004-schematic/build_sch.py --check-sch <path/to.sch> \
    [--hierarchical-check] --rcfile experiments/004-schematic/figs/xschemrc --workdir $SX_SCRATCH/pre
```

## 3. What the generator needed, and what it still needs

Five changes were needed in `spicexplorer_netlist2xschem` to draw this cell and its benches. They
are applied here as documented patches in `sch_support.py::apply_platform_proposals()`, each with a
guard that fails loudly the moment the upstream code changes, and proposed upstream as a diff that
applies cleanly at `1775a67` and still at `297493a` (`$SX_SCRATCH/ldo-schematic/platform-proposal/`). Nothing is worked
around silently, and no coordinate is hand-written: placement and wiring stay the generator's job.

| | change | why the drawing needed it |
|---|---|---|
| **P1+P2** | a declared supply port stays a port; the child inherits the parent's supply map | without both, a child is drawn as one flat row of transistors — the rail-banded floorplan is off, because `supply={}` tells the placer the block has no rails |
| **P3** | `register_subckt_symbol` for a design's own cell symbol | a bench's `XDUT ... ldo_ihp_capless` had no symbol and was dropped from the drawing |
| **P4** | a display shortening must not reach the netlist | see the truncated `pulse(...)` and the truncated `XMP` size above |
| **P5** | a child sheet may be wired label-only | with the default `hybrid` wiring a net's trunk wire **crosses** a pin's stub without a junction; xschem connects only at a junction, so the pin lands on an unnamed `net1`. Measured on the recertified cell: `XMB0A net1 net1 vss vss` in `bias_ref` (certified `nbias nbias vss vss`) and `XM3A` likewise in `ea_stage1` — both the first half of a duplicated diode-connected pair. The gate catches it (33 nets vs 35) |

P5 is applied **per block, on measurement, not by default**: every child is drawn `hybrid` (drawn
rails and wires — the readable form), netlisted on its own, and only a block whose netlist shows an
auto-named `netN` is redrawn label-only. On the cell of record that is 2 blocks of 5 (`bias_ref`,
`ea_stage1`); the other three keep their wires. `out/schematic.json` records which mode each child
got and which pins were lost.

Three smaller inconsistencies are post-processed here and reported upstream rather than patched:
`sync_symbol_pin_dirs` gives each block symbol the pin directions its own child sheet declares (the
two are computed independently, and xschem reported `Unmatched subcircuit schematic pin direction`
errors and a spurious shorted-output warning on a hierarchy that netlists perfectly),
`append_port_symbols` draws the top sheet's own three ports, which the parent emitter omits, and
`append_child_port_symbols` does the same for a label-wired child, which declares no interface of
its own. With all three, xschem netlists the whole hierarchy with no warnings and no errors.

**What is still not right, and is not fixable from this repo:**

1. **The top sheet is label-connected, not wire-connected.** The parent emitter lays the blocks in
   one row and joins them with a stub and a net-name label per pin; it draws no wires between
   blocks. Each pin carries both its functional name and its net, and the render colours every net,
   so the signal path reads left to right — but the loop is not visible *as* a loop. A block-level
   router (and a routing channel for the `fb` return path) is the proposal.
2. **`fb_divider`'s functional `in` and `out` both sit on the right.** A pin's side comes from the
   device roles its net touches, not from the contract's port names.
3. **The `rhigh` and `cap_cmim` symbols draw their own formulas.** Under `--show-params` the PDK symbol
   renders a ~90-character `tcleval(C=[ev {…}])` expression, and `rhigh` a ~120-character
   `R={ ( 1.6e-4 / r_w + 1360.0 * … ) }` sheet-resistance formula, that run across the sheet and
   collide with the neighbouring device's text. With 16 chained divider resistors the collision is
   the loudest thing on `blocks_fb_divider.png`. It is the PDK symbol's own text layout, identical at
   any placement, so no placer change can help; the platform vendors "no-params" symbol twins for MOS
   devices but explicitly not for PDK subcircuit primitives. A render-side option to suppress a PDK
   symbol's own annotation text is the proposal (P7).
4. **The annotation loader fails open.** `BlockAnnotationSet.load` silently drops a device it cannot
   find in the circuit, so a stale `blocks.json` yields a smaller hierarchy and no diagnostic. The
   coverage assertion in §2 is this repo's guard; failing closed upstream is the proposal (P8).

## 4. The figures

| figure | what it shows |
|---|---|
| `figs/ldo_ihp_capless.png` | the top sheet: five blocks left to right in signal order, `VREF`/`VLP` at the bottom left, `XCOUT` on `vout` |
| `figs/blocks_bias_ref.png` | the bias reference — label-wired (P5) |
| `figs/blocks_ea_stage1.png` | the 5T OTA, its four half-width pairs — label-wired (P5) |
| `figs/blocks_ea_stage2.png` | the common-source stage and the Miller cap |
| `figs/blocks_fvf_output.png` | the output stage, PMOS band over NMOS band, rails drawn |
| `figs/blocks_fb_divider.png` | the 8+8 divider chain and the feed-forward cap |
| `figs/ldo_ihp_capless_flat.png` | the same circuit on one sheet — the previous drawing of record, kept as the control |

Renders are produced headlessly and rasterized at 2400 px wide. xschem sizes its canvas to the
geometry bounding box, which clips every label that overhangs its anchor, so the export measures the
text extents and pads the canvas before rasterizing; the `.sch` is not touched. Only the PNGs are
committed — the SVG is the padding step's intermediate and is removed after rasterizing, so the
previously committed `figs/ldo_ihp_capless.svg` is gone.

## 5. Artefacts

| file | what it is |
|---|---|
| `circuits/ldo_ihp_capless/xschem/ldo_ihp_capless.sch` | **the schematic of record** — committed beside the circuit it draws |
| `circuits/ldo_ihp_capless/xschem/blocks/*.sch`, `*.sym` | the five child sheets and their generated symbols |
| `circuits/ldo_ihp_capless/xschem/ldo_ihp_capless.sym` | the cell symbol, pins in the certified `.subckt` port order `vdd vout vss` |
| `circuits/ldo_ihp_capless/xschem/ldo_ihp_capless.blocks.json` | the block decomposition that drives the hierarchy |
| `circuits/ldo_ihp_capless/xschem/ldo_ihp_capless_flat.sch` | the flat drawing, same two gates |
| `experiments/004-schematic/sch_support.py` | the generator patches, the hierarchy→flat splice, and the render/netlist helpers (006 imports it) |
| `out/ldo_ihp_capless_from_sch.spice` | the drawing's netlist, spliced flat, as compared |
| `out/ldo_ihp_capless_certified.spice` | the certified cell, flat, out of the frozen deck |
| `out/schematic.json` | both gates' verdicts, the parameter findings, xschem's own log |

Reproduce: `LDO_EXP=004 uv run --no-sync python experiments/004-schematic/build_sch.py`. The step is
an assertion, not a report: a skipped device, a vacuous or failed equivalence, one drifted parameter
or a missing figure all exit non-zero. xschem runs headless and needs the PDK symbol libraries on
`XSCHEM_LIBRARY_PATH`, which the build writes into an `xschemrc` beside the render (`figs/`). That
file holds absolute host PDK paths and is git-ignored; every run regenerates it.

## Lessons to graduate

- (`004`) An equivalence check that matched **zero** components is a vacuous pass, and both natural
  ways to call `compare_netlists` on a cell produce one. Always report `components_matched` next to
  `equivalent`, and compare the cell flat. Journal: `doc/journal/vacuous-equivalence-passes.md`.
- (`004`) A wiring-preserving isomorphism carries **no sizes**. After topology, join the two
  netlists device by device and compare every parameter by number — and never default `w`/`l`.
  Journal: `doc/journal/an-isomorphism-carries-no-sizes.md`.
- (`004`) A hierarchy is a drawing change, so it has to be *proved* to be one: splice the blocks back
  inline, keep the leaf names, and re-run the gates the flat sheet passes. Journal:
  `doc/journal/a-readable-hierarchy-must-flatten-back.md`.
- (`004`) A gate that measures the netlist says nothing about the **structure** of the drawing: a
  stale block annotation collapsed the hierarchy from five blocks to two and both gates stayed
  green. Assert what the drawing is supposed to BE — block count, device coverage — beside what it
  means. Journal: `doc/journal/a-green-gate-on-a-collapsed-drawing.md`.
- (`004`) "The tool cannot draw this" is a claim about the tool and needs the same evidence as a
  claim about a circuit — and when it is true, the answer is a proposed diff, not a workaround.
  Journal: `doc/journal/prefix-precedence-drops-drawable-devices.md`.
