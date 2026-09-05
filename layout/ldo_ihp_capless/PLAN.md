# Layout plan — `ldo_ihp_capless` (IHP SG13G2, sg13_lv 1.5 V)

**KIND: PLAN.** The floorplan of record for the second drawing of the capless FVF LDO. The first
(`experiments/005-layout`) was DRC-0 / LVS-matched and passed every bench, and is still rejected:
its 10 mA path is 12–28x over the process metal limit (`review-002` **B1**), its matched pairs are
adjacent mirrored single fingers with no dummies and periodic point taps instead of guard rings
(**m3**), its LVS reference is written by the generator from its own device table (**M7**), and no
committed case exercises the Metal1 obstacle map (**M8**). This plan fixes all four **before**
pixels, because the journal entry `metal-current-density-is-nobodys-check.md` measured what
retrofitting costs: 79–117 Metal1 spacing violations, because `rail_gap` and the track pitch were
sized for a thin rail.

Inputs: the certified netlist `circuits/ldo_ihp_capless/pdk/ihp-sg13g2/netlist.spice`
(sha `18bd9c95…`), `sizing.yaml` (design of record, 003), `decks/candidate/scorecard.json` (the
yardstick), and the **measured** layout brief `layout/ldo_ihp_capless/BRIEF.md` + `brief.json`.
Every constraint below cites a brief section; nothing here is a rule of thumb.

---

## 0. Assumed approvals

Autonomous run, no human at the gate. These are the decisions taken without review; each is
listed again in the PR body.

