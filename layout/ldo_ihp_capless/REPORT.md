# Layout report — `ldo_ihp_capless` (IHP SG13G2), second drawing

**KIND: REPORT.** The layout of record is the generator `layout/gen_ldo.py` at
`LayoutParams()` defaults, reading its sizing from the certified binding. Plan and assumed
approvals: [`PLAN.md`](PLAN.md). Brief: [`BRIEF.md`](BRIEF.md). Every number below is a verdict
this branch produced; nothing is quoted from the first drawing except where it is the comparison.

**Verdict.** Current density 27/27 segments (worst 0.836x), **DRC 0**, **LVS matched at two
sizing points**, kpex CC 182 C / 21 R, and the cell's own **13 frozen benches on the extracted
netlist pass the whole S1-S8 box**. Signature: **none**. `layout/postlayout.py` now logs the
post-layout scorecard as one ledger row tagged `005_postlayout_post` with `evidence="awaiting"` —
a delivery claim whose signature is the verifier's own re-measure (rule 7), never the designer's.
`runs/` is git-ignored and per checkout, so that row does not travel with this commit: re-run
`layout/postlayout.py --pex <work>/pex` to reproduce it.

## 1. Outline, area, aspect

| | first drawing (005) | this drawing | |
|---|---|---|---|
| outline | 287.4 x 122.9 um | **202.50 x 208.55 um** | |
| aspect | 2.34 : 1 | **1.03 : 1** | ceiling 2:1 (PLAN A2) |
| bbox area | 35 317 um^2 | **42 231 um^2** | +19.6 % |
| pass device | 19 fingers of 10 um | 76 fingers of 2.5 um | same W = 190 um (PLAN A5) |
| dummies | none | 16 MOS + 2 rhigh, all tied | PLAN §1 |
| guard rings | periodic point taps every 12 um | 5 closed rings | 3 n-well islands + 2 p-substrate |

**What the +19.6 % bought**, in the order it was spent: the closed guard rings and the
`ring_gap`/`isl_gap` they need (three n-well islands that must not merge, NW.b 0.62 um), one tied
dummy at each end of each of the eight matching groups (`n_dummy = 1`, 16 devices), the
`pwr_band_w = 6 um` Metal2 combs and their via risers over the pass array, and a pass array 4x
longer in x. Against that, the floorplan went from one 287 um row to a square block, which is why
the aspect improved while the area grew. The largest single void is the top-left corner
(~60 x 70 um, left of the pass device and above the passive column); it is the first thing a
placement optimizer should take.

Render: [`../../experiments/005-layout/figs/ldo_ihp_capless.png`](../../experiments/005-layout/figs/ldo_ihp_capless.png)

## 2. Current density — the stage that did not exist before (review-002 B1)

`spicexplorer_signoff.current_density` over the budget list the **generator emits from its own
drawn geometry** (`gen_ldo.power_budgets`), run by `layout/signoff.py` as a **blocking** stage.
Limits: `SG13G2_os_process_spec.pdf` §2.15. Measured currents: I(vdd) = 10.0318 mA,
I(XMP) = 10.0041 mA, I(vss) = 27.7 uA (brief §8).

