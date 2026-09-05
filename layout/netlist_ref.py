"""The certified netlist, parsed once — the single source of device identity for the layout.

`review-002` **M7**: the layout generator used to write the LVS reference from its own hand-typed
`MOS` table, so "LVS-identical to the certified netlist" was never what the flow proved — a
divergence between the generator's table and
`circuits/ldo_ihp_capless/pdk/ihp-sg13g2/netlist.spice` would still pass. This module removes the
second table. It parses the **certified binding** and hands out:

* :func:`devices` — what the generator places (name, kind, nets, W/L in um, multiplicity);
* :func:`lvs_reference` — the flat M/R/C netlist the KLayout LVS deck compares against.

Both come from the same parse, so the drawing and the compare cannot disagree about a device.

**The one thing the reference adds** to the certified netlist is the layout's **dummy devices**.
They are not optional and they are not schematic: a matched row needs tied-off dummies at both
ends (`review-002` m3), and the IHP LVS deck extracts a fully shorted dummy MOS as a real device
which ``--purge``/``--purge_nets`` does **not** remove (measured, see REPORT). So every dummy is
declared here — and :func:`lvs_reference` **asserts that each one has all four terminals on a
single rail**, which is what keeps M7 shut: a dummy card can only ever be electrically inert, and
a real device's size still comes from the certified file.

Sources (`VREF`, the loop-break marker `VLP`) are not devices: their nodes `vref` and `lp_brk`
become pins of the drawn cell.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CELL = "ldo_ihp_capless"
NETLIST = (Path(__file__).resolve().parents[1] / "circuits" / CELL / "pdk" / "ihp-sg13g2"
           / "netlist.spice")
SIZING_YAML = (Path(__file__).resolve().parents[1] / "circuits" / CELL / "pdk" / "ihp-sg13g2"
               / "sizing.yaml")

# model -> (n nodes in the certified card, LVS card letter, n nodes the LVS deck wants)
_MODELS = {
    "sg13_lv_nmos": (4, "M", 4),
    "sg13_lv_pmos": (4, "M", 4),
    # rhigh is drawn 3-terminal in SPICE (the third node is the poly body `bn`); the standalone
    # IHP LVS deck extracts it as a 2-terminal device, so the reference drops the body node.
    "rhigh": (3, "R", 2),
    "cap_cmim": (2, "C", 2),
}

_SI = {"a": 1e-18, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6}


def um(v: object) -> float:
    """A sizing value in micrometres. Strings carry an SI suffix (``"8u"``); floats are metres
    (the optimizer's `design.json` convention)."""
    if isinstance(v, str):
        m = re.match(r"^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(meg|[afpnumk])?", v, re.I)
        if not m:
            raise ValueError(f"bad sizing value {v!r}")
        return float(m.group(1)) * _SI.get((m.group(2) or "").lower(), 1.0) * 1e6
    return float(v) * 1e6


def count(v: object) -> int:
    return int(round(float(v)))


@dataclass(frozen=True)
class Card:
    """One device of the certified netlist, with its parameters still symbolic."""

    name: str          # "XM1"
    model: str         # "sg13_lv_pmos"
    nodes: tuple[str, ...]
    params: dict[str, str]   # {"w": "x_dut_xm1_w", "l": "x_dut_xm1_l", "m": ...}

    @property
    def kind(self) -> str:
        return {"sg13_lv_nmos": "n", "sg13_lv_pmos": "p", "rhigh": "r", "cap_cmim": "c"}[self.model]


def load_sizing(path: Path | None = None) -> dict[str, object]:
    """`sizing.yaml` defaults — the design of record."""
    import yaml

    doc = yaml.safe_load((path or SIZING_YAML).read_text())
    return {v["name"]: v["default"] for v in doc["variables"]}


def parse(path: Path | None = None) -> list[Card]:
    """Every device card of the certified netlist, in file order."""
    out: list[Card] = []
    for raw in (path or NETLIST).read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith(("*", ".")) or not s[0].upper() == "X":
            continue
        tok = s.split()
        name, rest = tok[0], tok[1:]
        params = {}
        while rest and "=" in rest[-1]:
            k, v = rest.pop().split("=", 1)
            params[k.lower()] = v
        if not rest:
            raise ValueError(f"no model on card {s!r}")
        model = rest[-1]
        nodes = tuple(rest[:-1])
        if model not in _MODELS:
            raise ValueError(f"unknown model {model!r} on card {s!r} — teach netlist_ref about it")
        n_nodes, _, _ = _MODELS[model]
        if len(nodes) != n_nodes:
            raise ValueError(f"{name}: {len(nodes)} nodes, expected {n_nodes} for {model}")
        out.append(Card(name, model, nodes, params))
    return out


@dataclass(frozen=True)
class MosDev:
    """A transistor as the generator needs it: micrometres, and `m` already separated."""

    name: str
    kind: str          # "n" | "p"
    drain: str
    gate: str
    source: str
    bulk: str
    w: float           # per unit, um
    l: float           # um
    m: int             # parallel units (the layout folds them into fingers)

    @property
    def w_total(self) -> float:
        return self.w * self.m


def devices(sizing: dict[str, object], path: Path | None = None) -> tuple[list[MosDev], list[Card]]:
    """(transistors, passive cards) at this sizing point."""
    mos, passives = [], []
    for c in parse(path):
        if c.kind in ("n", "p"):
            d, g, s, b = c.nodes
            mos.append(MosDev(c.name, c.kind, d, g, s, b,
                              um(sizing[c.params["w"]]), um(sizing[c.params["l"]]),
                              count(sizing[c.params["m"]]) if "m" in c.params else 1))
        else:
            passives.append(c)
    return mos, passives


@dataclass(frozen=True)
class Dummy:
    """A layout-only, electrically inert device: every terminal on ``rail``."""

    name: str
    kind: str      # "n" | "p" | "r"
    rail: str      # "vss" | "vdd"
    w: float       # um
    l: float       # um


# The cell's pins. `vref` and `lp_brk` are the nodes of the two sources the subckt carries but the
# layout does not draw, so they are drawn as pins; `fb` is a test/trim pin on the left edge.
PINS = ["vdd", "vout", "vss", "vref", "lp_brk", "fb"]


def lvs_reference(sizing: dict[str, object], dummies: list[Dummy] | None = None,
                  path: Path | None = None) -> str:
    """The flat netlist the KLayout LVS deck compares the layout against.

    Derived from the certified binding, never from the generator's own device list (M7). The only
    transformations, all mechanical:

    * ``X<name> ... <model> w=<key> l=<key>`` -> a primitive ``M``/``R``/``C`` card with the
      sizing values substituted (the deck reads primitives, not subcircuit calls);
    * a transistor's ``m`` is folded into ``w`` — the layout draws the ``m`` parallel units as
      fingers of one device, which the deck (with ``--combine_devices``) sees as one device of the
      summed width. **This is the side the deck is on**: a folded multi-finger device carries less
      junction area/perimeter than ``m`` separate ones, and the deck compares W and L only;
    * ``rhigh``'s third (poly body) node is dropped: the standalone IHP LVS deck extracts the poly
      resistor as a 2-terminal device;
    * the layout's dummy devices are appended, each asserted electrically inert.
    """
    mos, passives = devices(sizing, path)
    lines = [f"* {CELL} — LVS reference, derived from {NETLIST.name} (layout/netlist_ref.py)",
             f".subckt {CELL} {' '.join(PINS)}"]
    for d in mos:
        lines.append(f"M{d.name[1:]} {d.drain} {d.gate} {d.source} {d.bulk} "
                     f"sg13_lv_{d.kind}mos w={d.w_total:g}u l={d.l:g}u")
    for c in passives:
        w, l = um(sizing[c.params["w"]]), um(sizing[c.params["l"]])
        m = f" m={count(sizing[c.params['m']])}" if "m" in c.params else ""
        if c.kind == "r":
            lines.append(f"R{c.name[1:]} {c.nodes[0]} {c.nodes[1]} rhigh w={w:g}u l={l:g}u{m}")
        else:
            lines.append(f"C{c.name[1:]} {c.nodes[0]} {c.nodes[1]} cap_cmim w={w:g}u l={l:g}u{m}")
    for dm in dummies or []:
        # The guarantee that keeps M7 shut: a dummy card is inert by construction.
        assert dm.rail in ("vss", "vdd"), f"dummy {dm.name}: rail {dm.rail!r} is not a cell rail"
        if dm.kind in ("n", "p"):
            lines.append(f"M{dm.name} {dm.rail} {dm.rail} {dm.rail} {dm.rail} "
                         f"sg13_lv_{dm.kind}mos w={dm.w:g}u l={dm.l:g}u")
        elif dm.kind == "r":
            lines.append(f"R{dm.name} {dm.rail} {dm.rail} rhigh w={dm.w:g}u l={dm.l:g}u")
        else:
            raise ValueError(f"dummy {dm.name}: unknown kind {dm.kind!r}")
    lines.append(f".ends {CELL}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":  # pragma: no cover - a look at what the parse produced
    sz = load_sizing()
    m, p = devices(sz)
    for d in m:
        print(f"{d.name:6s} {d.kind} {d.drain:8s} {d.gate:8s} {d.source:8s} "
              f"w={d.w:g} l={d.l:g} m={d.m}")
    for c in p:
        print(c)
    print(lvs_reference(sz))
