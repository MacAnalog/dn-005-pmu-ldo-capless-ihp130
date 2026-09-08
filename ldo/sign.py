"""The verifier's half of rule 7 (designer != verifier) for this repo: re-measure a frozen dir
and, only if it reproduces its committed scorecard bit for bit, sign it.

`python -m ldo.metrics --certify DIR` is the DESIGNER'S delivery claim: it writes the frozen dir
and logs `evidence="awaiting"`. The harness's `scorecard-recompute` lint then reports the
scorecard "unverifiable" in every checkout that holds a ledger until a SECOND actor logs a
`signed` row carrying the same tag / corner / exp and the same hash block. This module is that
second actor's tool (`make sign DIR=decks/reference AUTHOR=<designer> VERIFIED_BY=<you>`):

1. simulate the dir's `*.spice` EXACTLY as frozen (bytes, never a rebuild -- what `--check` does);
2. re-derive the provenance block from those decks and the measured card
   (`spicexplorer_harness.ledger.provenance`) and diff it against the committed one
   (`spicexplorer_harness.verify.provenance_diff`): an equal `computation_hash` means identical
   scorer, identical deck bytes AND identical numbers, so the lint's own comparison passes;
3. only then `log_run(..., evidence="signed", author=<designer>, verified_by=<verifier>)` with
   the committed hash block. Anything else prints the column report and refuses (exit 1).

This file is deliberately NOT `ldo/metrics.py`: the committed provenance blocks name that file by
sha (`script_sha`), so a signing flow added there would have turned two "unverifiable" lints into
two "recompute failed" lints and forced a re-certification. The ledger is per checkout: sign where
`make lint` is red. `LDO_EXP` must be unset (the frozen blocks record `exp: ""`).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

from spicexplorer_harness import hashes, log_run, provenance, violations
from spicexplorer_harness.verify import compare_card, provenance_diff

from . import config as C
from . import metrics as M


def sign(out: Path, *, author: str, verified_by: str) -> int:
    out = Path(out).resolve()
    rel = out.relative_to(C.H.root).as_posix() if out.is_relative_to(C.H.root) else str(out)
    card_path = out / "scorecard.json"
    if not card_path.is_file():
        print(f"REFUSED: no scorecard.json in {rel} -- nothing certified there to sign")
        return 1
    doc = json.loads(card_path.read_text())
    prov = doc.get("provenance")
    if not isinstance(prov, dict) or not prov.get("computation_hash"):
        print(f"REFUSED: {rel}/scorecard.json has no v2 provenance block; re-certify it first "
              "(`python -m ldo.metrics --certify DIR && make freeze`)")
        return 1
    decks = {p.stem: p.read_text() for p in sorted(out.glob("*.spice"))}
    if not decks:
        print(f"REFUSED: no *.spice in {rel} -- nothing frozen to re-measure")
        return 1
    exp_env = C.H.exp_env
    if exp_env and os.environ.get(exp_env) and os.environ.get(exp_env) != (prov.get("exp") or ""):
        print(f"REFUSED: {exp_env}={os.environ[exp_env]!r} but the scorecard records "
              f"exp {prov.get('exp', '')!r}; a signing run must state the same experiment (unset it)")
        return 1

    tag = str(prov["tag"])
    corner = str(prov.get("corner") or "")
    values, records = M.run_decks(decks, tag)
    bad = sorted(b for b, r in records.items() if r["status"] != "ok")
    card = {k: v for k, v in values.items() if isinstance(v, float) and not math.isnan(v)}
    cmp = compare_card(doc.get("scorecard") or {}, card)
    print(cmp.report())
    if bad:
        print(f"NOT SIGNED: benches did not run: {bad}")
        return 1
    rederived = provenance(C.H, tag, card, corner=corner, script=prov.get("script") or M.SCRIPT,
                           raw=prov.get("raw"))
    diff = provenance_diff(prov, rederived)
    if diff:
        print(f"NOT SIGNED: the re-measure does not reproduce {rel}/scorecard.json -- "
              f"provenance differs in {diff}")
        print("    a within-resolution match is still not a signature: the lint compares the hash "
              "block exactly. If the simulator/PDK moved, the DESIGNER re-certifies deliberately")
        return 1
    dj = out / "design.json"
    design = json.loads(dj.read_text()) if dj.is_file() else None
    row = log_run(C.H, tag, values, corner=corner, deck="".join(decks.values()),
                  violations=violations(C.H.spec, values), design=design,
                  author=author, evidence="signed", verified_by=verified_by,
                  extra={"benches": {b: r["status"] for b, r in records.items()}, "signs": rel},
                  **{k: prov[k] for k in hashes.HASH_KEYS})
    print(f"SIGNED {rel} (tag {tag!r}, corner {corner!r}, exp {row.get('exp', '')!r}) "
          f"by {verified_by} for author {author}: {len(card)} columns reproduce exactly. "
          "`make lint` should now clear the scorecard-recompute item in this checkout")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ldo.sign", description=__doc__.split("\n\n")[0])
    ap.add_argument("dir", help="frozen dir to re-measure and sign (decks/reference, decks/candidate)")
    ap.add_argument("--author", required=True, help="the designer who certified it (who you are independent of)")
    ap.add_argument("--verified-by", required=True, help="you, the second actor (a `verifiers:` id if the roster exists)")
    a = ap.parse_args(argv)
    if not a.author.strip() or not a.verified_by.strip():
        ap.error("--author and --verified-by must both be non-empty")
    return sign(Path(a.dir), author=a.author.strip(), verified_by=a.verified_by.strip())


if __name__ == "__main__":
    sys.exit(main())
