# Sign-off — `ldo_ihp_capless`, round 5 (`50442a8`)

**KIND: REVIEW.** Independent sign-off under rule 7 (designer ≠ verifier). Every number below was
re-measured by the verifier from raw artefacts on this checkout; nothing is copied out of
`REPORT.md`, `scorecard*.json` or the designer's ledger rows. The claims answered are the five put
to this pass; each is **SIGNED** or **REFUSED with numbers**.

## 0. Environment, and the gate

| item | value |
|---|---|
| repo / branch | `agentic-design-ldo-ihp130` @ `50442a8`, `feat/001-reference` |
| simulator | native **ngspice-45** (`$HOME/local/bin/ngspice`, KLU build) via the platform `NGSpice_Wrapper`; `OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=1` |
| PDK | **IHP SG13G2**, IHP-Open-PDK `62c1d640dc1c91f57bc1a8e4e08e537a7a105ae8`; PSP 103.6, corner libs rev 200310 — the pin `doc/environment.md` records, i.e. the baseline's own revision |
| layout engines | **KLayout 0.30.5** (SG13G2 `sg13g2_maximal` runset, DRC + LVS), **kpex** 2.5D (`~/miniconda3/envs/pex`), generator on `gdsfactory` (`~/miniconda3/envs/ai_env`) |
| work dirs | `$SX_SCRATCH/ldo-verify/…` — nothing outside the repo was written into the repo, nothing under `/tmp` |
| **the gate** | `python -m ldo.metrics --check` → **"reference reproduces its certified scorecard"**, 10/10 benches `ok`. A sign-off in a repo where `make check` fails is void; it does not. |

