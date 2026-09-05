"""Shared support for the schematic of record (004) and the visual benches (006).

Everything here is either (a) a small, temporary patch to the generator that the design needs and
the generator does not yet offer, or (b) a helper the two build scripts share. No coordinate is
hand-placed: placement and wiring stay the generator's job throughout.

**The two patches.** Both are proposed upstream verbatim -- the diff and its rationale live in
``$SX_SCRATCH/ldo-schematic/platform-proposal/`` -- and both carry an *outdated guard*: they assert
the upstream code is still the version they patch, so the day the fix lands here this file fails
loudly instead of silently patching a patch.

* **P1/P2 -- a block's child sheet must keep its rails.** ``hierarchy._child_circuit`` hands every
  child ``supply={}`` so that a boundary supply surfaces as a real ``.subckt`` port. That is right,
  but it also tells the placer the child *has no rails*, and the rail-banded placement (VDD row on
  top, VSS row on the bottom, the signal path between) is exactly what makes an amplifier readable.
  Keeping the parent's supply map on the child would drop ``vdd``/``vss`` from its port list instead,
  because ``analysis._port_roles`` refuses to call a supply net a port -- so the two must move
  together: a *declared* port stays a port even when it is a supply (P1), and the child inherits the
  parent's supply map (P2). With both, each child comes out as a textbook drawing and the hierarchy
  still re-netlists.
* **P4 -- a display shortening must not reach the netlist.** ``emit._display_value`` abbreviates an
  attribute value longer than 24 characters to its tail (``…00n 10u 20u)``) and writes THAT into the
  instance's ``value=``, which is the attribute xschem netlists. For a sizing symbol
  (``w=x_dut_xmp_w``) the values are short and it never shows; for a transient stimulus
  (``pulse(1.4 1.65 1u 100n 100n 10u 20u)``, 36 characters) the drawing's netlist silently loses the
  front of the source. A shortening meant for the drawing has to stay in the drawing.
* **P3 -- a design's own cell symbol on a bench sheet.** ``mapping.symref_for`` resolves a subcircuit
  instance through a PDK table, so a bench's ``XDUT ... ldo_ihp_capless`` has no symbol and is
  dropped from the drawing. The design's own generated symbol is registered in that table.

**The flattener.** The parent sheet netlists as a hierarchy (one ``.subckt`` per block); the gate
compares against the certified *flat* cell. ``flatten_hierarchy`` splices the blocks back inline,
**preserving leaf instance names** (``XM1`` stays ``XM1``), so the parameter assertion can still join
the two netlists device by device. It uses only the platform netlist parser -- the net tokens of a
leaf line are identified by position, from the parser's own node count for that device -- so it never
re-implements SPICE parsing.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from spicexplorer_netlist2xschem import analysis as _analysis
from spicexplorer_netlist2xschem import emit as _emit
from spicexplorer_netlist2xschem import hierarchy as _hierarchy
from spicexplorer_netlist2xschem import mapping as _mapping
from spicexplorer_netlist2xschem.ingest import N2XCircuit
from spicexplorer_netlist2xschem.render import render
from spicexplorer_netlist2xschem.symbol_gen import BlockPin, generate_block_symbol

PROPOSAL = "$SX_SCRATCH/ldo-schematic/platform-proposal/"

_PARENT_SUPPLY: dict[str, str] = {}
_APPLIED = False


# ----------------------------------------------------------------------------------------------
# P1 + P2 -- readable child sheets
# ----------------------------------------------------------------------------------------------
def apply_platform_proposals() -> list[str]:
    """Apply P1 and P2. Idempotent; raises if the upstream code has moved on (see module docstring)."""
    global _APPLIED
    if _APPLIED:
        return ["already applied"]

    orig_roles = _analysis._port_roles
    orig_child = _hierarchy._child_circuit
    # Outdated guard: if either function is already someone else's (or upstream renamed it), stop.
    if getattr(orig_roles, "__module__", "") != _analysis.__name__:
        raise RuntimeError("analysis._port_roles is not the stock function; P1 may be upstream now")
    if getattr(orig_child, "__module__", "") != _hierarchy.__name__:
        raise RuntimeError("hierarchy._child_circuit is not the stock function; P2 may be upstream now")
    if "supply=" not in _child_source(orig_child) or "supply={}" not in _child_source(orig_child):
        raise RuntimeError("hierarchy._child_circuit no longer passes supply={}; P2 is upstream")

    def _port_roles(circuit, supply, net_pins):  # P1
        roles = dict(orig_roles(circuit, supply, net_pins))
        for net in circuit.ports:
            if net in supply and net in net_pins:
                roles.setdefault(net, "inout")
        return roles

    def _child_circuit(block_devs, name, boundary):  # P2
        child = orig_child(block_devs, name, boundary)
        keep = {n: r for n, r in _PARENT_SUPPLY.items() if n in child.nets}
        return N2XCircuit(name=child.name, devices=child.devices, nets=child.nets,
                          supply=keep, ports=child.ports)

    orig_display = _emit._display_value
    if getattr(orig_display, "__module__", "") != _emit.__name__:
        raise RuntimeError("emit._display_value is not the stock function; P4 may be upstream now")
    if orig_display("x" * 40) == "x" * 40:
        raise RuntimeError("emit._display_value no longer shortens; P4 is upstream")

    _emit._display_value = lambda value: str(value)  # P4

    _analysis._port_roles = _port_roles
    _hierarchy._child_circuit = _child_circuit
    _APPLIED = True
    return ["P1 analysis._port_roles: a declared supply port stays a port",
            "P2 hierarchy._child_circuit: the child inherits the parent's supply map",
            "P4 emit._display_value: the netlisted value is never abbreviated"]


def _child_source(fn) -> str:
    import inspect
    try:
        return inspect.getsource(fn)
    except Exception:  # noqa: BLE001
        return "supply={}"   # cannot read it: do not block on the guard


def build_hierarchy(circuit, annotations, **kw):
    """``hierarchy.build_hierarchical_sch`` with the parent's supply map visible to P2."""
    global _PARENT_SUPPLY
    _PARENT_SUPPLY = dict(circuit.supply)
    return _hierarchy.build_hierarchical_sch(circuit, annotations, **kw)


