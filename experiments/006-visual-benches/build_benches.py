"""006 -- the visual benches: one schematic per certified deck, proven to netlist back to it.

A testbench that is one block of SPICE text inside a frame is not a drawing; it is a deck with a
border. So every bench element -- supply, load, stimulus, the 0 V loop-break marker's own source,
the load capacitor -- is PLACED AND WIRED as a component, the cell is placed as its own symbol, and
only what has no symbol stays as text: the `.lib`/`.temp`/`.param` directives and the `.control`
block, lifted VERBATIM out of the certified deck into two `code_shown` blocks at the bottom of the
sheet (they are part of the netlist, so the drawing stays runnable).

The gate is not the picture. For each of the 13 frozen decks:

1. xschem netlists the bench `.sch` back out.
2. `compare_bench` joins that netlist and the certified deck through the platform's netlist parser
   -- never a private parser -- and requires: the same top-level instances (case-insensitively:
   the parser upper-cases refs), each one's nets equal IN ORDER (so `XDUT vdd vout vss` is a real
   check of the cell's port order), each one's value/parameters equal as numbers where they are
   numbers and as normalised text otherwise, and the lifted directive and `.control` text equal
   line by line.
3. One bench is then simulated FROM THE DRAWING's netlist through `ldo.metrics.run_decks` and its
   measures compared with `decks/candidate/scorecard.json` -- the drawing reproduces the certified
   number, or the step fails.

Any drift exits non-zero.

    LDO_EXP=006 uv run --no-sync python experiments/006-visual-benches/build_benches.py
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments" / "004-schematic"))

CELL = "ldo_ihp_capless"
DECKS = REPO / "decks" / "candidate"
SCH_DIR = REPO / "circuits" / CELL / "xschem"   # beside the cell symbol, so xschem resolves it
FIGS = HERE / "figs"
OUT = HERE / "out"
# Which bench proves which claim. One SHEET per deck (the gate is exact, and three loop-gain decks
# differ only in their load current, so one "family sheet" could not match all three); the README
# groups the sheets into these families.
FAMILY = {
    "dc_op": "operating point",
    "load_regulation": "load regulation",
    "line_regulation": "line regulation",
    "dropout": "dropout",
    "ac_loopgain": "loop gain / phase margin (Middlebrook)",
    "ac_loopgain_lo": "loop gain / phase margin (Middlebrook)",
    "ac_loopgain_hi": "loop gain / phase margin (Middlebrook)",
    "loop_stability": "closed-loop output impedance",
    "psrr": "PSRR",
    "psrr_1m": "PSRR",
    "noise": "output noise",
    "tran_load_step": "load-step transient",
    "tran_line_step": "line-step transient",
}
# The bench reproduced end to end, and the certified numbers it must return.
REPRO_BENCH = "ac_loopgain"


# ----------------------------------------------------------------------------------------------
# The deck, split into what is drawn and what stays text
# ----------------------------------------------------------------------------------------------
def split_deck(text: str) -> dict:
    """A certified deck as (title, directives, control, elements) -- verbatim lines, deck order.

    The cell's own `.subckt` body is neither: the drawing carries it as a hierarchy, and 004 is
    where it is proven equal to the certified cell.
    """
    title, directives, control, elements = "", [], [], []
    inside_cell = in_control = False
    for raw in text.splitlines():
        line, low = raw.rstrip(), raw.strip().lower()
        if not low:
            continue
        if low.startswith(".subckt "):
            inside_cell = True
            continue
        if low.startswith(".ends"):
            inside_cell = False
            continue
        if inside_cell or low == ".end":
            continue
        if low.startswith("*"):
            title = title or line.lstrip("* ").strip()
            continue
        if low.startswith(".control"):
            in_control = True
        if in_control:
            control.append(line)
            if low.startswith(".endc"):
                in_control = False
            continue
        if low.startswith("."):
            directives.append(line)
            continue
        elements.append(line)
    return {"title": title, "directives": directives, "control": control, "elements": elements}


# ----------------------------------------------------------------------------------------------
# Drawing: the generator places and wires; the text blocks go under the drawing
# ----------------------------------------------------------------------------------------------
def _escape(value: str) -> str:
    """A multi-line netlist fragment as an xschem property value."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def draw_bench(bench: str, parts: dict, deck: Path) -> Path:
    """Place + wire the bench with the generator, then append the two text blocks and a caption."""
    import sch_support
    from spicexplorer_netlist2xschem.emit import build_sch
    from spicexplorer_netlist2xschem.ingest import from_file
    from spicexplorer_netlist2xschem.sym_library import SymLibrary
    from build_sch import PDK, library_path

    # P3 -- the design's own cell symbol, so XDUT is DRAWN and not skipped as an unknown subckt.
    # P4 -- so a `pulse(...)` stimulus is not abbreviated on its way into the netlist.
    sch_support.register_cell_symbol(PDK, CELL, f"{CELL}.sym")
    sch_support.assert_platform_support()
    lib = SymLibrary([Path(p) for p in library_path().split(":")])
    circuit = from_file(deck, name=f"{bench}_tb")
    doc = build_sch(circuit, pdk=PDK, lib=lib, title=f"{bench}_tb", show_device_params=True)

    # The two text blocks sit under the drawing, SIDE BY SIDE: the sizing `.param` block is 30+
    # lines and stacking them would make a page three times taller than it is wide. Their anchors
    # come from the sheet's own extent and the widest line, not from typed-in coordinates.
    xmin, _, ymax = sch_support.sheet_extent(doc.text)
    y0 = ymax + 140
    wide = max((len(ln) for ln in parts["directives"]), default=20)
    extra = [f'T {{{bench}_tb -- {FAMILY[bench]}}} {xmin} {ymax + 40} 0 0 0.5 0.5 {{}}',
             f'T {{drawn from decks/candidate/{deck.name}; directives and .control lifted verbatim}} '
             f'{xmin} {ymax + 80} 0 0 0.3 0.3 {{}}']
    for x0, (name, lines) in zip((xmin, xmin + 8 * wide + 160),
                                 (("DIRECTIVES", parts["directives"]),
                                  ("CONTROL", parts["control"]))):
        extra.append(f'C {{devices/code_shown.sym}} {x0} {y0} 0 0 '
                     f'{{name={name} only_toplevel=false value="{_escape(chr(10).join(lines))}"}}')
    sch = SCH_DIR / f"{bench}_tb.sch"
    sch.write_text(doc.text.rstrip("\n") + "\n" + "\n".join(extra) + "\n")
    return sch


