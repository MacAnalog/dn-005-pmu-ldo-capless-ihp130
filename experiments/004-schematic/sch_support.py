"""Shared support for the schematic of record (004) and the visual benches (006).

Everything here is a helper the two build scripts share. No coordinate is hand-placed: placement and
wiring stay the generator's job throughout.

**The generator does the work now.** Five changes this design needed were carried as guarded local
patches for one round and have landed in ``spicexplorer_netlist2xschem``. This module used to
re-check them here by grepping the platform's own source; each is a regression test in that
package now (``tests/test_hierarchy_flatten.py``), which is where a regression belongs, and
:data:`PLATFORM_BEHAVIOURS` names the six the drawing of record depends on:

* **P1/P2 -- a block's child sheet keeps its rails.** A *declared* ``.subckt`` port stays a port even
  when it is a supply, and the child inherits the parent's supply map, so each child is placed
  rail-banded (VDD row on top, VSS row on the bottom, the signal path between) and still re-netlists.
* **P3 -- a design's own cell symbol on a bench sheet.** ``mapping.register_subckt_symbol`` puts the
  design's generated symbol in the table ``symref_for`` resolves, so a bench's
  ``XDUT ... ldo_ihp_capless`` is drawn rather than dropped.
* **P4 -- a display shortening must not reach the netlist.** ``emit._display_value`` no longer
  abbreviates a value over 24 characters to its tail; the abbreviation used to be written into the
  instance's ``value=``, which is the attribute xschem netlists (a truncated ``pulse(...)`` stimulus
  on two bench sheets, and this cell's own ``w={x_dut_xmp_w/x_dut_xmp_nf_mult}``).
* **P5 -- per-child wiring mode.** ``build_hierarchical_sch(..., child_wiring=...)`` takes a mode or
  a per-block mapping. Needed because ``hybrid`` lets a net's trunk wire CROSS a pin's stub with no
  junction, and xschem connects only at junctions, so the pin lands on an unnamed ``netN``. Children
  are drawn ``hybrid`` and netlisted one at a time; only a block measured to have lost a pin
  (:func:`blocks_losing_a_pin`) is redrawn ``labels``, which cannot lose one.
* **P8 -- the annotation loader fails closed.** ``BlockAnnotationSet.load(path, circuit=...)`` raises
  on a member the circuit does not have. Without it a netlist recertification that renamed devices
  silently emptied three of five blocks while the topology gate stayed green.

**The flattener.** The parent sheet netlists as a hierarchy (one ``.subckt`` per block); the gate
compares against the certified *flat* cell. Splicing the blocks back inline while **preserving
leaf instance names** (``XM1`` stays ``XM1``) is what lets the parameter assertion join the two
netlists device by device, and it is ``spicexplorer_netlist2xschem.hierarchy.flatten_hierarchy``
now. :func:`flatten_hierarchy` here is the record row this experiment writes around it.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from spicexplorer_netlist2xschem import hierarchy as _hierarchy
from spicexplorer_netlist2xschem import mapping as _mapping
from spicexplorer_netlist2xschem.render import render
from spicexplorer_netlist2xschem.symbol_gen import BlockPin, generate_block_symbol

# ----------------------------------------------------------------------------------------------
# The platform behaviours this design depends on (P1-P5, P8), asserted rather than patched
# ----------------------------------------------------------------------------------------------
#: The six generator behaviours the drawing of record depends on. This module used to assert
#: them by GREPPING the platform's own source — a design repo checking platform behaviour by
#: inspecting platform source is a symptom of that behaviour having no regression test. They are
#: now six cases in `spicexplorer-netlist2xschem/tests/test_hierarchy_flatten.py`, so a
#: regression fails there instead of quietly redrawing a wrong sheet here.
PLATFORM_BEHAVIOURS = (
    "P1 a declared supply port stays a port",
    "P2 the child inherits the parent's supply map",
    "P3 a design's own cell symbol can be registered",
    "P4 the netlisted value is never abbreviated",
    "P5 per-child wiring mode",
    "P8 the annotation loader fails closed",
)


def register_cell_symbol(pdk: str, cell: str, symref: str) -> None:
    """Make the generator place ``cell`` as ``symref`` (a bench's DUT instance) -- P3."""
    _mapping.register_subckt_symbol(pdk, cell, symref)


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


def blocks_losing_a_pin(children: dict[str, str], symbols: dict[str, str], rcfile_dir: Path,
                        library_path: str) -> dict[str, list[str]]:
    """Netlist each child sheet on its own and report any pin left on an auto-named net.

    xschem names an unconnected piece of wire ``netN``. The certified deck names every node, so a
    ``netN`` in a child's netlist is a pin the drawing failed to connect -- measured, per block,
    instead of assumed.
    """
    from spicexplorer_netlist2xschem.render import write_xschemrc

    probe = rcfile_dir
    probe.mkdir(parents=True, exist_ok=True)
    for fname, text in {**symbols, **children}.items():
        (probe / fname).write_text(text)
    rc = write_xschemrc(probe, os.pathsep.join([library_path, str(probe)]))
    lost: dict[str, list[str]] = {}
    for fname in sorted(children):
        netlist, _log = xschem_netlist(probe / fname, rc, probe)
        auto = sorted({m for ln in netlist.read_text().splitlines()
                       for m in re.findall(r"\bnet\d+\b", ln)})
        if auto:
            lost[fname] = auto
    return lost


def append_child_port_symbols(blocks_dir: Path) -> dict[str, list[str]]:
    """Draw each child sheet's own ports, in its symbol's pin order (P5c).

    ``wiring="labels"`` (P5) leaves a boundary net as a plain label, so the child sheet declares no
    interface and xschem reports the block symbol's pins against a schematic with none. Each
    sheet's ports and their directions are taken from the symbol the generator wrote for that same
    block -- so the two cannot disagree -- and drawn with the same helper the parent uses.
    """
    added: dict[str, list[str]] = {}
    for sch in sorted(blocks_dir.glob("*.sch")):
        sym = sch.with_suffix(".sym")
        if not sym.is_file() or "pin.sym}" in sch.read_text():
            continue
        pins = [(m.group(1), m.group(2)) for m in
                (re.search(r"\{name=(\S+) dir=(\S+)\}", ln) for ln in sym.read_text().splitlines())
                if m]
        if not pins:
            continue
        append_port_symbols(sch, pins)
        added[sch.name] = [f"{n} ({d})" for n, d in pins]
    return added


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
    # Some labels (the port symbols' own text) carry their font size in a different attribute
    # order and are not measured by the pattern above, so the right/bottom pad never falls below a
    # few characters' worth of overhang.
    pad_r = max(3 * margin, right - w + margin)
    pad_b = max(2 * margin, bottom - h + margin)
    head = (f'<svg{m.group(1)}width="{w + margin + pad_r:g}"{m.group(3)}'
            f'height="{h + margin + pad_b:g}"{m.group(5)}>'
            f'<g transform="translate({margin},{margin})">')
    text = text[: m.start()] + head + text[m.end():]
    text = text[: text.rindex("</svg>")] + "</g></svg>\n"
    svg.write_text(text)


# ----------------------------------------------------------------------------------------------
# hierarchy -> flat, leaf names preserved
# ----------------------------------------------------------------------------------------------
def flatten_hierarchy(netlist: Path, out: Path, *, note: str = "") -> dict:
    """The platform's flattener, as the record row this experiment writes.

    Splicing a block hierarchy back inline while PRESERVING leaf instance names is what lets the
    parameter assertion join the two netlists device by device; it is `spicexplorer_netlist2xschem
    .hierarchy.flatten_hierarchy` now, with its own cases for the two collisions it refuses and
    for the per-sheet `net1` two children both own.
    """
    r = _hierarchy.flatten_hierarchy(netlist, out, note=note)
    return {
        "out": str(r.out),
        "spliced": list(r.spliced),
        "devices": r.devices,
        "qualified_local_nets": sorted(r.qualified_local_nets),
    }