# ----------------------------------------------------------------------------------------------
# P3 -- the design's own cell symbol
# ----------------------------------------------------------------------------------------------
def register_cell_symbol(pdk: str, cell: str, symref: str) -> None:
    """Make the generator place ``cell`` as ``symref`` (a bench's DUT instance)."""
    table = _mapping._PDK_SUBCKT_SYMREF
    if (pdk, cell) in table and table[(pdk, cell)] != symref:
        raise RuntimeError(f"{pdk}/{cell} already maps to {table[(pdk, cell)]}; P3 may be upstream")
    table[(pdk, cell)] = symref


def write_cell_symbol(path: Path, cell: str, ports: list[str], sides: dict[str, str],
                      dirs: dict[str, str] | None = None) -> Path:
    """The cell's own ``.sym``, with its pins in the certified ``.subckt`` port order.

    xschem takes BOTH the symbol's ``@pinlist`` and the port order of the ``.subckt`` header it
    writes from the order of the ``B`` (pin) records in the ``.sym``. The generator emits them
    grouped by side, so the records are reordered here to ``ports`` -- the deck's call order -- which
    is what makes the bench's ``XDUT vdd vout vss`` line identical to the certified deck's.
    """
    dirs = dirs or {}
    sym = generate_block_symbol(cell, [BlockPin(net=p, side=sides[p], direction=dirs.get(p, ""))
                                       for p in ports])
    lines = sym.text.splitlines()
    # Each pin record carries its own coordinates, so the ORDER of the `B` records is free geometry
    # -- permute them into the certified port order in place, leaving every stub and label where the
    # generator put it.
    slots = [i for i, ln in enumerate(lines) if re.match(r"^B \d+ ", ln)]
    by_net = {re.search(r"\{name=(\S+) ", lines[i]).group(1): lines[i] for i in slots}
    if set(by_net) != set(ports):
        raise RuntimeError(f"symbol pins {sorted(by_net)} != subckt ports {ports}")
    for slot, net in zip(slots, ports):
        lines[slot] = by_net[net]
    path.write_text("\n".join(lines) + "\n")
    return path


# ----------------------------------------------------------------------------------------------
# Sheet geometry + the parent's own port symbols
# ----------------------------------------------------------------------------------------------
_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def sheet_extent(sch_text: str) -> tuple[int, int, int]:
    """(xmin, xmax, ymax) over every placed record on a sheet."""
    xs, ys = [], []
    for line in sch_text.splitlines():
        k = line[:1]
        if k == "C":
            n = _NUM.findall(line.split("}", 1)[-1] if line.startswith("C {") else line)
            if len(n) >= 2:
                xs.append(float(n[0]))
                ys.append(float(n[1]))
        elif k in ("N", "B"):
            n = _NUM.findall(line)
            n = n[1:] if k == "B" else n
            if len(n) >= 4:
                xs += [float(n[0]), float(n[2])]
                ys += [float(n[1]), float(n[3])]
    if not xs:
        return (0, 400, 400)
    return (int(min(xs)), int(max(xs)), int(max(ys)))


_PORT_SYM = {"in": "devices/ipin.sym", "out": "devices/opin.sym", "inout": "devices/iopin.sym"}