| net | segment | carries (mA) | drawn | limit (mA) | used/allowed |
|---|---|---|---|---|---|
| `vdd` | pass source column Metal1 riser (shared) | 0.263 | metal1 0.31 um | 0.36 | 0.731x |
| `vout` | pass drain column Metal1 riser (shared) | 0.263 | metal1 0.31 um | 0.36 | 0.731x |
| `vdd` | pass source column Via1 (shared) | 0.263 | via1 x4 | 1.60 | 0.165x |
| `vout` | pass drain column Via1 (shared) | 0.263 | via1 x4 | 1.60 | 0.165x |
| `vdd` | pass source column Metal2 finger | 0.263 | metal2 0.31 um | 0.62 | 0.425x |
| `vout` | pass drain column Metal2 finger | 0.263 | metal2 0.31 um | 0.62 | 0.425x |
| `vdd` | pass source Metal2 comb spine | 10.032 | metal2 6 um | 12.00 | 0.836x |
| `vout` | pass drain Metal2 comb spine | 10.004 | metal2 6 um | 12.00 | 0.834x |
| `vout` | pass drain diffusion contacts (shared column) | 0.263 | cnt x4 | 1.20 | 0.219x |
| `vdd` | vdd riser Metal2->Metal3 | 10.032 | via2 x48 | 19.20 | 0.522x |
| `vdd` | vdd riser Metal3->Metal4 | 10.032 | via3 x48 | 19.20 | 0.522x |
| `vdd` | vdd riser Metal4->Metal5 | 10.032 | via4 x48 | 19.20 | 0.522x |
| `vdd` | vdd Metal5->TopMetal1 stitch | 10.032 | topvia1 x12 | 16.80 | 0.597x |
| `vdd` | vdd riser Metal3 pad | 10.032 | metal3 6 um | 12.00 | 0.836x |
| `vdd` | vdd riser Metal4 pad | 10.032 | metal4 6 um | 12.00 | 0.836x |
| `vdd` | vdd riser Metal5 pad | 10.032 | metal5 6 um | 12.00 | 0.836x |
| `vout` | vout riser Metal2->Metal3 | 10.004 | via2 x48 | 19.20 | 0.521x |
| `vout` | vout riser Metal3->Metal4 | 10.004 | via3 x48 | 19.20 | 0.521x |
| `vout` | vout riser Metal4->Metal5 | 10.004 | via4 x48 | 19.20 | 0.521x |
| `vout` | vout Metal5->TopMetal1 stitch | 10.004 | topvia1 x12 | 16.80 | 0.596x |
| `vout` | vout riser Metal3 pad | 10.004 | metal3 6 um | 12.00 | 0.834x |
| `vout` | vout riser Metal4 pad | 10.004 | metal4 6 um | 12.00 | 0.834x |
| `vout` | vout riser Metal5 pad | 10.004 | metal5 6 um | 12.00 | 0.834x |
| `vdd` | cell Metal1 vdd rail (row-B sources + XRB, Iq only) | 0.037 | metal1 0.8 um | 0.80 | 0.046x |
| `vss` | cell Metal1 vss rail (Iq only) | 0.028 | metal1 0.8 um | 0.80 | 0.035x |
| `vdd` | vdd TopMetal1 strap (top edge) | 10.032 | topmetal1 2 um | 30.00 | 0.334x |
| `vout` | vout TopMetal1 strap (right edge + XCOUT bus) | 10.004 | topmetal1 2 um | 30.00 | 0.334x |

**Worst 0.836x, i.e. every segment has at least 1.2x headroom.** The first drawing was 12-28x
over on four of these.

**The one thing the brief could not fix, and what replaced it.** Brief §8 asks for a 1.1 um Metal1
riser per shared S/D column. At L = 0.13 um the contacted column pitch is ~0.51 um, so a riser is
capped near 0.30 um by M1.b — and every Metal1 width from 0.16 to 0.36 um gets the same flat
0.36 mA, so widening buys nothing. The brief's option (ii) (raise `nf` to >= 56) is rejected there
because it would change `x_dut_xmp_m`. It does not have to: the layout already folds `m = 19` into
fingers, and folding it into **4x as many, 4x narrower** fingers (`xmp_nf_mult = 4`, 76 fingers of
2.5 um) leaves `w = 10 um, m = 19` untouched in `sizing.yaml`, leaves the extracted device at
`W = 190 um, L = 0.13 um` — what `--combine_devices` compares — and cuts the shared-column current
from 1.053 mA to **0.263 mA**.

