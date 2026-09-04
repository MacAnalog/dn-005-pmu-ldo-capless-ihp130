"""004 — the schematic of record: netlist -> xschem .sch -> PNG, proven equal to the netlist.

The reviewable artefact of the cell is a drawing, and the only drawing worth having is one that
provably IS the certified netlist (`.claude/skills/schematic-of-record`). So:

1. The input is the frozen `decks/candidate/dc_op.spice` -- the certified deck, byte for byte,
   not a rebuild -- and `--into XDUT` descends into the cell itself.
2. `spicexplorer_netlist2xschem` places and wires every device; `--render png` gives the figure.
3. `spicexplorer_circuitgraph` re-netlists nothing and compares nothing by eye: it builds the
   device/connectivity graph of the ORIGINAL netlist and of the netlist xschem writes back out
   of the drawing, and reports whether they are the same circuit.

    LDO_EXP=004 uv run --no-sync python experiments/004-schematic/build_sch.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[2]
FIGS = HERE / "figs"
OUT = HERE / "out"
CELL = "ldo_ihp_capless"
DECK = REPO / "decks" / "candidate" / "dc_op.spice"
# The .sch is the DELIVERABLE, not a run artefact, so it is written beside the circuit it draws
# and committed -- `experiments/*/out/` is git-ignored and would have swallowed it. The xschemrc
# netlist2xschem drops next to it is host-specific (absolute PDK library paths) and stays ignored.
SCH_DIR = REPO / "circuits" / CELL / "xschem"


def _certified_subckt(deck: Path) -> str:
    """The cell subckt out of the frozen deck, verbatim (plus its `.param` bindings)."""
    lines = deck.read_text().splitlines()
    params = [ln for ln in lines if ln.lower().startswith(".param")]
    i = next(i for i, ln in enumerate(lines) if ln.lower().startswith(f".subckt {CELL}"))
    j = next(j for j in range(i, len(lines)) if lines[j].lower().startswith(".ends"))
    body = [ln for ln in lines[i + 1:j] if ln.strip()]
    return "* certified cell out of " + deck.name + " (flat)\n" + "\n".join(params + body) + "\n.end\n"


def _run_xschem(sch: Path, rcfile: Path, out: Path) -> dict:
    """Netlist the drawing back out. xschem needs its own rcfile for the PDK symbol libraries;
    netlist2xschem writes one beside the .sch."""
    xschem = "xschem"
    cmd = [xschem, "-n", "-q", "-r", "--rcfile", str(rcfile), "-o", str(out), str(sch)]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(out))
    return {"cmd": " ".join(cmd), "rc": r.returncode,
            "netlist": str(out / f"{CELL}.spice") if (out / f"{CELL}.spice").is_file() else None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", default=str(DECK))
    a = ap.parse_args()
    FIGS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    SCH_DIR.mkdir(parents=True, exist_ok=True)
    sch, png = SCH_DIR / f"{CELL}.sch", FIGS / f"{CELL}.png"

    cmd = [sys.executable, "-m", "spicexplorer_netlist2xschem.cli", a.deck,
           "--into", "XDUT", "--name", CELL, "-o", str(sch),
           "--render", "png", "--out-image", str(png), "--show-params"]
    print("$", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    print((r.stdout + r.stderr)[-1500:])
    if not sch.is_file():
        raise SystemExit("no .sch produced")

    rec: dict = {"sch": str(sch), "png": str(png) if png.is_file() else None, "deck": a.deck,
                 "skipped": [ln.split(":")[0].replace("skipping ", "").strip()
                             for ln in (r.stdout + r.stderr).splitlines() if ln.startswith("skipping ")]}

    # --- drawing == netlist -------------------------------------------------
    # xschem netlists the DRAWING back out; circuitgraph then compares that netlist with the
    # certified one as graphs (devices, models, connectivity), which is the only comparison worth
    # making -- a .sch is a drawing file, not a netlist, so it is never handed to circuitgraph.
    back = OUT / f"{CELL}.spice"
    rcfile = SCH_DIR / "xschemrc"   # written by netlist2xschem beside the .sch
    xs = _run_xschem(sch, rcfile, OUT)
    rec["xschem"] = xs
    if back.is_file():
        wrapped = OUT / f"{CELL}_from_sch.spice"
        body = "\n".join(ln for ln in back.read_text().splitlines()
                          if not ln.startswith("**") and not ln.startswith("*.")
                          and ln.strip() and ln.strip() != ".end")
        wrapped.write_text(f"* netlisted by xschem from {sch.name} -- FLAT: circuitgraph matches\n"
                           f"* top-level instances, so the cell body is not wrapped in a subckt\n"
                           f"{body}\n.end\n")
        src = OUT / f"{CELL}_certified.spice"
        src.write_text(_certified_subckt(Path(a.deck)))
        # Second file: the certified cell MINUS the devices netlist2xschem could not place, so the
        # comparison separates "the drawing is wrong" from "the tool cannot draw a 3-terminal
        # rhigh" (doc/journal/netlist2xschem-skips-3-terminal-resistors.md).
        src_min = OUT / f"{CELL}_certified_minus_skipped.spice"
        skipped = set(rec["skipped"])
        src_min.write_text("\n".join(
            ln for ln in src.read_text().splitlines()
            if ln.split()[:1] and ln.split()[0] not in skipped) + "\n")
        try:
            from spicexplorer_circuitgraph import compare_netlists
            cmp_min = compare_netlists(str(src_min), str(wrapped))
            rec["equivalence_minus_skipped"] = {
                "equivalent": bool(getattr(cmp_min, "equivalent", cmp_min)),
                "components_matched": len(getattr(cmp_min, "component_mapping", {}) or {}),
                "nets_matched": len(getattr(cmp_min, "net_mapping", {}) or {}),
                "reason": str(getattr(cmp_min, "reason", ""))[:400]}
            cmp = compare_netlists(str(src), str(wrapped))
            n_dev = len(getattr(cmp, "component_mapping", {}) or {})
            rec["equivalence"] = {
                "equivalent": bool(getattr(cmp, "equivalent", cmp)),
                "components_matched": n_dev,
                "nets_matched": len(getattr(cmp, "net_mapping", {}) or {}),
                # A comparison that matched nothing is a vacuous pass, not a proof.
                "vacuous": n_dev == 0,
                "reason": str(getattr(cmp, "reason", ""))[:400]}
        except Exception as exc:  # noqa: BLE001
            rec["equivalence_error"] = f"{type(exc).__name__}: {exc}"
    (OUT / "schematic.json").write_text(json.dumps(rec, indent=1, default=str) + "\n")
    print(json.dumps(rec, indent=1, default=str)[:1200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
