#!/usr/bin/env python3
"""Parameterized gdsfactory layout of ``ldo_ihp_capless`` (IHP SG13G2, sg13_lv devices).

Generator contract (``spicexplorer_layout.gen``): ``build(params, sizing=None) -> Component``,
``write_lvs_reference(params, sizing, out)``.  Run it with the interpreter that has gdsfactory +
ihp-gdsfactory (``~/miniconda3/envs/ai_env/bin/python``, see doc/environment.md), never the
repo venv.

Floorplan (all y derived from live device bounding boxes, x from the device list):

    row C   XMP (pass PMOS, x_dut_xmp_m fingers of x_dut_xmp_w)                    vout bus on top
    ------- vdd rail (Metal1) with n-taps -------
    row B   PMOS: XMBP XMT XM6 | XM1 XM2 (mirror pair) | XMC | XMCP XMD (mirror pair)
    ------- channel 1: one Metal1 track per internal net, every vertical is Metal2 -------
    row A   NMOS: XMB0 XMB1 XMS | XMA XMB (mirror pair) | XM3 XM4 (mirror pair) | XM5
    ------- vss rail (Metal1) with p-taps -------
    left:   rhigh serpentines XR1, XR2 (divider), XRB (bias)      right: MIM caps XCFF, XCC, XCOUT (unit array)

Routing discipline: device straps + channel tracks + rails are Metal1 (horizontal); every
inter-row connection is a Metal2 vertical with a Via1 pad at each end, at an x that is unique to
that terminal (gate pad left of the device, drain pad right of it, source pad further right), so
no two nets ever share a column.  The pass-gate net runs one Metal2 vertical from XMD/XMS to the
XMP gate bar (doc/journal/fvf-gate-cap-is-slew.md: keep that net short).

Sizes come from the sizing dict (``lab.dut.Design.knobs()`` units: SI strings such as ``"8u"``,
or floats in metres from the optimizer's ``design.json``); ``SIZING`` below = sizing.yaml
defaults.  Layout knobs (``LayoutParams``) are the free constants a layout optimizer may move.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
from pathlib import Path

import gdsfactory as gf
from ihp import PDK
from ihp import cells as C
from ihp.cells.fet_transistors import _mos_core

PDK.activate()

CELL = "ldo_ihp_capless"
GRID = 0.005
VIA = 0.19      # V1.a / Vn.a exact
TVIA = 0.42     # TV1.a exact
VPAD = 0.38     # via pad (< 0.39 "wide line", so the 0.21 space rule applies)
STRAP = 0.5     # S/D strap centre offset from the active edge
GATE = 1.5      # gate bar centre offset from the active edge
GPAD = 0.5      # gate bar height
CONT = 0.16     # Cnt.a exact
MIM_BIAS = 0.72  # gdsfactory grows the MIM box by 0.36/side vs the cmim() args
W_M1 = 0.2
W_M2 = 0.2

# --- sizing: read from the circuit binding so drawing and netlist cannot drift ---
# The design of record lives in ONE place: circuits/<id>/pdk/<pdk>/sizing.yaml `default:` fields
# (experiments/003-sizing moves them to the optimizer's rounded winner). This module reads that
# file rather than carrying a copy, so a re-sized cell redraws itself with no edit here.
SIZING_YAML = Path(__file__).resolve().parents[1] / "circuits" / CELL / "pdk" / "ihp-sg13g2" / "sizing.yaml"


def _load_sizing() -> dict[str, object]:
    import yaml
    doc = yaml.safe_load(SIZING_YAML.read_text())
    return {v["name"]: v["default"] for v in doc["variables"]}


SIZING: dict[str, object] = _load_sizing()

_SI = {"a": 1e-18, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6}


def _um(v: object) -> float:
    """Sizing value -> micrometres (strings with SI suffix, or metres as floats)."""
    if isinstance(v, str):
        m = re.match(r"^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(meg|[afpnumk])?", v, re.I)
        if not m:
            raise ValueError(f"bad sizing value {v!r}")
        return float(m.group(1)) * _SI.get((m.group(2) or "").lower(), 1.0) * 1e6
    return float(v) * 1e6


def _count(v: object) -> int:
    return int(round(float(v)))


def _s(v: float) -> float:
    return round(round(v / GRID) * GRID, 4)


@dataclasses.dataclass(frozen=True)
class LayoutParams:
    """Free layout constants (um) — the layout-optimizer search space."""

    dev_gap: float = 3.2      # x gap between devices in a row (three 0.6 via columns + the neighbour's gate pad)
    grp_gap: float = 1.6      # extra gap between functional groups in a row
    track_pitch: float = 0.7  # channel-1 Metal1 track pitch (0.38 pads -> 0.32 space)
    ch_margin: float = 0.9    # clearance from the gate/drain bars to the first track
    rail_w: float = 0.8       # vdd / vss rail width
    rail_gap: float = 1.6     # active edge -> rail centre (source-strap pad top + M1 space + rail_w/2)
    mim_gap: float = 3.0      # gap between MIM units / blocks
    res_pitch: float = 2.0    # serpentine segment pitch (rhigh cell is 0.9 wide)
    r_segs: int = 4           # divider resistors: serpentine segments (l/r_segs each)
    rb_segs: int = 2          # bias resistor segments
    blk_gap: float = 6.0      # gap between the transistor stack and the passive blocks
    tap_pitch: float = 12.0   # max spacing of well/substrate ties along the rails (LU.a/b: 20 um)


BOUNDS: dict[str, tuple[float, float]] = {
    "dev_gap": (3.0, 6.0), "grp_gap": (0.0, 6.0), "track_pitch": (0.65, 1.2), "ch_margin": (0.8, 2.0),
    "rail_w": (0.5, 2.0), "rail_gap": (1.4, 2.5), "mim_gap": (2.5, 8.0), "res_pitch": (1.8, 4.0),
    "blk_gap": (4.0, 15.0), "tap_pitch": (6.0, 18.0),
}

_STACK = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5", "TopMetal1"]
_VIA = {  # bottom layer -> (via layer, size, space, min enclosure)
    "Metal1": ("Via1drawing", VIA, 0.24, 0.06),   # rule 0.22 + grid slack
    "Metal2": ("Via2drawing", VIA, 0.24, 0.06),
    "Metal3": ("Via3drawing", VIA, 0.24, 0.06),
    "Metal4": ("Via4drawing", VIA, 0.24, 0.06),
    "Metal5": ("TopVia1drawing", TVIA, 0.44, 0.45),
}


# --- the device list: one place for netlist identity (also drives write_lvs_reference) ---
# (name, kind, drain, gate, source, w_key, l_key, nf/m key or None)
MOS = [
    ("XMB0", "n", "nbias", "nbias", "vss", "x_dut_xmb0_w", "x_dut_xmb0_l"),
    ("XMB1", "n", "pbias", "nbias", "vss", "x_dut_xmb1_w", "x_dut_xmb0_l"),
    ("XMBP", "p", "pbias", "pbias", "vdd", "x_dut_xmbp_w", "x_dut_xmbp_l"),
    ("XMT", "p", "ea_tail", "pbias", "vdd", "x_dut_xmt_w", "x_dut_xmbp_l"),
    ("XM1", "p", "ea_n", "fb", "ea_tail", "x_dut_xm1_w", "x_dut_xm1_l"),
    ("XM2", "p", "ea_o1", "vref", "ea_tail", "x_dut_xm1_w", "x_dut_xm1_l"),
    ("XM3", "n", "ea_n", "ea_n", "vss", "x_dut_xm3_w", "x_dut_xm3_l"),
    ("XM4", "n", "ea_o1", "ea_n", "vss", "x_dut_xm3_w", "x_dut_xm3_l"),
    ("XM5", "n", "ea_out", "ea_o1", "vss", "x_dut_xm5_w", "x_dut_xm5_l"),
    ("XM6", "p", "ea_out", "pbias", "vdd", "x_dut_xm6_w", "x_dut_xmbp_l"),
    ("XMC", "p", "x1", "ea_out", "vout", "x_dut_xmc_w", "x_dut_xmc_l"),
    ("XMA", "n", "x1", "x1", "vss", "x_dut_xma_w", "x_dut_xma_l"),
    ("XMB", "n", "y", "x1", "vss", "x_dut_xma_w", "x_dut_xma_l"),
    ("XMCP", "p", "y", "y", "vdd", "x_dut_xmcp_w", "x_dut_xmcp_l"),
    ("XMD", "p", "gate", "y", "vdd", "x_dut_xmcp_w", "x_dut_xmcp_l"),
    ("XMS", "n", "gate", "nbias", "vss", "x_dut_xms_w", "x_dut_xms_l"),
    ("XMP", "p", "vout", "gate", "vdd", "x_dut_xmp_w", "x_dut_xmp_l"),
]
# core pins: the ideal VREF and the 0 V loop-break marker VLP stay OUTSIDE the drawn core
PINS = ["vdd", "vout", "vss", "vref", "lp_brk"]
# channel-1 tracks (Metal1, bottom to top); vdd/vss are rails, not tracks
TRACKS = ["nbias", "pbias", "ea_tail", "ea_n", "ea_o1", "ea_out", "vref", "fb", "lp_brk", "x1", "y", "gate", "vout"]


@dataclasses.dataclass
class Dev:
    name: str
    kind: str
    ref: object
    cols: list[float]
    gates: list[float]
    ax0: float
    ax1: float
    ay0: float
    ay1: float
    wf: float
    term: dict[str, tuple[float, float]] = dataclasses.field(default_factory=dict)  # net -> via point


class Builder:
    def __init__(self, p: LayoutParams, sz: dict[str, object]):
        self.p, self.sz = p, sz
        self.c = gf.Component(CELL)
        self.verticals: list[tuple[str, float, float, float]] = []  # (net, x, y0, y1) Metal2
        self.track_y: dict[str, float] = {}
        self.track_pts: dict[str, list[float]] = {t: [] for t in TRACKS}  # x of each vertical
        # Every Metal1 feature that a later stub must not run into, as (net, y0, y1, x0, x1).
        # Without this the Metal1 stub that `to_track` draws from a terminal to its allocated
        # Metal2 column can walk sideways straight through a NEIGHBOUR's gate bar -- a short that
        # DRC cannot see (overlapping same-layer shapes merge into one legal polygon) and that
        # only LVS catches. doc/journal/metal1-stub-shorts-are-drc-invisible.md.
        self.m1_rows: list[list] = []
        self.rail_y: dict[str, float] = {}

    # -- primitives --------------------------------------------------------
    def rect(self, layer: str, x0: float, y0: float, x1: float, y1: float) -> None:
        x0, x1 = sorted((_s(x0), _s(x1)))
        y0, y1 = sorted((_s(y0), _s(y1)))
        if x1 - x0 < GRID / 2 or y1 - y0 < GRID / 2:
            return
        self.c.add_polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer=layer)

    def h(self, layer: str, y: float, x0: float, x1: float, w: float) -> None:
        self.rect(layer, min(x0, x1) - w / 2, y - w / 2, max(x0, x1) + w / 2, y + w / 2)

    def v(self, layer: str, x: float, y0: float, y1: float, w: float) -> None:
        self.rect(layer, x - w / 2, min(y0, y1) - w / 2, x + w / 2, max(y0, y1) + w / 2)

    def m1h(self, y, x0, x1, w=W_M1):
        self.h("Metal1drawing", y, x0, x1, w)

    def m1v(self, x, y0, y1, w=W_M1):
        self.v("Metal1drawing", x, y0, y1, w)

    def vstack(self, x: float, y: float, bot: str, top: str, size: float = VPAD) -> None:
        i0, i1 = _STACK.index(bot), _STACK.index(top)
        for i in range(i0, i1 + 1):
            lay = _STACK[i]
            s = max(size, 1.64) if lay == "TopMetal1" else size
            self.rect(lay + "drawing", x - s / 2, y - s / 2, x + s / 2, y + s / 2)
        for i in range(i0, i1):
            vl, vs, vsp, enc = _VIA[_STACK[i]]
            avail = size - 2 * enc
            n = max(1, min(3, int((avail + vsp + 1e-9) // (vs + vsp))))
            span = n * vs + (n - 1) * vsp
            for a in range(n):
                for b in range(n):
                    xx = x - span / 2 + a * (vs + vsp)
                    yy = y - span / 2 + b * (vs + vsp)
                    self.rect(vl, xx, yy, xx + vs, yy + vs)

    def v12(self, x, y):
        self.vstack(x, y, "Metal1", "Metal2")

    def label(self, net: str, x: float, y: float, layer: str = "Metal1text") -> None:
        self.c.add_label(text=net, position=(_s(x), _s(y)), layer=layer)

    def vert(self, net: str, x: float, y0: float, y1: float) -> None:
        """Metal2 vertical between two Via1 pads (both drawn)."""
        self.v12(x, y0)
        self.v12(x, y1)
        self.v("Metal2drawing", x, y0, y1, W_M2)
        self.verticals.append((net, _s(x), _s(min(y0, y1)), _s(max(y0, y1))))

    def m1_claim(self, net: str, y: float, x0: float, x1: float, h: float = W_M1) -> None:
        self.m1_rows.append([net, _s(y - h / 2), _s(y + h / 2), _s(min(x0, x1)), _s(max(x0, x1))])

    def m1_retag(self, old: str, new: str) -> None:
        for r in self.m1_rows:
            if r[0] == old:
                r[0] = new

    def stub_clear(self, net: str, y: float, xa: float, xb: float,
                   cx: float = 0.28, cy: float = 0.22) -> bool:
        """Would a Metal1 stub of ``net`` at ``y`` from ``xa`` to ``xb`` touch another net's
        Metal1?"""
        lo, hi = min(xa, xb) - cx, max(xa, xb) + cx
        ylo, yhi = y - W_M1 / 2 - cy, y + W_M1 / 2 + cy
        for n, y0, y1, x0, x1 in self.m1_rows:
            if n == net or y1 < ylo or y0 > yhi or x1 < lo or x0 > hi:
                continue
            return False
        return True

    def alloc(self, net: str, x: float, y0: float, y1: float, step: float = 0.6) -> float:
        """First x from ``x`` in ``step`` increments whose Metal2 vertical over [y0, y1] clears
        every other net's vertical by >= 0.6 um (pad 0.38 + M2 space 0.21)."""
        lo, hi = min(y0, y1), max(y0, y1)
        # Preferred direction first, then the other one: a column that is free of Metal2 but whose
        # Metal1 stub would cross a foreign gate bar is NOT usable, so the walk must be able to
        # turn round instead of marching into the neighbour.
        for k in range(60):
            for s in (step, -step) if k else (step,):
                xx = _s(x + k * s)
                if all(v[0] == net or abs(v[1] - xx) >= 0.6 - 1e-6 or v[3] < lo - 0.6 or v[2] > hi + 0.6
                       for v in self.verticals) and self.stub_clear(net, y0, x, xx):
                    return xx
        raise AssertionError(f"no free Metal2 column for {net} near x={x} (widen LayoutParams.dev_gap)")

    def to_track(self, net: str, x: float, y: float, step: float = 0.6) -> float:
        """Connect the Metal1 point (x, y) to the channel track / rail of ``net`` with a Metal2
        vertical at a collision-free x (a Metal1 stub bridges any shift); returns the x used."""
        yt = self.rail_y.get(net, self.track_y.get(net))
        if yt is None:
            raise KeyError(f"no track or rail for net {net}")
        xx = self.alloc(net, x, y, yt, step)
        if xx != _s(x):
            self.m1h(y, x, xx)
            self.m1_claim(net, y, x, xx)
        self.vert(net, xx, y, yt)
        self.track_pts.setdefault(net, []).append(xx)  # type: ignore[arg-type]
        return xx

    # -- transistor --------------------------------------------------------
    def mos(self, name: str, w: float, l: float, nf: int, pmos: bool, x0: float, y_act: float,
            *, mirror: bool = False, d_top: bool, g_top: bool) -> Dev:
        """Place one lv MOS with its active's left edge at x0 and bottom at y_act.

        Straps: S/D bars at +-STRAP outside the active, gate bar at +-GATE (poly tabs + contacts
        + Metal1).  Returns column/gate x lists; the caller wires S/D/G."""
        # _mos_core: the public nmos/pmos wrappers cap width at 10 um regardless of nf
        cell = _mos_core(width=w, length=l, nf=nf, is_pmos=pmos, is_hv=False)
        ref = self.c << cell
        if mirror:
            ref.dmirror_x()
        sx, sy = ref.ports["S"].center
        dx = ref.ports["D"].center[0]
        gx = ref.ports["G"].center[0]
        pitch = dx - sx
        wf = w / nf
        cols = [sx + k * pitch for k in range(nf + 1)]
        gates = [gx + k * pitch for k in range(nf)]
        ax0, ax1 = min(cols) - 0.15, max(cols) + 0.15
        ay0 = sy - wf / 2
        ddx, ddy = x0 - ax0, y_act - ay0
        ref.dmovex(_s(ddx))
        ref.dmovey(_s(ddy))
        cols = [_s(v + ddx) for v in cols]
        gates = [_s(v + ddx) for v in gates]
        ax0, ax1 = _s(ax0 + ddx), _s(ax1 + ddx)
        ay0, ay1 = _s(y_act), _s(y_act + wf)
        d = Dev(name, "p" if pmos else "n", ref, cols, gates, ax0, ax1, ay0, ay1, wf)
        # gate: poly tabs -> poly bar -> contacts -> Metal1 bar
        tab = min(GPAD, l)                     # tab = the gate's own width: no step at the active edge (Cnt.f / Gat.d)
        y_g = (ay1 + GATE) if g_top else (ay0 - GATE)
        py = ay1 if g_top else ay0
        for gxx in gates:
            self.rect("GatPolydrawing", gxx - tab / 2, py, gxx + tab / 2, y_g)
        gb0, gb1 = min(gates) - 0.25, max(gates) + 0.25   # bar ends enclose the end contacts by >= 0.07
        self.rect("GatPolydrawing", gb0, y_g - GPAD / 2, gb1, y_g + GPAD / 2)
        self.rect("Metal1drawing", gb0, y_g - GPAD / 2, gb1, y_g + GPAD / 2)
        for gxx in gates:
            self.rect("Contdrawing", gxx - CONT / 2, y_g - CONT / 2, gxx + CONT / 2, y_g + CONT / 2)
        d.term["_gate_bar"] = (y_g, gb0, gb1)  # type: ignore[assignment]
        self.m1_claim(f"@g:{name}", y_g, gb0, gb1, GPAD)
        return d

    def strap(self, d: Dev, which: str, top: bool, ext_to: float | None = None,
              net: str | None = None) -> float:
        """Metal1 bar joining the S (even) or D (odd) columns outside the active; returns its y."""
        grp = d.cols[0::2] if which == "S" else d.cols[1::2]
        y = d.ay1 + STRAP if top else d.ay0 - STRAP
        for xx in grp:
            self.m1v(xx, d.ay1 if top else d.ay0, y)
        x0, x1 = min(grp), max(grp)
        if ext_to is not None:
            x0, x1 = min(x0, ext_to), max(x1, ext_to)
        self.m1h(y, x0, x1)
        if net:
            self.m1_claim(net, y, x0, x1)
        return y

    def columns_to_rail(self, d: Dev, which: str, y_rail: float) -> None:
        """S (or D) columns straight to a rail on Metal1 (the rail must be on that side)."""
        grp = d.cols[0::2] if which == "S" else d.cols[1::2]
        for xx in grp:
            self.m1v(xx, d.ay0 if y_rail < d.ay0 else d.ay1, y_rail)

    def gate_pad(self, d: Dev, x: float, net: str) -> float:
        """Extend the gate bar's Metal1 to x and return the bar y (a via pad goes there)."""
        y_g, gb0, gb1 = d.term["_gate_bar"]  # type: ignore[misc]
        x0, x1 = min(gb0, x - VPAD / 2), max(gb1, x + VPAD / 2)
        self.rect("Metal1drawing", x0, y_g - GPAD / 2, x1, y_g + GPAD / 2)
        self.m1_retag(f"@g:{d.name}", net)          # the bar now belongs to a real net
        self.m1_claim(net, y_g, x0, x1, GPAD)
        return y_g

    # -- passives ----------------------------------------------------------
    def serpentine(self, name: str, w: float, l_total: float, segs: int, x0: float, y0: float) -> tuple[tuple[float, float], tuple[float, float]]:
        """rhigh as ``segs`` vertical segments joined top/bottom by Metal1; returns the two end pads."""
        seg = _s(l_total / segs)
        cell = C.rhigh(dy=seg, dx=w)
        ends = []
        for i in range(segs):
            ref = self.c << cell
            b = ref.bbox()
            ref.dmovex(_s(x0 + i * self.p.res_pitch - b.left))
            ref.dmovey(_s(y0 - b.bottom))
            p1, p2 = ref.ports["P1"].center, ref.ports["P2"].center  # P1 top, P2 bottom
            ends.append((p1, p2))
        for i in range(segs - 1):
            top, bot = ends[i][0], ends[i][1]
            ntop, nbot = ends[i + 1][0], ends[i + 1][1]
            if i % 2 == 0:   # join at the top
                self.m1h(top[1], top[0], ntop[0], 0.3)
            else:            # join at the bottom
                self.m1h(bot[1], bot[0], nbot[0], 0.3)
        first = ends[0][1]                       # bottom of segment 0
        last = ends[-1][1] if segs % 2 == 0 else ends[-1][0]   # even: both ends at the bottom
        return first, last

    def mim(self, unit: float, x0: float, y0: float) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float, float, float]]:
        """One MIM unit with its Metal5 plate's lower-left at (x0, y0); returns
        (bottom-plate pad point on Metal1, top-plate pad point on Metal1, plate bbox)."""
        cell = C.cmim(width=unit - MIM_BIAS, length=unit - MIM_BIAS)
        ref = self.c << cell
        b = ref.bbox()
        ref.dmovex(_s(x0 - b.left))
        ref.dmovey(_s(y0 - b.bottom))
        b = ref.bbox()
        yc = (b.bottom + b.top) / 2
        # bottom plate (Metal5): stack down to Metal1 just left of the plate
        xb = _s(b.left - 1.2)
        self.vstack(xb, yc, "Metal2", "Metal5", 1.0)   # Metal1<->Metal2 comes from the track vertical's own pad
        self.h("Metal5drawing", yc, xb, b.left + 0.3, 0.6)
        # top plate (TopMetal1): stack down to Metal1 right of the plate, TopMetal1 strap
        xt = _s(b.right + 2.2)
        self.vstack(xt, yc, "Metal2", "TopMetal1", 1.0)
        self.h("TopMetal1drawing", yc, ref.ports["PLUS"].center[0], xt, 1.64)
        return (xb, yc), (xt, yc), (b.left, b.bottom, b.right, b.top)

    # -- checks ------------------------------------------------------------
    def check(self) -> None:
        vs = self.verticals
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                a, b = vs[i], vs[j]
                if a[0] != b[0] and abs(a[1] - b[1]) < 0.6 - 1e-6 and not (a[3] < b[2] - 0.6 or b[3] < a[2] - 0.6):
                    raise AssertionError(f"Metal2 verticals collide: {a} vs {b}")