**That LVS matches does not make it electrically free, and it is not claimed to be.** The deck
compares W and L; a folded 76-finger device carries different junction area and perimeter, and a
different gate-bar length, from 19 long fingers. The measurement is column 3 of §6 — the drawn
geometry with **zero parasitics** — and it moves Iq by −2.23 uA, Vout by −0.6 mV and dropout by
−1.4 mV. By the layout lane's own rule a generator-legalized finger split is a **sizing change to
be re-certified at the projected geometry**, so that column *is* the projection, and whether
`decks/candidate/scorecard.json` should be re-certified on it is the owner's call, not this
report's (§10.2).

`xmp_nf_mult`'s documented range is **(3, 8)**: at 2 and 1 the shared column is 1.46x and 2.92x
over and the current-density stage blocks the build. A build forced through at `xmp_nf_mult = 1`
(bypassing the stage) extracts `gate` shorted to `vout` — recorded in §8 as an open item.

## 3. DRC

| | |
|---|---|
| engine | KLayout 0.30.5, IHP SG13G2 runset, `sg13g2_maximal` |
| flags | `--no_density` (PLAN A7: fill is a chip-assembly step and distorts the PEX of a bare cell) |
| result | **0 violations**, no waivers |
| second sizing point | **0 violations** (002 hand sizing) |

**"0 violations" is conditional on the density/fill tables being off** — that is the only rule
group switched off, and nothing else is waived.

## 4. LVS

| | record sizing | 002 hand sizing |
|---|---|---|
| reference | `lower(certified netlist) + declared dummies` | same |
| flags | `--combine_devices` | `--combine_devices` |
| result | **matched** | **matched** |

**The reference is derived, not typed (review-002 M7).** `layout/netlist_ref.py` parses
`circuits/ldo_ihp_capless/pdk/ihp-sg13g2/netlist.spice`, substitutes the sizing values, lowers the
`X` subcircuit calls to the primitive `M`/`R`/`C` cards the deck reads, folds a transistor's `m`
into `w`, and drops `rhigh`'s poly-body node. `gen_ldo.py` no longer carries a device table at
all: the same parse drives the placement. The only thing the reference *adds* is the layout's
**dummy devices**, and the emitter asserts every added card has all four terminals on one rail —
so a dummy card can only ever be electrically inert, while a real device's size still comes from
the certified file.

**Why the dummies are in the reference at all.** Measured, not assumed: the IHP LVS deck extracts
a fully shorted dummy MOS as a device, and `--purge --purge_nets` does **not** remove it. With the
dummy absent from the reference the compare fails; with it declared, it matches.

The second sizing point is the 002 hand point (`git show 76eddd6:.../sizing.yaml`), which differs
in 14 knobs including `x_dut_xmp_m` 19 -> 20 and `r_bias_l` 138.5 -> 100 um.

## 5. PEX

| mode | halo | C | R | benches |
|---|---|---|---|---|
| **CC** (the reported row) | tech default, SG13G2 8 um sidewall | 182 | 21 | 13/13 ran, 0 spec violations |
| **RC** (once, for this report) | same | 182 | 8 418 | 2/13 ran |

**RC does not converge in this cell's benches** and the reason is recorded rather than worked
around: eleven of thirteen abort with `Warning: singular matrix: check node xdut.n_25.n_2.17` —
dangling nodes inside the R mesh of the `rhigh` serpentines — and then
`The operating point could not be simulated successfully`. A `.nodeset` was not attempted. The
**two transient benches that do converge reproduce the CC row to the last digit** (undershoot
127.6 mV, recovery 0.2005 us, line step 55.63 mV), so no metric this cell is measured on moves
when the extracted wire resistance is put in. The RC netlist is kept at
`$LDO_WORK/layout/pex_rc/`.

**Extraction blind spots, stated not discovered.** The MIM capacitors are stripped from the GDS
before kpex (it cannot read `cap_cmim`) and spliced back as schematic devices, so **Metal5
bottom-plate coupling to the neighbourhood is extracted and top-plate coupling is not**;
n-well-to-substrate junction capacitance is in neither the extractor nor the model cards; and
couplings wider than the 8 um tech sidewall halo are dropped. There is no inductance.

