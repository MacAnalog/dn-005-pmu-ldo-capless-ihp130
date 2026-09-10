# Pre-layout sign-off — dn-005 capless LDO

KIND: REPORT (fidelity: schematic netlist, no interconnect parasitics)

**The scorecard of record for this fidelity is `decks/candidate/scorecard.json`**, and it did not
move into this directory — see `../README.md`, "Where this design's sign-off actually lives". This
file is the fidelity's index, not a second copy of its numbers.

## Conditions

| condition | value |
|---|---|
| decks | `decks/candidate/` (sha-locked; 13 benches) |
| scorecard | `decks/candidate/scorecard.json`, tag `candidate_certify` |
| corner, temperature | tt, 27 °C |
| yardstick | `decks/reference/` — the analog-db `ldo_005_buffered_ref` |

## What this does not cover

- Corners and mismatch beyond tt/27 °C are experiment work, not part of this certified row.
- Post-layout fidelities are not run: `../postlayout-pex/` and `../postlayout-em/` are planned.
- `make check` reproduces the **yardstick**, not this scorecard (see `../README.md`).
