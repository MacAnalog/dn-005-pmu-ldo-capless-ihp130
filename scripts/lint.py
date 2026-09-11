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

# Where a committed artefact is allowed to live (template 2.00, "every artefact has a home").
# A figure or a table is evidence: it belongs beside the claim it supports, in a directory a reader
# can find without being told. Raw simulator output is the opposite — it stays in the scratch root
# and is never committed at all.
ARTIFACT_SUFFIXES = (".png", ".svg", ".pdf", ".csv", ".gds", ".gds.gz")
# ADD THIS DESIGN'S OWN HOMES HERE, deliberately, one line each with why. That is the whole
# escape hatch and it is on purpose: a home nobody wrote down is a directory the next reader has
# to guess at, and a one-line declaration in a reviewed file costs nothing.
ARTIFACT_HOMES = (
    "signoff/",        # the design of record, by fidelity — what a reader is entitled to trust
    "experiments/",    # the working space: agents organize inside it freely (figs/ + tables/ is the habit)
    "layout/",         # the generator's own working output; what is SIGNED OFF moves to signoff/layout/
    "decks/",          # candidate and control deck dirs (the CERTIFIED ones live in signoff/)
    "references/",     # papers, datasheets, standards
    "doc/",            # figures that belong to a document
    "notebooks/",      # executed in place, outputs committed
    ".claude/", ".sx/", ".github/",
)


def artifact_home(L: Lint) -> None:
    """Every committed figure, table or layout sits in a home this repo has declared.

    An agent that leaves a plot in whichever directory it was standing in produces a repo nobody
    can read six weeks later, and a reviewer who cannot find the evidence treats the claim as
    unsupported. The check is not about tidiness: it is about whether the evidence is findable.

    It is deliberately not a straitjacket. `experiments/` is wide open — that IS the working space
    — and a design with its own durable output directory adds one line to `ARTIFACT_HOMES` above.
    What it refuses is the undeclared case: an artefact somewhere nobody wrote down.
    """
    import subprocess  # noqa: PLC0415 - local: a design's lint.py may not import it at module level

    root = L.h.root
    r = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True)
    if r.returncode:
        return  # not a git checkout (a template copied by hand): nothing to check
    # Grouped by top-level directory, because that is the unit you DECLARE. Reporting one failure
    # per file would print 248 blocks on a design with a physics lane, and a lint nobody can read
    # is a lint that gets switched off. `dict` keeps first-seen order; it also dedupes the stages
    # `git ls-files` emits for an unmerged path mid-merge.
    stray: dict[str, list[str]] = {}
    for rel in dict.fromkeys(r.stdout.split("\0")):
        if not rel or not rel.endswith(ARTIFACT_SUFFIXES) or (root / rel).is_symlink():
            continue
        if rel.startswith(ARTIFACT_HOMES):
            continue
        stray.setdefault(rel.split("/")[0] + "/" if "/" in rel else "(repo root)", []).append(rel)
    for where, files in stray.items():
        eg = files[0] if len(files) == 1 else f"{len(files)} files, e.g. {files[0]}"
        L.fail("artifact-home", f"{where} holds committed artefacts outside every declared home "
                                f"({eg})",
               f"either MOVE them — an experiment's evidence to `experiments/NNN-*/figs|tables/`, "
               f"a measured result to `signoff/<fidelity>/`, a document's figure to `doc/`, a "
               f"paper to `references/` — or DECLARE `{where}` in `ARTIFACT_HOMES` in this file, "
               f"with one line saying what lives there. Raw simulator output is neither: it is "
               f"never committed, and stays in the scratch root ($SX_SCRATCH)")


