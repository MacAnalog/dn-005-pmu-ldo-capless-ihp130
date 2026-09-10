# Pre-layout sign-off — dn-005 capless LDO

KIND: REPORT (fidelity: schematic netlist, no interconnect parasitics)

**The scorecard of record for this fidelity is `decks/scorecard.json`, in this directory.** The
13 certified benches moved here from `decks/candidate/` under template 2.02, provenance intact.

## Conditions

| condition | value |
|---|---|
| decks | `decks/` (sha-locked, 13 benches; `SHA256SUMS` regenerated after the move) |
| scorecard | `decks/scorecard.json`, tag `candidate_certify` |
| corner, temperature | tt, 27 °C |
| yardstick | `../../decks/reference/` — the analog-db `ldo_005_buffered_ref` |

## What this does not cover

- Corners and mismatch beyond tt/27 °C are experiment work, not part of this certified row.
- Post-layout fidelities are not run: `../postlayout-pex/` and `../postlayout-em/` are planned.
- `make check` reproduces the **yardstick**, not this scorecard (see `../README.md`).