| # | decision | default it came from | why this and not that |
|---|---|---|---|
| A1 | **Pins**: `vdd` TopMetal1 strap on the **top** edge, `vss` Metal1 rail on the **bottom** edge, `vout` TopMetal1 strap on the **right** edge, `vref` + `fb` Metal1/Metal2 on the **left** edge | brief §9 pin-intent table | The coordinator's default ("vdd/vss on the long edges, vin/vout/vref/fb on the short edges") is self-contradictory here: `vin` **is** `vdd` in this cell (one supply pin). Resolved in favour of the brief, which is measured. |
| A2 | **Aspect ratio ceiling 2:1**, target ~1.1:1 | coordinator | 005 is 2.34:1 (287.4 x 122.9). The cap block (XCOUT 2x2 ~ 125 x 125 um) dominates; it goes *under* the transistor stack rather than beside it. |
| A3 | **Cap plan: XCOUT is the unit-cell array (2x2 common centroid of the certified 58 um unit); XCC and XCFF are single certified units inside the same block, same orientation, same plate side. NO MIM dummy ring.** | deviates from the coordinator's "ONE unit-cell array with a dummy ring" | Arithmetic: the three plate areas are 64 / 2916 / 13456 um^2; a common unit needs `u^2` to divide all three, i.e. `u = 2 um` and ~3400 tiles. Any coarser unit rounds XCC/XCOUT by >= 0.8 %, which changes the drawn device and is a **sizing change** (re-certify), not a layout choice. `m = 4` on XCOUT already *is* a unit array. The dummy ring is dropped because it is measured to buy nothing: brief §6 gives `mim_cout_unit` **no bound**, `mim_feedforward` 133 sigma and `mim_miller` 794 sigma of headroom, while a ring of 58 um units triples the block area. A Metal5/TopMetal1 keep-out frame is drawn instead (metal-density environment, no extracted device). |
| A4 | **Strap plan**: TopMetal1 `vdd` along the top edge and `vout` along the right edge, `pwr_w = 4.0 um` (TM1.a floor is 1.64; **2.0 in the first drawing — raised in the fix round, review-003 F1**, because the strap's own series R is 1.13 Ohm on `vdd` and 1.03 Ohm on `vout` at 2.0 um and the extractor measures neither); each stitched to a Metal5 landing pad with **12 TopVia1**, and down to the pass array through **48 cuts per level** on Via2/3/4 and 2 Via1 per S/D column | brief §8 | See §3. The Metal1 rails keep `rail_w = 0.8 um` because after this change **no Metal1 in the cell carries more than 0.27 mA**. |
| A5 | **The pass array is redrawn with 4x the fingers (`x_dut_xmp_nf_mult = 4`: 76 unit fingers of 2.5 um, total W unchanged at 190 um)** | not in the brief; see §3 | This is the only way the shared-diffusion column riser gets legal. **A5 originally filed it as "not a sizing change" because `w`/`m` were untouched; review F19 overturned that and the ruling is adopted** — see §0.1. The knob now lives in `sizing.yaml`, the certified netlist draws the unit fingers, and the benches simulate them. |
| A6 | **Matched-row dummies are real, fully-tied devices declared in the LVS reference** (G=S=D=B on one rail) | none | Measured: the IHP LVS deck extracts a fully shorted dummy MOS as a device and `--purge --purge_nets` does **not** remove it (probe log `lvs_d2`/`lvs_d2p`); LVS matches only when the dummy is in the reference. The reference is therefore `lower(certified netlist) + dummy cards`, and the emitter asserts every added card has all four nodes on one rail — a divergence in a *real* device still fails. |
| A7 | **Density / fill and sealring are out of scope**; DRC runs with the density tables off by default (`--density` re-enables them) and the REPORT names the flag | 005 precedent, `review-002` m1 | Fill is a chip-assembly step and distorts the PEX of a bare cell. |
| A8 | **The GDS is not committed**; the layout of record is `layout/gen_ldo.py`. The render PNG *is* committed at `experiments/005-layout/figs/ldo_ihp_capless.png` | 005 precedent + `.gitignore` | An 845 kB binary can only drift from the generator. |
| A10 | **The `vss` return is a KELVIN CAP RETURN**: the pin is the foot of a **single** left-edge `vss_ret_w = 3.0 um` riser, the active devices reach it down that riser alone, and XCOUT's four bottom plates reach the *same pin* along the bottom rail on their own `vss_ret_w`-wide straps | re-derived brief §4a (review-003 F9, mechanism corrected) | The first attempt widened the rail, on the reviewer's reading that 32 Ohm of return R was the problem. The re-derived brief settles it by splitting the injection: **active devices only** behind 32 Ohm moves S7 by +0.44 mV, **XCOUT's plate only** behind 32 Ohm *improves* S7 to 103.2 mV, and the 11 Ohm cliff needs **both halves behind one R** — Cout's load-step displacement current develops a ground bounce the FVF sources and the EA read as a reference step. So the fix is a **connection**, not a width, and the second (right-edge) riser is deliberately **deleted**: it would put the active current back onto the cap's own return rail, which is the shared impedance the cliff is made of. Hand model: common series element 4.9 Ohm, worst-device total 14.3 Ohm, against the brief's 16 Ohm active-only budget. **One** `vss` label, at that pin. |
| A11 | **The pass gate's channel track is Metal3, not Metal1** (`TRACK_LAYER`) | not in the brief; review-003 F3 | `gate` was the only net whose track ran the length of the cell on Metal1 0.6 um above the substrate, and gate-only parasitics alone put S7 at 204.5 mV. Metal3 is ~2 um further up and is also the layer that lets the net cross the pass array's Metal2 comb without the hard-coded hop F7 flagged. The measured effect is in REPORT §6. |
| A12 | **`lp_brk` stays a pin and is escaped to the RIGHT edge, beside `vout`** | brief §4 + review-003 F8 | The certified netlist closes the divider with `VLP lp_brk vout dc 0` — a loop-break port the benches drive — so the cell cannot merge the two nets without deleting a pin. What the layout decides is *where* the external short lands, and brief §4 wants the sense at the OUTPUT PIN (0.026 mV of load regulation) rather than the pass drain (~10 mV against a 5.0 mV line). Drawn, labelled and stated here, so the GDS says which. |
| A13 | **`gpad` (0.5) and `isl_gap` (2.0) are knobs; `tap_pitch` is deleted** | review-003 F11 | `tap_pitch` gave a byte-identical GDS at both ends of its range — a dead search dimension. `isl_gap` moved the floorplan and was in neither the plan nor `BOUNDS`. `gpad` sets every gate bar's own area, which is what F3 is about. §5 is now generated from the dataclass and an assertion in `gen_ldo.py` fails the build if `BOUNDS` and `LayoutParams` ever disagree again. |
| A14 | **Every port label gets a 0.2 um square on its layer's PIN purpose** (`Metal1` 8/2, `Metal3` 30/2, `TopMetal1` 126/2), 17 in all; `PIN_SIDE` is a module constant, not a knob | review-004 F25 + the platform probe `@7d55218` | A text alone is not a pin: kpex emits a `[Pin]` node only when the label sits inside a polygon on the pin purpose, and without one the RC stitch anchors each port on a node it picks (measured: a proxy ~100 um from where the port is drawn), so every port-referred series-R number is referred to the wrong place. The purpose layer does not conduct, so this is geometry only — proved, not assumed: DRC 0, LVS matched, current density 30/30 unchanged, and the CC extracted netlist is **byte-identical** to the one the record scorecard was made from (418 of 418 lines). After it, 15 of 15 named ports anchor on `pin` instead of `proxy`. It does **not** remove the need for the RC stitch — the stitch still joins mesh to devices; what it changes is *where* the stitch anchors. Whether it also changed the two zero-ohm anchor ties REPORT §5 traces is **unmeasured**: there is no stitched netlist for `it12` to compare against. |
| A9 | **`LDO_GF_PYTHON` stays `~/miniconda3/envs/ai_env/bin/python`** | — | The coordinator's `LDO_GDS_PYTHON=…/envs/pex/bin/python` has **no gdsfactory** (verified). `pex` is the kpex interpreter; `ai_env` is the gdsfactory one. |

### 0.1 Re-certification of `decks/candidate` on the drawn device set (review F19, adopted)

A5 argued that folding `m` into fingers is a file-level detail because LVS compares W and L. The
reviewer measured that argument and it does not hold: three things the generator has drawn since
**it01** — the pass array's finger split, every common-centroid member as two half-width units,
and the resistors as segment chains — are electrical, and the certified deck described none of
them. Every budget in `BRIEF.md` is 25 % of a margin measured on that deck, so the yardstick was
being read against a device that is not drawn.

`circuits/ldo_ihp_capless/pdk/ihp-sg13g2/netlist.spice` now carries the drawn set, so it and the
LVS reference `layout/netlist_ref.py` emits are the same devices in the same numbers:

| certified before | certified now | why |
|---|---|---|
| `XMP … w=x_dut_xmp_w m=x_dut_xmp_m` (19 units of 10 um) | `w={x_dut_xmp_w/x_dut_xmp_nf_mult} m={x_dut_xmp_m*x_dut_xmp_nf_mult}` (76 unit fingers of 2.5 um) | the drawn array; `x_dut_xmp_nf_mult` is a new `sizing.yaml` knob (default 4, 2–8) and `LayoutParams.xmp_nf_mult` is **gone** — a number that moves a bench number is not a layout knob |
| `XM1 … w=x_dut_xm1_w` (one card) | `XM1A`/`XM1B … w={x_dut_xm1_w/2}` — and the same for XM2/XM3/XM4/XMS/XMB1/XMB0 | a matching pattern draws unit devices whichever pattern it is; interdigitation would draw the same halves |
| `XR1 … l=r_fb_l` | `XR1_1..XR1_8 … l={r_fb_l/8}` chained; `XR2` the same, `XRB` 5 | the drawn serpentines; `LayoutParams.r_segs`/`rb_segs` are gone, the generator reads the chain length |

Card parameters may now be `{expressions}` over sizing knobs; `netlist_ref.value()` evaluates them
(arithmetic on knob names only, no builtins). `--combine_devices` folds the halves and the chains,
so **LVS is unaffected** and matched at DRC 0 on the first build after the change.

**The new certified row** (`decks/candidate/scorecard.json`, all 13 benches, tt/27 °C, `make
freeze` re-run). "reviewer" is the same quantity measured independently in `REVIEW.md` from the
extracted device set with every `Cext_` card deleted:

| spec | certified before | certified now | delta | reviewer's what-if |
|---|---|---|---|---|
| `i_q_ua` (S5 ≤ 50) | 36.2771 | **33.8054** | **−2.472** | 33.80539 |
| `v_out_v` (S1 ∈ [1.176, 1.224]) | 1.200072 | **1.199499** | −0.573 mV | 1.199499 |
| `v_undershoot_mv` (S7 ≤ 150) | 104.847 | **115.057** | **+10.21** | 115.065 |
| `pm_loop_deg` (S8 ≥ 60) | 72.4188 | **72.5064** | +0.088° | 72.50641 |
| `v_dropout_mv` (S4 ≤ 200) | 106.143 | **104.671** | −1.47 (below the 2 mV bench resolution) | — |
| `load_reg_mv` / `line_reg_mv` | 0.028 / 0.059 | 0.026 / 0.056 | −0.002 / −0.003 | — |
| `ugf_loop_khz` / `ms_peak_db` / `t_transient_us` | 836.5 / 7.150 / 0.1254 | 801.5 / 7.813 / 0.1563 | −35.0 / +0.66 / +0.031 | — |

Still PASS on all eight spec lines, and the four rows the reviewer measured independently agree to
4–6 digits. **What that costs the brief**: the S7 margin is 150 − 115.1 = **34.9 mV**, not 45.2,
so every parasitic budget derived from it tightens by ~23 %. The brief is re-derived on this row
before the fix round is judged.

**One encoding fork, measured rather than argued.** The PDK subckt has its own finger parameter
`ng`, which looks like the better model of a shared-diffusion array (it recomputes as/ad/ps/pd for
the shared columns). It is **not** used, because at constant total width and constant junction
geometry it alone reads a different S7:

| pass-device card, everything else the drawn set | S7 | `t_transient_us` |
|---|---|---|
| `m=76 w=2.5u` (the certified card) | **115.057** | 0.1563 |
| `m=76 w=2.5u` with kpex's own measured `as/ad/ps/pd` forced on | 115.065 | 0.1563 |
| `ng=76 w=190u` (PDK finger formula) | 105.231 | 0.1166 |
| `ng=76 w=190u` with the old `m=19` card's `as/ad/ps/pd` forced on | 105.214 | 0.1166 |
| `ng=1 w=190u` (one 190 um finger) | 252.650 | 0.5273 |
| `m=19 w=10u` (the old card) inside the otherwise-drawn set | 115.318 | 0.1591 |

Rows 1–4 show the 9.8 mV is **entirely the PSP `nf` parameter**, not junction area or perimeter:
forcing the areas equal moves S7 by 0.02 mV either way. kpex extracts the drawn array as **76
separate `ng=1` cards** (counted: 76 cards, 190.0 um total, half with drain and source swapped),
so `ng=76` in the certified deck would bank a ~10 mV pre→post credit that is a model parameter
rather than a layout. The unit-finger card puts the yardstick and the extracted measurement on one
device model, which is the whole point of re-certifying.

**Not done here, and why.** F14 asks for the resolved sizing inside `decks/candidate/design.json`.
`design.json` is what the `deck-rebuild` lint round-trips through `Design.from_dict`, so resolved
values there would pin the frozen dir to a snapshot of `sizing.yaml`; and writing them from
`certify()` edits `ldo/metrics.py`, which is the `script` of **both** scorecards' provenance
blocks — measured: it invalidates all 33 of `decks/reference`'s computation hashes, and only the
verifier may re-sign that dir. F14's second option is taken instead: the sizing of record is
`circuits/ldo_ihp_capless/pdk/ihp-sg13g2/sizing.yaml`, named as such in `BRIEF.md` and `REPORT.md`.

---

## 1. Device table, grouped by matching class

Sizes are read from `sizing.yaml` at build time and are never retyped here (`W/L` column is the
design of record for orientation only). Pattern column: what the brief's tolerated mismatch
implies (§6: `< 3 sigma` -> common centroid + dummies; `3–6` -> interdigitated + dummies;
`6–20` -> same row same orientation; `> 20` -> any).

| class | devices | W/L (um) | headroom | brief pattern | **drawn as** |
|---|---|---|---|---|---|
| `ea_in_pair` | `XM1`, `XM2` | 9.53 / 0.5 | 1.85 sigma | common_centroid+dummies | **A B B A** along row B: each member = 2 instances of `nf = 2` (4 fingers of 2.3825 um), one common x-centroid, same orientation, dummy at each end of the group |
| `ea_nmos_load` | `XM3`, `XM4` | 2.95 / 1 | 2.10 sigma | common_centroid+dummies | **A B B A** along row A, same construction (4 fingers of 0.7375 um each), dummies both ends |
| `fb_divider` | `XR1`, `XR2` | 0.5 / 340 | 1.71 sigma | common_centroid+dummies | **A B B A A B B A** serpentine segments (4 per arm, `r_segs`), common centroid in x, dummy `rhigh` segment at each end |
| `bias_n_group` | `XMB0`, `XMB1`, `XMS` | 1 / 1, 1.39 / 1, 2.2 / 0.95 | 3.15 sigma | interdigitated+dummies | **S B1 B0 | B0 B1 S** — each member split in two halves about one axis (a common centroid, which is stronger than interdigitation and no more expensive at three members), dummies both ends |
| `bias_p_group` | `XMBP`, `XMT`, `XM6` | 10 / 1, 10 / 1, 5.53 / 1 | 7.16 sigma | same_row_same_orientation | one row-B group, same orientation, no interleave, dummies both ends. **Directional note (brief §6): the S7 step is on the side that makes `XMT` stronger than `XMBP`; the group is drawn `XMBP XMT XM6` with `XMT` in the middle so any linear gradient weakens rather than strengthens it relative to the diode.** |
| `fvf_fold_n` | `XMA`, `XMB` | 5.79 / 0.5 | 17.9 sigma | same_row_same_orientation | adjacent, same orientation, in the row-A FVF group |
| `fvf_fold_p` | `XMCP`, `XMD` | 9.02 / 0.5 | 19.2 sigma | same_row_same_orientation | adjacent, same orientation, in the row-B FVF island |
| `pass_array` | `XMP` | 10 / 0.13 x 19 | — | any | 76 shared-diffusion fingers of 2.5 um (§3), its own nwell island and guard ring |
| `mim_*` | `XCFF`, `XCC`, `XCOUT` | 8, 54, 58 x4 | 133 / 794 / no bound | any | §4 |
| unmatched | `XM5`, `XMC` | | | any | placed where the routing wants them |

**Dummies.** One dummy device at each end of every group in rows A and B (`n_dummy = 1`), drawn
with the group's own L and finger width, all four terminals on the group's rail (vss for row A,
vdd for row B). They are declared in the LVS reference (A6).

## 2. Floorplan

Vertical stack of bands; the axis of symmetry is **local per matched pair** (brief §9: this cell
has no global differential axis).

```
   ______________________________________________________________________  <- vdd PIN (top edge)
  |  vdd  TopMetal1 strap  pwr_w = 4.0 um, full core width                |
  |            [ M5 pad + 12 TopVia1 + 48-cut Via4/3/2 riser ]            |
  |                                                    ______________     |   v
  |                                                   | XMP island  |     |   o
  |  (free channel for the vdd riser)                 | nwell+ntap  |     |   u
  |                                                   | 76 fingers  |     |   t
  |  ------------------------ vdd Metal1 rail ------------------------    |
  |  [ nwell island "quiet" + ntap ring ]     [ nwell island "fvf" ]      |   T
  |  d XM1a XM2a XM2b XM1b d | d XMBP XMT XM6 d      d XMC XMCP XMD d     |   M
  |  ---- channel: one Metal1 track per internal net (track_pitch) ----   |   1
  |  [ ptap ring, row A ]                                                 |
  |  d XM5 d | d XM3a XM4a XM4b XM3b d | d XMA XMB d | d XMS XMB1 XMB0 XMB0 XMB1 XMS d
  |  ------------------------ vss Metal1 rail ------------------------    |   s
  |                                                                       |   t
  |  passive band:                                                        |   r
  |   [ XR1/XR2 A B B A A B B A + XRB ]   [ XCC ]   [ XCOUT 2x2 array ]   |   a
  |                                       [ XCFF ]  [ common centroid ]   |   p
  |_______________________________________________________________________|  <- vout PIN (right)
      vss Metal1 rail (bottom edge)                              vss PIN (bottom)
```

- **`vout` sensing.** `lp_brk` (the divider top) taps the **vout TopMetal1 strap at the pin end**,
  not the pass drain: brief §4 makes that a 14x budget difference (0.126 Ohm -> 1.78 Ohm) and
  removes S2 from the metallisation's problem list entirely.
- **Thermal.** `XMP` dissipates 3.0 mW; the divider serpentines are at the **far diagonal corner**
  (bottom-left vs top-right). 1 K across `XR1<->XR2` costs 1.35 mV = 23 % of the S1 quarter margin
  (brief §9).
- **`gate` clustering.** `XMD` (row B, right), `XMS` (row A, right) and `XMP`'s gate bar (top
  right) are adjacent, and the `gate` track runs **beside the vout bus**, not in the rail channel:
  brief §3 measures gate-to-vout at 10–24x cheaper than gate-to-rail. Hard limit 100 fF to vout.
  This is why the bias NMOS group moved to the *right* end of row A even though `nbias`/`pbias`
  then run the length of the cell — those two nets have a 16 nF "budget", i.e. none (brief §10).
