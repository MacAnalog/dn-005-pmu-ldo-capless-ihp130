"""Sign a post-layout row: the verifier's own re-measure of the 13 frozen benches, logged with
an evidence block.

Two rows, one script (`--row cc|rc`):

* ``cc`` — the capacitance-only extraction.  The block the benches ran on came from THIS
  verifier's kpex CC run on ITS OWN rebuilt GDS and is byte-identical (bar kpex's date stamp) to
  the committed ``asbuilt/core_pex.sp``, so that committed file is the ``raw`` the block hashes.
* ``rc`` — the stitched RC extraction, the post-layout row of record.  The extracted netlist is a
  5 000-card artefact that is NOT committed (rule: never commit rawfiles), so ``raw`` points at
  the committed digest file ``verify/rc_netlist.sha256`` instead -- the pattern
  ``hashes.recompute`` documents for an untracked rawfile.

The script REFUSES to sign unless every column of the committed reference scorecard is
reproduced.  The primary tolerance is the harness's own 1e-9 relative; a column that misses it is
re-checked against the bench resolution `brief.json` records, and the miss is printed either way,
because the two netlists differ by construction (the stitcher now CONTRACTS the zero-ohm pin
edges the older run floored at 1 mOhm).

    python verify/sign_postlayout.py --row rc [--sign]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

# this file lives at layout/<cell>/verify/, so the repo root is three levels up
REPO = Path(__file__).resolve().parents[3]
# the verifier's own work dir: neutral scratch root, never inside the repo, never /tmp
WORK = Path(os.environ.get("SX_SCRATCH") or (Path.home() / "sx-scratch")) / "ldo-verify"
sys.path.insert(0, str(REPO))

from spicexplorer_harness import hashes, log_run, provenance, violations  # noqa: E402

from ldo import config as C  # noqa: E402
from ldo.dut import CANDIDATE  # noqa: E402

CELL = REPO / "layout" / "ldo_ihp_capless"
ROWS = {
    "cc": {"mine": WORK / "post/scorecard.json", "ref": CELL / "scorecard_post.json",
           "tag": "verify_postlayout_post", "raw": "layout/ldo_ihp_capless/asbuilt/core_pex.sp",
           "kind": "CC, verifier's own kpex run"},
    "rc": {"mine": WORK / "post_rc/scorecard.json", "ref": CELL / "scorecard_post_rc.json",
           "tag": "verify_postlayout_rc",
           "raw": "layout/ldo_ihp_capless/verify/rc_netlist.sha256",
           "kind": "RC stitched, verifier's own kpex run"},
}
REL = 1e-9
# Fallback for a column the 1e-9 path misses.  The two netlists differ BY CONSTRUCTION -- the
# platform's stitcher now CONTRACTS the zero-ohm `[Pin]` edges that the run behind the committed
# RC scorecard floored at 1 mOhm -- so the matrix is not the same matrix and the last couple of
# significant digits are not expected to be.  A spec metric is therefore checked against the bench
# resolution `brief.json` records; every other (diagnostic) column against 1e-4 relative, which is
# still four orders of magnitude tighter than any decision the row supports.
REL_DIAG = 1e-4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--row", choices=sorted(ROWS), required=True)
    ap.add_argument("--sign", action="store_true")
    a = ap.parse_args()
    cfg = ROWS[a.row]

    mine = json.loads(Path(cfg["mine"]).read_text())
    ref = json.loads(Path(cfg["ref"]).read_text())
    post = mine["post"]
    res = json.loads((CELL / "brief.json").read_text())["resolution"]

    hard, soft = [], []
    for k, v in ref["post"].items():
        got = post.get(k)
        if not isinstance(got, (int, float)) or isinstance(got, bool):
            hard.append((k, v, got, "not measured"))
            continue
        d = float(got) - float(v)
        if abs(d) <= REL * max(1.0, abs(float(v))):
            continue
        tol = res.get(k)
        lim = tol if tol is not None else REL_DIAG * max(1.0, abs(float(v)))
        why = f"delta {d:+.6g} ({abs(d) / max(1.0, abs(float(v))):.2e} rel), " + (
            f"bench resolution {tol:g}" if tol is not None else f"diagnostic column, limit {lim:.3g}")
        (soft if abs(d) <= lim else hard).append((k, v, got, why))

    print(f"row={a.row}  columns={len(ref['post'])}  exact(1e-9)={len(ref['post']) - len(hard) - len(soft)}"
          f"  within-resolution={len(soft)}  outside={len(hard)}")
    for k, v, got, why in soft + hard:
        print(f"    {k:24s} committed {v!r}  measured {got!r}  ({why})")
    if hard:
        return 1

    card = {k: v for k, v in post.items() if isinstance(v, float) and not math.isnan(v)}
    prov = provenance(C.H, cfg["tag"], card, corner="tt",
                      script="layout/postlayout.py", raw=cfg["raw"])
    viol = violations(C.H.spec, post)
    print(f"  spec violations: {viol or 'none'}")
    if not a.sign:
        print("  (dry run — pass --sign to append the ledger row)")
        return 0
    row = log_run(C.H, cfg["tag"], post, corner="tt", violations=viol, design=CANDIDATE.as_dict(),
                  evidence="signed", author="ldo-design-agent", verified_by="signoff-verifier",
                  extra={"benches": mine["bench_status"], "netlist": "extracted",
                         "pex_netlist_kind": cfg["kind"]},
                  **{k: prov[k] for k in hashes.HASH_KEYS})
    print(f"SIGNED {row['t']} {row['tag']} corner={row['corner']!r} exp={row['exp']!r} "
          f"violations={viol or 'none'} columns={len(card)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
