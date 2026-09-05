#!/usr/bin/env python3
"""`make lint`: the platform harness checks (driven by harness.yaml) plus this repo's own."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from spicexplorer_harness import lint, load  # noqa: E402
from spicexplorer_harness.lint import Lint  # noqa: E402


def deck_rebuild(L: Lint) -> None:
    """Every frozen bench must still be reproducible from ldo.dut.Design + design.json.

    decks/reference/*.spice are bytes; ldo.dut (analog-db assemble + the sizing point) is the
    generator. If the analog-db submodule, the class templates or the builder drift, every
    experiment silently measures a different bench than the certified one.
    """
    ref = REPO / "decks" / "reference"
    dj = ref / "design.json"
    if not dj.exists():
        return  # nothing certified yet; the frozen check reports a missing manifest
    try:
        # resolved through `package:`, never `from ldo.dut import ...`: the check that catches a
        # half-finished package rename must not itself be broken BY the rename
        Design = importlib.import_module(f"{L.h.package}.dut").Design
        d = Design.from_dict(json.loads(dj.read_text()))
        built = {b: d.deck(b) for b in d.benches()}
    except Exception as exc:  # noqa: BLE001
        L.fail("deck-rebuild", f"cannot rebuild the reference decks from design.json: {exc!r}",
               "design.json must round-trip through ldo.dut.Design.from_dict; fix the loader or re-certify")
        return
    fix = ("a class template, the analog-db submodule pin or ldo.dut changed: revert it, or re-certify "
           "deliberately (`python -m ldo.metrics --certify && make freeze`) -- an un-reproducible "
           "reference means every A/B is measured against a bench nobody can rebuild")
    for b, text in built.items():
        p = ref / f"{b}.spice"
        if not p.exists():
            L.fail("deck-rebuild", f"decks/reference/{b}.spice is missing", fix)
        elif p.read_text() != text:
            L.fail("deck-rebuild", f"ldo.dut.Design.deck({b!r}) no longer reproduces decks/reference/{b}.spice", fix)


def spec_reference(L: Lint) -> None:
    """The certified reference numbers quoted in doc/target-spec.md are the certified ones."""
    h = L.h
    try:
        sc = json.loads(h.text(h.reference_scorecard))["scorecard"]
    except (ValueError, KeyError, TypeError):
        return
    flat = h.text(h.spec_doc).replace("**", "")
    for key, fmt in (("load_reg_mv", "{:.2f}"), ("i_q_ua", "{:.0f}"), ("psrr_1k_db", "{:.1f}"),
                     ("pm_loop_deg", "{:.1f}")):
        if key in sc and fmt.format(sc[key]) not in flat:
            L.fail("spec-sync", f"certified {key} = {fmt.format(sc[key])} is not quoted in {h.spec_doc}",
                   "the spec table's 'reference baseline' column quotes decks/reference/scorecard.json; "
                   "copy the certified numbers across (or re-certify)")


if __name__ == "__main__":
    sys.exit(lint.main(load(REPO), extra=(deck_rebuild, spec_reference)))
