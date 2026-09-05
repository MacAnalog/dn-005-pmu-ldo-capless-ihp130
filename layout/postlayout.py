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
import datetime
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


# The 2.5D R mesh anchors a named net on its `[Pin]` node with a **zero-ohm** resistor -- the
# stitcher means "merge these two nodes".  ngspice does not merge: it clamps the value to 1e-12
# ohm and puts a 1e12 S entry into a conductance matrix whose signal entries are ~1e-5 S, and the
# direct solve then returns an operating point that is not a solution of the network.  It is not
# a convergence failure -- it converges, silently, to the wrong answer, and it does so with both
# SPARSE and KLU and with a `.nodeset` seeded from the correct solution.  Measured on the LDO's
# feedback divider, sixteen IDENTICAL 126 kOhm segments in series between vout and vss:
#
#     two 0-ohm ties present   fb = 9.99 mV   (top half drops 186.25 mV/segment, bottom 1.25)
#     the same two at 1e-3     fb = 599.7 mV  (uniform 75 mV/segment, vout 1.1995 V, Iq 33.77 uA)
#
# The first row violates KCL at `fb` by 1.5 uA with no path to carry it, and it survives the
# resistors being replaced by ideal linear ones -- so it is arithmetic, not a model.  A finite
# floor is the smallest honest repair: 1 mOhm against a mesh whose own segments are 0.2-20 ohm
# adds at most a nanovolt, and unlike a node merge it leaves the netlist's shape (and every node
# name a reviewer might probe) intact.
R_FLOOR = 1e-3
_R_MESH = re.compile(r"^(R\S*)\s+(\S+)\s+(\S+)\s+([-+.\deE]+)\s*(.*)$")


def floor_zero_r(txt: str) -> tuple[str, int]:
    """Give every zero-valued mesh resistor a finite value; return the text and the count."""
    out, n = [], 0
    for ln in txt.splitlines():
        m = _R_MESH.match(ln)
        if m and m.group(1).lower().startswith("rext"):
            try:
                v = float(m.group(4))
            except ValueError:
                out.append(ln); continue
            if v == 0.0:
                n += 1
                ln = f"{m.group(1)} {m.group(2)} {m.group(3)} {R_FLOOR:g}" + (
                    f" {m.group(5)}" if m.group(5) else "")
        out.append(ln)
    return "\n".join(out) + ("\n" if txt.endswith("\n") else ""), n


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

    raw = Path(pex_netlist).read_text()
    # An already-prepared block (`asbuilt/core_pex.sp`, `extracted_subckt.spice`) is NOT an
    # extractor output: preparing it twice re-inserts VREF/VSUBSTIE/VLP and the three MIM cards
    # a second time and every bench fails at the operating point.  Say so instead of doing it.
    if "VSUBSTIE" in raw:
        raise SystemExit(f"{pex_netlist} is already a prepared block (it carries VSUBSTIE) — "
                         "point --netlist at the extractor's own output, or read it directly")
    txt = ngspice_cards(prep_pex_subckt(pex_netlist, CELL))
    txt, n_zero = floor_zero_r(txt)
    if n_zero:
        print(f"pex: {n_zero} zero-ohm mesh tie(s) floored at {R_FLOOR:g} Ohm", flush=True)
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


_C_CARD = re.compile(r"^(C\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s*$")


def filter_caps(block: str, keep: str = "", drop: str = "") -> tuple[str, int, int]:
    """Delete extracted coupling/ground capacitors, for a what-if.

    ``keep`` (comma list) keeps only the `Cext_` cards that touch one of those nets; ``drop``
    keeps everything except those.  Nothing else in the block changes, so the difference between
    two runs is exactly the capacitance named — this is how "the `gate` parasitics alone move S7
    by X" is measured rather than asserted (review-003 F3).  The re-inserted MIM cards are `X`
    calls, not `C` cards, so they always survive."""
    kk = {n for n in keep.split(",") if n}
    dd = {n for n in drop.split(",") if n}
    out, gone, left = [], 0, 0
    for ln in block.splitlines():
        m = _C_CARD.match(ln.strip())
        if m and m.group(1).lower().startswith("cext"):
            nets = {m.group(2), m.group(3)}
            hit = bool(nets & kk) if kk else not (nets & dd)
            if not hit:
                gone += 1
                continue
            left += 1
        out.append(ln)
    return "\n".join(out) + "\n", left, gone


