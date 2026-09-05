"""007 — the extracted cell outside tt/27: process/temperature corners and device mismatch.

review-004 F16: both scorecards of record are tt / 27 C, and both open rulings in
`layout/ldo_ihp_capless/PLAN.md` §6b depend on what happens away from that point. This
experiment measures it on the **committed extraction** — `layout/ldo_ihp_capless/asbuilt/
core_pex.sp`, the 3-pin block the post-layout scorecard was made from — through the cell's
own frozen benches, with the schematic row at the same corner as the control.

Two stages, both driven from the same spliced deck builder:

``corners``   5 MOS corner bundles (tt/ss/ff/sf/fs, each with its res/cap bundle) x
              -40 / 27 / 125 C, 13 benches, extracted AND schematic. 003-sizing ran this
              grid on the OLD sizing point; the re-certified cell (`bf3a4f8`, Iq 33.81 uA)
              has never been run at corners by either lane, so the schematic row is not a
              copy from 003 — it is re-measured here.
``mismatch``  sigma-injection on the two classes the brief prices below one sigma:
              `ea_nmos_load` (XM3/XM4, 0.61 sigma) and `bias_p_group` (XMBP/XMT/XM6,
              1.07 sigma). A class offset is a dc source in series with the gate of EVERY
              card the design device is drawn as, exactly as BRIEF.md section 6b does it;
              the platform's `inject_vsource` has the opposite sign to dVT, so a +dVT is
              injected as a negative gate source. The distribution itself is not simulated
              (see README, "Why sigma-injection and not a Monte Carlo").

    LDO_EXP=007 LDO_JOBS=12 uv run --no-sync python experiments/007-post-layout-corners/run.py \
        --stage corners
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "layout"))

from ldo import config as C  # noqa: E402
from ldo import metrics as M  # noqa: E402
from ldo.dut import CANDIDATE  # noqa: E402
from postlayout import run_frozen  # noqa: E402  (the frozen path, shared with 005)

CELL = "ldo_ihp_capless"
PEX = REPO / "layout" / CELL / "asbuilt" / "core_pex.sp"
OUT = HERE / "out"
TEMPS = (-40.0, 27.0, 125.0)

# ------------------------------------------------------------------ classes ----
# The extraction carries no design-device names: every MOS is `XMn_<k>`, so a class member is
# found by (model family, gate net, drain net, source net) — all of which ARE labelled, because
# the generator names its nets after the certified netlist. Each design device is drawn as two
# half-width cards (the re-certification, PLAN 0.1), so the finder asserts the count it expects.
CLASSES = {
    # class: {design device: (family, drain, gate, source, expected card count)}
    "ea_nmos_load": {
        "XM3": ("nmos", "ea_n", "ea_n", "vss", 2),     # the diode side — the dangerous sign
        "XM4": ("nmos", "ea_o1", "ea_n", "vss", 2),
    },
    "bias_p_group": {
        "XMBP": ("pmos", "pbias", "pbias", "vdd", 1),
        "XMT": ("pmos", "ea_tail", "pbias", "vdd", 1),
        "XM6": ("pmos", "ea_out", "pbias", "vdd", 1),
    },
}
# Which member carries the injection, and the sigma of the CLASS (pair sigma, brief.json).
INJECT_ON = {"ea_nmos_load": "XM3", "bias_p_group": "XMT"}


def block_text() -> str:
    return PEX.read_text()


def find_cards(block: str, family: str, drain: str, gate: str, source: str) -> list[str]:
    """Names of every extracted MOS card matching (family, d, g, s)."""
    out = []
    for ln in block.splitlines():
        t = ln.split()
        if len(t) < 6 or not t[0].upper().startswith("XM"):
            continue
        if not t[5].lower().endswith(f"_{family}"):
            continue
        if (t[1], t[2], t[3]) == (drain, gate, source):
            out.append(t[0])
    return out


def class_cards(block: str, cls: str) -> dict[str, list[str]]:
    got = {}
    for dev, (fam, d, g, s, n) in CLASSES[cls].items():
        cards = find_cards(block, fam, d, g, s)
        if len(cards) != n:
            raise SystemExit(f"{cls}/{dev}: expected {n} extracted card(s), found {cards}")
        got[dev] = cards
    return got


def inject_dvt(block: str, cards: list[str], dvt_mv: float) -> str:
    """+dvt_mv on every card of one design device.

    `sensitivity.inject_vsource` makes the device see ``net + dv`` on the chosen pin, so a
    threshold-voltage INCREASE of `dvt` is a gate source of `-dvt` (BRIEF.md section 6b).
    """
    from spicexplorer_signoff.sensitivity import inject_vsource

    for c in cards:
        block = inject_vsource(block, CELL, c, -dvt_mv * 1e-3, pin="g")
    return block


# ------------------------------------------------------------------- running ----
def decks_for(block: str, corner: str, temp: float, benches: list[str]) -> dict[str, str]:
    from spicexplorer_signoff.postlayout import splice_subckt

    d = CANDIDATE.at(corner, temp)
    return {b: splice_subckt(d.deck(b), block, CELL, check_pins=False) for b in benches}


def score(decks: dict[str, str], tag: str) -> dict:
    t0 = time.time()
    values, records = run_frozen(decks, tag)
    viol = M.violations(C.H.spec, values)
    return {"values": {k: v for k, v in values.items() if not k.startswith("_")},
            "violations": viol,
            "bench_status": {b: r["status"] for b, r in sorted(records.items())},
            "seconds": round(time.time() - t0, 1)}


def stage_corners(args) -> None:
    block = block_text()
    benches = CANDIDATE.benches()
    rows = {}
    grid = [(c, t) for c in C.CORNERS for t in TEMPS]
    if args.only:
        want = set(args.only.split(","))
        grid = [(c, t) for c, t in grid if f"{c}_{t:g}" in want or c in want]
    for corner, temp in grid:
        key = f"{corner}_{temp:g}"
        for which in ("pre", "post"):
            d = CANDIDATE.at(corner, temp)
            decks = ({b: d.deck(b) for b in benches} if which == "pre"
                     else decks_for(block, corner, temp, benches))
            r = score(decks, f"007_{key}_{which}")
            rows[f"{key}_{which}"] = r
            print(f"  {key:10s} {which:4s} {len(r['violations']):2d} violation(s) "
                  f"in {r['seconds']:6.1f}s", flush=True)
            (OUT / f"corner_{key}_{which}.json").write_text(json.dumps(r, indent=1) + "\n")
    print(f"wrote {len(rows)} corner row(s) to {OUT}")


def stage_mismatch(args) -> None:
    base = block_text()
    benches = CANDIDATE.benches()
    sigmas = json.loads((HERE / "sigma.json").read_text())
    for cls, dev in INJECT_ON.items():
        cards = class_cards(base, cls)[dev]
        sig = sigmas[cls]
        print(f"{cls}: injecting on {dev} = {cards}, 1 sigma = {sig} mV", flush=True)
        for k in args.sigma_points:
            dvt = round(k * sig, 6)
            blk = inject_dvt(base, cards, dvt)
            r = score(decks_for(blk, "tt", 27.0, benches), f"007_mm_{cls}_{k:+g}s")
            r.update({"class": cls, "device": dev, "cards": cards,
                      "sigma_mv": sig, "k_sigma": k, "dvt_mv": dvt})
            (OUT / f"mm_{cls}_{k:+g}s.json").write_text(json.dumps(r, indent=1) + "\n")
            s7 = r["values"].get("v_undershoot_mv")
            print(f"  {cls} {k:+g} sigma ({dvt:+.4f} mV): S7 {s7} "
                  f"{len(r['violations'])} violation(s)", flush=True)


def stage_mm_control(args) -> None:
    """Why the brief's cliff does not reproduce: the same dVT with the extracted C removed.

    BRIEF.md section 6b puts `ea_nmos_load` out of the box at +2.0 mV of dVT; on the extracted
    cell nothing moves out to +14.4 mV. Either the extracted capacitance damps the class, or the
    injection is not equivalent to the brief's. The control is the injection held fixed while the
    ONLY thing that changes is which extracted `Cext_` cards are present -- none, the EA node
    `ea_o1` alone (the net section 3 shows buys the cold-corner recovery), or all of them.
    """
    from postlayout import filter_caps

    base = block_text()
    benches = CANDIDATE.benches()
    cls = "ea_nmos_load"
    cards = class_cards(base, cls)[INJECT_ON[cls]]
    variants = {"allC": (None, None), "noC": ("__none__", None), "ea_o1": ("ea_o1", None)}
    for dvt in args.control_dvt:
        for name, (keep, drop) in variants.items():
            blk = base if keep is None else filter_caps(base, keep, drop or "")[0]
            blk = inject_dvt(blk, cards, dvt) if dvt else blk
            r = score(decks_for(blk, "tt", 27.0, benches), f"007_ctl_{name}_{dvt:+g}")
            r.update({"class": cls, "cards": cards, "caps": name, "dvt_mv": dvt})
            (OUT / f"ctl_{name}_{dvt:+g}mV.json").write_text(json.dumps(r, indent=1) + "\n")
            print(f"  {name:6s} dVT {dvt:+6.2f} mV: v_out {r['values'].get('v_out_v')} "
                  f"S7 {r['values'].get('v_undershoot_mv')} "
                  f"{len(r['violations'])} violation(s)", flush=True)


def stage_threshold(args) -> None:
    """Bisect the dVT that puts the cell out of the spec box, one bench batch per point."""
    base = block_text()
    benches = CANDIDATE.benches()
    sigmas = json.loads((HERE / "sigma.json").read_text())
    for cls, dev in INJECT_ON.items():
        cards = class_cards(base, cls)[dev]
        lo, hi = args.lo, args.hi          # mV, lo assumed in box, hi to be checked
        trail = []
        # A bisection is only meaningful if the bracket really brackets: check the top first.
        r = score(decks_for(inject_dvt(base, cards, hi), "tt", 27.0, benches),
                  f"007_th_{cls}_{hi:g}")
        trail.append({"dvt_mv": hi, "out_of_box": bool(r["violations"]),
                      "violations": r["violations"], "values": r["values"]})
        print(f"  {cls} {hi:+8.4f} mV -> {'OUT' if r['violations'] else 'in '} box "
              f"({len(r['violations'])})  [bracket top]", flush=True)
        if not r["violations"]:
            (OUT / f"threshold_{cls}.json").write_text(json.dumps(
                {"class": cls, "device": dev, "cards": cards, "sigma_mv": sigmas[cls],
                 "in_box_up_to_mv": hi, "out_of_box_from_mv": None,
                 "note": f"no crossing found up to {hi} mV = {hi / sigmas[cls]:.2f} sigma",
                 "trail": trail}, indent=1) + "\n")
            continue
        for _ in range(args.iters):
            mid = round((lo + hi) / 2, 4)
            blk = inject_dvt(base, cards, mid)
            r = score(decks_for(blk, "tt", 27.0, benches), f"007_th_{cls}_{mid:g}")
            out_of_box = bool(r["violations"])
            trail.append({"dvt_mv": mid, "out_of_box": out_of_box,
                          "violations": r["violations"], "values": r["values"]})
            print(f"  {cls} {mid:+8.4f} mV -> {'OUT' if out_of_box else 'in '} box "
                  f"({len(r['violations'])})", flush=True)
            if out_of_box:
                hi = mid
            else:
                lo = mid
        (OUT / f"threshold_{cls}.json").write_text(json.dumps(
            {"class": cls, "device": dev, "cards": cards, "sigma_mv": sigmas[cls],
             "in_box_up_to_mv": lo, "out_of_box_from_mv": hi, "note": "", "trail": trail},
            indent=1) + "\n")


# --------------------------------------------------------------------------------- tables ----
def _worst(op, vals):
    """The value furthest into violation for one spec line, and where it happens."""
    if op == ">=":
        return min(vals, key=lambda kv: kv[1])
    if op in ("<=", "in"):
        return max(vals, key=lambda kv: kv[1])
    return max(vals, key=lambda kv: kv[1])


def _fmt(x):
    return "—" if x is None else (f"{x:.4g}" if abs(x) < 1e4 else f"{x:.6g}")


def stage_tables(args) -> None:
    spec = {d.key: d for d in C.H.spec}
    rows = {}
    for f in sorted(OUT.glob("corner_*.json")):
        key = f.stem[len("corner_"):]
        rows[key] = json.loads(f.read_text())
    grid = [f"{c}_{t:g}" for c in C.CORNERS for t in TEMPS]

    # 1. the full grid, one row per corner, spec metrics only
    keys = [k for k in spec]
    md = ["| corner | " + " | ".join(f"`{k}`" for k in keys) + " | box |",
          "|" + "---|" * (len(keys) + 2)]
    for g in grid:
        for which in ("pre", "post"):
            r = rows.get(f"{g}_{which}")
            if r is None:
                continue
            v = r["values"]
            cells = []
            for k in keys:
                x = v.get(k)
                bad = any(spec[k].label.split(",")[0] in msg for msg in r["violations"])
                cells.append(("**" + _fmt(x) + "**") if bad else _fmt(x))
            md.append(f"| {g} {which} | " + " | ".join(cells) + " | "
                      + ("PASS" if not r["violations"] else f"FAIL ({len(r['violations'])})") + " |")
    (OUT / "grid.md").write_text("\n".join(md) + "\n")

    # 2. worst corner per metric, both rows
    # The delta column is taken AT THE POST-LAYOUT WORST CORNER -- subtracting two numbers
    # measured at different corners is not a layout effect, it is a corner effect (the S7 pair
    # 171.1 mV @ss_125 and 301.8 mV @sf_-40 differ by the corner, not by the parasitics).
    md2 = ["| spec | bound | worst pre-layout | at | worst post-layout | at | "
           "pre at the post worst | post - pre there |",
           "|---|---|---|---|---|---|---|---|"]
    for k, d in spec.items():
        b = d.bound
        bound = f"{d.op} {b}" if d.op != "in" else f"in {b[0]}..{b[1]}"
        cell = []
        for which in ("pre", "post"):
            vals = [(g, rows[f"{g}_{which}"]["values"].get(k))
                    for g in grid if f"{g}_{which}" in rows
                    and rows[f"{g}_{which}"]["values"].get(k) is not None]
            if not vals:
                cell.append((None, "—")); continue
            if d.op == "in":                       # furthest from the middle of the window
                mid = (b[0] + b[1]) / 2
                g, x = max(vals, key=lambda kv: abs(kv[1] - mid))
            else:
                g, x = _worst(d.op, vals)
            cell.append((x, g))
        (xp, gp), (xq, gq) = cell
        same = (rows.get(f"{gq}_pre") or {}).get("values", {}).get(k) if xq is not None else None
        delta = "—" if (same is None or xq is None) else _fmt(xq - same)
        md2.append(f"| {d.label} | {bound} {d.unit} | {_fmt(xp)} | {gp} | "
                   f"{_fmt(xq)} | {gq} | {_fmt(same)} | {delta} |")
    (OUT / "worst.md").write_text("\n".join(md2) + "\n")

    # 3. mismatch
    md3 = ["| class | injected on | k sigma | dVT (mV) | S7 (mV) | S6 (dB) | S1 (V) | box |",
           "|---|---|---|---|---|---|---|---|"]
    for f in sorted(OUT.glob("mm_*.json"), key=lambda p: (p.stem.split("_")[1], float(p.stem.split("_")[-1][:-1]))):
        r = json.loads(f.read_text()); v = r["values"]
        md3.append(f"| `{r['class']}` | `{r['device']}` ({len(r['cards'])} card) | {r['k_sigma']:+g} | "
                   f"{r['dvt_mv']:+.4f} | {_fmt(v.get('v_undershoot_mv'))} | "
                   f"{_fmt(v.get('psrr_1k_db'))} | {_fmt(v.get('v_out_v'))} | "
                   + ("PASS" if not r["violations"] else f"**FAIL** ({len(r['violations'])})") + " |")
    (OUT / "mismatch.md").write_text("\n".join(md3) + "\n")

    # 4. yield from the measured threshold
    md4 = ["| class | 1 sigma dVT | in box up to | out of box from | first spec line out | "
           "threshold / sigma | one-sided P(out of box) |", "|---|---|---|---|---|---|---|"]
    for f in sorted(OUT.glob("threshold_*.json")):
        r = json.loads(f.read_text())
        import math
        sig, thr = r["sigma_mv"], r["out_of_box_from_mv"]
        first = "—"
        if thr is not None:
            hits = [t for t in r["trail"] if t["dvt_mv"] == thr and t["violations"]]
            if hits:
                first = ", ".join(sorted({v.split(" ")[0] for v in hits[0]["violations"]}))
        if thr is None:
            k = r["in_box_up_to_mv"] / sig
            pr = 0.5 * math.erfc(k / math.sqrt(2))
            md4.append(f"| `{r['class']}` | {sig:.4f} mV | {r['in_box_up_to_mv']:.4f} mV | "
                       f"none up to {r['in_box_up_to_mv']:.4g} mV | {first} | > {k:.3f} | "
                       f"**< {pr * 100:.2g} %** |")
        else:
            k = thr / sig
            pr = 0.5 * math.erfc(k / math.sqrt(2))
            md4.append(f"| `{r['class']}` | {sig:.4f} mV | {r['in_box_up_to_mv']:.4f} mV | "
                       f"{thr:.4f} mV | {first} | {k:.3f} | **{pr * 100:.2g} %** |")
    (OUT / "yield.md").write_text("\n".join(md4) + "\n")

    # 5. the mismatch control: the same injection, three cap sets
    ctl = sorted(OUT.glob("ctl_*.json"), key=lambda q: (float(q.stem.split("_")[-1][:-2]), q.stem))
    if ctl:
        md5 = ["| extracted C kept | dVT on `XM3` (mV) | S1 v_out (V) | S7 undershoot (mV) | box |",
               "|---|---|---|---|---|"]
        for f in ctl:
            r = json.loads(f.read_text()); v = r["values"]
            md5.append(f"| {r['caps']} | {r['dvt_mv']:+g} | {_fmt(v.get('v_out_v'))} | "
                       f"{_fmt(v.get('v_undershoot_mv'))} | "
                       + ("PASS" if not r["violations"]
                          else "**FAIL** (" + "; ".join(x.split(" in ")[0].split(" <=")[0]
                                                        for x in r["violations"]) + ")") + " |")
        (OUT / "control.md").write_text("\n".join(md5) + "\n")

    for name in ("worst", "grid", "mismatch", "yield", "control"):
        if not (OUT / f"{name}.md").exists():
            continue
        print(f"\n### {name}\n")
        print((OUT / f"{name}.md").read_text())
    plots()


def plots() -> None:
    """S5/S7 across the grid, pre vs post — the two lines the corners move."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grid = [f"{c}_{t:g}" for c in C.CORNERS for t in TEMPS]
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
    for ax, (key, bound, lab) in zip(axes, (("i_q_ua", 50, "S5 quiescent current (uA)"),
                                            ("v_undershoot_mv", 150, "S7 undershoot (mV)"))):
        for which, mk in (("pre", "o"), ("post", "s")):
            xs, ys = [], []
            for i, g in enumerate(grid):
                f = OUT / f"corner_{g}_{which}.json"
                if not f.is_file():
                    continue
                v = json.loads(f.read_text())["values"].get(key)
                if v is not None:
                    xs.append(i); ys.append(v)
            ax.plot(xs, ys, mk + "-", label=f"{which}-layout", ms=4)
        ax.axhline(bound, color="crimson", lw=1, ls="--", label="spec")
        ax.set_ylabel(lab); ax.grid(alpha=.3)
    axes[0].legend(fontsize=8)
    axes[-1].set_xticks(range(len(grid)))
    axes[-1].set_xticklabels(grid, rotation=60, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(HERE / "figs" / "corners_s5_s7.png", dpi=150)
    print("wrote", HERE / "figs" / "corners_s5_s7.png")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("corners", "mismatch", "threshold", "control", "tables"))
    ap.add_argument("--only", default="", help="corners: a comma list of tt / tt_-40 keys")
    ap.add_argument("--sigma-points", default="-3,-2,-1,1,2,3",
                    type=lambda s: [float(x) for x in s.split(",")])
    ap.add_argument("--control-dvt", default="0,2",
                    type=lambda s: [float(x) for x in s.split(",")],
                    help="control: the dVT points (mV) to hold while the C set changes")
    ap.add_argument("--lo", type=float, default=0.0)
    ap.add_argument("--hi", type=float, default=6.0)
    ap.add_argument("--iters", type=int, default=5)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"extraction: {PEX} ({hashlib.sha256(PEX.read_bytes()).hexdigest()[:16]}…)", flush=True)
    {"corners": stage_corners, "mismatch": stage_mismatch,
     "threshold": stage_threshold, "control": stage_mm_control,
     "tables": stage_tables}[args.stage](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