- **Wells.** Three nwell islands, all tied to vdd (brief §7): `XMP` alone (hot, 10 mA, fast dV/dt);
  "quiet" (`XMBP XMT XM1 XM2 XM6`); "fvf" (`XMC XMCP XMD`). Each gets a **closed** ntap guard ring
  (`ihp.cells.guard_ring`, `nwell`). Row A gets a closed ptap ring at vss, and a second ptap ring
  separates `XMP` from everything else. `XMC`'s and `XM1`/`XM2`'s bulks stay on `vdd` — the brief
  says explicitly that their Vsb is deliberate and a source-tied well would be a design change.
- **Expected outline** ~210 x 200 um (aspect ~1.05:1), against 005's 287.4 x 122.9 (2.34:1).
  Area is expected to grow ~15 %; the cost is measured and reported, not argued.

## 3. Power path — sized before drawing

Currents from brief §8 (measured): `I(vdd) = 10.0318 mA`, `I(XMP) = 10.0041 mA`, `vss` carries
only `27.7 uA` (the load returns off-cell). Limits from `SG13G2_os_process_spec.pdf` §2.15 via
`spicexplorer_signoff.current_density`.

**The one thing the brief could not fix, and what replaces it.** Brief §8 asks for a **1.1 um
Metal1 riser per shared S/D column**. That cannot be drawn: at `L = 0.13 um` the contacted column
pitch is ~0.55 um, so a column riser is capped near 0.34 um by M1.b — and every Metal1 width from
0.16 to 0.36 um gets the same flat 0.36 mA, so widening buys nothing. The brief's own option (ii)
(raise `nf` to >= 56) is rejected there because it changes `x_dut_xmp_m`. **It does not have to.**
The layout already folds `m = 19` into fingers; folding it into **4x as many, 4x narrower** fingers
leaves `w = 10 um, m = 19` untouched in `design.json`, leaves the extracted device at
`W = 190 um, L = 0.13 um` (which is what `--combine_devices` compares), and cuts the shared-column
current by 4. That is knob `xmp_nf_mult = 4`: **76 fingers of 2.5 um**, `I_finger = 0.1316 mA`,
`I_shared_column = 0.2633 mA`. What it does change is junction area/perimeter (less, not more:
more shared diffusion) — stated here, and measured in the pre/post scorecard.