## 6. Pre- vs post-layout scorecard, and where each delta comes from

The cell's own 13 frozen benches, all rows simulated through the frozen path
(`ldo.sim.run` + `ldo.metrics.promote`), `layout/postlayout.py`. Column 3 is a **schematic-only
what-if**: the certified subckt with exactly the split the layout draws (every matched device as
two half-width instances, the pass array as 76 fingers) and **no parasitics**, so the two
increments are separable.

| metric | pre-layout | + drawn device split (no parasitics) | + parasitics = post-layout | total delta |
|---|---|---|---|---|
| `v_out_v` | 1.2 | 1.199 | **1.199** | -0.000573 |
| `i_q_ua` | 36.28 | 34.05 | **33.81** | -2.472 |
| `load_reg_mv` | 0.028 | 0.026 | **0.026** | -0.002 |
| `line_reg_mv` | 0.059 | 0.057 | **0.056** | -0.003 |
| `v_dropout_mv` | 106.1 | 104.7 | **104.7** | -1.472 |
| `psrr_1k_db` | 69.95 | 70.03 | **70.11** | 0.1539 |
| `v_undershoot_mv` | 104.8 | 110.7 | **127.6** | 22.73 |
| `pm_loop_deg` | 72.42 | 72.35 | **68.76** | -3.657 |
| `pm_loop_lo_deg` | 72.38 | 72.31 | **68.73** | -3.651 |
| `pm_loop_hi_deg` | 72.31 | 72.23 | **68.64** | -3.665 |
| `loopgain_db` | 49.95 | 50.21 | **50.22** | 0.2789 |
| `ugf_loop_khz` | 836.5 | 809.9 | **771.9** | -64.59 |
| `gm_loop_db` | 6.427 | 6.396 | **7.972** | 1.546 |
| `ms_peak_db` | 7.15 | 7.07 | **9.059** | 1.909 |
| `psrr_1m_db` | 15.3 | 15.1 | **14.19** | -1.116 |
| `t_transient_us` | 0.1254 | 0.1407 | **0.2005** | 0.07513 |
| `vn_out_urms` | 366.4 | 369.7 | **360.4** | -6.01 |
| `v_line_pp_mv` | 51.62 | 51.63 | **55.63** | 4.016 |
| **spec box** | [1.176,1.224] / <=50 / <=5 / <=2 / <=200 / >=40 / <=150 / >=60 (x3) | | **0 violations** | |

Bench resolutions (brief §1): `v_out_v` 2e-6, `load_reg`/`line_reg`/`i_q` 0.001, `v_dropout` 2,
`psrr_1k` 0.001, `v_undershoot` 0.005, `pm_loop` 0.03. Everything below is above its floor except
`v_dropout` (-1.5 mV against a 2 mV floor: **no bound**).

**Every delta, with its cause:**

- **`i_q_ua` −2.47 uA** — **the device split, not the parasitics**: the schematic-only split row
  already gives 34.05 uA (−2.23 uA), and a second schematic-only what-if that changes *only* the
  serpentine segmentation (XR1/XR2 4 -> 8 segments, XRB 2 -> 5) accounts for −0.26 uA of the rest.
  A 0.5 um NMOS is not half of a 1 um one: LVS folds the common-centroid halves back together, the
  compact model does not. Iq moves **further under** its 50 uA bound.
- **`v_out_v` −0.6 mV** and **`v_dropout_mv` −1.5 mV** — the same split; both are fully present
  in the no-parasitics row. Dropout improves because 76 short fingers are a slightly stronger pass
  device than 19 long ones at the same W.
