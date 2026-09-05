"""004 — the schematic of record: netlist -> xschem .sch -> PNG, proven equal to the netlist.

The reviewable artefact of the cell is a drawing, and the only drawing worth having is one that
provably IS the certified netlist. So:

1. The input is the frozen `decks/candidate/dc_op.spice` -- the certified deck, byte for byte,
   not a rebuild -- and `--into XDUT` descends into the cell itself.
2. `spicexplorer_netlist2xschem` places and wires every device; `--render png` gives the figure.
3. `spicexplorer_circuitgraph` re-netlists nothing and compares nothing by eye: it builds the
   device/connectivity graph of the ORIGINAL netlist and of the netlist xschem writes back out
   of the drawing, and reports whether they are the same circuit.
4. Topology is not the whole drawing. `check_parameters` then joins the two netlists device by
   device and compares every parameter -- w, l, m, ng, nf, the model/subckt name, a source's dc
   value -- by NUMBER, after resolving the symbols against the deck's own `.param` bindings and
   normalising SPICE unit suffixes. A device whose size is absent from the drawing fails the
   step, which is what review-002 finding M3 asked for: an isomorphism proves the wiring, not
   the design.

    LDO_EXP=004 uv run --no-sync python experiments/004-schematic/build_sch.py

Re-run only the parameter assertion against any drawing (e.g. an older committed one):

    uv run --no-sync python experiments/004-schematic/build_sch.py --check-sch <path/to.sch>
"""
from __future__ import annotations

import argparse
import json
import math
import re
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
# xschem resolves the PDK symbol libraries from a Tcl variable the stock system rcfile leaves
# unset, so it needs the rcfile `netlist2xschem` writes -- which lands beside the RENDER, not
# beside the .sch. Host-specific (absolute PDK paths) and git-ignored; regenerated every run.
RCFILE = FIGS / "xschemrc"
# The reference the design is regulated against, as a `.param` name in the certified deck. It
# binds from `circuits/ldo_ihp_capless/pdk/ihp-sg13g2/sizing.yaml` (`vref_val`, default 0.6 V,
# min == max) and is quoted in `datasheet.yaml` as `vref.typical`.
VREF_PARAM = "vref_val"
VREF_DEVICE = "VREF"

# Parameters a SPICE instance line may legally omit because the simulator supplies the value.
# `w`/`l` are deliberately NOT here: the device model's own default (7 um x 7 um on cap_cmim) is
# exactly the drift M3 caught, so an absent size is a failure, never a default.
# `b` is the SG13G2 poly resistor's bend count (`leff=(b+1)*l+…`); the model library's
# `.subckt rhigh` and the PDK symbol template both default it to 0, and the symbol's `format`
# line writes `b=@b` unconditionally, so the drawing states a default the netlist left implicit.
CLASS_DEFAULTS = {"m": 1.0, "ng": 1.0, "nf": 1.0, "b": 0.0}
# A token parse_value may be handed. It must START with a digit or a sign, so a bare identifier
# never reaches it -- `x_dut_xmp_m` ends in `m` and would otherwise parse as 0 milli.
_NUMBER = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?[a-zA-Z]{0,3}$")


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
    netlist = out / f"{sch.stem}.spice"   # xschem names its output after the .sch stem
    return {"cmd": " ".join(cmd), "rc": r.returncode,
            "stderr": (r.stdout + r.stderr).strip()[-600:] or None,
            "netlist": str(netlist) if netlist.is_file() else None}


def _flatten_xschem_netlist(back: Path, wrapped: Path, sch_name: str) -> None:
    """xschem's output, stripped to bare instance lines so circuitgraph matches them flat."""
    body = "\n".join(ln for ln in back.read_text().splitlines()
                     if not ln.startswith("**") and not ln.startswith("*.")
                     and ln.strip() and ln.strip() != ".end")
    wrapped.write_text(f"* netlisted by xschem from {sch_name} -- FLAT: circuitgraph matches\n"
                       f"* top-level instances, so the cell body is not wrapped in a subckt\n"
                       f"{body}\n.end\n")


# ----------------------------------------------------------------------------------------------
# The parameter assertion (review-002 M3)
# ----------------------------------------------------------------------------------------------
def _norm(text: object) -> str:
    """An instance's parameter token, whitespace- and brace-normalised for a string compare."""
    s = re.sub(r"\s+", " ", str(text).strip())
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1].strip()
    return s.lower()