Collection topology: **no horizontal Metal1 bar ever carries the load.** Each column's Metal1 stub
leaves the active (S upward, D downward), takes 2 Via1 into a Metal2 comb finger, and the comb's
spine (Metal2, `pwr_band_w = 6 um`) runs clear of the active and carries the total.

| net | segment | carries (mA) | drawn | limit (mA) | margin |
|---|---|---|---|---|---|
| `vdd` | TopMetal1 strap, top edge | 10.03 | TopMetal1 2.0 um | 30.0 | 0.33x |
| `vout` | TopMetal1 strap, right edge | 10.00 | TopMetal1 2.0 um | 30.0 | 0.33x |
| `vdd` | Metal5 -> TopMetal1 stitch | 10.03 | TopVia1 x12 | 16.8 | 0.60x |
| `vout` | Metal5 -> TopMetal1 stitch | 10.00 | TopVia1 x12 | 16.8 | 0.60x |
| `vdd`/`vout` | Metal5 landing pad | 10.0 | Metal5 6.0 um | 12.0 | 0.84x |
| `vdd`/`vout` | riser Metal4/3/2 pads | 10.0 | Metal{4,3,2} 6.0 um | 12.0 | 0.84x |
| `vdd`/`vout` | riser Via4 / Via3 / Via2 | 10.0 | 48 cuts each | 19.2 | 0.52x |
| `vdd`/`vout` | Metal2 comb spine over the pass array | 10.0 | Metal2 6.0 um | 12.0 | 0.84x |
| `vdd`/`vout` | Metal2 comb finger, per shared column | 0.263 | Metal2 0.3 um | 0.6 | 0.44x |
| `vdd`/`vout` | Via1, per shared column | 0.263 | Via1 x2 | 0.8 | 0.33x |
| `vdd`/`vout` | Metal1 column riser, per shared column | 0.263 | Metal1 0.34 um | 0.36 | 0.73x |
| `vout` | diffusion contacts, per shared column | 0.263 | Cnt x4 | 1.2 | 0.22x |
| `vdd` | cell Metal1 rail (row-B sources + XRB, Iq only) | 0.037 | Metal1 0.8 um | 0.8 | 0.05x |
| `vss` | cell Metal1 rail (Iq only) | 0.028 | Metal1 0.8 um | 0.8 | 0.03x |