- **`v_undershoot_mv` +22.7 mV** — +5.9 mV from the split, **+16.9 mV from the parasitics**, and
  the parasitic part is `gate`. `gate` extracts to 47.5 fF in CC mode: 28.2 fF to the substrate,
  10.9 fF to `vout`, 6.0 fF to `vdd`, 0.3 fF to `vss` and ~2 fF to other signals. Brief §3 measures
  gate-to-`vout` at 10-24x cheaper than gate-to-rail, so the **to-rail-equivalent load is ~35 fF**,
  and at the brief's +0.386 mV/fF that is +13.5 mV; `x1` and `y` (< 17.7 fF each, +0.245 and
  +0.182 mV/fF) add ~+7 mV and `ea_o1` (64.9 fF, −0.181 mV/fF) gives ~−12 mV back. The linear
  coefficients therefore account for roughly half of the +16.9 mV; the balance is the slew
  mechanism the brief says is *not* a slope. S7 keeps **22 mV** of margin, and `gate` sits 21 %
  below the measured 60-65 fF step.
- **`pm_loop_deg` −3.66 deg** (and the two corners, −3.65 / −3.67) — **`fb`**, and the arithmetic
  is exact: 34.0 fF at the brief's −0.111 deg/fF is −3.77 deg. The split contributes −0.07 deg.
  S8 keeps 8.8 deg.
- **`ugf_loop_khz` −64.6 kHz** — −26.6 kHz split, −38 kHz parasitics (`ea_o1` 64.9 fF on the
  Miller node). No spec line.
- **`t_transient_us` +0.075 us** — the recovery time of the same `gate` slew as the undershoot.
- **`gm_loop_db` +1.55**, **`ms_peak_db` +1.91** — the loop's gain margin and closed-loop peaking
  both rise with the added phase lag; no spec line on either.
- **`psrr_1k_db` +0.15**, **`loopgain_db` +0.28**, **`load_reg_mv` −0.002**, **`line_reg_mv`
  −0.003** — all improvements, all within one or two resolution steps, all present in the split
  row: the split, not the layout.
- **`psrr_1m_db` −1.12**, **`v_line_pp_mv` +4.0**, **`vn_out_urms` −6.0 uVrms** — high-frequency
  and noise columns, no spec line; the first two are parasitic, the last is the split.

## 7. Per-net parasitic budget (brief §2, CC mode, 8 um halo)

| net | budget (fF) | hard limit | 005 spent | this cell | used/allowed |
|---|---|---|---|---|---|
| `gate` | 29.3 | **step 60-65 fF** | 28.4 | **47.5** (~35 to a rail) | 1.62x raw / **1.19x** to-rail |
| `fb` | 27.9 | ~125 fF (S8 = 60 deg) | 19.2 | **34.0** | **1.22x** |
| `x1` | 46.1 | - | 11.5 | < 17.7 | < 0.38x |
| `y` | 62.0 | - | 10.6 | < 17.7 | < 0.29x |
| `ea_o1` | 627 | - | 44.7 | 64.9 | 0.10x |
| `ea_out` | 631 | - | 22.6 | 26.4 | 0.04x |
| `ea_n` | 980 | - | - | 17.7 | 0.02x |
| `pbias` | no bound | - | 13.9 | 25.8 | - |
| `ea_tail` | no bound | - | 12.1 | 19.4 | - |
| `lp_brk` | no bound | - | 16.4 | 18.2 | - |
| `nbias` | no bound | - | - | 31.4 | - |
| `vout` | no bound | - | 72.0 | 82.7 | - |
| `vdd` | no bound | - | 43.3 | 159.2 | - |

**Two nets are over budget and neither is fixed here; both are explained.** The budget is 25 % of
the pre-layout margin, not a bound.

