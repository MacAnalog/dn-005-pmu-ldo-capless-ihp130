"""Independent re-measure of the LDO's mismatch (claim 4) and corner (claim 5) claims.

Nothing here calls the designer's `experiments/007-post-layout-corners/run.py`.  The extracted
block is the verifier's OWN extraction (rebuilt GDS -> DRC/LVS/kpex CC -> `postlayout.pex_subckt`,
byte-identical to `layout/ldo_ihp_capless/asbuilt/core_pex.sp` bar kpex's date stamp); the class
members are found here by connectivity against the certified netlist's own device rows; and the
gate offset is inserted here by node renaming plus a series dc source, cross-checked once against
the platform's `inject_vsource` for equivalence.

    python verify_mismatch_corners.py --stage {check,mismatch,control,corners}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# this file lives at layout/<cell>/verify/, so the repo root is three levels up
REPO = Path(__file__).resolve().parents[3]
# the verifier's own work dir: neutral scratch root, never inside the repo, never /tmp
WORK = Path(os.environ.get("SX_SCRATCH") or (Path.home() / "sx-scratch")) / "ldo-verify"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "layout"))

from ldo import config as C  # noqa: E402
from ldo import metrics as M  # noqa: E402
from ldo.dut import CANDIDATE  # noqa: E402
from postlayout import filter_caps, run_frozen  # noqa: E402

CELL = "ldo_ihp_capless"
BLOCK = WORK / "post/extracted_subckt.spice"
OUT = WORK / "mm"

# (family, drain, gate, source) of each design device, read off the CERTIFIED netlist
# (circuits/ldo_ihp_capless/pdk/ihp-sg13g2/netlist.spice) -- XM3A/B and XM4A/B are the two
# half-width cards of the error-amp NMOS mirror load, XMT the error-amp tail of the PMOS bias
# group.  `n` is the number of extracted cards each design device must appear as.
DEVICES = {
    "XM3": ("nmos", "ea_n", "ea_n", "vss", 2),      # ea_nmos_load, diode side
    "XM4": ("nmos", "ea_o1", "ea_n", "vss", 2),     # ea_nmos_load, output leg
    "XMBP": ("pmos", "pbias", "pbias", "vdd", 1),   # bias_p_group, diode
    "XMT": ("pmos", "ea_tail", "pbias", "vdd", 1),  # bias_p_group, EA tail
    "XM6": ("pmos", "ea_out", "pbias", "vdd", 1),   # bias_p_group, stage-2 source
}
# The class, the member the offset is injected on, and the PAIR sigma of the class in mV of dVT
# (brief.json matching[].sigma.dvt_mv, re-derived below from the per-member sigmas).
CLASSES = {
    "ea_nmos_load": {"inject": "XM3", "sigma_mv": 1.6468, "edge_mv": 15.0},
    "bias_p_group": {"inject": "XMT", "sigma_mv": 1.1180, "edge_mv": 20.0},
}


def cards_of(block: str, dev: str) -> list[str]:
    fam, d, g, s, n = DEVICES[dev]
    out = []
    for ln in block.splitlines():
        t = ln.split()
        if len(t) < 6 or not t[0].upper().startswith("XM"):
            continue
        if t[5].lower().endswith(f"_{fam}") and (t[1], t[2], t[3]) == (d, g, s):
            out.append(t[0])
    if len(out) != n:
        raise SystemExit(f"{dev}: expected {n} extracted card(s) at ({fam},{d},{g},{s}), found {out}")
    return out


def inject_dvt(block: str, cards: list[str], dvt_mv: float) -> str:
    """A threshold-voltage INCREASE of `dvt_mv` on every named card.

    The card's gate node is renamed to a private node and a dc source ties it to the original
    net at `-dvt_mv`, so the device sees V(gate) - dvt.  This is the verifier's own
    implementation; `--stage check` proves it produces the same operating point as the
    platform's `inject_vsource(..., pin='g')` at -dvt.
    """
    if not dvt_mv:
        return block
    want, out, added = set(cards), [], []
    for ln in block.splitlines():
        t = ln.split()
        if t and t[0] in want and len(t) >= 6:
            priv = f"{t[2]}_vinj_{t[0]}"
            added.append(f"VINJ_{t[0]} {priv} {t[2]} dc {-dvt_mv * 1e-3:.9g}")
            t[2] = priv
            ln = " ".join(t)
        out.append(ln)
    txt = "\n".join(out)
    # the sources go just before the block's .ends
    m = list(re.finditer(r"(?im)^\.ends\b", txt))
    i = m[-1].start()
    return txt[:i] + "\n".join(added) + "\n" + txt[i:]


def score(block: str, tag: str, corner: str = "tt", temp: float = 27.0, pre: bool = False) -> dict:
    from spicexplorer_signoff.postlayout import splice_subckt

    d = CANDIDATE.at(corner, temp)
    benches = CANDIDATE.benches()
    decks = ({b: d.deck(b) for b in benches} if pre
             else {b: splice_subckt(d.deck(b), block, CELL, check_pins=False) for b in benches})
    t0 = time.time()
    values, records = run_frozen(decks, tag)
    viol = M.violations(C.H.spec, values)
    bad = {b: r["status"] for b, r in records.items() if r["status"] != "ok"}
    row = {"tag": tag, "corner": corner, "temp": temp, "row": "pre" if pre else "post",
           "values": {k: v for k, v in values.items() if not k.startswith("_")},
           "violations": viol, "bad_benches": bad, "seconds": round(time.time() - t0, 1)}
    v = row["values"]
    print(f"  {tag:34s} S1 {v.get('v_out_v'):.4f}  S5 {v.get('i_q_ua'):7.3f}  "
          f"S4 {v.get('v_dropout_mv'):7.2f}  S6 {v.get('psrr_1k_db'):6.2f}  "
          f"S7 {v.get('v_undershoot_mv'):7.2f}  S8 {v.get('pm_loop_deg'):6.2f}  "
          f"{'PASS' if not viol else 'FAIL: ' + '; '.join(x.split(' ')[0] for x in viol)}"
          + (f"  BAD {bad}" if bad else ""), flush=True)
    return row


def save(rows: list[dict], name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(rows, indent=1) + "\n")
    print("wrote", OUT / f"{name}.json")


def stage_check(_) -> None:
    """Card census + the injection cross-check against the platform's own helper."""
    from spicexplorer_signoff.sensitivity import inject_vsource

    block = BLOCK.read_text()
    print("extracted cards found by connectivity:")
    for dev in DEVICES:
        print(f"  {dev:6s} {DEVICES[dev][:4]} -> {cards_of(block, dev)}")
    # sigma re-derivation from brief.json's per-member sigmas
    brief = json.loads((REPO / "layout" / CELL / "brief.json").read_text())
    for m in brief.get("matching", []):
        if m.get("class") in CLASSES:
            s = [x["sigma_vt_mv"] for x in m["members"]]
            pair = sum(v * v for v in s[:2]) ** 0.5
            print(f"  {m['class']}: members sigma {s} -> pair {pair:.4f} mV "
                  f"(brief says {m['sigma']['dvt_mv']}, tolerated {m['tolerated']['dvt_mv']}, "
                  f"headroom {m['tolerated']['dvt_mv'] / m['sigma']['dvt_mv']:.3f} sigma)")
    # equivalence of the two injections at +2 mV on XM3
    cards = cards_of(block, "XM3")
    mine = inject_dvt(block, cards, 2.0)
    theirs = block
    for c in cards:
        theirs = inject_vsource(theirs, CELL, c, -2.0e-3, pin="g")
    a = score(mine, "chk_mine_xm3_p2")
    b = score(theirs, "chk_platform_xm3_p2")
    same = all(abs(a["values"][k] - b["values"][k]) <= 1e-9 * max(1, abs(b["values"][k]))
               for k in b["values"] if isinstance(b["values"][k], float))
    print(f"  injections agree to 1e-9 relative on every metric: {same}")
    save([a, b], "check")