def build(p: LayoutParams = LayoutParams(), sizing: dict[str, object] | None = None) -> gf.Component:
    sz = {**SIZING, **(sizing or {})}
    b = Builder(p, sz)
    W = {n: _um(sz[wk]) for n, _, _, _, _, wk, _ in MOS}
    L = {n: _um(sz[lk]) for n, _, _, _, _, _, lk in MOS}
    NF = {n: 1 for n, *_ in MOS}
    NF["XMP"] = _count(sz["x_dut_xmp_m"])     # the m parallel units are drawn as nf fingers
    W["XMP"] = W["XMP"] * NF["XMP"]           # total width; fingers of x_dut_xmp_w
    net = {n: (dn, gn, sn) for n, _, dn, gn, sn, _, _ in MOS}

    # ---------------- row A: NMOS, sources to the vss rail below ----------------
    rowA = [["XMB0", "XMB1", "XMS"], ["XMA", "XMB"], ["XM3", "XM4"], ["XM5"]]
    y_vss = 0.0
    b.rail_y["vss"] = y_vss
    yA = y_vss + p.rail_gap
    devs: dict[str, Dev] = {}
    x = 0.0
    for gi, grp in enumerate(rowA):
        if gi:
            x += p.grp_gap
        for k, n in enumerate(grp):
            mirror = (len(grp) == 2 and k == 1)
            d = b.mos(n, W[n], L[n], NF[n], False, x + 0.6, yA, mirror=mirror, d_top=True, g_top=True)
            devs[n] = d
            x = d.ax1 + p.dev_gap
    ayA = max(d.ay1 for d in devs.values())
    y_ch0 = ayA + GATE + GPAD / 2 + p.ch_margin          # first track y
    for i, t in enumerate(TRACKS):
        b.track_y[t] = _s(y_ch0 + i * p.track_pitch)
    y_ch1 = b.track_y[TRACKS[-1]] + p.ch_margin
    # rails and straps of row A (drain pads right of the device, gate pads left of it)
    for n, d in devs.items():
        b.columns_to_rail(d, "S", y_vss)
        xr = _s(d.ax1 + 0.55)
        yd = b.strap(d, "D", True, ext_to=xr, net=net[n][0])
        b.to_track(net[n][0], xr, yd)
        xl = _s(d.ax0 - 0.55)
        yg = b.gate_pad(d, xl, net[n][1])
        b.to_track(net[n][1], xl, yg, step=-0.6)

    # ---------------- row B: PMOS, sources to the vdd rail above ----------------
    rowB = [["XMBP", "XMT", "XM6"], ["XM1", "XM2"], ["XMC"], ["XMCP", "XMD"]]
    wfB = max(W[n] for grp in rowB for n in grp)
    yB = y_ch1 + GATE + GPAD / 2 + 0.3
    x = 0.0
    for gi, grp in enumerate(rowB):
        if gi:
            x += p.grp_gap
        for k, n in enumerate(grp):
            mirror = (len(grp) == 2 and k == 1)
            d = b.mos(n, W[n], L[n], NF[n], True, x + 0.6, yB, mirror=mirror, d_top=False, g_top=False)
            devs[n] = d
            x = d.ax1 + p.dev_gap
    y_vdd = _s(yB + wfB + p.rail_gap)
    b.rail_y["vdd"] = y_vdd
    for grp in rowB:
        for n in grp:
            d = devs[n]
            dn, gn, sn = net[n]
            xr = _s(d.ax1 + 0.55)
            yd = b.strap(d, "D", False, ext_to=xr, net=dn)
            b.to_track(dn, xr, yd)
            xl = _s(d.ax0 - 0.55)
            yg = b.gate_pad(d, xl, gn)
            b.to_track(gn, xl, yg, step=-0.6)
            if sn == "vdd":
                b.columns_to_rail(d, "S", y_vdd)
            else:
                xs = _s(d.ax1 + 1.15)
                ys = b.strap(d, "S", True, ext_to=xs, net=sn)
                b.to_track(sn, xs, ys)

    # ---------------- row C: the pass device ----------------
    yC = y_vdd + p.rail_gap
    xC = devs["XMD"].ax1 + p.dev_gap + 2.0            # right of row B, its own columns
    dP = b.mos("XMP", W["XMP"], L["XMP"], NF["XMP"], True, xC, yC, d_top=True, g_top=True)
    devs["XMP"] = dP
    b.columns_to_rail(dP, "S", y_vdd)
    xr = _s(dP.ax1 + 0.55)
    y_vout = b.strap(dP, "D", True, ext_to=xr, net="vout")
    b.m1h(y_vout, min(dP.cols[1::2]), xr, 0.6)         # thicker vout bus
    b.to_track("vout", xr, y_vout)
    xl = _s(dP.ax0 - 0.55)
    yg = b.gate_pad(dP, xl, "gate")
    b.to_track("gate", xl, yg, step=-0.6)
    x_stack = max(d.ax1 for d in devs.values()) + 2.0
    y_top = dP.ay1 + GATE + GPAD / 2 + 0.5

    # ---------------- rails, taps, wells ----------------
    x_left = -p.blk_gap - 1.0
    ntap = C.ntap1(width=0.78, length=1.0, rows=2, cols=1)
    ptap = C.ptap1(width=0.78, length=1.0, rows=2, cols=1)
    # well / substrate ties every <= tap_pitch along both rails (LU.a / LU.b: <= 20 um to a tie);
    # they sit on the rails in the device gaps, never under a Metal2 column pad
    x_lo = min(d.ax0 for d in devs.values()) - 1.4
    x_hi = x_stack - 0.8
    n_t = int((x_hi - x_lo) / p.tap_pitch) + 2
    for i in range(n_t):
        xt = _s(x_lo + i * (x_hi - x_lo) / (n_t - 1))
        nt = b.c << ntap
        nt.dcenter = (xt, _s(y_vdd))
        pt = b.c << ptap
        pt.dcenter = (xt, _s(y_vss))
    x_min_dev = min(d.ax0 for d in devs.values()) - 2.2
    # one n-well over rows B + C (merges the cells' own wells; keeps NW.b spacing trivial)
    b.rect("NWelldrawing", x_min_dev, yB - GATE - GPAD / 2 - 0.5, x_stack + 0.2, y_top)

    # ---------------- passives: resistors left, MIMs right ----------------
    # divider XR1 (lp_brk-fb), XR2 (fb-vss), bias XRB (vdd-nbias): serpentines left of the stack
    r_w = _um(sz["r_w"])
    xres = x_left - p.res_pitch * (p.r_segs * 2 + p.rb_segs) - 2.0
    yres = y_ch1 + 1.0
    r1a, r1b = b.serpentine("XR1", r_w, _um(sz["r_fb_l"]), p.r_segs, xres, yres)
    r2a, r2b = b.serpentine("XR2", r_w, _um(sz["r_fb_l"]), p.r_segs, xres + p.res_pitch * p.r_segs, yres)
    rba, rbb = b.serpentine("XRB", r_w, _um(sz["r_bias_l"]), p.rb_segs, xres + p.res_pitch * 2 * p.r_segs, yres)
    res_ends = {"XR1": (r1a, r1b, "lp_brk", "fb"), "XR2": (r2a, r2b, "fb", "vss"), "XRB": (rba, rbb, "vdd", "nbias")}
    for nm, (e0, e1, n0, n1) in res_ends.items():
        for (ex, ey), nn in ((e0, n0), (e1, n1)):
            b.to_track(nn, _s(ex), _s(ey))
    # MIMs: XCFF (lp_brk top / fb bottom), XCC (ea_out top / ea_o1 bottom), XCOUT (vout top / vss bottom) x m
    xm = x_stack + p.blk_gap
    ym = y_vss + 1.0
    cff = _um(sz["c_ff_w"])
    bt, tp, bb = b.mim(cff, xm, ym)
    b.to_track("fb", *bt)
    b.to_track("lp_brk", *tp)
    ym2 = bb[3] + p.mim_gap
    ccw = _um(sz["c_comp_w"])
    bt, tp, bb = b.mim(ccw, xm, ym2)
    b.to_track("ea_o1", *bt)
    b.to_track("ea_out", *tp)
    xm3 = bb[2] + p.mim_gap + 3.0
    cw, cm = _um(sz["c_out_w"]), _count(sz["c_out_m"])
    cols_ = 2 if cm > 1 else 1
    yy, xx = ym, xm3
    for i in range(cm):
        col, row = i % cols_, i // cols_
        bt, tp, bb = b.mim(cw, xm3 + col * (cw + 1.2 + p.mim_gap + 4.0), ym + row * (cw + 1.2 + p.mim_gap))
        b.to_track("vss", *bt)
        b.to_track("vout", *tp)
        y_top = max(y_top, bb[3] + 1.0)
    x_right = bb[2] + 4.0

    # ---------------- channel tracks, rails, pins ----------------
    b.m1h(y_vss, xres - 1.0, x_right, p.rail_w)            # under the resistors too
    b.m1h(y_vdd, xres - 1.0, x_stack, p.rail_w)            # XRB's vdd end sits over the resistors
    b.label("vss", 0.0, y_vss)
    b.label("vdd", 0.0, y_vdd)
    for t in TRACKS:
        xs = b.track_pts[t]
        if not xs:
            raise AssertionError(f"net {t} has no terminals")
        b.m1h(b.track_y[t], min(xs) - VPAD / 2, max(xs) + VPAD / 2)
    # Label EVERY track, not just the pins: the KLayout extractor names a net after its label, so
    # this is what makes the PEX netlist readable (per-net C by name) and lets the post-layout
    # deck re-attach the MIM capacitors, whose plates are stripped before extraction, to
    # `ea_out`/`ea_o1`/`fb` rather than to \$12-style anonymous nets.
    for t_ in TRACKS:
        xs = b.track_pts[t_]
        b.label(t_, (min(xs) + max(xs)) / 2, b.track_y[t_])
    b.check()
    return b.c