- **`gate` 47.5 fF (1.62x).** Two causes, both deliberate. (a) `xmp_nf_mult = 4` makes the pass
  device's gate bar 4x longer in x (10 um -> 40 um of Metal1 + poly over the array) — that is the
  price of the current-density fix, and it is the price of B1 being closed. (b) The cell is
  larger, so the `gate` track and its Metal3 hop over the vout comb are longer. Against the
  quantity the brief actually measured — capacitance **to a rail** — the load is ~35 fF, 1.19x the
  budget and 0.58x of the 60 fF step, and the measured S7 keeps 22 mV. The brief's own escape was
  used: the `gate` track is the top channel track, directly under the vout bus, and 10.9 fF of the
  total is gate-to-`vout` at 1/10 to 1/24 of the rail coefficient.
- **`fb` 34.0 fF (1.22x).** The divider is at the bottom-left and `XM1`'s gate is in the quiet
  n-well island at the left of row B, which is the shortest route available in a square floorplan;
  the growth over 005's 19.2 fF is track length plus the `fb` plate of `XCFF`. Measured cost:
  −3.66 deg of phase margin, against 12.4 deg of pre-layout margin. S8 keeps 8.8 deg.

**Series resistance.** RC mode extracts 8 418 wire resistors; the mesh cannot be reduced to one
number per net without a solve, and the benches that would show it (dropout at 13.2 mV/Ohm, load
regulation at 9.9 mV/Ohm) do not converge on the RC netlist. The bound that *is* measured: the two
transient benches reproduce the CC row exactly (§5), and the `vout` sense is Kelvin by
construction — the `vout` **pin label sits on the TopMetal1 strap at the right edge**, so the
extraction's pin node is the output pin and not the pass drain (brief §4: 0.126 Ohm -> 1.78 Ohm,
a 14x budget difference that is a floorplan decision, not a width).

## 8. Matching — what was drawn, per class

| class | brief pattern (headroom) | drawn |
|---|---|---|
| `ea_in_pair` `XM1`,`XM2` | common_centroid+dummies (1.85 sigma) | **A B B A** in row B: each member 2 half-width instances, one common x-centroid, same orientation, tied dummy each end |
| `ea_nmos_load` `XM3`,`XM4` | common_centroid+dummies (2.10 sigma) | **A B B A** in row A, same construction |
| `fb_divider` `XR1`,`XR2` | common_centroid+dummies (1.71 sigma) | **[A B B A] x4** = 16 serpentine segments, both centroids at the block centre, one tied dummy segment each end; one arm links on Metal1, the other on Metal3 |
| `bias_n_group` `XMB0`,`XMB1`,`XMS` | interdigitated+dummies (3.15 sigma) | **S B1 B0 | B0 B1 S** — every member split about one axis, i.e. a common centroid for all three, dummies both ends |
| `bias_p_group` `XMBP`,`XMT`,`XM6` | same_row_same_orientation (7.16 sigma) | one row-B group, `XMT` **between** `XMBP` and `XM6`, so a linear gradient weakens `XMT` relative to the diode — brief §6 measures the S7 step only on the side that strengthens it |
| `fvf_fold_n` `XMA`,`XMB` | same_row_same_orientation (17.9 sigma) | adjacent, same orientation, dummies at the group ends |
| `fvf_fold_p` `XMCP`,`XMD` | same_row_same_orientation (19.2 sigma) | adjacent, same orientation, dummies at the group ends |
| `pass_array` `XMP` | any | 76 shared-diffusion fingers, own n-well island, own n-tap ring, own p-substrate ring |
| `mim_cout` `XCOUT` | any (no bound) | **2 x 2 common-centroid array** of the certified 58 um unit about a central TopMetal1 top-plate spine, right column mirrored so the block has one plate-connection side per terminal |

**Deviations from the plan and the brief, both recorded:**

1. **No MIM dummy ring** (PLAN A3). Brief §6 gives `mim_cout_unit` **no bound**, `mim_feedforward`
   133 sigma and `mim_miller` 794 sigma of headroom, and a ring of 58 um units would roughly triple
   the block. The four units are drawn as a common-centroid array instead. A single common unit for
   all three capacitors is arithmetically impossible at the certified sizes: the plate areas are
   64 / 2916 / 13456 um^2, so a common unit is 2 um and needs ~3400 tiles; any coarser unit rounds
   XCC or XCOUT by >= 0.8 %, which is a sizing change, not a layout choice.