# ----------------------------------------------------------------------------------------------
# The gate: the drawing's netlist IS the certified deck
# ----------------------------------------------------------------------------------------------
_NUMBER = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?[a-zA-Z]{0,3}$")
# A bench element may omit these because the simulator supplies them; the drawing states them
# because the PDK/generic symbol's `format` line writes them unconditionally.
CLASS_DEFAULTS = {"m": 1.0}


def _norm(text: object) -> str:
    s = re.sub(r"\s+", " ", str(text).strip())
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1].strip()
    return s.lower()


def _resolve(expr: object, params: dict[str, str], _depth: int = 0) -> float | None:
    if expr is None or _depth > 8:
        return None
    s = _norm(expr)
    if s.startswith("dc "):
        s = _norm(s[3:])
    if s in params:
        return _resolve(params[s], params, _depth + 1)
    if not s or not _NUMBER.match(s):
        return None
    try:
        from spicexplorer_core.eng import parse_value
        return float(parse_value(s))
    except Exception:  # noqa: BLE001
        return None


def compare_bench(deck_text: str, sch_netlist: str, parts: dict) -> dict:
    """The drawing's netlist against the certified deck: instances, nets in order, values, text."""
    from spicexplorer_core.spice_engine import NetlistView

    deck = NetlistView.from_string(deck_text)
    drawn = NetlistView.from_string(sch_netlist)
    params = {str(k).lower(): str(v) for k, v in deck.get_parameters().items()}
    findings: list[dict] = []

    d_refs = {r.upper(): r for r in deck.get_components()}
    s_refs = {r.upper(): r for r in drawn.get_components()}
    for ref in sorted(set(d_refs) - set(s_refs)):
        findings.append({"item": ref, "certified": "present", "drawn": "ABSENT",
                         "why": "bench element is not on the sheet"})
    for ref in sorted(set(s_refs) - set(d_refs)):
        findings.append({"item": ref, "certified": "ABSENT", "drawn": "present",
                         "why": "the sheet carries an element the deck does not"})

    nets_checked = params_checked = 0
    for ref in sorted(set(d_refs) & set(s_refs)):
        dn = [n.lower() for n in deck.get_component_nodes(d_refs[ref])]
        sn = [n.lower() for n in drawn.get_component_nodes(s_refs[ref])]
        nets_checked += len(dn)
        if dn != sn:
            findings.append({"item": ref, "certified": " ".join(dn), "drawn": " ".join(sn),
                             "why": "connectivity (or its order) differs"})
        dv, sv = deck.get_component_value(d_refs[ref]), drawn.get_component_value(s_refs[ref])
        params_checked += 1
        if _norm(dv) != _norm(sv):
            a, b = _resolve(dv, params), _resolve(sv, params)
            if not (a is not None and b is not None and math.isclose(a, b, rel_tol=1e-9)):
                findings.append({"item": f"{ref}.value", "certified": _norm(dv),
                                 "drawn": _norm(sv), "why": "value differs"})
        pd = {str(k).lower(): v for k, v in deck.get_component_parameters(d_refs[ref]).items()}
        ps = {str(k).lower(): v for k, v in drawn.get_component_parameters(s_refs[ref]).items()}
        for key in sorted(set(pd) | set(ps)):
            params_checked += 1
            a_raw, b_raw = pd.get(key), ps.get(key)
            if a_raw is not None and b_raw is not None and _norm(a_raw) == _norm(b_raw):
                continue
            a = _resolve(a_raw, params) if a_raw is not None else CLASS_DEFAULTS.get(key)
            b = _resolve(b_raw, params) if b_raw is not None else CLASS_DEFAULTS.get(key)
            if a is not None and b is not None and math.isclose(a, b, rel_tol=1e-9):
                continue
            findings.append({"item": f"{ref}.{key}",
                             "certified": "ABSENT" if a_raw is None else _norm(a_raw),
                             "drawn": "ABSENT" if b_raw is None else _norm(b_raw),
                             "why": "parameter differs"})

    # The text half: the directives and the .control block the sheet carries as code blocks must be
    # the deck's own lines. Whitespace-normalised, order preserved.
    got = split_deck(sch_netlist)
    for tag in ("directives", "control"):
        want_lines = [re.sub(r"\s+", " ", ln.strip()) for ln in parts[tag]]
        got_lines = [re.sub(r"\s+", " ", ln.strip()) for ln in got[tag]]
        if want_lines != got_lines:
            only_want = [ln for ln in want_lines if ln not in got_lines]
            only_got = [ln for ln in got_lines if ln not in want_lines]
            findings.append({"item": f"text.{tag}", "certified": f"{len(want_lines)} lines",
                             "drawn": f"{len(got_lines)} lines",
                             "why": f"missing={only_want[:4]} extra={only_got[:4]}"})
    return {"ok": not findings, "instances": len(set(d_refs) & set(s_refs)),
            "nets_checked": nets_checked, "params_checked": params_checked,
            "text_lines": len(parts["directives"]) + len(parts["control"]), "findings": findings}


