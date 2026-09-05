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
| A4 | **Strap plan**: TopMetal1 `vdd` along the top edge and `vout` along the right edge, `pwr_w = 2.0 um` (TM1.a floor is 1.64); each stitched to a Metal5 landing pad with **12 TopVia1**, and down to the pass array through **48 cuts per level** on Via2/3/4 and 2 Via1 per S/D column | brief §8 | See §3. The Metal1 rails keep `rail_w = 0.8 um` because after this change **no Metal1 in the cell carries more than 0.27 mA**. |
| A5 | **The pass array is redrawn with 4x the fingers (`x_dut_xmp_nf_mult = 4`: 76 unit fingers of 2.5 um, total W unchanged at 190 um)** | not in the brief; see §3 | This is the only way the shared-diffusion column riser gets legal. **A5 originally filed it as "not a sizing change" because `w`/`m` were untouched; review F19 overturned that and the ruling is adopted** — see §0.1. The knob now lives in `sizing.yaml`, the certified netlist draws the unit fingers, and the benches simulate them. |
| A6 | **Matched-row dummies are real, fully-tied devices declared in the LVS reference** (G=S=D=B on one rail) | none | Measured: the IHP LVS deck extracts a fully shorted dummy MOS as a device and `--purge --purge_nets` does **not** remove it (probe log `lvs_d2`/`lvs_d2p`); LVS matches only when the dummy is in the reference. The reference is therefore `lower(certified netlist) + dummy cards`, and the emitter asserts every added card has all four nodes on one rail — a divergence in a *real* device still fails. |
| A7 | **Density / fill and sealring are out of scope**; DRC runs with the density tables off by default (`--density` re-enables them) and the REPORT names the flag | 005 precedent, `review-002` m1 | Fill is a chip-assembly step and distorts the PEX of a bare cell. |
| A8 | **The GDS is not committed**; the layout of record is `layout/gen_ldo.py`. The render PNG *is* committed at `experiments/005-layout/figs/ldo_ihp_capless.png` | 005 precedent + `.gitignore` | An 845 kB binary can only drift from the generator. |
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
  |  vdd  TopMetal1 strap  pwr_w = 2.0 um, full core width                |
  |            [ M5 pad + 12 TopVia1 + 48-cut Via4/3/2 riser ]            |
  |                                                    ______________     |   v
  |                                                   | XMP island  |     |   o
  |  (free channel for the vdd riser)                 | nwell+ntap  |     |   u
  |                                                   | 76 fingers  |     |   t
  |  ------------------------ vdd Metal1 rail ------------------------    |
  |  [ nwell island "quiet" + ntap ring ]     [ nwell island "fvf" ]      |   T
  |  d XMBP XMT XM6 d | d XM1a XM2a XM2b XM1b d      d XMC XMCP XMD d     |   M
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
`sizing.yaml`.

| knob | default | range | what it moves |
|---|---|---|---|
| `dev_gap` | 3.2 | 3.0–6.0 | x gap between devices in a row |
| `grp_gap` | 2.0 | 0.0–8.0 | extra gap between matching groups |
| `track_pitch` | 0.7 | 0.65–1.2 | channel Metal1 track pitch |
| `ch_margin` | 0.9 | 0.8–2.0 | gate/drain bar -> first track |
| `rail_w` | 0.8 | 0.5–2.0 | vdd / vss Metal1 rail width |
| `rail_gap` | 1.6 | 1.4–2.5 | active edge -> rail centre |
| `ring_w` | 0.6 | 0.5–1.5 | guard-ring width (ntap / ptap) |
| `ring_gap` | 1.2 | 0.6–3.0 | device bbox -> guard ring |
| `n_dummy` | 1 | 0–2 | dummy devices at each end of a matched group |
| `pwr_w` | 2.0 | 1.64–6.0 | TopMetal1 strap width |
| `pwr_stitch` | 12 | 8–24 | TopVia1 cuts per strap stitch |
| `pwr_riser_vias` | 48 | 28–72 | Via2/3/4 cuts per riser level |
| `pwr_band_w` | 6.0 | 5.0–12.0 | Metal2 comb spine / riser pad width |
| `xmp_nf_mult` | 4 | 1–8 | fingers per `m` unit of the pass device |
| `col_vias` | 2 | 1–4 | Via1 per pass-array S/D column |
| `mim_gap` | 3.0 | 2.5–8.0 | gap between MIM units |
| `res_pitch` | 2.0 | 1.8–4.0 | serpentine segment pitch |
| `r_segs` | 4 | 2–8 | divider segments per arm (even, for the ABBA pattern) |
| `rb_segs` | 2 | 1–6 | bias-resistor segments |
| `blk_gap` | 6.0 | 4.0–15.0 | transistor stack -> passive band |
| `tap_pitch` | 12.0 | 6.0–18.0 | tie spacing along a ring segment |