2. **The MIM plate assignment follows the certified card, not brief §9.** `cap_cmim` is a
   *polarised* device class in the LVS deck: `nodes[0]` is the top (PLUS) plate and `nodes[1]` the
   Metal5 bottom. Brief §9 asks for the sensitive terminal on top (kpex does not extract the top
   plate), which for `XCFF` and `XCC` is the opposite of the certified card — and LVS said so
   (round it05: CFF and CC mismatched with `fb`/`lp_brk` and `ea_o1`/`ea_out` swapped). Swapping the
   plates moves the bottom-plate parasitic to the other node, i.e. it is a **design change**. The
   generator now reads the assignment off the certified card; the brief's preference is a re-sizing
   question, not a layout one.
3. **Routing is not matched half-for-half.** The channel allocator finds each terminal a free
   column, so the two halves of a common-centroid pair do not get identical routing topology. The
   devices are matched; the routing is not. Not measured.

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


Every round is `build -> current density -> DRC -> LVS`, snapshotted before the generator was
touched again; `it09` adds PEX and is the layout of record. Three dead ends are worth carrying
forward:

**A Metal2 short is as invisible as a Metal1 one.** it02 -> it03: the pass device's gate left its
island on a Metal2 column at the array's left edge, which is exactly where the `vout` Metal2 comb
spine runs. Two overlapping Metal2 shapes merge into one legal polygon, DRC reported 0, and the
extracted netlist said `gate|vout`. The obstacle map the first drawing built for Metal1 does not
cover the power combs, and the fix was structural — the gate hops the spine and both guard rings
on **Metal3**. The same round found the divider comb tapped twice by a `to_track` stub walking
along the resistors' port row (`XR2` extracted as 212.5 + 85 + 42.5 um with `fb` in the middle),
because the `rhigh` end pads were not claimed either.

**The chase around the MIM pads (it04 -> it08) was five rounds of the same lesson.** A 1.3 um
plate pad with a 3x3 Via1 array cannot share the 0.6 um column pitch with a routing pad: every
patch (skip the second stack, then a 0.95 um minimum shift, then 1.4 um) moved the violation
rather than removing it. What worked was structure: the plate pad is **claimed in the obstacle
map** so the allocator refuses those columns outright, and `mim()` hands the caller a Metal1 arm
2 um clear of the plate. The first version of that arm pointed *outward* and landed on the
cell's left-edge `vss` strap — DRC 0, `ea_o1|fb|vss` — which is the same lesson a third time.

**`postlayout.py`'s default `--pex` path is the *first* drawing's work dir.** Re-running it
without `--pex $SX_SCRATCH/ldo-lay/work/pex` silently re-measured the 2026-09-04 morning
extraction and wrote the first drawing's row into `experiments/005-layout/out/scorecard.json`
(undershoot 113.9 mV) — a stale artefact that looks exactly like a fresh one because every stage
succeeded. `hits[-1]` on an `rglob` is a sort order, not a freshness check. The run dir is now
named in every reproduce line in this report.

**The PDK's own guard-ring cell is not DRC-clean.** `ihp.cells.guard_ring` violates Cnt.b
(min. Cont space 0.18 um) at every corner; measured on a standalone ring at seven width/spacing
combinations, 2-4 hits each. `Builder.ring` draws the ring instead, putting the corner contact
*on* the corner and starting each side one pitch away, so every neighbour pair is axis-aligned.

## 10. What stays open

1. **No independent review.** `layout-reviewer` has not rebuilt or re-measured any of this. The
   post-layout row is logged `evidence="awaiting"`.
