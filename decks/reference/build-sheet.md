# decks/reference — build sheet

Frozen 2026-09-04 by `python -m ldo.metrics --certify decks/reference` (the sizing point is read
back from `design.json`, so a re-certification cannot quietly change what it certifies).

**Re-certified 2026-09-04** on the corrected LDO class noise bench (analog-db PR #68 dropped the
extra `sqrt`: ngspice's `onoise_total` is already V rms). `vn_out_urms` moved 5037.94 -> 25.38
µVrms; every other certified number reproduces to the last committed digit.

| item | value |
|---|---|
| circuit | analog-db `ldo_005_buffered_ref`, `pdk/ihp-sg13g2/` binding, corner `tt`, sizing.yaml defaults, no overrides |
| analog-db commit | `7b164965afde91b3a5306f04ce878199bbf3b2be` (platform submodule `examples/analog-db`) — a re-pin that changes the class templates or the lowered netlist breaks `deck_rebuild` and forces re-certification |
| generator | `ldo.dut.Design.deck(bench)` = analog-db `assemble()` with comment lines dropped |
| lane | native ngspice-45 via `NGSpice_Wrapper`; PDK pin in `doc/environment.md` |
| benches | the ten `*.spice` here, one per class template; `scorecard.json` holds the certified values + every raw measure |
| provenance | `scorecard.json`'s `provenance:` block (`spicexplorer_harness.ledger.provenance`) hashes the scorer `ldo/metrics.py` and `decks.sha256` — the digest of these deck bytes — plus one `computation_hash` per certified metric. `SHA256SUMS` (`make freeze`) locks the whole dir; the block deliberately does NOT name it, since freeze covers `scorecard.json` too and could never re-derive |
| signature | the certification run is logged `evidence=awaiting`: it is a delivery claim. `make lint` stays red on `scorecard-recompute` until a verifier re-measures and logs `evidence=signed` with the same `tag`/`corner`/`exp` |