def write_lvs_reference(p: LayoutParams = LayoutParams(), sizing: dict[str, object] | None = None,
                        out: str | os.PathLike | None = None) -> str:
    """Flat M/R/C-card netlist for the KLayout LVS deck (widths folded: XMP = one device of
    w*m).  VREF and VLP are not devices: vref and lp_brk are core pins."""
    sz = {**SIZING, **(sizing or {})}
    lines = [f"* {CELL} — LVS reference (generated by gen_ldo.write_lvs_reference)",
             f".subckt {CELL} {' '.join(PINS)}"]
    for n, kind, dn, gn, sn, wk, lk in MOS:
        w, l = _um(sz[wk]), _um(sz[lk])
        if n == "XMP":
            w *= _count(sz["x_dut_xmp_m"])
        bulk = "vdd" if kind == "p" else "vss"
        lines.append(f"M{n[1:]} {dn} {gn} {sn} {bulk} sg13_lv_{'p' if kind == 'p' else 'n'}mos w={w:g}u l={l:g}u")
    rw = _um(sz["r_w"])
    lines += [f"R1 lp_brk fb rhigh w={rw:g}u l={_um(sz['r_fb_l']):g}u",
              f"R2 fb vss rhigh w={rw:g}u l={_um(sz['r_fb_l']):g}u",
              f"RB vdd nbias rhigh w={rw:g}u l={_um(sz['r_bias_l']):g}u",
              f"CFF lp_brk fb cap_cmim w={_um(sz['c_ff_w']):g}u l={_um(sz['c_ff_w']):g}u",
              f"CC ea_out ea_o1 cap_cmim w={_um(sz['c_comp_w']):g}u l={_um(sz['c_comp_w']):g}u",
              f"COUT vout vss cap_cmim w={_um(sz['c_out_w']):g}u l={_um(sz['c_out_w']):g}u m={_count(sz['c_out_m'])}",
              f".ends {CELL}"]
    text = "\n".join(lines) + "\n"
    if out is not None:
        Path(out).write_text(text)
    return text


def main() -> None:
    ap = argparse.ArgumentParser(description=f"Generate {CELL} (gdsfactory, IHP SG13G2)")
    ap.add_argument("-o", "--out", default=str(Path(__file__).with_name(f"{CELL}.gds")))
    ap.add_argument("--params", default=None, help="JSON overrides for LayoutParams")
    ap.add_argument("--sizing", default=None, help="JSON file of sizing knobs (Design.knobs())")
    ap.add_argument("--lvs", default=None, help="also write the LVS reference netlist here")
    a = ap.parse_args()
    p = LayoutParams(**json.loads(a.params)) if a.params else LayoutParams()
    sizing = json.loads(Path(a.sizing).read_text()) if a.sizing else None
    comp = build(p, sizing)
    comp.write_gds(a.out)
    bb = comp.bbox()
    print(f"wrote {a.out}; bbox um: ({bb.left:.2f},{bb.bottom:.2f})-({bb.right:.2f},{bb.top:.2f}); "
          f"area um2: {(bb.right - bb.left) * (bb.top - bb.bottom):.0f}")
    if a.lvs:
        write_lvs_reference(p, sizing, a.lvs)
        print("wrote", a.lvs)


if __name__ == "__main__":
    main()