**Every row of this table is re-derived by `layout/signoff.py` from the generator's own
`LayoutParams` and the drawn geometry — not retyped — and the `current_density` stage is a
blocker.** The table above is the plan; the REPORT carries the as-built one.

## 4. Passives

- **`XR1`/`XR2`** — `r_segs = 4` serpentine segments per arm at `res_pitch`, ordered
  **A B B A A B B A** (common centroid in x, both centroids at the block centre), plus one dummy
  `rhigh` segment at each end tied to `vss`. Same orientation, same segment length. Series-R
  merging in the LVS deck folds the segments back to one `l = 340 um` device.
- **`XRB`** — `rb_segs = 2` segments beside the divider, at the far end from `XMP` (its `tc1`
  sets every branch current, brief §9).
- **MIM block** (A3): `XCOUT` as a **2 x 2 common-centroid array** of the certified 58 um unit;
  `XCC` (54 um) and `XCFF` (8 um) as single certified units in the same block, **same orientation
  and one plate-connection side**. Plate orientation per brief §9 — kpex extracts the **Metal5
  bottom** plate and not the top, so the *insensitive* terminal goes on the bottom:
  `XCFF` bottom -> `lp_brk` (no budget) and top -> `fb` (27.9 fF); `XCC` bottom -> `ea_out`;
  `XCOUT` bottom -> `vss`.

## 5. Parameter list — the optimizer knobs

`LayoutParams` fields; sizes that LVS pins (W, L, m) are **not** here — they come from
`sizing.yaml`, which is the sizing of record (review F14). The table is **generated from the
dataclass**, and `gen_ldo.py` asserts at import that `BOUNDS` and `LayoutParams` name the same
knobs (review-003 F11): a knob that is not in both is a dead search dimension or an undocumented
one, and this cell has had each.

Every range below was **walked**: `layout/signoff.py --stages bounds` builds, current-density
checks, DRC-checks and LVS-checks the cell at *both* ends of every row, two KLayout jobs at a
time, and the stage fails if any endpoint does not come back clean (review-003 F2 — five of ten
values the previous table documented produced a cell that was not the certified circuit). The
run of record is in REPORT §4.

