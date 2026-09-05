# 2026-09-04 — the lint asks for a signature the certifier cannot produce

KIND: journal entry | type: semantic | status: superseded

[superseded 2026-09-04 — both halves landed. The harness gained
`spicexplorer_harness.ledger.provenance()` and a `provenance.tag` fallback in `_backing_rows`
(platform #129), and this repo's `certify()` now writes that block and logs the run from it, so
`scorecard-recompute` is backable by a signed row. The rule below is the part worth keeping.]

**Observation** (review-002-capless-ldo M1). This repo reported `make lint` as red "only for want
of an independent signed verifier row". An independent verifier then signed **both** scorecards
and the lint stayed red with the identical message, `(tag None)`.

The two halves do not agree on where the tag lives. `spicexplorer_harness`'s
`lint.py::_backing_rows` matches a signed ledger row on the scorecard's **top-level** `tag`, and
it also wants a hash block (`script_sha` / `raw_sha` / `computation_hash`) for its exact-match
path. `lab/metrics.py::certify()` writes the tag **inside `provenance`** and writes no hash block
at all. Neither the exact path nor the loose path can match, for any row, ever.

**So the failure is a permanent false alarm, not a missing signature** — and worse, it is a false
alarm that *looks* actionable, so it absorbs effort repeatedly. A fresh clone is red on arrival
for the same reason and cannot be made green by anything a reader does, because the ledger is
git-ignored and per checkout.

**Rule.** Before recording a red gate as "waiting on someone to do X", do X once and check the
gate actually goes green. A gate whose passing condition has never been demonstrated is not a
gate; it is an assumption.

**Harness follow-up (platform).** Either have `certify()` emit a top-level `tag` (plus `corner`)
and a hash block, or have `_backing_rows` fall back to `provenance.tag`.

**Resolved 2026-09-04.** Both, in the end. `ldo/metrics.py::certify()` builds the block with
`ledger.provenance(h, tag, card, corner=…, script=…, raw=…)` and logs the certification run from
the same block with the same `corner=` and `evidence="awaiting"`; the remaining
`scorecard-recompute` failure now says exactly what it means — *no verifier has signed these two
scorecards yet* — and a signed row with the same `tag`/`corner`/`exp` clears it. The gate has
been shown to be clearable, which is what the rule above asks for.