## 6. Sensitivity -> concrete constraint

| brief row | budget | generator constraint |
|---|---|---|
| `gate` C | **29.3 fF**, step at 60–65 fF; to `vout` 10–24x cheaper, hard limit 100 fF | `XMD`/`XMS`/`XMP` clustered at the right; the `gate` track is the **top** channel track, immediately under the vout bus; no Metal2 column of another net allowed to run parallel to it (the existing obstacle map already enforces one net per column) |
| `fb` C | **27.9 fF**, binds S8; coupling to `vdd` *buys* +0.122 dB/fF of PSRR | `fb` is a **short** track: the divider is placed so `fb` reaches `XM1`'s gate without crossing the cell; it is kept off the right half (vout/gate edges) entirely |
| `fb` leakage | **5.43 nA** | no antenna diode and no added diffusion on `fb` or `lp_brk`; the `fb` route is Metal1/Metal2 only and short enough not to attract an antenna fix |
| `ea_n` leakage | 12.5 nA, binds S6 | same rule on the `ea_n` track |
| `vout_all` R | 0.126 Ohm if sensed at the pass drain, **1.78 Ohm at the pin** | `lp_brk` taps the TopMetal1 vout strap at the **pin** end (§2) |
| `vdd` R | 1.77 Ohm (dropout, 13.2 mV/Ohm) | TopMetal1 strap + 12 TopVia1 + 48-cut risers; nothing on Metal1 |
| `vss` R | 17 Ohm (PSRR, −0.44 dB/Ohm) | Metal1 rail plus the ptap ring in parallel; only 27.7 uA |
| don't-cares | `nbias`, `pbias`, `ea_tail`, `lp_brk`, `x1`, `y`, `vout` C; `gate`/`fb`/`vref`/`lp_brk` R | used as the routing freedom: `nbias`/`pbias` run the full cell length so the bias group can sit next to `gate` |

## 7. What this plan does NOT do

Density/fill, sealring, pads, ESD, antenna diodes, corner/Monte-Carlo re-measurement post-layout,
inductance/EM-solver claims. The post-layout row is tt/27 C, as the pre-layout one is.

## 8. Gates

1. Build (deterministic; same params -> same GDS).
2. **Current density** (`spicexplorer_signoff.current_density`) — blocker, from the drawn geometry.
3. **DRC 0** with the density tables off (A7); every waiver written down with rule and count.
4. **LVS matched** against `lower(certified netlist) + declared dummies`, at the **record sizing**
   and at the **002 hand sizing** (`git show 76eddd6:…/sizing.yaml`).
5. **kpex** 2.5D, mode CC (and RC once for the report if it converges).
6. The **13 frozen benches** on the extracted netlist through `layout/postlayout.py`; per-net
   parasitic budget table against brief §2; every delta above the bench resolution explained.
7. `iterations/` snapshot of every round, failures included; the REPORT's Iterations table is
   generated, not typed.