# ----------------------------------------------------------------------------------------------
def reproduce(bench: str, netlist: str) -> dict:
    """Simulate the DRAWING's netlist and compare with the certified scorecard."""
    from ldo import metrics
    cert = json.loads((DECKS / "scorecard.json").read_text())["bench_measures"][bench]
    _, records = metrics.run_decks({bench: netlist}, f"006_from_sch_{bench}")
    rec = records[bench]
    measures = rec.get("measures") or {}
    rows = []
    for k in sorted(cert):
        want, got = cert.get(k), measures.get(k)
        same = (want is not None and got is not None
                and math.isclose(float(want), float(got), rel_tol=1e-6, abs_tol=1e-9))
        rows.append({"key": k, "certified": want, "from_sch": got, "same": same})
    return {"bench": bench, "status": rec["status"], "error": rec.get("error"),
            "rows": rows, "ok": rec["status"] == "ok" and all(r["same"] for r in rows)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="build just this bench (comma-separated)")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-sim", action="store_true")
    a = ap.parse_args()
    import sch_support
    from build_sch import library_path
    from spicexplorer_netlist2xschem.render import write_xschemrc

    FIGS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    libp = library_path()
    rcfile = write_xschemrc(OUT, libp)
    benches = a.only.split(",") if a.only else sorted(FAMILY)

    rec: dict = {"benches": {}}
    ok = True
    for bench in benches:
        deck = DECKS / f"{bench}.spice"
        parts = split_deck(deck.read_text())
        sch = draw_bench(bench, parts, deck)
        back, log = sch_support.xschem_netlist(sch, rcfile, OUT)
        cmp = compare_bench(deck.read_text(), back.read_text(), parts)
        png = None if a.no_render else sch_support.render_png(sch, FIGS, libp, width=2400)
        rec["benches"][bench] = {
            "family": FAMILY[bench], "deck": str(deck), "sch": str(sch),
            "netlist": str(back), "png": str(png) if png else None,
            "xschem_log": [ln for ln in log.splitlines() if "arning" in ln or "rror" in ln],
            "gate": cmp}
        ok = ok and cmp["ok"] and (a.no_render or png is not None)
        flag = "OK " if cmp["ok"] else "DRIFT"
        print(f"{flag} {bench:<16} {cmp['instances']} instances, {cmp['nets_checked']} nets, "
              f"{cmp['params_checked']} params, {cmp['text_lines']} text lines")
        for f in cmp["findings"]:
            print(f"     {f['item']:<16} certified={f['certified']!r} drawn={f['drawn']!r} "
                  f"({f['why']})")

    if not a.no_sim and REPRO_BENCH in rec["benches"]:
        nl = Path(rec["benches"][REPRO_BENCH]["netlist"]).read_text()
        rec["reproduction"] = reproduce(REPRO_BENCH, nl)
        ok = ok and rec["reproduction"]["ok"]
        print(f"\nreproduced {REPRO_BENCH} from the drawing's netlist "
              f"({rec['reproduction']['status']}):")
        for r in rec["reproduction"]["rows"]:
            print(f"  {r['key']:<12} certified={r['certified']} from_sch={r['from_sch']} "
                  f"{'OK' if r['same'] else 'DRIFT'}")
        if rec["reproduction"].get("error"):
            print(rec["reproduction"]["error"])

    (OUT / "benches.json").write_text(json.dumps(rec, indent=1, default=str) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