`make lint` was **red on exactly two rows** before this pass (`decks/reference/scorecard.json` and
`decks/candidate/scorecard.json`: *"unverifiable — no signed ledger row backs this provenance
block"*) and is **green after it** — see §1. Those two rows *are* this signature.

The pass leaves **four** `evidence="signed"` ledger rows, all `author = ldo-design-agent`,
`verified_by = signoff-verifier`, `corner='tt'`, `exp=''`:

| ledger row | what it signs | § |
|---|---|---|
| `reference_certify` | the frozen analog-db reference decks reproduce their certified scorecard | §1 |
| `candidate_certify` | the frozen candidate decks reproduce theirs, on the drawn device set | §1 |
| `verify_postlayout_post` | the **CC** extraction — the ideal-metal comparison row | §2 |
| `verify_postlayout_rc` | the **stitched RC** extraction — the **post-layout row of record** | §3 |

## 1. Claim 1 — the certified decks reproduce, and are signed — **SIGNED**

Method (`verify/verify_decks.py`, committed beside this file): for each `frozen:` dir, rebuild
**every** bench from that dir's own `design.json` through `ldo.dut.Design`, assert the generated
bytes equal the committed `*.spice`, re-derive `decks.sha256` and assert it equals the digest the
scorecard's `raw_sha` names, simulate all of them through the frozen path
(`ldo.sim.run` + `ldo.metrics.promote`), and compare every scorecard column. Then re-derive the
whole `provenance` block with `spicexplorer_harness.provenance()` **over the verifier's own
measured card** and compare it key by key — equal `computation_hash` means identical scorer bytes,
identical deck bytes *and* identical numbers.

| | `decks/reference` | `decks/candidate` |
|---|---|---|
| benches rebuilt from `design.json` | 10 | **13** |
| deck byte mismatches | **none** | **none** |
| `decks.sha256` re-derives | ✅ | ✅ |
| bench status | 10/10 `ok`, no NaN | **13/13 `ok`, no NaN** |
| scorecard columns compared | 33 | **49** |
| columns differing (1e-9 rel) | **0** | **0** |
| `provenance` block re-derives | ✅ (`script_sha 75d0a667…`, `raw_sha 38d97cfc…`) | ✅ (`script_sha 75d0a667…`, `raw_sha fb9810c2…`) |
| spec box | 4 violations — the reference is the *yardstick*, not a candidate (S1 1.60913 V, S3 4.32 mV, S5 758.695 µA, S8 46.3897°) | **0 violations — the whole S1–S8 box** |

The candidate's re-measured row, at tt / 27 °C, digit for digit against
`decks/candidate/scorecard.json`:

| | S1 `v_out_v` | S2 `load_reg_mv` | S3 `line_reg_mv` | S4 `v_dropout_mv` | S5 `i_q_ua` | S6 `psrr_1k_db` | S7 `v_undershoot_mv` | S8 `pm_loop_deg` (1 mA / 0.1 mA / 10 mA) |
|---|---|---|---|---|---|---|---|---|
| box | [1.176, 1.224] | ≤ 5 | ≤ 2 | ≤ 200 | ≤ 50 | ≥ 40 | ≤ 150 | ≥ 60 |
| certified | 1.199499 | 0.026 | 0.056 | 104.671 | 33.80539 | 70.00703 | 115.057 | 72.5064 / 72.47302 / 72.41834 |
| **re-measured** | **1.199499** | **0.026** | **0.056** | **104.671** | **33.80539** | **70.00703** | **115.057** | **72.5064 / 72.47302 / 72.41834** |
| Δ | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**Signature.** Two `evidence="signed"` ledger rows, `verified_by=signoff-verifier`,
`author=ldo-design-agent`, carrying the re-derived hash block and every scorecard column:

```
2026-09-05T08:36:29  reference_certify  corner='tt' exp=''
2026-09-05T08:36:48  candidate_certify  corner='tt' exp=''
```

`make lint` after them: **`LINT: all invariants hold`** (frozen, frozen_clean, experiments,
paper_index, journal, spec_sync, denylist, gitignore, package_importable, pack,
verdict_provenance, evidence_signoff, **scorecard_recompute**, deck_rebuild, spec_reference).

**Caveat, and it is the harness's own:** `runs/` is git-ignored and per checkout, so the green
lint travels with *this* checkout, not with the commit. The lint's own fix text says so.

## 2. Claim 2 — the capacitance-only (CC) extraction — **SIGNED (as the ideal-metal comparison row)**

> **Label changed mid-pass.** Claim 2 was put as *"the CC row is the post-layout row of record"*.
> The coordinator's round-3 platform result (below, §3) moved the record to the stitched **RC**
> row, which this verifier re-ran and signed. Everything in this section still holds and the CC
> row is still signed — it is now the **ideal-metal comparison row**: the same layout with every
> wire resistance set to zero. Read it against §3, not instead of it.

Rebuilt and re-run end to end by the verifier, into `$SX_SCRATCH/ldo-verify/layout`, two KLayout
jobs at a time, `layout/signoff.py --stages guards,build,cd,drc,lvs,pex --pex-mode CC`:

| stage | verifier's result | REPORT.md |
|---|---|---|
| router guards (`test_builder.py`) | passed, 0 failures | blocking stage, passes |
| build (`gen_ldo.py`, `LayoutParams()` defaults) | bbox (−73.50, −135.50)–(137.64, 74.15), **area 44 266 µm²** | 44 266 µm² ✅ |
| current density | **30/30 checked, 0 violations, worst 0.836×** | 30/30, worst 0.836× ✅ |
| DRC (`sg13g2_maximal`, `--no_density`) | **0 violations**, `violations_per_rule {}` | 0 ✅ |
| LVS (`--combine_devices`, reference from `netlist_ref.py`) | **matched**, `unmatched {}` | matched ✅ |
| PEX kpex CC | **ok, 186 C / 21 R** | 186 C / 21 R ✅ |
| per-net C (fF, total) | `vout` 109.174, `ea_o1` 64.113, **`gate` 44.495**, `lp_brk` 37.935, `fb` 31.904 | 109.17 / 64.11 / 44.50 / 37.93 / 31.90 ✅ |

The extracted block prepared from **the verifier's own kpex run** (`postlayout.pex_subckt`) is
**byte-identical, all 425 lines, to the committed `asbuilt/core_pex.sp`** — the only difference is
kpex's date stamp:

```
6c6
< ***     Date: 2026-09-05 08:37:05
---
> ***     Date: 2026-09-05 03:46:19
```

`sha256(asbuilt/core_pex.sp) = f89e0105cc5462cfa31c2f1f59ea46c7504161d6a277e1cbedde7b64a0ff3e7e`,
the digest `experiments/007` cites. **REPORT.md §0/§5 says the record row is the CC extraction and
`it13`'s CC netlist is byte-identical to `it12`'s — the row of record is therefore it12/it13's,
and this verifier's rebuild lands on it.**

The 13 frozen benches on **the verifier's own extraction** (`layout/postlayout.py --pex <mine>`),
against `scorecard_post.json`:

| | 49 `pre` columns | 49 `post` columns | bench status |
|---|---|---|---|
| columns differing at 1e-9 relative | **0** | **0** | 13/13 `ok`, identical map |
| spec violations | 0 | **0** | |

| metric | pre (schematic) | post (extracted) | Δ | box |
|---|---|---|---|---|
| `v_out_v` | 1.199499 | 1.199499 | 0 | ✅ |
| `i_q_ua` | 33.80539 | 33.80539 | 0 | ✅ |
| `load_reg_mv` / `line_reg_mv` | 0.026 / 0.056 | 0.026 / 0.056 | 0 | ✅ |
| `v_dropout_mv` | 104.671 | 104.671 | 0 | ✅ |
| `psrr_1k_db` | 70.00703 | **70.09323** | +0.086 | ✅ |
| `v_undershoot_mv` | 115.057 | **127.560** | **+12.50** | ✅ (22.4 mV margin) |
| `pm_loop_deg` (1 / 0.1 / 10 mA) | 72.5064 / 72.47302 / 72.41834 | **69.30095 / 69.27011 / 69.18642** | −3.21 / −3.20 / −3.23 | ✅ |
| `ugf_loop_khz` | 801.4999 | 777.2662 | −24.2 | — |

**The ideal-ground-return disclosure is present and it is the right one.** REPORT §6.4 states
verbatim that *"the CC extraction carries no wire resistance at all, so the committed `psrr_1k` =
70.093 dB is measured with an ideal ground return"*, and it prints the in-circuit lumped
alternative. Re-measured here (`postlayout.py --vss-r 4.74`, 65 cards moved off the pin):

| in-circuit `vss` return | `psrr_1k_db` | `v_undershoot_mv` | box |
|---|---|---|---|
| ideal (the committed CC row) | 70.093 | 127.560 | PASS |
| **the solved common series element, 4.74 Ω** | **67.33** | 127.56 | **PASS — 27.3 dB above the 40 dB line** |

67.33 dB reproduces REPORT's 67.329 dB and the reviewer's ≈ 67.3 dB. S6 is signed at either
number.

Two containment checks passed: no stray `*_extracted.cir` appeared above the repo or inside it
(kpex's copy landed in its own run directory under `$SX_SCRATCH`, the contained branch REPORT §5
describes), and no repo file was modified by the re-run.

**Signature.** `2026-09-05T08:47:14  verify_postlayout_post  corner='tt' exp=''`,
`evidence="signed"`, 49 columns, `raw = layout/ldo_ihp_capless/asbuilt/core_pex.sp`,
`script = layout/postlayout.py`, 0 violations.

## 3. Claim 3 (as re-scoped) — the stitched RC row is the post-layout row of record — **SIGNED**

Claim 3 was originally *"the RC row is disclosed, NOT signed"*. Mid-pass the coordinator re-scoped
it on the platform's round-3 result and asked for the opposite: re-extract in **RC** mode with the
mesh stitcher on, re-measure, and **sign the RC row as the record** if it reproduces
`scorecard_post_rc.json`. It does. Both halves are answered below: first what this verifier
measured, then what the original claim asked about the documents.

### 3.1 The platform fix, checked on the verifier's own artefacts

The platform pin is `spicexplorer-platform` `feat/harness-spec-v2` @ `6c07a02` — *"fix(signoff):
contract a zero-ohm edge that lands on a kpex `[Pin]` node, and never ship one"* — live in this
checkout's venv as an editable install, and `run_pex(..., stitch_mesh=True)` is the default, so
`layout/signoff.py` picks it up unchanged. RC extraction re-run by the verifier on **its own
rebuilt GDS** (DRC 0, LVS matched, §2), `--pex-mode RC`, one KLayout job:

| the fix predicts | the verifier's own `signoff.json` `pex.mesh` | verdict |
|---|---|---|
| the two survivors were `[Pin]` squares, now contracted | `n_zero_edges_merged` **3101**, `n_cards_collapsed` **3101** | ✅ 3101/3101 |
| `n_zero_r_cards == 0` gates `ok` | `n_zero_r_cards` **0**, `ok` **true** | ✅ |
| 15/15 named ports anchor on a `[Pin]` | `n_anchor_pins` **15**, every one of the 15 named nets `("<net>", <layer>, "pin")`; the 18 proxies are all anonymous `$nn` nets | ✅ |
| mesh healthy | `mesh_connected` **true**, `n_open_nets` **0**, `n_pins_on_mesh` **220/243** | ✅ |
| `floor_zero_r()` becomes a no-op | grep on the stitched file: **5461 `Rext_` + 21 `rhigh` primitives = 5482 R**, 186 C, **0 zero-valued `Rext`**; `postlayout.py` printed no `floored` line and reported the netlist kind as **`[stitched]`** | ✅ no-op |

(Note in passing: 5482 R, not the 5 484 `REPORT.md` §5 quotes — a two-card difference from the
older floored run. It changes nothing and is listed as finding **V3** below.)

### 3.2 The 13 benches on the stitched RC netlist — the row of record

`layout/postlayout.py --pex <verifier's own pex_rc>`, 13/13 benches `ok`, against the committed
`scorecard_post_rc.json`:

| | result |
|---|---|
| columns reproduced exactly (1e-9 relative) | **41 / 49** |
| columns reproduced within bench resolution / 1e-4 diagnostic | **8 / 49** — largest miss `t_transient_us` **2.00e-6 relative**; every spec metric's miss is ≤ 1.5e-7 relative against resolutions of 2 mV (`v_dropout_mv`) and 0.03° (`pm_loop_*`) |
| columns outside tolerance | **0** |
| spec violations | **none**, 8/8 |

The eight near-misses are **expected and not a refusal**: the two netlists differ *by
construction*. The committed RC row was measured on a run where two zero-ohm `[Pin]` edges were
**floored at 1 mΩ**; this one contracts them, so it is not the same matrix and the last one or two
significant digits are not the same digits. Nothing that carries a decision moves — `v_dropout_mv`
agrees to 0.0001 mV on a 2 mV bench resolution.

**Verdict: reproduced. The stitched RC row is SIGNED as the post-layout row of record.**

`2026-09-05T09:10:06  verify_postlayout_rc  corner='tt' exp=''`, `evidence="signed"`, 49 columns,
0 violations, `script = layout/postlayout.py`,
`raw = layout/ldo_ihp_capless/verify/rc_netlist.sha256`. The extracted netlist is a ~5 000-card
extractor output and is not committed (rule 6 — never commit rawfiles), so `raw` points at a
committed **digest file** carrying its sha256 and the mesh census, the pattern
`spicexplorer_harness.hashes.recompute` documents for an untracked rawfile.

### 3.3 What the record row costs — measured, all three columns

Pre-layout and CC-post are unchanged from §2 (the `pre` block is bit-identical between the two
runs); RC is this verifier's own:

| metric | pre (schematic) | CC (ideal metal) | **RC (record)** | RC − CC | box | margin at RC |
|---|---|---|---|---|---|---|
| `v_out_v` | 1.199499 | 1.199499 | **1.199498** | −1 µV (at printed precision) | 1.176–1.224 V | ✅ |
| `load_reg_mv` | 0.026 | 0.026 | **0.027** | +0.001 | ≤ 5 | ✅ |
| `line_reg_mv` | 0.056 | 0.056 | **0.056** | 0 | ≤ 2 | ✅ |
| **`v_dropout_mv`** | 104.671 | 104.671 | **134.663** | **+29.99** | ≤ 200 | ✅ **65.3 mV** |
| `i_q_ua` | 33.80539 | 33.80539 | **33.76923** | −0.036 | ≤ 50 | ✅ |
| `psrr_1k_db` | 70.007 | 70.093 | **70.062** | −0.031 | ≥ 40 | ✅ 30.1 dB |
| `v_undershoot_mv` | 115.057 | 127.560 | **129.533** | +1.97 | ≤ 150 | ✅ 20.5 mV |
| `pm_loop_deg` (1 / 0.1 / 10 mA) | 72.506 / 72.473 / 72.418 | 69.301 / 69.271 / 69.186 | **69.328 / 69.297 / 69.173** | +0.03 / +0.03 / −0.01 | ≥ 60 | ✅ 9.2° |
| `ugf_loop_khz` | 801.50 | 777.27 | **775.51** | −1.76 | — | — |
| `ms_peak_db` | 7.813 | 10.316 | **8.588** | −1.73 | — | — |

**The +30 mV is physical, not an extraction artefact.** Three independent facts from this
verifier's own run say so: (a) there are now **zero** zero-ohm cards in the netlist, so no floor
and no contraction can be carrying it; (b) the CC row — the *same* layout with the *same*
capacitances and no wire resistance — sits at 104.671 mV, so the whole +29.99 mV is series
resistance; (c) at the 10 mA dropout point that is **29.99 mV / 10 mA = 3.00 Ω** of pooled
`vdd`+`vout` metal, which is the size of a real strap-and-via stack, not of a numerical residue.
The coordinator's round-3 decomposition attributes it as 15.67 mV (vdd → the 39 pass sources) +
15.21 mV (drains → vout) = 30.88 mV = 10 mA × 3.088 Ω, 85 % of it the shared TopMetal1 strap
(0.59 Ω) and the Via2–TopVia1 stack (0.75 Ω) that do **not** divide by 39, contacts 4 %, and the
two former zero cards worth 0.00 mV. That attribution is **the coordinator's, quoted, not
re-derived here** — this verifier measured the 3.00 Ω total and its three consequences above.

### 3.4 Open finding for the designer — the dropout series-R budget is MISSED

`brief.json` `dropout_pool` states the rule the layout was drawn against, at quarter-margin:

> `10.34 × R(vdd) + 8.65 × R(vout) ≤ 23.83 mV`

scored against the record row:

| term | brief | this verifier's RC measurement |
|---|---|---|
| pooled budget (quarter of the S4 margin) | **23.83 mV** | — |
| pooled consumption | hand model 20.04 mV (0.841 of the pool, R 1.13 + 1.03 Ω, REVIEW F1) | **29.99 mV** |
| ratio | 0.84× | **1.26× — BUDGET MISS** |
| implied pooled series R at 10 mA | 2.16 Ω | **3.00 Ω** |
| individual budgets | `R(vdd) ≤ 2.3056 Ω`, `R(vout,pin) ≤ 2.7569 Ω` | each met (coordinator's split: 1.57 / 1.52 Ω) |

The precise shape of the miss: **each individual net's series-R budget is met; the shared
`dropout_pool` they both draw on is not.** Scored the other way — the brief's *linear* rule fed the
coordinator's split — `10.3368 × 1.567 + 8.6445 × 1.521 = 29.35 mV`, **1.23×** the pool: the linear
model under-predicts the measured drop by ~0.6 mV, and **both** readings miss. The brief priced the two terms against one quarter of
S4's margin and the layout spends 1.26 quarters of it.

**This is a finding, not a refusal.** S4 is measured at **134.663 mV against a 200 mV bound — 65.3
mV of margin, 33 %** — and every other spec passes at the record row. The budget is a
design-discipline guard-band, not the spec. What it points at is exactly what does not divide by
39: the shared **TopMetal1 strap** and the **Via2–TopVia1 stack**. Widening the strap and
multiplying the via array is the designer's action; it is not this verifier's to make (rule 7,
"report, never fix").

### 3.5 The documents, which the original claim asked about

Checked line by line — and note this is the state **before** the coordinator's re-scoping; the
coordinator has said the designer will reconcile `REPORT.md`/`PLAN.md`, so nothing here is edited.

| where | says |
|---|---|
| `REPORT.md` §5 item 3 | *"Per this round's instruction the **record row stays CC** and the difference is reported, not adopted … which row is the row of record is the coordinator's call, not this report's."* CC/RC table prints `v_dropout_mv` **104.7 → 134.7, +30.0 (+28.7 %)**. |
| `REPORT.md` §5 item 2 | the two surviving zero-Ω cards named, and `postlayout.floor_zero_r()` flooring them at 1 mΩ. |
| `REPORT.md` §10.7 | *"the record row **stays CC** … **Open for the platform:** kpex emits 3 101 zero-ohm cards on this cell and the stitcher leaves 2 — the file does not simulate as written."* |
| `experiments/007/README.md` §5 | RC named as **not** the grid's basis; the +30 mV called *"an **addition, not a measurement**"*. |
| `scorecard_post_rc.json` | carries the RC row; nothing referenced it as the record. |

So the original claim was **true as written**: no file quoted the RC row as the record, and the
disclosure of the +30 mV, the CC-is-the-record ruling and the two zero-Ω cards was present and
correct in `REPORT.md`/`007`. It is now **stale in the other direction** — the record has moved and
the platform's open item is closed. Four documentation findings, none of which changes a verdict:

- **V1 (now moderate) — `README.md` says nothing about which row is the record.** Its only mention
  is *"kpex CC + RC, 13/13 benches inside the box"*, which a reader can take as "both extractions
  are part of the record". With the record now RC, the README's headline dropout (104.7 mV) is the
  comparison row's, not the record's.
- **V2 (minor) — `experiments/005-layout/README.md` still carries the superseded RC status.**
  Line 130: *"RC mode does not converge in these benches: 11 of 13 abort with `Warning: singular
  matrix`"*; line 39 quotes `RC 182 C / 8 418 R` from the previous drawing. This verifier measured
  **13/13 `ok`**.
- **V3 (trivial) — `REPORT.md` §5's RC card count is 5 484 R; this verifier measures 5 482** (5461
  `Rext_` + 21 `rhigh`) on the contracted netlist — the two former zero cards.
- **V4 (moderate, new) — `REPORT.md` §10.7's "Open for the platform" item is closed.** The platform
  fix is in and re-verified here: 3101/3101 contracted, 0 zero-ohm cards, the file simulates as
  written.

## 4. Claim 4 — the mismatch dispute — **the designer's numbers are the ones that describe the cell as built**

Nothing below came from `experiments/007/run.py`. `verify/verify_mismatch_corners.py` finds the
class members **by connectivity** against the certified netlist's own device rows, injects the
offset with its own node-rename + series dc source, and was cross-checked once against the
platform's `inject_vsource(..., pin='g')` at −ΔVT: the two agree to **1e-9 relative on every
metric** (`--stage check`). Card census, also this verifier's: `XM3 → XMn_7, XMn_9`;
`XM4 → XMn_6, XMn_13`; `XMBP → XMn_18`; `XMT → XMn_19`; `XM6 → XMn_20` — the A/B halves the brief
declares. The pair σ re-derives independently: √2 · 1.164445 = **1.6468 mV** for `ea_nmos_load`
(and √2 · A_VT/√(W·L) = √2 · 2.0 / √2.95 = 1.64677, the reviewer's own derivation ✓) and
√2 · 0.790569 = **1.1180 mV** for `bias_p_group`. Injection is on the **XM3 / XMT side** — the
dangerous sign the brief names.

### 4.1 The distance to the box edge, measured on the CC-extracted cell (tt / 27 °C)

| ΔVT on `XM3` (`ea_nmos_load`, 1 σ = 1.6468 mV) | S1 V | S5 µA | S4 mV | S6 dB | S7 mV | S8 ° | verdict |
|---|---|---|---|---|---|---|---|
| 0 (nominal) | 1.1995 | 33.805 | 104.67 | 70.09 | 127.56 | 69.30 | PASS |
| −3 σ (−4.940 mV) | 1.1914 | 33.807 | 104.89 | 64.01 | 127.34 | 70.07 | PASS |
| −1 σ (−1.647 mV) | 1.1968 | 33.806 | 103.45 | 67.74 | 127.49 | 69.55 | PASS |
| +1 σ (+1.647 mV) | 1.2022 | 33.805 | 103.95 | 72.44 | 127.63 | 69.05 | PASS |
| +3 σ (+4.940 mV) | 1.2076 | 33.804 | 102.51 | 71.85 | 127.77 | 68.54 | PASS |
| **+14.375 mV** (last in-box step) | 1.2231 | 33.801 | 102.79 | 60.98 | 128.12 | 67.09 | **PASS** |
| **+15.0 mV (box edge)** | **1.2242** | 33.801 | 101.77 | 60.52 | 128.14 | 67.00 | **FAIL — S1** (`> 1.224 V`) |

| ΔVT on `XMT` (`bias_p_group`, 1 σ = 1.1180 mV) | S1 V | S5 µA | S4 mV | S6 dB | S7 mV | S8 ° | verdict |
|---|---|---|---|---|---|---|---|
| −3 σ (−3.354 mV) | 1.1997 | 33.586 | 104.47 | 70.12 | 127.27 | 70.14 | PASS |
| −1 σ (−1.118 mV) | 1.1996 | 33.731 | 104.60 | 70.10 | 127.46 | 69.58 | PASS |
| +1 σ (+1.118 mV) | 1.1994 | 33.880 | 104.74 | 70.08 | 127.66 | 69.03 | PASS |
| +3 σ (+3.354 mV) | 1.1993 | 34.032 | 104.87 | 70.05 | 127.86 | 68.43 | PASS |
| **+19.375 mV** (last in-box step) | 1.1983 | 35.220 | 103.87 | 69.79 | 129.47 | 64.02 | **PASS** |
| **+20.0 mV (box edge)** | 1.1983 | 35.270 | 103.90 | 69.78 | **194.97** | 63.85 | **FAIL — S7** (`> 150 mV`) |

**Both box edges reproduce the designer to the digit** — 007's `threshold_*.json` records
`in_box_up_to 14.375 / out_of_box_from 15.0` and `19.375 / 20.0`, and so does this verifier.
Hence **15.0 / 1.6468 = 9.109 σ** and **20.0 / 1.1180 = 17.889 σ**: the designer's two numbers,
independently obtained. Note what is *not* moving: at ±3 σ the largest excursion of S7 is
**0.30 mV** on either class. On the extracted cell S7 is flat in ΔVT until a step, and the step is
9–18 σ away.

### 4.2 The two controls — the tie-breaker

| extracted C kept | ΔVT on `XM3` | S1 V | S7 mV | verdict |
|---|---|---|---|---|
| all 186 cards | 0 | 1.1995 | 127.56 | PASS |
| all 186 cards | +2.0 mV | 1.2028 | **127.65** | PASS — S7 moves **+0.09 mV** |
| only `ea_o1` (20 cards) | +2.0 mV | 1.2028 | **107.05** | PASS (designer: 107.0 ✓) |
| **none (0 cards ≈ the schematic)** | +2.0 mV | 1.2028 | **197.99** | **FAIL — S7** (designer: 198.0 ✓; brief: "step at 2 mV") |
| none | 0 | 1.1995 | 115.06 | PASS |

The designer's control reproduces exactly. **The brief's cliff is real — on the cell the brief
priced.** Delete the extracted capacitance and +2.0 mV of ΔVT puts S7 at 198 mV, out of the box,
precisely where `brief.json` puts it (`out_of_box_dvt_mv = 2.0`). Re-attach **one net's** 64 fF —
`ea_o1` alone — and it is gone (107.05 mV).

### 4.3 Where each side's arithmetic comes from

Both are correct; they are answers to different questions, and neither party said which.

| | the reviewer (`REVIEW.md` F16 / §1 item 2) | the designer (`PLAN.md` §6b item 2, `007` §4) |
|---|---|---|
| the number | **0.61 σ** / **1.07 σ**, and *"P(ΔVT > 2 mV on the dangerous XM3 side) = 11 % of dies from one class alone, and `bias_p_group` is 9 %"* | box edge **+15.0 mV = 9.1 σ**, **+20.0 mV = 17.9 σ**, tails 4e−18 % / 7e−70 % |
| what it actually is | 0.61 = `brief.json` `tolerated.dvt_mv` 1.0 / σ 1.6468 and 1.07 = 1.2 / 1.118 — i.e. **`headroom_sigma` verbatim, a quarter-margin BUDGET-CONSUMPTION ratio**, not a distance to failure. The 11 % / 9 % are the one-sided tails of `out_of_box_dvt_mv`/σ: 2.0/1.6468 = 1.2145 σ → **11.23 %**; 1.5/1.118 = 1.3417 σ → **8.98 %** (both re-derived here) | the ΔVT at which the **as-built, CC-extracted** cell first leaves the eight-line spec box, bisected at 0.625 mV, divided by the same σ |
| which circuit | the **schematic** cell: `out_of_box_dvt_mv` is a `brief.json` field measured pre-layout, with no extracted capacitance | the **extracted** cell — the row of record |
| reproduced here | yes: the arithmetic closes on `brief.json`'s own fields, and §4.2's `noC` row **is** that circuit and **does** fail at +2.0 mV | yes: both edges, to the digit |

**Verdict.** *For the row of record, the designer is right.* The mismatch distances on the cell
that was drawn, extracted and signed are **9.109 σ** and **17.889 σ**; at ±3 σ every one of the
eight spec lines holds with the same margins it has at nominal, and no measurable yield is lost to
either class at tt / 27 °C. *The reviewer is right about the circuit the brief priced, and his
arithmetic is not wrong anywhere* — 0.61 σ and 1.07 σ are `brief.json`'s own `headroom_sigma`
fields, and 11 % / 9 % follow correctly from `out_of_box_dvt_mv`; what makes them not apply is
that `out_of_box_dvt_mv` was measured with no layout capacitance, and this verifier's `noC`
control shows the cliff returning at exactly +2.0 mV the moment that capacitance is removed. The
disagreement is not arithmetic. It is that **the extraction changed the circuit**, and the brief
was not re-derived on the extracted cell.

Three qualifiers this verifier owes the owner ruling, none of which changes the verdict:

- **The record row's mismatch margin rests on a parasitic.** `ea_o1`'s 64 fF is what removes the
  cliff, and it is drawn-by-accident capacitance, not a certified component — the same net PLAN
  §6b ruling 1 is about. §3.4's open finding asks the designer to widen the `vdd`/`vout` strap and
  via stack; **if that redraw changes `ea_o1`'s capacitance, both box edges must be re-bisected.**
- **`brief.json`'s `out_of_box_dvt_mv` (2.0 / 1.5 mV) is now stale for the as-built cell** and will
  keep generating the reviewer's reading as long as it stands unqualified beside a post-layout
  scorecard. It is right about the schematic; it should say so.
- **This is tt / 27 °C and one class at a time.** Neither the designer's bisection nor this
  re-measure is a Monte Carlo over the PDK's own mismatch sections, and `007`'s README says why one
  was not run. Two classes moving together, or either class at 125 °C where §5 shows S7 already
  outside the box, is unmeasured by both parties.

**Carry-over to the record row.** The dispute was argued on the CC extraction; the record is now
the stitched RC row. RC moves S7 by **+1.97 mV**, S1 by **−1 µV** (printed precision) and S8 by **+0.03°** against CC
(§3.3), so the σ-distances above carry to the record row unchanged in the first digit.

## 5. Claim 5 — the three decisive corner rows — **SIGNED**

Re-measured by the verifier, not by `experiments/007/run.py`: `verify/verify_mismatch_corners.py
--stage corners` drives `CANDIDATE.at(corner, temp)` and splices in **this verifier's own extracted
block**, `pre` = the same sizing point with no extraction at all.

| row | verifier | `experiments/007` | Δ | violations (verifier) |
|---|---|---|---|---|
| **ff / 125 `pre`** `i_q_ua` | **58.371** | 58.37122 | 0 | **S5** (`> 50 µA`) |
| **ff / 125 `post`** `i_q_ua` | **58.371** | 58.37121 | 0 | **S5** |
| ff / 125 `post` `v_undershoot_mv` | 130.41 | 130.406 | 0 | — |
| **ss / 125 `post`** `v_undershoot_mv` | **171.09** | 171.086 | 0 | **S7** (`> 150 mV`) |
| ss / 125 `pre` `v_undershoot_mv` | 152.75 | 152.755 | 0 | **S7** |
| **sf / −40 `pre`** `v_undershoot_mv` | **301.81** | 301.8075 | 0 | **S7** |
| sf / −40 `post` `v_undershoot_mv` | 106.12 | 106.117 | 0 | none (**PASS**) |

All three decisive rows reproduce to the printed digit. Now the second half of the claim — *are
they schematic corner failures already known from the schematic lane?* The honest answer has three
parts, and `experiments/007` already says all three itself:

1. **The failure *classes* are known from the schematic lane.** `experiments/003-sizing`'s 15-corner
   table (old sizing, `i_q` 36.28 µA) records exactly these two: **S5 binds at ff/125** (61.93 µA)
   and **S7 binds at the slow/cold end** (ss/−40 310.8 mV, ss/27 254.6 mV). 003 states the mechanism
   and that it is not a sizing problem — *"the binding spec is S5 at ff/125 and S7 at ss/−40, and
   they are one mechanism"*, the resistor-referenced bias spreading 2.4× across corners, so the two
   failures pull `r_bias_l` in opposite directions.
2. **The specific rows are new to 007, at the re-certified sizing.** 003's ss/125 **passed**
   (144.1 mV); at `i_q` 33.81 µA the `pre` row is **152.75 mV — a schematic failure**, and
   003's sf/−40 passed where 007's `pre` is 301.81 mV. So ss/125 and sf/−40 are S7 failures **of
   the schematic at the current sizing**, first visible in 007's own `pre` column, not carried over
   from 003.
3. **ff/125 S5 is purely schematic — `pre` and `post` are identical to 5 significant figures**
   (58.371 both), because `i_q` is a dc quantity and the extraction adds no dc path. Layout cannot
   fix it and did not cause it.

**And the layout-induced part is separated, not hidden.** ss/125 S7 goes 152.75 → 171.09
(**+18.3 mV from extraction**, on top of a schematic failure); sf/−40 S7 goes the *other* way,
301.81 → 106.12, i.e. the extracted `ea_o1` capacitance **repairs** the cold-corner ringing — the
same mechanism §4's controls isolate. `REPORT.md` §10.6 discloses precisely this split.

**Verdict: SIGNED.** The three rows reproduce exactly; both failure classes were known from the
schematic lane (003) and are disclosed as schematic-side in 007; the individual rows at the
re-certified sizing are new to 007 and 007 says so. One qualifier a reader is owed: *"already known
from the schematic lane"* is true of the **classes**, not of the **rows** — 003's ss/125 passed.

## 6. Verdict table — one row per spec line

Every number in the **verifier** columns was measured on this pass, on this verifier's own rebuilt
GDS and its own extractions. `ref` is the certified analog-db reference `ldo_005_buffered_ref`
(`decks/reference/`, IHP tt/27 — the yardstick the mission names, itself out of the box on four
lines). `claim` is the committed `scorecard_post_rc.json` (record) / `scorecard_post.json` (CC).

| # | spec | bound | ref `ldo_005` | pre (schematic) | CC (ideal metal) | **RC — record** | verdict | Δ vs ref | Δ vs claim |
|---|---|---|---|---|---|---|---|---|---|
| S1 | `v_out_v`, no load | in [1.176, 1.224] V | 1.609127 ✗ | 1.199499 | 1.199499 | **1.199498** | **PASS** (23.5 mV to the low edge, 24.5 mV to the high) | −0.409629 | **0** |
| S2 | `load_reg_mv`, 0.1→10 mA | ≤ 5 mV | 1.274 | 0.026 | 0.026 | **0.027** | **PASS** (185×) | −1.247 | **0** |
| S3 | `line_reg_mv`, 1.4→1.65 V | ≤ 2 mV | 4.32 ✗ | 0.056 | 0.056 | **0.056** | **PASS** (36×) | −4.264 | **0** |
| S4 | `v_dropout_mv` at 10 mA | ≤ 200 mV | 169.675 | 104.671 | 104.671 | **134.6634** | **PASS** (65.3 mV margin) | −35.0116 | **−0.0001** |
| S5 | `i_q_ua`, no load | ≤ 50 µA | 758.6951 ✗ | 33.80539 | 33.80539 | **33.76923** | **PASS** (16.2 µA margin; **22.5× below the reference** — the mission headline) | −724.926 | **0** |
| S6 | `psrr_1k_db` at 1 mA | ≥ 40 dB | 44.52535 | 70.00703 | 70.09323 | **70.06213** | **PASS** (30.1 dB); with the solved 4.74 Ω in-circuit `vss` return, 67.33 dB — still 27.3 dB clear | +25.5368 | **0** |
| S7 | `v_undershoot_mv`, 0.1→10 mA | ≤ 150 mV | 1.957 | 115.057 | 127.560 | **129.533** | **PASS** (20.5 mV margin) — the reference has a 1 µF external cap; this cell is capless | +127.576 | **0** |
| S8 | `pm_loop_deg` at 1 mA | ≥ 60° | 46.38975 ✗ | 72.5064 | 69.30095 | **69.32791** | **PASS** (9.3°) | +22.9382 | **0** |
| S8lo | `pm_loop_lo_deg` at 0.1 mA | ≥ 60° | not measured | 72.47302 | 69.27059 | **69.29748** | **PASS** (9.3°) | n/a | **−1e−5** |
| S8hi | `pm_loop_hi_deg` at 10 mA | ≥ 60° | not measured | 72.41834 | 69.18628 | **69.17304** | **PASS** (9.2°) | n/a | **+1e−5** |

**8/8 spec lines pass at the record row, and every one of them reproduces the designer's claim** —
eight columns exactly at 1e-9, two (`pm_loop_lo/hi`) at 1e-5 °, four thousand times finer than the
0.03 ° bench resolution. Against the mission's own yardstick the cell meets or beats
`ldo_005_buffered_ref` on S1–S6 and S8 while drawing **33.77 µA against 758.70 µA**, and gives back
only S7, which is the price of removing the reference's external capacitor.

**Two things this table does not say.** It is **tt / 27 °C**: §5 records the corner failures (S5 at
ff/125, S7 at 125 °C and cold), which are schematic-side and disclosed. And it is **nominal**: §4
records the mismatch distances.