def _resolve(expr: object, params: dict[str, str], _depth: int = 0) -> float | None:
    """A parameter token as a NUMBER: symbol -> `.param` binding -> SI suffix -> float.

    Returns None when the token is not something this table can bind to a number (an unbound
    symbol, an arithmetic expression, a model name). Callers must then fall back to comparing
    the tokens as strings rather than pretending the values agree.
    """
    if expr is None or _depth > 8:
        return None
    s = _norm(expr)
    if s.startswith("dc "):          # a source's value carries its analysis keyword
        s = _norm(s[3:])
    if not s:
        return None
    if s in params:
        return _resolve(params[s], params, _depth + 1)
    if not _NUMBER.match(s):
        return None
    try:
        from spicexplorer_core.eng import parse_value
        # lower-cased on purpose: SPICE reads both `m` and `M` as milli, while parse_value's own
        # convention is case-sensitive (`M` = mega). Lower-casing gives the SPICE reading.
        return float(parse_value(s))
    except Exception:  # noqa: BLE001
        return None


def check_parameters(certified: Path, from_sch: Path) -> dict:
    """Every device in the drawing's netlist must carry the certified device's parameters.

    Joins the two netlists by instance name (a name present on one side only is itself a
    finding, so a lost device cannot hide inside the join), then compares each parameter of
    each device: equal as tokens, or equal as numbers once the deck's `.param` bindings and the
    SI suffixes are resolved. `w` and `l` may never be defaulted; `m`/`ng`/`nf` may.
    """
    from spicexplorer_core.spice_engine import NetlistView

    cert = NetlistView.from_file(str(certified))
    drawn = NetlistView.from_file(str(from_sch))
    # The drawing carries the sizing SYMBOLICALLY and holds no `.param` block of its own -- that
    # is the point of it -- so both sides resolve against the certified deck's bindings.
    params = {str(k).lower(): str(v) for k, v in cert.get_parameters().items()}

    cert_refs = {r.upper(): r for r in cert.get_components()}
    drawn_refs = {r.upper(): r for r in drawn.get_components()}
    findings: list[dict] = []
    for ref in sorted(set(cert_refs) - set(drawn_refs)):
        findings.append({"device": ref, "param": "*", "certified": "present",
                         "drawn": "ABSENT", "why": "device is not in the drawing"})
    for ref in sorted(set(drawn_refs) - set(cert_refs)):
        findings.append({"device": ref, "param": "*", "certified": "ABSENT",
                         "drawn": "present", "why": "device is not in the certified cell"})

    compared = 0
    for ref in sorted(set(cert_refs) & set(drawn_refs)):
        pc = {str(k).lower(): v for k, v in cert.get_component_parameters(cert_refs[ref]).items()}
        pd = {str(k).lower(): v for k, v in drawn.get_component_parameters(drawn_refs[ref]).items()}
        for key in sorted(set(pc) | set(pd)):
            compared += 1
            cv, dv = pc.get(key), pd.get(key)
            if cv is not None and dv is not None and _norm(cv) == _norm(dv):
                continue
            a = _resolve(cv, params) if cv is not None else CLASS_DEFAULTS.get(key)
            b = _resolve(dv, params) if dv is not None else CLASS_DEFAULTS.get(key)
            if a is not None and b is not None and math.isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
                continue
            why = ("parameter absent from the drawing and not defaultable" if dv is None else
                   "parameter absent from the certified cell" if cv is None else
                   "values differ")
            findings.append({"device": ref, "param": key,
                             "certified": "ABSENT" if cv is None else f"{_norm(cv)}"
                                          + (f" = {a:g}" if a is not None else ""),
                             "drawn": "ABSENT" if dv is None else f"{_norm(dv)}"
                                      + (f" = {b:g}" if b is not None else ""),
                             "why": why})

    # The reference the whole regulation loop is measured against gets its own named check, so a
    # wrong reference can never be reported as just one more parameter row.
    want = _resolve(VREF_PARAM, params)
    got = (_resolve(drawn.get_component_value(drawn_refs[VREF_DEVICE]), params)
           if VREF_DEVICE in drawn_refs else None)
    vref = {"param": VREF_PARAM, "expected_v": want, "drawn_v": got,
            "binds_from": f"circuits/{CELL}/pdk/ihp-sg13g2/sizing.yaml",
            "ok": want is not None and got is not None
                  and math.isclose(want, got, rel_tol=1e-9, abs_tol=0.0)}
    if not vref["ok"]:
        findings.append({"device": VREF_DEVICE, "param": "dc",
                         "certified": f"{VREF_PARAM} = {want}", "drawn": f"{got}",
                         "why": "the drawing's reference is not the design's reference voltage"})
    return {"ok": not findings, "devices_compared": len(set(cert_refs) & set(drawn_refs)),
            "parameters_compared": compared, "reference_voltage": vref, "findings": findings}