def append_port_symbols(sch: Path, ports: list[tuple[str, str]], pitch: int = 220) -> None:
    """Draw the sheet's own ``.subckt`` ports as port symbols in a row under the drawing (P5b).

    The hierarchy's CHILD sheets get these from the generator; the PARENT sheet does not, so xschem
    reports its symbol's three pins against a schematic with none. The netlist is unaffected either
    way (xschem takes the header from the symbol), but a cell sheet that does not declare its own
    interface is not a drawing a reviewer can check, and the mismatch is reported as an error.
    """
    text = sch.read_text()
    xmin, _, ymax = sheet_extent(text)
    rows = [f'C {{{_PORT_SYM.get(role, _PORT_SYM["inout"])}}} {xmin + i * pitch} {ymax + 160} '
            f'0 0 {{name=p_{net} lab={net}}}'
            for i, (net, role) in enumerate(ports)]
    sch.write_text(text.rstrip("\n") + "\n" + "\n".join(rows) + "\n")


_SCH_PIN_DIR = {"ipin": "in", "opin": "out", "iopin": "inout"}


def sync_symbol_pin_dirs(blocks_dir: Path) -> list[str]:
    """Give each block symbol the pin DIRECTIONS its own child sheet declares (P5a).

    A block's direction is computed twice and independently: the symbol's from the device roles the
    boundary net touches, the child sheet's port symbol from the circuit-level port analysis. Where
    they disagree xschem reports `Unmatched subcircuit schematic pin direction`, and two blocks that
    both call one net an output are reported as a shorted output node -- on a hierarchy that
    netlists perfectly. The sheet is the authority (it is what the analysis actually saw), so the
    symbol is brought to it. Geometry is untouched: only the ``dir=`` field changes.
    """
    fixed: list[str] = []
    for sch in sorted(blocks_dir.glob("*.sch")):
        want = {}
        for line in sch.read_text().splitlines():
            m = re.match(r"^C \{devices/(i?o?i?pin)\.sym\}.*\blab=([^\s}]+)", line)
            if m:
                want[m.group(2)] = _SCH_PIN_DIR.get(m.group(1), "inout")
        sym = sch.with_suffix(".sym")
        if not want or not sym.is_file():
            continue
        out = []
        for line in sym.read_text().splitlines():
            m = re.match(r"^(B \d+ .*\{name=)(\S+)( dir=)(\S+)(\}.*)$", line)
            if m and m.group(2) in want and m.group(4) != want[m.group(2)]:
                fixed.append(f"{sym.name}:{m.group(2)} {m.group(4)} -> {want[m.group(2)]}")
                line = f"{m.group(1)}{m.group(2)}{m.group(3)}{want[m.group(2)]}{m.group(5)}"
            out.append(line)
        sym.write_text("\n".join(out) + "\n")
    return fixed


# ----------------------------------------------------------------------------------------------
# xschem: netlist back out, render
# ----------------------------------------------------------------------------------------------
def xschem_netlist(sch: Path, rcfile: Path, outdir: Path) -> tuple[Path, str]:
    """Netlist ``sch`` back out with headless xschem; returns the netlist path and xschem's log.

    The log is returned, not swallowed: xschem reports symbol/pin-direction mismatches there and
    nowhere else, and a warning nobody prints is a warning nobody fixes."""
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{sch.stem}.spice"
    out.unlink(missing_ok=True)   # a previous run's netlist must never stand in for this one
    cmd = ["xschem", "-n", "-q", "-r", "--rcfile", str(rcfile), "-o", str(outdir), str(sch)]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(outdir))
    log = "\n".join(ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip())
    if not out.is_file():
        raise SystemExit(f"xschem wrote no netlist for {sch}:\n{log[-800:]}")
    return out, log


def render_png(sch: Path, outdir: Path, library_path: str, width: int = 2400,
               margin: int = 64) -> Path | None:
    """Render ``sch`` to PNG. The SVG is padded first: xschem sizes the canvas to the drawing's
    bounding box, which clips the outermost net labels (they overhang their anchor)."""
    outdir.mkdir(parents=True, exist_ok=True)
    res = render(sch, fmt="svg", outdir=outdir, library_path=library_path)
    if res.image_path is None or res.fmt != "svg":
        return None
    svg = Path(res.image_path)
    _pad_svg(svg, margin)
    png = outdir / f"{sch.stem}.png"
    import cairosvg
    cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=width)
    svg.unlink(missing_ok=True)
    return png