| knob | default | range | what it moves |
|---|---|---|---|
| `dev_gap` | 3.2 | 3–6 | x gap between devices in a row |
| `grp_gap` | 2 | 0–8 | extra gap between matching groups |
| `track_pitch` | 0.7 | 0.65–1.2 | channel Metal1 track pitch (0.38 pads -> 0.32 space) |
| `ch_margin` | 0.9 | 0.8–2 | clearance from the gate/drain bars to the first track |
| `rail_w` | 0.8 | 0.5–1.4 | vdd / vss Metal1 rail width (Iq only: 0.037 mA worst) |
| `rail_gap` | 1.6 | 1.4–2.5 | active edge -> rail centre |
| `ring_w` | 0.6 | 0.5–1.5 | guard-ring width (ntap / ptap) |
| `ring_gap` | 1.4 | 0.6–3 | device/pad bbox -> guard ring inner edge |
| `isl_gap` | 2 | 1.3–6 | Activ gap between two well islands (NW.b 0.62 + Act.b 0.21) |
| `n_dummy` | 1 | 1–2 | dummy devices at each end of a matched group |
| `pwr_w` | 4 | 1.64–8 | TopMetal1 power-strap width (TM1.a floor is 1.64) |
| `pwr_stitch` | 12 | 8–24 | TopVia1 cuts per Metal5 -> TopMetal1 stitch |
| `pwr_riser_vias` | 48 | 28–72 | Via2/3/4 cuts per riser level |
| `pwr_band_w` | 6 | 5.1–12 | Metal2 comb spine / riser pad width |
| `col_vias` | 2 | 1–4 | Via1 per pass-array S/D column |
| `mim_gap` | 3 | 2.5–8 | gap between MIM units |
| `res_pitch` | 2 | 1.9–3 | serpentine segment pitch (rhigh cell is 0.9 wide) |
| `blk_gap` | 6 | 4–15 | transistor stack -> passive band |
| `gpad` | 0.5 | 0.34–0.6 | gate-bar height (Metal1 + GatPoly): sets every gate's own C |
| `vss_ret_w` | 3 | 0.8–6 | bottom vss rail + its two edge risers (brief's 17 Ohm budget) |

Three ranges were **narrowed** rather than fixed, each because the limit is geometric and the
knob has somewhere else to go: `rail_w` stops at 1.4 (at 1.6 the channel runs out of free Metal2
columns for `vout` — and `vss_ret_w` is now the knob that sizes the return path, so `rail_w` no
longer has to), `res_pitch` at 1.9–3.0 (below 1.9 the `rhigh` cells' Metal1 end pads merge and the
divider extracts as four resistors instead of two; above 3.0 the block's own links reach the vdd
rail), `gpad` at 0.6 (0.8 gives 38 M1.b — the gate bars meet the S/D straps). Four failures were
**fixed in the generator** instead: `col_vias` 3–4 (the pass drain's via pad reached into the gate
bar — the gate stand-off is now derived from the pad, not the module constant), `ring_gap` 3.0
(the n-well ring's Metal2 riser fell off the end of the source comb spine and the pass device's
bulk extracted as an unnamed node), and `pwr_w` 8.0 / `vss_ret_w` 0.8 (the right cell edge is now
placed by TopMetal1 spacing to the XCOUT block, not by a constant margin).

## 6. Sensitivity -> concrete constraint

| brief row | budget | generator constraint |
|---|---|---|
| `gate` C | **12 fF to-rail**, step between 12 and 13 fF; to `vout` **26x cheaper** (+0.0197 vs +0.507 mV/fF), hard limit **40 fF** there | `XMD`/`XMS`/`XMP` clustered at the right; the `gate` track is the **top** channel track and is drawn on **Metal3** (`TRACK_LAYER`, review-003 F3 — on Metal1 the same run sits 0.6 um above the substrate and gate-only parasitics put S7 at 204.5 mV); no column of another net may run parallel to it on that layer, which the obstacle map now enforces **per layer** |
| `fb` C | **27.1 fF to-rail**, binds S8hi; coupling to `vdd` *buys* +0.122 dB/fF of PSRR. The brief's −0.111 °/fF is a **to-rail** coefficient, so the budget column is read to-rail throughout (review-003 F10) | `fb` is a **short** track: `ea_in_pair` is the FIRST group of row B, nearest the divider (review-003 F5 — as the second group the track measured 107 um, 53 % of the cell width and into the right half this row forbids) |
| `fb` leakage | **5.43 nA** | no antenna diode and no added diffusion on `fb` or `lp_brk`; the `fb` route is Metal1/Metal2 only and short enough not to attract an antenna fix |
| `ea_n` leakage | 12.5 nA, binds S6 | same rule on the `ea_n` track |
| `vout` R | **0.126 Ohm** if sensed at the pass drain (S2 = 10.2 mV, OUT), **2.76 Ohm at the pin** | `lp_brk` is escaped to the **right cell edge beside the `vout` pin** and labelled there, so the external short lands at the pin (A12) |
| `vdd` R | **2.31 Ohm**, and `vdd` + `vout` share one pooled rule: **10.34 x R(vdd) + 8.64 x R(vout) <= 23.83 mV** | `pwr_w = 4.0 um` TopMetal1 strap + 12 TopVia1 + 48-cut risers; nothing on Metal1. Hand model 0.598 + 0.556 Ohm = 10.98 mV, 46 % of the pool |
| `vss` R | **11 Ohm with XCOUT sharing the return (a step, S7), 16 Ohm for the active devices alone (S6)** | A **Kelvin cap return** (A10): XCOUT's bottom plates and the active devices meet only at the pin, so the 11 Ohm cliff does not apply; the active-only path is 4.9 Ohm of common riser, 14.3 Ohm worst-device |
| don't-cares | `nbias`, `pbias`, `ea_tail`, `lp_brk`, `x1`, `y`, `vout` C; `gate`/`fb`/`vref`/`lp_brk` R | used as the routing freedom: `nbias`/`pbias` run the full cell length so the bias group can sit next to `gate` |

## 6b. Open rulings — decisions this plan cannot take

These are measured conflicts between the spec box and the topology. Layout can report them; it
cannot resolve them.

1. **`gate`: certify the capacitance the cell already relies on** *(restated after review-004
   F3 — the previous wording, "12 fF cannot be reached at any legal sizing", asked for a topology
   decision on a number the assembled cell contradicts).* The 12 fF budget in the brief is a
   **gate-only** figure: it is measured by injecting capacitance on `gate` with every other
   parasitic zeroed, and in that experiment S7 steps between 12 and 13 fF. Swept **in situ** —
   a lumped `gate`→`vss` capacitor added to the full 186-card extraction and run through the
   frozen `tran_load_step` — there is no step at all:

   | added on `gate` | +0 | +20 | +40 | +45 | +50 | +80 fF |
   |---|---|---|---|---|---|---|
   | S7 undershoot (mV) | 127.560 | 137.404 | 147.293 | 149.623 | **151.899** | 167.900 |

   0.455 mV/fF, smooth, crossing the 150 mV line at **≈ +46 fF** — 134 % of the 34.45 fF the cell
   draws (reviewer: ≈ +45 fF, 0.44 mV/fF; reproduced here to the digit). So the question is not
   "the drawn `gate` capacitance fails S7". It is that **the cell's tt/27 margin depends on
   error-amp-path capacitance it acquired by accident**: `ea_o1` alone (44 fF to-rail, drawn, not
   designed) is what holds S7 at 89–107 mV instead of 289 mV at −40 °C (007 §3). Four options, and
   **option 3 is what is drawn today**:

   1. a smaller pass device or a different output stage — buys `gate` capacitance the cell does
      not need;
   2. a wider S7 spec;
   3. **certify the EA-path capacitance** — put a deliberate, sized capacitor on `ea_o1` in the
      netlist so the margin is a design parameter with a corner and a mismatch behaviour, instead
      of a layout artefact that changes every time the floorplan does (brief §3b);
   4. do nothing and accept that S7 is a layout-dependent number.

   **No option should be chosen before the corner and mismatch row** (experiments/007, item 2
   below): 007 shows S7 already leaves the box at **125 °C in four of the five corners
   post-layout** and S5 leaves it at ff/125 in *both* rows, so the binding constraint may not be
   `gate` at all — and item 2's control now shows the same `ea_o1` capacitance is what hides the
   brief's mismatch cliff, so the two rulings are one decision. **Owner's call**, and it is a
   certified-netlist decision, not a layout one.
2. **S7's undershoot margin leaves sub-sigma mismatch budgets on `ea_nmos_load` and
   `bias_p_group`, and the stakes are now measured.** The re-derived brief prices `ea_nmos_load`
   at 1.0 mV of ΔVT = **0.61 sigma** and `bias_p_group` at 1.2 mV = **1.07 sigma** of the PDK's
   own random mismatch. Common-centroid placement removes the *systematic* part only; nothing a
   layout can draw removes a sub-sigma random budget. What 007 §4 adds is the price, and it is
   **not** the price the brief implies. Injecting each class's offset into the extracted cell and
   bisecting for the box edge:

   | class | 1 sigma dVT | box edge | in sigma | first line out | one-sided tail |
   |---|---|---|---|---|---|
   | `ea_nmos_load` | 1.647 mV | **+15.0 mV** | 9.1 | S1 (dc offset) | 4e-18 % |
   | `bias_p_group` | 1.118 mV | **+20.0 mV** | 17.9 | S7 | 7e-70 % |

   So on the **drawn** cell neither class costs measurable yield at tt/27, and the reviewer's
   ~11 % / ~9 % estimate does not reproduce. 007 §4 also says why, with the control the claim
   needs: delete the extracted capacitance and the brief's cliff comes back exactly where the
   brief puts it (+2.0 mV of ΔVT on `XM3` gives S7 = 198.0 mV, out of the box), and **the single
   net `ea_o1` is enough to remove it again** (107.0 mV). The brief is right about the schematic;
   the drawn cell is a different circuit, and it is different by the same accidental capacitance
   ruling 1 is about. That makes the two rulings **one decision**: certify `ea_o1` (ruling 1
   option 3) and this margin becomes a design property with a corner behaviour; leave it
   accidental and the 9.1 sigma above is a number that moves with the floorplan. **Owner's call**;
   the numbers are at tt/27 only, and 007 §5 says the joint corner x mismatch question is open.
   The layout draws the best common-centroid available and reports the achieved sigma-multiple
   per class in REPORT §8.

   **Independent verdict on the mismatch dispute (`SIGNOFF.md`, round 5/6, quoted).** Both
   rulings above stand as owner rulings — the verifier does not resolve them, it re-measured the
   dispute they sit on. Its verdict: *"For the row of record, the designer is right."* The
   mismatch distances on the cell that was drawn, extracted and signed are **9.109 σ**
   (`ea_nmos_load`, +15.0 mV box edge / 1.6468 mV·σ) and **17.889 σ** (`bias_p_group`, +20.0 mV /
   1.1180 mV·σ); at ±3 σ every one of the eight spec lines holds with the same margins it has at
   nominal, and no measurable yield is lost to either class at tt/27 °C. *"The reviewer is right
   about the circuit the brief priced"*, and his arithmetic is not wrong anywhere: the **0.61 σ**
   and **1.07 σ** the reviewer quotes are `brief.json`'s own `headroom_sigma` fields verbatim (a
   budget-consumption ratio, not a distance to failure), and the **11 % / 9 %** are the one-sided
   tails of `out_of_box_dvt_mv`/σ (2.0/1.6468 = 1.2145 σ → 11.23 %; 1.5/1.118 = 1.3417 σ → 8.98 %)
   — both re-derived independently by the verifier and both correct **for the schematic-priced
   circuit**, where `out_of_box_dvt_mv` was measured with no layout capacitance. The disagreement
   was never arithmetic: the extraction changed the circuit, and the brief was not re-derived on
   the extracted cell. The verifier's own qualifier carries forward unchanged: the record row's
   mismatch margin rests on `ea_o1`'s 64 fF, which is drawn-by-accident capacitance, not a
   certified component — so ruling 1 (certify `ea_o1`) and this ruling remain one decision, and a
   redraw that changes `ea_o1`'s capacitance (A15 below is one candidate that could) must
   re-bisect both box edges rather than assume they hold.

