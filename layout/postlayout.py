"""005 — the post-layout scorecard: the cell's OWN frozen benches on the extracted netlist.

The rule (`doc/benches.md`) is that post-layout numbers come from the same bench definitions as
pre-layout ones, so nothing here measures anything new -- it only makes the kpex-extracted
subcircuit a drop-in replacement for the schematic `.subckt ldo_ihp_capless vdd vout vss`:

1. ``prep_pex_subckt`` rewrites the extractor's primitive ``M`` cards as ``XM`` (the IHP ngspice
   devices are subcircuits).
2. Every labelled net becomes a pin of the extracted block, and ``VREF`` / the loop-break marker
   ``VLP`` are sources rather than drawn devices. Both sources are put BACK INSIDE the block and
   the header is narrowed to the schematic's three pins, so `vref`/`lp_brk`/`fb`/... become
   internal nodes exactly as in the schematic. kpex's substrate node ``VSUBS`` is tied to `vss`.
3. The three MIM capacitors are re-attached by name. kpex cannot extract ``cap_cmim``
   (`spicexplorer_signoff.pex` docstring), so their plates are stripped from the GDS before
   extraction; the layout's own labels give `fb`, `ea_out`, `ea_o1` real names to hang them on.
   **What this costs is stated, not hidden:** MIM bottom-plate (Metal5) coupling to the
   neighbourhood IS extracted, top-plate coupling is not.

    LDO_EXP=005 uv run --no-sync python layout/postlayout.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ldo import config as C  # noqa: E402
from ldo import metrics as M  # noqa: E402
from ldo import sim  # noqa: E402
from ldo.dut import CANDIDATE  # noqa: E402

CELL = "ldo_ihp_capless"
OUT = Path(__file__).resolve().parents[1] / "experiments" / "005-layout" / "out"

# The devices the layout does not carry, re-inserted inside the extracted block. Values stay
# symbolic: the deck's own `.param` block (from sizing.yaml) binds them, so the post-layout deck
# and the pre-layout deck are the same sizing point by construction.
REINSERT = """VREF vref vss dc {vref_val}
* kpex hangs every extracted ground capacitance on a substrate node VSUBS that is NOT in the
* subckt pin list; the p-substrate is at vss through the layout's own ptap ring, so tie it (a 0 V
* source rather than a rename, so the substrate branch stays visible to a reviewer). Without this
* the operating point is singular at `xdut.vsubs`.
VSUBSTIE VSUBS vss dc 0
VLP lp_brk vout dc 0
XCFF lp_brk fb cap_cmim w=c_ff_w l=c_ff_w
XCC ea_out ea_o1 cap_cmim w=c_comp_w l=c_comp_w
XCOUT vout vss cap_cmim w=c_out_w l=c_out_w m=c_out_m"""


# kpex writes an extracted poly resistor as a THREE-node primitive card,
#   ``R$36 lp_brk \\$37 vss 0.5 rhigh l=85 ps=0 b=0 m=1``   (w and l in um, no suffix)
# but ngspice's IHP ``rhigh`` is a 3-terminal SUBCIRCUIT (``.subckt rhigh 1 2 bn``), so the card
# has to become an ``XR`` call or ngspice reports ``unknown parameter (vss)`` -- it is trying to
# read the third node as the resistance. Journal: doc/journal/kpex-cards-are-not-ngspice-cards.md.
_RES_CARD = re.compile(
    r"^(R\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+([-+.\d eE]+?)\s+(rhigh|rppd|rsil)\s*(.*)$", re.I)
_L_PARAM = re.compile(r"\bl\s*=\s*([-+.\deE]+)", re.I)


def ngspice_cards(txt: str) -> str:
    """kpex element cards -> cards ngspice can read."""
    out = []
    for ln in txt.splitlines():
        s = ln.strip()
        m = _RES_CARD.match(s)
        if m:
            name, n1, n2, n3, w, model, rest = m.groups()
            lm = _L_PARAM.search(rest)
            length = f"{float(lm.group(1)):g}u" if lm else "1u"
            rest = _L_PARAM.sub("", rest).strip()
            keep = " ".join(p for p in rest.split() if p.split("=")[0].lower() in ("m",))
            ln = f"X{name} {n1} {n2} {n3} {model} w={float(w):g}u l={length}" + (f" {keep}" if keep else "")
        out.append(ln)
    # `$` opens an in-line comment in SPICE, so the extractor's anonymous nets (`\$21`) must be
    # renamed before ngspice ever sees them.
    return re.sub(r"\\?\$(\w+)", r"n_\1", "\n".join(out)) + "\n"


def pex_subckt(pex_netlist: Path) -> str:
    """The extracted block, made pin-compatible with the schematic subckt."""
    from spicexplorer_signoff.postlayout import prep_pex_subckt

    txt = ngspice_cards(prep_pex_subckt(pex_netlist, CELL))
    # The header spills onto `+` continuation lines: every labelled net becomes a pin, so the
    # extracted block has ~15 of them where the schematic subckt has three.
    m = re.search(rf"(?im)^\.subckt\s+{CELL}\b[^\n]*\n(?:\+[^\n]*\n)*", txt)
    if not m:
        raise SystemExit(f"no .subckt {CELL} in {pex_netlist}")
    head = m.group(0)
    pins = [w for w in re.sub(r"(?m)^\+", " ", head).split()[2:] if "=" not in w]
    missing = {"vdd", "vout", "vss"} - {p.lower() for p in pins}
    if missing:
        raise SystemExit(f"extracted subckt is missing pin(s) {sorted(missing)}: {pins}")
    # Narrow the header to the schematic's three pins; every other labelled net (vref, lp_brk,
    # fb, ea_out ...) becomes an internal node again, which is what the benches expect.
    txt = txt[: m.start()] + f".subckt {CELL} vdd vout vss\n" + REINSERT + "\n" + txt[m.end():]
    return txt


def run_frozen(decks: dict[str, str], tag: str) -> tuple[dict, dict]:
    """Score `decks` through the FROZEN measurement path -- `ldo.sim.run` + `ldo.metrics.promote`,
    the same two calls `ldo.metrics.evaluate` makes for the pre-layout row.

    This used to be `run_tolerant`, a local rule that re-parsed the log whenever the only fatal
    line was ngspice's benign `Warning: singular matrix` from gmin stepping. That override existed
    because `ldo/sim.py` carried its own fatal-line table which ranked the bare substring above
    the warning prefix; the platform's classifier, which `ldo/sim.py` now calls, already gets this
    right. Rule 2 says the frozen definitions certify, so the post-layout row and the pre-layout
    row it is compared against must come from one path -- with the override in place they did not
    (review-002 M4/M5)."""
    from spicexplorer_harness import batch

    def one(bench: str):
        try:
            r = sim.run(decks[bench], f"{tag}__{bench}")
            return bench, {"status": "ok", "measures": r.measures}
        except sim.SimError as exc:
            return bench, {"status": "sim_error", "measures": {}, "error": str(exc)[:400]}

    records = dict(batch(list(decks), one, env=C.H.jobs_env, on_error="raise"))
    values: dict = {}
    for bench, rec in records.items():
        if rec["status"] == "ok":
            values.update(M.promote(bench, rec["measures"]))
    return values, records


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pex", default=str(C.WORK / "layout" / "pex"))
    ap.add_argument("--tag", default="005_postlayout")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    hits = sorted(Path(a.pex).rglob("*_pex_netlist.spice"))
    if not hits:
        raise SystemExit(f"no kpex netlist under {a.pex} — run layout/signoff.py first")
    block = pex_subckt(hits[-1])
    (OUT / "extracted_subckt.spice").write_text(block)

    from spicexplorer_signoff.postlayout import splice_subckt

    benches = CANDIDATE.benches()
    pre_decks = {b: CANDIDATE.deck(b) for b in benches}
    post_decks = {b: splice_subckt(pre_decks[b], block, CELL, check_pins=False) for b in benches}

    print("pre-layout:", flush=True)
    pre, pre_rec = run_frozen(pre_decks, f"{a.tag}_pre")
    print("post-layout:", flush=True)
    post, post_rec = run_frozen(post_decks, f"{a.tag}_post")
    for b, r in sorted(post_rec.items()):
        if r["status"] != "ok":
            print(f"    {b}: {r['status']}")
    for row, d in ((pre, "pre"), (post, "post")):
        row["_violations"] = M.violations(C.H.spec, row)
        print(f"  {d}: {len(row['_violations'])} violation(s)")

    table = M.table({"pre-layout (schematic)": pre, "post-layout (extracted)": post},
                    cols=M.COLS_CANDIDATE)
    (OUT / "scorecard.md").write_text(table + "\n")
    (OUT / "scorecard.json").write_text(json.dumps(
        {"pre": {k: v for k, v in pre.items() if not k.startswith("_")},
         "post": {k: v for k, v in post.items() if not k.startswith("_")},
         "pre_violations": pre["_violations"], "post_violations": post["_violations"],
         "bench_status": {b: r["status"] for b, r in sorted(post_rec.items())},
         "pex_netlist": str(hits[-1])}, indent=1) + "\n")
    print("\n" + table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
