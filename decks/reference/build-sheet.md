# decks/reference — build sheet

Frozen 2026-09-04 by `python -m lab.metrics --certify` (`lab.dut.REFERENCE`, see `design.json`).

| item | value |
|---|---|
| circuit | analog-db `ldo_005_buffered_ref`, `pdk/ihp-sg13g2/` binding, corner `tt`, sizing.yaml defaults, no overrides |
| analog-db commit | `c63d43512b97b80fa8c14d890b046d1eacebc969` (platform submodule `examples/analog-db`) — a re-pin that changes the class templates or the lowered netlist breaks `deck_rebuild` and forces re-certification |
| generator | `lab.dut.Design.deck(bench)` = analog-db `assemble()` with comment lines dropped |
| lane | native ngspice-45 via `NGSpice_Wrapper`; PDK pin in `doc/environment.md` |
| benches | the ten `*.spice` here, one per class template; `scorecard.json` holds the certified values + every raw measure |