3. **A15 — new open finding: the pooled `vdd`/`vout` dropout series-R budget is missed at the
   record row** (`SIGNOFF.md` §3.4, round 6). `brief.json`'s `dropout_pool` rule
   (`10.34 × R(vdd) + 8.65 × R(vout) ≤ 23.83 mV`, a quarter of the S4 margin) was met on the
   per-net hand model (§6.3: 0.598 Ω + 0.556 Ω, 10.98 mV, 46 % of the pool) but is **missed** on
   the stitched RC mesh — now the post-layout row of record — at **29.99 mV, 1.26× the
   allowance**. Each net's *individual* series-R budget is still met (`R(vdd)` 1.57 Ω of 2.31 Ω,
   `R(vout)` 1.52 Ω of 2.76 Ω); the shared pool they both draw on is not. S4 itself is not at risk
   — 134.66 mV against 200 mV, 65.3 mV of margin — this is a design-discipline miss, not a spec
   failure. The 3.00 Ω pooled at the record row is 85 % the shared **TopMetal1 strap** (0.59 Ω)
   and the **Via2–TopVia1 stack** (0.75 Ω) — neither divides by the 39 parallel pass-device
   columns the hand model assumes — and 4 % contacts. **Fix path**: widen the shared strap and/or
   multiply the via array; not drawn here (rule 7, report never fix). **Caution**: both candidate
   fixes touch metal at or near `ea_o1`, so a redraw must re-bisect the mismatch box edges in
   ruling 2 above, not assume the 64 fF and the 9.109 σ / 17.889 σ margins survive unchanged.

