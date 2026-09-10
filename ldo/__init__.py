"""The design package: the code this design owns.

* `dut`     — the sizing point, and the deck every bench is built from
* `metrics` — the scorecard: KEYMAP, check the box, log the row, and the certify/check lifecycle
* `sim`     — this repo's simulator-lane policy (where runs go, which binary, which model libs)
* `config`  — paths and the PDK pin
* `sign`    — the second actor's re-measure-and-sign path (rule 7)

The generic harness work — ledger, context pack, lint, spec — is `spicexplorer_harness`, driven by
`harness.yaml`. This design computes every scorecard number inside `metrics`, so it carries no
separate `bench` module: `make check` reproduces what `metrics` produced.
"""
