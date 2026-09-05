# 004 — schematic of record: the drawing that provably IS the certified netlist

**Paper(s):** none
**Hypothesis:** `spicexplorer_netlist2xschem` can turn the frozen `decks/candidate/dc_op.spice` into a reviewable xschem schematic of the cell, and `spicexplorer_circuitgraph` can prove the drawing and the certified netlist are the same circuit — every device, model, size expression and net — so the figure a reviewer reads carries no claim the simulator has not already scored. Falsified if the round trip loses or invents any device, or if the equivalence check cannot be made non-vacuous.
**Control:** the certified deck itself, byte for byte (`decks/candidate/dc_op.spice`, SHA-locked) — never a rebuild.
**Verdict:** **TOPOLOGY CONFIRMED, SIZES PARTLY FALSIFIED.** The drawing is the certified cell for all **25 of its 25 devices — 25 components and 15 nets matched under a wiring-preserving isomorphism**, with nothing skipped (§1). The parameter check added for review-002 finding **M3** then compares the sizes too, and it is **red on 8 of 114 parameter rows** (§2): the three `cap_cmim` capacitors are drawn without `w`/`l`, and `VREF` is drawn as 3 V instead of the design's 0.6 V. Both are named platform gaps in the *emitter*, not errors in this cell (§3). **The reproduce command therefore exits 1 today, on purpose.**

## 1. Drawing ≡ netlist (topology)

The chain is: frozen deck → `netlist2xschem --into XDUT` → `.sch` → **xschem netlists the drawing back out** → `circuitgraph.compare_netlists` on the two netlists. A `.sch` is a drawing file, so it is never handed to circuitgraph directly; the thing compared is what the drawing *means*.

| comparison | components | nets | verdict |
|---|---|---|---|
| certified cell vs the drawing's netlist | **25 vs 25** | **15** | **equivalent** — wiring-preserving isomorphism, non-vacuous |
| devices `netlist2xschem` could not place | **0** | — | — |