def insert_vss_return(block: str, ohm: float, kelvin: str = "XCOUT") -> tuple[str, int]:
    """What-if: put the drawn `vss` return resistance in circuit (review-004 **F9**).

    The extraction is CC, so it carries no wire resistance at all: the committed `psrr_1k` is
    measured with an IDEAL ground return. This renames `vss` to `vss_ret` on every card inside
    the block except the subckt header and the Kelvin-returned devices (`XCOUT`, whose bottom
    plate has its own strap to the pin — PLAN A10), and adds one resistor `vss_ret -> vss`.
    `ohm` is therefore the COMMON series element, the quantity F9 says the budget should be
    written on; the per-device spread beyond it is a separate, much smaller term.
    """
    keep = {k.strip().upper() for k in kelvin.split(",") if k.strip()}
    out, touched = [], 0
    for ln in block.splitlines():
        t = ln.split()
        if (t and not ln.lstrip().startswith("*") and not ln.lstrip().startswith(".")
                and t[0].upper() not in keep and "vss" in t[1:]):
            ln = " ".join([t[0]] + ["vss_ret" if x == "vss" else x for x in t[1:]])
            touched += 1
        out.append(ln)
    txt = "\n".join(out)
    i = txt.lower().rindex(".ends")
    return txt[:i] + f"Rvssret vss_ret vss {ohm:g}\n" + txt[i:] + "\n", touched


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