### 6b.1 Open items, consolidated

Carried from REPORT §10 and REVIEW.md, none of which changes a passing verdict at the record row:

- **A15** (above) — pooled dropout series-R budget miss; fix path is a strap/via redraw, which
  must re-bisect the mismatch edges in ruling 2.
- **F13** — `vref` labelled 71 µm inside the cell (not on its declared left edge) and `vdd` now
  carries two labels (Metal1 + TopMetal1) where one is expected; one label per pin, on the
  declared edge.
- **F18** — DRC has never been run with `--density` on this floorplan, so whether the twelve-rule
  waived set grew with the wider straps and the larger cell is unverified.
- **F15** — the MIM plate swap (`XCFF`/`XCC` bottom-plate assignment vs brief §9) is accepted and
  deferred to the next certified-netlist re-freeze; worth ≈ +0.3° of phase margin by hand.
- **Proper Monte Carlo** — the PDK's own `*_mismatch.lib` sections are not yet selected into
  `corners.yaml` (a schematic-lane change); the two sub-σ classes are currently priced by
  single-class injection only, not by distribution.
- **Corners × mismatch jointly** — 007 runs corners and mismatch as separate sweeps at tt/27 and
  at the corner grid respectively; neither party has run a class's mismatch offset *at* a failing
  corner (e.g. ss/−40 or ff/125), which is where both effects could compound.

## 7. What this plan does NOT do

Density/fill, sealring, pads, ESD, antenna diodes, inductance/EM-solver claims. The **scorecard
of record** is tt/27 C, as the pre-layout one is — but "post-layout is tt/27 only" is no longer
true of the cell: `experiments/007-post-layout-corners` measures the extracted netlist over the
five MOS corner bundles x -40/27/125 C with the schematic row beside it as the control, and
prices the two sub-sigma matching classes by injection (review-004 F16). A **Monte Carlo over the
PDK's own mismatch distributions is still not run**, and 007's README says why: selecting the
`*_mismatch.lib` sections would mean editing the certified `corners.yaml`, which belongs to the
schematic lane.

## 8. Gates

1. Build (deterministic; same params -> same GDS).
2. **Current density** (`spicexplorer_signoff.current_density`) — blocker, from the drawn geometry.
3. **DRC 0** with the density tables off (A7); every waiver written down with rule and count.
4. **LVS matched** against `lower(certified netlist) + declared dummies`, at the **record sizing**
   and at the **002 hand sizing** (`git show 76eddd6:…/sizing.yaml`).
5. **kpex** 2.5D, mode CC for the record, **and RC once for the report** — with
   `mesh_connected` and the anchor census in the sign-off record, and the stage refusing an RC
   row whose mesh is open (review-004 F26). Port labels carry a **pin-purpose polygon** so kpex
   emits a `[Pin]` node and the stitch anchors on the drawn port instead of a proxy (F25).
6. The **13 frozen benches** on the extracted netlist through `layout/postlayout.py`; per-net
   parasitic budget table against brief §2; every delta above the bench resolution explained.
7. `iterations/` snapshot of every round, failures included; the REPORT's Iterations table is
   generated, not typed.