2. **The drawn geometry is not the certified geometry, and nothing has re-certified it.** The
   pass array is 76 fingers where the certified card is 19, and every matched device is drawn as
   two half-width instances. LVS matches (W and L are unchanged) but the schematic-only what-if
   in §6 measures the difference at **−2.23 uA of Iq, −0.6 mV of Vout, −1.4 mV of dropout with no
   parasitics at all**. The lane's rule is that a generator-legalized finger split is a sizing
   change to be re-certified at the projected geometry; §6 column 3 is that projection, but
   `decks/candidate/scorecard.json` still records the unsplit device. Re-certifying is an owner
   decision (it re-freezes the candidate decks), so it is filed here rather than done.
3. **`gate` and `fb` are over budget** (1.19x to-rail and 1.22x). Both inside their hard limits and
   the spec box; both are the first thing to attack if the corner run needs the margin.
4. **Corners and Monte Carlo are not re-run post-layout.** Everything here is tt / 27 C, as the
   pre-layout row is. 003 §3 already shows S5 and S7 binding at corners *before* layout, and this
   drawing adds 22.7 mV of undershoot, so ss/−40 gets worse, not better. That is the next run.
5. **`xmp_nf_mult = 1` extracts `gate` shorted to `vout`.** The current-density stage rejects that
   knob value anyway (1.46x over on the shared column at 2, 2.92x at 1) and `BOUNDS` now says
   (3, 8) — but the generator is only *verified* at `xmp_nf_mult = 4`, at two sizing points. The
   other knobs' ranges in `BOUNDS` are likewise unverified over their whole span.
6. **RC-mode benches do not converge** (§5). A `.nodeset` was not tried.
7. **Routing is not matched half-for-half** (§8.3), and no mismatch Monte Carlo has been run on
   this drawing — the brief's own conclusion is that the three tight classes sit inside 3 sigma of
   the PDK's *random* mismatch, which layout cannot fix.
8. **Density/fill and sealring are out of scope** (PLAN A7), so the DRC-0 result is conditional on
   the density tables being off.

## Summary

**What was done.** Second drawing of `ldo_ihp_capless`, from a plan written against the measured
layout brief. Closes the four findings the first drawing was rejected on: the 10 mA path is on
TopMetal1 with a Metal2 comb and count-driven via risers and every segment is scored by a blocking
current-density stage (B1); matched classes are common-centroid or same-row by measured headroom
with tied dummies and five closed guard rings (m3); the LVS reference is derived from the certified
netlist and `gen_ldo.py` no longer holds a device table (M7); and the Metal1 obstacle map has its
own regression case, which the sign-off driver runs first and blocks on (M8) — the Metal2 class
that bit this round is fixed by a Metal3 bypass and still has no such case. DRC 0, LVS matched at
two sizing points, kpex CC + RC, 13/13 benches PASS, nine snapshotted rounds with before|after
diffs.

**Assumptions.** PLAN §0 lists nine (pin sides, 2:1 aspect ceiling, the cap plan and its deviation,
the strap plan, dummies as declared devices, density off, the GDS not committed, the gdsfactory
interpreter). One more was taken during the work and is in §8: the MIM plate
assignment follows the certified card rather than the brief. `xmp_nf_mult = 4` is deliberately
*not* filed as an assumption — the drawn split is a measurable device change (§2, §6 column 3) and
the re-certification question is open (§10.2).

**Errors / setbacks / gotchas.** §9 and §10.5. The three that generalise: a Metal2 power spine is
as good at hiding a short as a Metal1 gate bar, so an obstacle map that only covers Metal1 is half
a guard; a via array under a fat pad cannot share a routing pitch, and patching the pitch moves the
violation rather than removing it; and `ihp.cells.guard_ring` is not DRC-clean at its corners.

**Next steps.** An independent `layout-reviewer` pass; the post-layout corner + Monte-Carlo run
(item 3), which is where the 22.7 mV of undershoot will be paid for; then, if the margin is needed,
`gate` — the knob is `xmp_nf_mult`, and the trade against the current-density margin is one build.