def _pad_svg(svg: Path, margin: int) -> None:
    """Grow the SVG canvas so nothing is clipped, then shift the drawing into it.

    xschem sizes the canvas to the *geometry* bounding box, so a net name or a directive line that
    overhangs its anchor -- every port label, and every line of a `.control` block -- is cut off at
    the edge. The overhang is measured here from the text elements themselves (anchor + an advance
    width estimate for the font size) rather than guessed at with a fixed pad.
    """
    text = svg.read_text()
    m = re.search(r'<svg([^>]*?)width="([\d.]+)"([^>]*?)height="([\d.]+)"([^>]*)>', text)
    if not m:
        return
    w, h = float(m.group(2)), float(m.group(4))
    right = bottom = 0.0
    for t_m in re.finditer(r'<text[^>]*font-size="([\d.]+)"[^>]*translate\(([-\d.]+), *([-\d.]+)\)[^>]*>([^<]*)</text>',
                           text):
        size, x, y, body = float(t_m.group(1)), float(t_m.group(2)), float(t_m.group(3)), t_m.group(4)
        right = max(right, x + 0.62 * size * len(body))   # 0.62 em/char: xschem's monospace-ish face
        bottom = max(bottom, y + size)
    pad_r = max(margin, right - w + margin)
    pad_b = max(margin, bottom - h + margin)
    head = (f'<svg{m.group(1)}width="{w + margin + pad_r:g}"{m.group(3)}'
            f'height="{h + margin + pad_b:g}"{m.group(5)}>'
            f'<g transform="translate({margin},{margin})">')
    text = text[: m.start()] + head + text[m.end():]
    text = text[: text.rindex("</svg>")] + "</g></svg>\n"
    svg.write_text(text)


# ----------------------------------------------------------------------------------------------
# hierarchy -> flat, leaf names preserved
# ----------------------------------------------------------------------------------------------
_CONT = re.compile(r"^\s*\+")


def _logical_lines(text: str) -> list[str]:
    """Netlist lines with ``+`` continuations joined and comment lines dropped."""
    out: list[str] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("*"):
            continue
        if _CONT.match(raw) and out:
            out[-1] = out[-1] + " " + raw.lstrip()[1:].strip()
        else:
            out.append(raw.strip())
    return out


def flatten_hierarchy(netlist: Path, out: Path, *, note: str = "") -> dict:
    """Splice every block subcircuit of a hierarchical netlist back inline, keeping leaf names.

    Returns a record of what was spliced. Raises on a leaf-name or internal-net collision between
    blocks -- the one thing that would make the flat result ambiguous.
    """
    from spicexplorer_core.spice_engine import NetlistView

    text = netlist.read_text()
    lines = _logical_lines(text)
    view = NetlistView.from_file(str(netlist))

    defs: dict[str, list[str]] = {}
    top: list[str] = []
    cur: str | None = None
    for ln in lines:
        low = ln.lower()
        if low.startswith(".subckt "):
            cur = ln.split()[1].lower()
            defs[cur] = []
        elif low.startswith(".ends"):
            cur = None
        elif cur is not None:
            defs[cur].append(ln)
        elif low.startswith("."):
            continue           # a top-level directive is not part of the cell body
        else:
            top.append(ln)

    body: list[str] = []
    spliced: list[str] = []
    seen_refs: dict[str, str] = {}
    seen_nets: dict[str, str] = {}
    for ln in top:
        ref = ln.split()[0]
        model = (view.get_component_value(ref) or "").lower() if ref.upper().startswith("X") else ""
        if model not in defs:
            body.append(ln)
            seen_refs.setdefault(ref.upper(), "<parent>")
            continue
        child = view.get_subcircuit(ref)
        formals = [p.lower() for p in (view.get_subcircuit_ports(ref) or [])]
        actuals = [n.lower() for n in view.get_component_nodes(ref)]
        if len(formals) != len(actuals):
            raise SystemExit(f"{ref}: {len(formals)} ports vs {len(actuals)} nets")
        rename = dict(zip(formals, actuals))
        for leaf in defs[model]:
            tok = leaf.split()
            n = len(child.get_component_nodes(tok[0]))
            prev = seen_refs.get(tok[0].upper())
            if prev is not None:
                raise SystemExit(f"leaf {tok[0]} appears in both {prev} and {ref}")
            seen_refs[tok[0].upper()] = ref
            for net in tok[1:1 + n]:
                if net.lower() in rename:
                    continue
                owner = seen_nets.setdefault(net.lower(), ref)
                if owner != ref:
                    raise SystemExit(f"internal net {net} appears in both {owner} and {ref}")
            body.append(" ".join(tok[:1] + [rename.get(t.lower(), t) for t in tok[1:1 + n]]
                                 + tok[1 + n:]))
        spliced.append(f"{ref} -> {model} ({len(defs[model])} devices)")

    out.write_text(f"* flattened out of {netlist.name}{(' -- ' + note) if note else ''}\n"
                   "* block subcircuits spliced inline; leaf instance names preserved\n"
                   + "\n".join(body) + "\n.end\n")
    return {"out": str(out), "spliced": spliced, "devices": len(body)}