def dropout_threshold_binding(L: Lint) -> None:
    """`VOUT_THRESH` is bound in `analyses/dropout.yaml` exactly while the class template needs it.

    review-002 **m5** found the parameter dead: the LDO-class dropout bench measures a regulation
    window (`|Vout-VOUT_NOM| <= VREG_TOL`) plus a slope test and never reads a threshold. Deleting
    the binding (**m5-r**) then broke the `dropout` bench for a whole review round, because
    analog-db's `assemble()` scans the RENDERED template text — comment lines included — for
    unresolved `${...}`, and the class template still explains the retired criterion using
    `${VOUT_THRESH}`.

    Both directions are a defect, so both fail here:

    * placeholder present, binding missing → `dropout` does not assemble, and one bench of thirteen
      sinks every scorecard;
    * binding present, placeholder gone → analog-db has retired it, `safe_substitute` now ignores
      the key, and the binding is exactly the dead declared condition m5 was about.

    The second direction is what closes m5-r: it fires the moment the shared root re-pins past the
    analog-db change, rather than leaving the row open until someone remembers.
    """
    try:  # noqa: PLC0415 - local imports: a checkout with `.sx/platform` unlinked has neither
        from spicexplorer_analog_db.assemble import resolve_template

        from ldo.dut import LOCAL_CIRCUITS, circuit
    except Exception:
        return  # analog-db is not importable here; `package-importable` is the check that says so
    for d in sorted(p for p in LOCAL_CIRCUITS.glob("*") if (p / "circuit.yaml").is_file()):
        adoc_path = d / "analyses" / "dropout.yaml"
        if not adoc_path.is_file():
            continue
        try:
            adoc = circuit(d.name).analysis("dropout")
            tpath = resolve_template(circuit(d.name).klass, adoc.get("template", "dropout"))
        except Exception:
            continue  # a malformed circuit dir is `deck_rebuild`'s failure to report, not this one
        if tpath is None or not Path(tpath).is_file():
            continue  # the class template library is not resolvable in this checkout
        rel = adoc_path.relative_to(L.h.root).as_posix()
        needs = "${VOUT_THRESH}" in Path(tpath).read_text(errors="replace")
        bound = "VOUT_THRESH" in (adoc.get("params") or {})
        if needs and not bound:
            L.fail("dropout-threshold",
                   f"{rel} binds no VOUT_THRESH, but the class template still carries "
                   f"`${{VOUT_THRESH}}` ({tpath})",
                   "assemble() scans the rendered text INCLUDING comments, so the dropout bench "
                   "will not build and every 13-bench scorecard fails with it: restore "
                   "`VOUT_THRESH: 1.14` under params, with the reason beside it (review-002 m5-r)")
        elif bound and not needs:
            L.fail("dropout-threshold",
                   f"{rel} still binds VOUT_THRESH, but the class template no longer has the "
                   f"placeholder ({tpath})",
                   "analog-db has retired it and safe_substitute now ignores the key, so the "
                   "binding is a declared bench condition the bench does not read: delete it, "
                   "re-certify the frozen decks (`make check && make freeze`) and close m5-r in "
                   "README.md")


def signoff_index(L: Lint) -> None:
    """Every directory under `signoff/` is named in `signoff/README.md`.

    `signoff/` is the tree a reader trusts, so an unlisted directory in it is worse than no
    directory: it looks certified and says nothing about the conditions it was measured under.
    The README's table is the index — one row per fidelity, with its scorecard and its status.
    """
    d = L.h.root / "signoff"
    if not d.is_dir():
        return  # a design that has not started signing anything off
    idx = d / "README.md"
    if not idx.is_file():
        L.fail("signoff-index", "signoff/ exists but signoff/README.md does not",
               "copy it from the template (`make template-update`): it is the index of what is "
               "signed off, at which fidelity, by whom and when")
        return
    text = idx.read_text()
    # `__pycache__` and dot-dirs are tooling debris, not fidelities: they are not sign-offs and
    # demanding a README row for them would teach people to ignore this check.
    subs = (p.name for p in d.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.name != "__pycache__")
    for sub in sorted(subs):
        if f"`{sub}`" not in text and f"`{sub}/" not in text:
            L.fail("signoff-index", f"signoff/{sub}/ is not named in signoff/README.md",
                   f"add a row for `{sub}` to the table — what the number includes, its scorecard "
                   f"path, its status, who signed it and when. A fidelity nobody described is not "
                   f"a sign-off")


# `package-importable` is NOT here: the platform ships it (driven by `package:` in harness.yaml).
EXTRA = (spec_reference, deck_portable, dropout_threshold_binding, artifact_home, signoff_index)

if __name__ == "__main__":
    # NOTE: this tuple, not EXTRA, is what `make lint` runs — `spicexplorer_harness.lint.main`
    # takes the checks as an argument and never reads a module-level EXTRA. `artifact_home` and
    # `signoff_index` are therefore defined and NOT run; that divergence predates this line and is
    # left for whoever owns those two checks to rule on, rather than silently switched on here.
    sys.exit(lint.main(load(REPO), extra=(spec_reference, deck_portable,
                                          dropout_threshold_binding)))
