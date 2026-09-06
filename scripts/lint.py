#!/usr/bin/env python3
"""`make lint`: the platform harness checks (driven by harness.yaml) plus this repo's own."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from spicexplorer_harness import lint, load  # noqa: E402
from spicexplorer_harness.lint import Lint  # noqa: E402

# `deck-rebuild` -- every frozen dir still rebuilds from its own design.json through
# `ldo.dut.Design` -- used to live here. It is now a GENERIC harness check
# (`spicexplorer_harness.lint.deck_rebuild`), resolved through `package:` by name, so this repo
# gets it from `lint.GENERIC` and the transmitter gets the same one instead of its own copy.


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
    sys.exit(lint.main(load(REPO), extra=(spec_reference,)))