def select_pex_netlist(pex_dir, explicit: str | None = None,
                       record: str | None = None) -> tuple[Path, str]:
    """`(path, "raw"|"stitched")` — WHICH extracted netlist the benches measure.

    review-004 **F27**. For an RC/R run the platform writes two files side by side:

    * ``<cell>_k25d_pex_netlist.spice`` — kpex's own output, whose resistor mesh is an
      electrical island (no card joins a mesh node to a device pin), and
    * ``<cell>_k25d_pex_netlist_stitched.spice`` — the repaired one, which is what
      ``PexResult.netlist_path`` names.

    The old rule here was ``rglob("*_pex_netlist.spice")`` + "exactly one match". The stitched
    name does not match that pattern, so with both files present the glob found exactly one,
    reported no ambiguity, and measured the netlist the extractor did **not** name — a scorecard
    from the unstitched file, silently. Hence: an explicit path wins, else the PEX stage's own
    record (`signoff.json` → `pex.netlist`), else the directory — and if the directory holds both
    kinds and nobody said which, this raises instead of choosing.
    """
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise SystemExit(f"--netlist {p} does not exist")
        return p, ("stitched" if p.name.endswith("_stitched.spice") else "raw")
    if record:
        rp = Path(record)
        if rp.is_file():
            named = ((json.loads(rp.read_text()).get("pex") or {}).get("netlist"))
            if named and Path(named).is_file():
                p = Path(named)
                # The record is only evidence about the directory it belongs to. A run dir that
                # holds a CC stage AND an RC stage has ONE signoff.json, whose `pex.netlist` is
                # whichever stage wrote last -- so honouring it while the caller asked for the
                # other stage's directory measures the wrong extraction and says the right name
                # (review-005: `--pex .../pex_rc --record .../signoff.json` silently scored the
                # CC netlist). If they disagree, the explicit directory wins and says so.
                if Path(pex_dir).resolve() in p.resolve().parents:
                    return p, ("stitched" if p.name.endswith("_stitched.spice") else "raw")
                print(f"note: {rp} names {p}, which is not under the requested {pex_dir}; "
                      "reading the directory instead", flush=True)
    pex_dir = Path(pex_dir)
    stitched = sorted(pex_dir.rglob("*_pex_netlist_stitched.spice"))
    raw = sorted(pex_dir.rglob("*_pex_netlist.spice"))   # does NOT match the stitched name
    hits = [(p, "stitched") for p in stitched] + [(p, "raw") for p in raw]
    if not hits:
        raise SystemExit(f"no kpex netlist under {pex_dir} — run layout/signoff.py first")
    # One RC run leaves a matched PAIR: `<stem>.spice` and `<stem>_stitched.spice`.  The stitched
    # one is the netlist `PexResult.netlist_path` names and the only one whose mesh is in the
    # circuit, so the pair is not an ambiguity — it is answered, loudly.  Anything else (two runs
    # under one directory) is an ambiguity and stops.
    if len(stitched) == 1 and len(raw) == 1 and raw[0].stem + "_stitched" == stitched[0].stem:
        print(f"note: {pex_dir} holds an RC pair; measuring the STITCHED netlist "
              f"({stitched[0].name}) — the raw one's resistor mesh is not in the circuit. "
              "Pass --netlist to override.", flush=True)
        return stitched[0], "stitched"
    if len(hits) > 1:
        raise SystemExit(
            f"{len(hits)} extracted netlists under {pex_dir} (stitched: {len(stitched)}, "
            "raw: {}); name the one THIS scorecard measures with --netlist:\n  ".format(len(raw))
            + "\n  ".join(f"{p} [{k}] ({datetime.datetime.fromtimestamp(p.stat().st_mtime)})"
                          for p, k in hits))
    return hits[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pex", default=str(C.WORK / "layout" / "pex"))
    ap.add_argument("--tag", default="005_postlayout")
    ap.add_argument("--keep-c", default="", help="what-if: keep only the extracted C on these nets")
    ap.add_argument("--drop-c", default="", help="what-if: drop the extracted C on these nets")
    ap.add_argument("--no-c", action="store_true", help="what-if: drop every extracted C")
    ap.add_argument("--add-c", default="",
                    help="what-if: add lumped capacitance, 'net:fF[,net:fF]' to vss "
                         "(review-004 F3: the in-situ headroom of a net)")
    ap.add_argument("--vss-r", type=float, default=None,
                    help="what-if: insert the drawn vss return resistance (Ohm) between the "
                         "internal ground and the pin, XCOUT excepted (review-004 F9)")
    ap.add_argument("--out-dir", default=None,
                    help="where the scorecard goes (a what-if must NOT overwrite the record)")
    ap.add_argument("--netlist", default=None,
                    help="the extracted netlist to measure (review-004 F27); default: the PEX "
                         "stage's own record, else the only one under --pex")
    ap.add_argument("--record", default=None,
                    help="signoff.json naming the netlist; default <--pex>/../signoff.json")
    a = ap.parse_args()
    whatif = bool(a.keep_c or a.drop_c or a.no_c or a.add_c or a.vss_r is not None)
    out_dir = Path(a.out_dir) if a.out_dir else OUT
    if whatif and out_dir == OUT:
        raise SystemExit("a what-if run needs --out-dir: it must not overwrite the record")
    out_dir.mkdir(parents=True, exist_ok=True)

    # review-003 **F17** (freshness) and review-004 **F27** (identity) are one decision, and it
    # is made in `select_pex_netlist` so it can be tested without a simulator.
    rec = a.record or str(Path(a.pex).parent / "signoff.json")
    netlist, kind = select_pex_netlist(a.pex, explicit=a.netlist, record=rec)
    print(f"pex netlist: {netlist} [{kind}]", flush=True)
    block = pex_subckt(netlist)
    if a.keep_c or a.drop_c or a.no_c:
        block, left, gone = filter_caps(block, "__none__" if a.no_c else a.keep_c, a.drop_c)
        print(f"what-if: kept {left} extracted C card(s), dropped {gone}", flush=True)
    if a.add_c:
        from spicexplorer_signoff.sensitivity import inject_caps
        caps = [(n.split(":")[0], "vss", float(n.split(":")[1]) * 1e-15)
                for n in a.add_c.split(",") if n]
        block = inject_caps(block, CELL, caps)
        print("what-if: added " + ", ".join(f"{a_}->{b} {v * 1e15:g} fF" for a_, b, v in caps),
              flush=True)
    if a.vss_r is not None:
        block, n = insert_vss_return(block, a.vss_r)
        print(f"what-if: {a.vss_r} Ohm vss return, {n} card(s) moved off the pin", flush=True)
    (out_dir / "extracted_subckt.spice").write_text(block)

    from spicexplorer_signoff.postlayout import splice_subckt

    benches = CANDIDATE.benches()
    pre_decks = {b: CANDIDATE.deck(b) for b in benches}
    post_decks = {b: splice_subckt(pre_decks[b], block, CELL, check_pins=False) for b in benches}

    if whatif:
        pre, pre_rec = {}, {}
    else:
        print("pre-layout:", flush=True)
        pre, pre_rec = run_frozen(pre_decks, f"{a.tag}_pre")
    print("post-layout:", flush=True)
    post, post_rec = run_frozen(post_decks, f"{a.tag}_post")
    for b, r in sorted(post_rec.items()):
        if r["status"] != "ok":
            print(f"    {b}: {r['status']}")
    for row, d in (((pre, "pre"), (post, "post")) if not whatif else ((post, "post"),)):
        row["_violations"] = M.violations(C.H.spec, row)
        print(f"  {d}: {len(row['_violations'])} violation(s)")

    # One `evaluate` row per scorecard, so `make runs --kind evaluate` can find them. The
    # post-layout row is a DELIVERY CLAIM, so it is logged `evidence="awaiting"` exactly as
    # `metrics.certify()` logs a certification: the signature is the verifier's own re-measure
    # (rule 7, designer != verifier), never the designer's. The pre-layout row is the control and
    # stays `scratch` -- the certified pre-layout scorecard lives in decks/candidate/.
    if whatif:
        table = M.table({"post-layout (what-if)": post}, cols=M.COLS_CANDIDATE)
        (out_dir / "scorecard.md").write_text(table + "\n")
        (out_dir / "scorecard.json").write_text(json.dumps(
            {"post": {k: v for k, v in post.items() if not k.startswith("_")},
             "post_violations": post["_violations"],
             "whatif": {"keep_c": a.keep_c, "drop_c": a.drop_c, "no_c": a.no_c,
                        "add_c": a.add_c, "vss_r": a.vss_r},
             "pex_netlist": str(netlist), "pex_netlist_kind": kind}, indent=1) + "\n")
        print("\n" + table)
        return 0
    M.log_run(C.H, f"{a.tag}_pre", {k: v for k, v in pre.items() if not k.startswith("_")},
              violations=pre["_violations"], design=CANDIDATE.as_dict(),
              extra={"benches": {b: r["status"] for b, r in pre_rec.items()}, "netlist": "schematic"})
    M.log_run(C.H, f"{a.tag}_post", {k: v for k, v in post.items() if not k.startswith("_")},
              violations=post["_violations"], design=CANDIDATE.as_dict(), evidence="awaiting",
              extra={"benches": {b: r["status"] for b, r in post_rec.items()},
                     "netlist": "extracted", "pex_netlist": str(netlist),
                     "pex_netlist_kind": kind})

    table = M.table({"pre-layout (schematic)": pre, "post-layout (extracted)": post},
                    cols=M.COLS_CANDIDATE)
    (out_dir / "scorecard.md").write_text(table + "\n")
    (out_dir / "scorecard.json").write_text(json.dumps(
        {"pre": {k: v for k, v in pre.items() if not k.startswith("_")},
         "post": {k: v for k, v in post.items() if not k.startswith("_")},
         "pre_violations": pre["_violations"], "post_violations": post["_violations"],
         "bench_status": {b: r["status"] for b, r in sorted(post_rec.items())},
         "pex_netlist": str(netlist), "pex_netlist_kind": kind}, indent=1) + "\n")
    print("\n" + table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
