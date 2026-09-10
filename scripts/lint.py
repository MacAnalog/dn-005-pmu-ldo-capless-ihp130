#!/usr/bin/env python3
"""`make lint`: the platform harness checks (driven by harness.yaml) plus this repo's own."""
from __future__ import annotations

import json
import re
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



# An include/library line naming an ABSOLUTE path: what `deck_portable` refuses in a frozen deck.
_ABS_INCLUDE = re.compile(r'^\s*\.?(?:include|lib)\b[^\n]*?["\'\s](/[^"\'\s]+)', re.I | re.M)


def abs_includes(text: str) -> list[str]:
    """Absolute paths named on a deck's include/library lines (`include`, `.include`, `.lib`)."""
    return [m.group(1) for m in _ABS_INCLUDE.finditer(text)]


def deck_portable(L: Lint) -> None:
    """A frozen deck may not carry an absolute path from the machine that certified it.

    From the template (release 1.01), which took it from two designs that froze a deck naming a
    machine-specific model library: the certified reference then reproduces only where it was made.
    Redacting the path on write does not help — `deck_rebuild` compares bytes. The portable form is
    a `$VAR` in the deck text, resolved as the deck reaches the simulator.
    """
    for rel in L.h.frozen:
        d = L.h.path(rel)
        if not (d / "design.json").is_file():
            continue
        for f in sorted(d.glob("*.spice")) + sorted(d.glob("*.scs")):
            for path in abs_includes(f.read_text(errors="replace")):
                L.fail("deck-portable",
                       f"{f.relative_to(L.h.root).as_posix()} includes the absolute path {path}",
                       "a frozen deck is committed, hashed and rebuilt byte for byte, so the path "
                       "may not be in it: name it `$VAR` in the deck, resolve it where the deck is "
                       "handed to the simulator, then re-certify (`make certify && make freeze`)")


if __name__ == "__main__":
    sys.exit(lint.main(load(REPO), extra=(spec_reference, deck_portable)))