def _report(par: dict) -> None:
    print(f"\nparameters: {par['parameters_compared']} compared over "
          f"{par['devices_compared']} devices -> {'OK' if par['ok'] else 'FAILED'}")
    for f in par["findings"]:
        print(f"  {f['device']:<6} {f['param']:<6} certified={f['certified']!r} "
              f"drawn={f['drawn']!r}  ({f['why']})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", default=str(DECK))
    ap.add_argument("--check-sch", default=None,
                    help="netlist this .sch and run ONLY the parameter assertion against the "
                         "certified cell (used to show the assertion fails on an older drawing)")
    ap.add_argument("--rcfile", default=None,
                    help="xschem rcfile with the PDK symbol libraries "
                         "(default: the one the render step writes into figs/)")
    ap.add_argument("--workdir", default=None,
                    help="where --check-sch writes its scratch netlists (default: out/)")
    a = ap.parse_args()
    FIGS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    SCH_DIR.mkdir(parents=True, exist_ok=True)
    sch, png = SCH_DIR / f"{CELL}.sch", FIGS / f"{CELL}.png"

    if a.check_sch:
        probe = Path(a.check_sch).resolve()
        work = Path(a.workdir).resolve() if a.workdir else OUT
        work.mkdir(parents=True, exist_ok=True)
        rcfile = Path(a.rcfile).resolve() if a.rcfile else RCFILE
        back = work / f"{probe.stem}.spice"   # xschem names its output after the .sch stem
        back.unlink(missing_ok=True)   # a previous run's netlist must never stand in for this one
        xs = _run_xschem(probe, rcfile, work)
        print(json.dumps(xs, indent=1))
        if not back.is_file():
            raise SystemExit(f"xschem produced no netlist for {probe}")
        wrapped = work / f"{probe.stem}_from_sch.spice"
        _flatten_xschem_netlist(back, wrapped, probe.name)
        src = work / f"{CELL}_certified.spice"
        src.write_text(_certified_subckt(Path(a.deck)))
        par = check_parameters(src, wrapped)
        _report(par)
        return 0 if par["ok"] else 1

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
    rcfile = Path(a.rcfile).resolve() if a.rcfile else RCFILE
    back.unlink(missing_ok=True)   # never let a previous run's netlist stand in for this one
    xs = _run_xschem(sch, rcfile, OUT)
    rec["xschem"] = xs
    ok = True
    if back.is_file():
        wrapped = OUT / f"{CELL}_from_sch.spice"
        _flatten_xschem_netlist(back, wrapped, sch.name)
        src = OUT / f"{CELL}_certified.spice"
        src.write_text(_certified_subckt(Path(a.deck)))
        try:
            from spicexplorer_circuitgraph import compare_netlists
            cmp = compare_netlists(str(src), str(wrapped))
            n_dev = len(getattr(cmp, "component_mapping", {}) or {})
            rec["equivalence"] = {
                "equivalent": bool(getattr(cmp, "equivalent", cmp)),
                "components_matched": n_dev,
                "nets_matched": len(getattr(cmp, "net_mapping", {}) or {}),
                # A comparison that matched nothing is a vacuous pass, not a proof.
                "vacuous": n_dev == 0,
                "reason": str(getattr(cmp, "reason", ""))[:400]}
            ok = ok and rec["equivalence"]["equivalent"] and not rec["equivalence"]["vacuous"]
            # Second comparison: the certified cell MINUS whatever netlist2xschem could not place.
            # It only means anything while something IS skipped -- it separates "the drawing is
            # wrong" from "the tool cannot draw this device". With nothing skipped it would just
            # restate the row above, so it is not run.
            skipped = set(rec["skipped"])
            if skipped:
                src_min = OUT / f"{CELL}_certified_minus_skipped.spice"
                src_min.write_text("\n".join(
                    ln for ln in src.read_text().splitlines()
                    if ln.split()[:1] and ln.split()[0] not in skipped) + "\n")
                cmp_min = compare_netlists(str(src_min), str(wrapped))
                rec["equivalence_minus_skipped"] = {
                    "equivalent": bool(getattr(cmp_min, "equivalent", cmp_min)),
                    "components_matched": len(getattr(cmp_min, "component_mapping", {}) or {}),
                    "nets_matched": len(getattr(cmp_min, "net_mapping", {}) or {}),
                    "reason": str(getattr(cmp_min, "reason", ""))[:400]}
            else:
                rec["equivalence_minus_skipped"] = None
                rec["equivalence_minus_skipped_note"] = (
                    "not run: no device was skipped, so it would restate the row above")
        except Exception as exc:  # noqa: BLE001
            rec["equivalence_error"] = f"{type(exc).__name__}: {exc}"
            ok = False
        # --- drawing carries the SIZES too (review-002 M3) --------------------
        rec["parameters"] = check_parameters(src, wrapped)
        ok = ok and rec["parameters"]["ok"]
    else:
        rec["xschem_error"] = "xschem wrote no netlist"
        ok = False
    if rec["skipped"]:
        ok = False
    (OUT / "schematic.json").write_text(json.dumps(rec, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in rec.items() if k != "parameters"}, indent=1, default=str)[:1200])
    _report(rec["parameters"]) if "parameters" in rec else None
    # The step is an ASSERTION, not a report: a skipped device, a vacuous or failed equivalence,
    # or one drifted parameter all exit non-zero.
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