The three `rhigh` resistors (`XR1`, `XR2`, `XRB`) that the first run of this experiment reported as "not drawable" are drawn. They were never undrawable: the cause was a prefix-precedence bug in the schematic writer, now fixed upstream (platform #129 — `c846437`, `f0b78c5`, `b37afcc`). The PDK's `rhigh.sym` has two pins and carries the substrate node on a `body=` attribute, so the `.sch` holds `body=vss` and the netlist round trip reproduces `XR1 lp_brk fb vss rhigh w=r_w l=r_fb_l` exactly. The second comparison this experiment used to run — the certified cell *minus* the skipped devices — is no longer run when nothing is skipped, because it would only restate the row above; `build_sch.py` records why in `out/schematic.json`.

Two earlier attempts at this check were **vacuous passes** and are recorded because they are the trap: comparing the two files while each only *defines* a subckt returns `equivalent=True, matched 0 components`, and wrapping the cell in a subckt with one `XDUT` instance returns `equivalent=True, matched 1 component`. Only the flat comparison actually walks the devices. `build_sch.py` therefore reports `components_matched` and a `vacuous` flag beside every verdict — an equivalence result that matched nothing is not evidence.

## 2. Drawing ≡ netlist (the sizes) — review finding M3

An isomorphism compares devices, models and connectivity. It does **not** compare parameters, and review-002 M3 showed what that costs: the drawing netlisted `cap_cmim` with no `w`/`l` and `VREF vref vss 3`, and the equivalence check passed anyway. `build_sch.py::check_parameters` now closes that hole. It joins the certified netlist and the drawing's netlist device by device — through `spicexplorer_core.spice_engine.NetlistView`, the platform's own parser, never a new one — and compares **every parameter by number**: each token is resolved against the deck's own `.param` bindings (the drawing carries the sizing symbolically, which is the point of it) and normalised through `spicexplorer_core.eng.parse_value`, so `c_out_w` and `58u` and `5.8e-05` are one value.

- A device present on one side only is its own finding, so a lost device cannot hide inside the join.
- A model or subckt name (`rhigh`, `cap_cmim`, `sg13_lv_pmos`) is compared as a **case-insensitive string**, not semantically: the check would not notice a symbol that renamed a device to an equivalent model.
- **`w` and `l` may never be defaulted.** An absent size is a failure, not a device at its model default — a `cap_cmim` with no size is 7 µm × 7 µm ≈ 74 fF, which is exactly the drift being looked for. Only no-op counts default: `m`/`ng`/`nf` → 1 and the poly resistor's bend count `b` → 0, each the value the model library itself declares.
- `VREF` gets its own named check against `vref_val` (0.6 V, `circuits/ldo_ihp_capless/pdk/ihp-sg13g2/sizing.yaml`, `min == max`; quoted as `vref.typical` in `datasheet.yaml`), so a wrong reference can never be reported as just one more parameter row.

**Result: 114 parameter rows over 25 devices, 8 rows red on 4 devices.**

| device | parameter | certified | drawn | |
|---|---|---|---|---|
| `XCFF` | `w`, `l` | `c_ff_w` = 8 µm | **absent** | falls back to the model's 7 µm × 7 µm |
| `XCC` | `w`, `l` | `c_comp_w` = 54 µm | **absent** | " |
| `XCOUT` | `w`, `l` | `c_out_w` = 58 µm | **absent** | " (`m=c_out_m` = 4 does survive) |
| `VREF` | `value`, `dc` | `dc {vref_val}` = 0.6 V | **3 V** | the render draws the `3`, so the figure carries the bug |

Everything else matches: all 17 MOSFETs carry `w`/`l`/`m` symbolically, `XMP` keeps `m=x_dut_xmp_m` (19), and the three resistors carry `w`/`l` with the substrate on `body=vss`.

**The assertion is proven to bite.** Against the drawing committed at `6bd5aba` — the one M3 was written about — it reports **11** rows and exits 1: the 8 rows above on the same 4 devices, *plus* one row each for `XR1`/`XR2`/`XRB`, which are missing from that drawing entirely.

```
# figs/xschemrc is git-ignored and is written by the render step, so run the main build once
# first (or point --rcfile at any xschemrc that has the PDK symbol libraries on XSCHEM_LIBRARY_PATH)
git show 6bd5aba:circuits/ldo_ihp_capless/xschem/ldo_ihp_capless.sch > $SX_SCRATCH/pre/ldo_ihp_capless.sch
uv run --no-sync python experiments/004-schematic/build_sch.py \
    --check-sch $SX_SCRATCH/pre/ldo_ihp_capless.sch \
    --rcfile experiments/004-schematic/figs/xschemrc --workdir $SX_SCRATCH/pre
```

## 3. What is still wrong is in the emitter

Both remaining failures are siblings of the resistor bug — a device typed by its reference prefix and then written through a symbol that has no slot for its size. Neither is a defect in this cell, and neither can be fixed from this repo. Journal: `doc/journal/an-isomorphism-carries-no-sizes.md`; both are added to `doc/journal/template-gaps-t8.md`.

1. **A 2-node PDK primitive shipped as a subckt loses its size.** `XCFF a b cap_cmim w=.. l=..` has exactly two nets, so the prefix test in `ingest.py` succeeds and types it `CAP` — it never reaches the subcircuit fallback that rescued the 3-node `rhigh`. `mapping._GENERIC_SYMREF[CAP]` picks `devices/capa.sym`, whose `format` is `@name @pinlist @value m=@m`, and the two-terminal branch of `emit._device_attrs` writes only `value` + `m`. The PDK *does* ship `sg13g2_pr/cap_cmim.sym` with `format="@spiceprefix@name @pinlist @model w=@w l=@l m=@m"` — the `rhigh` shape minus `body` — but the PDK symbol table is keyed on `DeviceKind.SUBCKT` only.
2. **A braced expression cannot ride in a quoted xschem attribute.** `emit._fmt_value` quotes any value containing a space, so `dc {vref_val}` is written `value="dc {vref_val}"`. xschem treats `{}` as its own attribute delimiters, trips on the brace inside the quotes (`SKIPPING |"}|` on stderr, exit status still 0) and falls back to the `vsource.sym` template default, which is `value=3`. `VLP`'s `dc 0` has no braces and round-trips. Any source whose value is a `.param` expression is affected.

## 4. The render

`figs/ldo_ihp_capless.png` (1600 × 438, `--show-params`) is legible and every device, net label and size expression is on it — but it is a single wide row, so it is a zoom-in figure, not a page figure. Three items, all cosmetic and all in the placer rather than the circuit:

- `XR1` and `XRB` sit on the same row and the long `R={…}` expression the PDK `rhigh.sym` draws for each of them **overlaps horizontally**.
- `XCFF`'s rotated instance label crosses the `ea_o1`/`lp_brk` wire.
- MOS parameter text is drawn over the symbol bodies.

The resistors' substrate net is on the `body=vss` attribute and is **not drawn** — documented here, not visible in the figure. `VREF` is drawn showing `3`, which is the M3 failure of §2 visible in the artefact itself.

## 5. Artefacts

| file | what it is |
|---|---|
| `circuits/ldo_ihp_capless/xschem/ldo_ihp_capless.sch` | **the schematic of record** (25 devices, 48 labels) — committed beside the circuit it draws, because it is the deliverable and `experiments/*/out/` is git-ignored |
| `figs/ldo_ihp_capless.png`, `.svg` | the render a reviewer reads |
| `out/ldo_ihp_capless.spice` | the netlist xschem writes back out of the drawing |
| `out/ldo_ihp_capless_certified.spice` | the certified cell, flat, out of the frozen deck |
| `out/ldo_ihp_capless_from_sch.spice` | the drawing's netlist, flat, as compared |
| `out/schematic.json` | the equivalence verdict, the parameter findings, the skipped list, the xschem command |

Reproduce: `LDO_EXP=004 uv run --no-sync python experiments/004-schematic/build_sch.py`. It **exits 1** while §2 is red — the step is an assertion, not a report, and it also exits non-zero on a skipped device or a vacuous equivalence. xschem runs headless (`-n -q -r`); it needs the interpreter that has the PDK symbol libraries on `XSCHEM_LIBRARY_PATH`, which `netlist2xschem` writes into an `xschemrc` beside the **render** (`figs/`, not beside the `.sch`). That `xschemrc` holds absolute host PDK paths and is git-ignored — it is regenerated by every run.

## Lessons to graduate

- (`004`) An equivalence check that matched **zero** components is a vacuous pass, and both natural ways to call `compare_netlists` on a cell produce one. Always report `components_matched` next to `equivalent`, and compare the cell **flat**. Journal: `doc/journal/vacuous-equivalence-passes.md`.
- (`004`) A wiring-preserving isomorphism carries **no sizes**. After topology, join the two netlists device by device and compare every parameter by number — and never default `w`/`l`, because the model default is the drift being looked for. With that check in place the honest claim is that the drawing **cannot drift unnoticed**, not that it cannot drift: the netlist stays the design of record, and the drawing is evidence only while the check is green. Journal: `doc/journal/an-isomorphism-carries-no-sizes.md`.
- (`004`) "The tool cannot draw it" is a claim about the tool and needs the same evidence as a claim about a circuit. The three `rhigh` resistors were recorded here as undrawable; they were a precedence bug, now fixed upstream. Journal: `doc/journal/prefix-precedence-drops-drawable-devices.md` (resolved), superseding `doc/journal/netlist2xschem-skips-3-terminal-resistors.md`.