def stage_mismatch(_) -> None:
    block = BLOCK.read_text()
    rows = [score(block, "mm_nominal")]
    for cls, cfg in CLASSES.items():
        cards = cards_of(block, cfg["inject"])
        for k in (-3, -1, +1, +3):
            dvt = k * cfg["sigma_mv"]
            rows.append({**score(inject_dvt(block, cards, dvt),
                                 f"mm_{cls}_{k:+d}sig"), "class": cls, "k_sigma": k, "dvt_mv": dvt})
        for dvt in (cfg["edge_mv"] - 0.625, cfg["edge_mv"]):
            rows.append({**score(inject_dvt(block, cards, dvt),
                                 f"mm_{cls}_p{dvt:g}mV"), "class": cls,
                         "k_sigma": dvt / cfg["sigma_mv"], "dvt_mv": dvt})
    save(rows, "mismatch")


def stage_control(_) -> None:
    """The designer's two controls: +2.0 mV on XM3 with the extracted C deleted, and with only
    `ea_o1`'s C kept."""
    block = BLOCK.read_text()
    cards = cards_of(block, "XM3")
    rows = []
    for label, keep, no_c in (("allC", "", False), ("ea_o1", "ea_o1", False), ("noC", "", True)):
        for dvt in (0.0, 2.0):
            b = block
            if no_c or keep:
                b, left, gone = filter_caps(b, "__none__" if no_c else keep, "")
                print(f"    [{label}] kept {left} Cext card(s), dropped {gone}")
            b = inject_dvt(b, cards, dvt)
            rows.append({**score(b, f"ctl_{label}_dvt{dvt:g}"), "cset": label, "dvt_mv": dvt})
    save(rows, "control")


def stage_corners(a) -> None:
    block = BLOCK.read_text()
    grid = [("ff", 125.0, False), ("ff", 125.0, True),   # S5 58.37 pre AND post
            ("ss", 125.0, False), ("ss", 125.0, True),   # S7 171.1 post (152.8 pre)
            ("sf", -40.0, False), ("sf", -40.0, True)]   # S7 301.8 pre
    rows = [score(block, f"cnr_{c}_{t:g}_{'pre' if pre else 'post'}", corner=c, temp=t, pre=pre)
            for c, t, pre in grid]
    save(rows, "corners")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True,
                    choices=("check", "mismatch", "control", "corners"))
    args = ap.parse_args()
    {"check": stage_check, "mismatch": stage_mismatch,
     "control": stage_control, "corners": stage_corners}[args.stage](args)
