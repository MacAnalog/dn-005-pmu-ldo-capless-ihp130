#!/usr/bin/env python3
"""Parameterized gdsfactory layout of ``ldo_ihp_capless`` (IHP SG13G2, sg13_lv devices).

Generator contract (``spicexplorer_layout.gen``): ``build(params, sizing=None) -> Component``,
``write_lvs_reference(params, sizing, out)``, ``power_budgets(params, sizing)``.  Run it with the
interpreter that has gdsfactory + ihp-gdsfactory (``$LDO_GF_PYTHON``, default
``~/miniconda3/envs/ai_env/bin/python``; see doc/environment.md) — never the repo venv.

**Second drawing.**  The first (`experiments/005-layout`) was DRC-0 and LVS-matched and is
rejected on four counts, all fixed here and all planned in `layout/ldo_ihp_capless/PLAN.md`:

* **B1** — the 10 mA path was 12–28x over the process metal limit.  The load current now never
  touches a Metal1 conductor wider than one pass-array column: TopMetal1 straps (`pwr_w`), Metal5
  landing pads stitched with `pwr_stitch` TopVia1, `pwr_riser_vias` cuts per Via2/3/4 level, a
  Metal2 comb over the pass array, and `xmp_nf_mult` x as many fingers so a shared diffusion
  column carries 0.26 mA against a 0.36 mA allowance (§3 of the PLAN).
* **m3** — matched pairs are common-centroid or same-row-same-orientation *by class*, with tied
  dummies at both ends of every group, and every well island carries a **closed** guard ring
  instead of periodic point taps.
* **M7** — the LVS reference is derived from the certified netlist (`layout/netlist_ref.py`), not
  from a device table in this file.  This module no longer carries one.
* **M8** — `Builder.stub_clear` (the Metal1 obstacle map) has its own unit test,
  `layout/test_builder.py`, which fails without it.

Floorplan (all y derived from live device bounding boxes; see the PLAN for the sketch):

    vdd TopMetal1 strap  (top edge)                                  <- vdd pin
    XMP island: nwell + ntap ring, m*xmp_nf_mult fingers, Metal2 combs
    vdd Metal1 rail
    row B: [nwell island "quiet": bias_p_group | ea_in_pair]  [nwell island "fvf": XMC XMCP XMD]
    channel: one Metal1 track per internal net, every vertical is Metal2
    row A: [XM5] [ea_nmos_load] [fvf_fold_n] [bias_n_group]           (one ptap ring)
    vss Metal1 rail
    passive band: [XR1/XR2 common centroid + XRB]   [XCC XCFF]   [XCOUT 2x2 array]
    vss Metal1 rail (bottom edge)                                    <- vss pin
    vout TopMetal1 strap down the right edge                         <- vout pin

Routing discipline: device straps, channel tracks and rails are Metal1 (horizontal); every
inter-row connection is a Metal2 vertical with a Via1 pad at each end, at an x unique to that
terminal, and no Metal1 stub may cross a foreign net's Metal1 (`stub_clear`).  Guard-ring metal is
claimed in the same obstacle map, so a stub can never walk out through a ring.

Sizes come from the certified netlist + the sizing record; they are never retyped here.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path

import gdsfactory as gf
from ihp import PDK
from ihp import cells as C
from ihp.cells.fet_transistors import _mos_core

sys.path.insert(0, str(Path(__file__).resolve().parent))
import netlist_ref as NR  # noqa: E402
from router import ObstacleMap  # noqa: E402

PDK.activate()

CELL = NR.CELL
GRID = 0.005
VIA = 0.19       # V1.a / Vn.a exact
VIA_SP = 0.24    # Vn.b + grid slack
VIA_ENC = 0.06   # Mn.c
TVIA = 0.42      # TV1.a exact
TVIA_SP = 0.44   # TV1.b
TVIA_ENC_M5 = 0.42   # TV1.d (Metal5 enclosure)
TVIA_ENC_TM1 = 0.45  # TM1.c
VPAD = 0.38      # via pad (< 0.39 "wide line", so the 0.21 space rule applies)
STRAP = 0.5      # S/D strap centre offset from the active edge
GATE = 1.5       # gate bar centre offset from the active edge
GPAD = 0.5       # gate bar height
CONT = 0.16      # Cnt.a exact
MIM_BIAS = 0.72  # gdsfactory grows the MIM box by 0.36/side vs the cmim() args
W_M1 = 0.2
W_M2 = 0.2
TM1_MIN_W = 1.64   # TM1.a
TM1_MIN_SP = 1.64  # TM1.b
COL_M1_W = 0.16    # the mos cell's own S/D column Metal1 width (measured from _mos_core)

_um, _count = NR.um, NR.count
SIZING: dict[str, object] = NR.load_sizing()


def _s(v: float) -> float:
    return round(round(v / GRID) * GRID, 4)


@dataclasses.dataclass(frozen=True)
class LayoutParams:
    """Free layout constants (um / counts) — the layout-optimizer search space (PLAN §5)."""

    dev_gap: float = 3.2       # x gap between devices in a row
    grp_gap: float = 2.0       # extra gap between matching groups
    track_pitch: float = 0.7   # channel Metal1 track pitch (0.38 pads -> 0.32 space)
    ch_margin: float = 0.9     # clearance from the gate/drain bars to the first track
    rail_w: float = 0.8        # vdd / vss Metal1 rail width (Iq only: 0.037 mA worst)
    rail_gap: float = 1.6      # active edge -> rail centre
    ring_w: float = 0.6        # guard-ring width (ntap / ptap)
    ring_gap: float = 1.4      # device/pad bbox -> guard ring inner edge
    isl_gap: float = 2.0       # Activ gap between two well islands (NW.b 0.62 + Act.b 0.21)
    n_dummy: int = 1           # dummy devices at each end of a matched group
    pwr_w: float = 2.0         # TopMetal1 power-strap width (TM1.a floor is 1.64)
    pwr_stitch: int = 12       # TopVia1 cuts per Metal5 -> TopMetal1 stitch
    pwr_riser_vias: int = 48   # Via2/3/4 cuts per riser level
    pwr_band_w: float = 6.0    # Metal2 comb spine / riser pad width
    xmp_nf_mult: int = 4       # fingers per `m` unit of the pass device (PLAN §3)
    col_vias: int = 2          # Via1 per pass-array S/D column
    mim_gap: float = 3.0       # gap between MIM units
    res_pitch: float = 2.0     # serpentine segment pitch (rhigh cell is 0.9 wide)
    r_segs: int = 8            # divider segments per arm (even: the ABBA pattern needs pairs)
    rb_segs: int = 5           # bias resistor segments (l/rb_segs must land on 0.01 um)
    blk_gap: float = 6.0       # transistor stack -> passive band
    tap_pitch: float = 12.0    # (unused by the rings; kept for the optimizer's search space)


BOUNDS: dict[str, tuple[float, float]] = {
    "dev_gap": (3.0, 6.0), "grp_gap": (0.0, 8.0), "track_pitch": (0.65, 1.2),
    "ch_margin": (0.8, 2.0), "rail_w": (0.5, 2.0), "rail_gap": (1.4, 2.5),
    "ring_w": (0.5, 1.5), "ring_gap": (0.6, 3.0), "isl_gap": (1.3, 6.0), "n_dummy": (0, 2),
    "pwr_w": (1.64, 6.0), "pwr_stitch": (8, 24), "pwr_riser_vias": (28, 72),
    "pwr_band_w": (5.0, 12.0), "xmp_nf_mult": (3, 8), "col_vias": (1, 4),
    "mim_gap": (2.5, 8.0), "res_pitch": (1.8, 4.0), "r_segs": (2, 8), "rb_segs": (1, 6),
    "blk_gap": (4.0, 15.0), "tap_pitch": (6.0, 18.0),
}

_STACK = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5", "TopMetal1"]
_VIA = {  # bottom layer -> (via layer, size, space, min enclosure)
    "Metal1": ("Via1drawing", VIA, VIA_SP, VIA_ENC),
    "Metal2": ("Via2drawing", VIA, VIA_SP, VIA_ENC),
    "Metal3": ("Via3drawing", VIA, VIA_SP, VIA_ENC),
    "Metal4": ("Via4drawing", VIA, VIA_SP, VIA_ENC),
    "Metal5": ("TopVia1drawing", TVIA, TVIA_SP, TVIA_ENC_M5),
}

# ---------------------------------------------------------------- placement ----
# A row is a list of GROUPS; a group is a list of SLOTS.  One slot = one placed instance:
# (device name, fraction of the device's total W, fingers).  Splitting a device across several
# slots is what makes a matching pattern: the LVS deck (`--combine_devices`) folds the parallel
# instances back into one device of the summed width, so the pattern costs nothing at the compare.
# Patterns are the brief's (§6), by measured headroom.
Slot = tuple[str, float, int]
Group = tuple[str, str, list[Slot]]

# row A — NMOS, sources on the vss rail.  Left to right: stage 2, the EA load pair, the FVF folds,
# then the bias group.  The bias group is RIGHTMOST on purpose: XMS drives `gate`, whose 29.3 fF
# budget is 97 % spent, and `nbias`/`pbias` (which then run the cell's length) have no bound.
ROW_A: list[Group] = [
    ("ea_stage2", "any", [("XM5", 1.0, 1)]),
    ("ea_nmos_load", "common_centroid",
     [("XM3", 0.5, 1), ("XM4", 0.5, 1), ("XM4", 0.5, 1), ("XM3", 0.5, 1)]),
    ("fvf_fold_n", "same_row_same_orientation", [("XMA", 1.0, 1), ("XMB", 1.0, 1)]),
    ("bias_n_group", "common_centroid",
     [("XMS", 0.5, 1), ("XMB1", 0.5, 1), ("XMB0", 0.5, 1),
      ("XMB0", 0.5, 1), ("XMB1", 0.5, 1), ("XMS", 0.5, 1)]),
]
# row B — PMOS, in two nwell islands (brief §7): "quiet" and "fvf", both tied to vdd.
ROW_B_QUIET: list[Group] = [
    # XMT sits between XMBP and XM6: a linear gradient then WEAKENS XMT relative to the diode,
    # and brief §6 measures the S7 step only on the side that STRENGTHENS it.
    ("bias_p_group", "same_row_same_orientation",
     [("XMBP", 1.0, 1), ("XMT", 1.0, 1), ("XM6", 1.0, 1)]),
    ("ea_in_pair", "common_centroid",
     [("XM1", 0.5, 1), ("XM2", 0.5, 1), ("XM2", 0.5, 1), ("XM1", 0.5, 1)]),
]
ROW_B_FVF: list[Group] = [
    ("fvf_ctrl", "any", [("XMC", 1.0, 1)]),
    ("fvf_fold_p", "same_row_same_orientation", [("XMCP", 1.0, 1), ("XMD", 1.0, 1)]),
]

# channel-1 tracks (Metal1, bottom to top); vdd/vss are rails, not tracks.  `gate` is the TOP
# track, immediately under the vout bus: brief §3 measures gate-to-vout at 10-24x cheaper than
# gate-to-rail.  `fb` is kept low and far from it.
TRACKS = ["fb", "vref", "lp_brk", "ea_n", "ea_o1", "ea_out", "ea_tail",
          "nbias", "pbias", "x1", "y", "vout", "gate"]


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
    term: dict[str, tuple[float, float]] = dataclasses.field(default_factory=dict)


class Builder(ObstacleMap):
    """The drawing side; the Metal1 obstacle map and the column allocator come from
    :class:`router.ObstacleMap`, which `layout/test_builder.py` exercises directly (M8)."""

    def __init__(self, p: LayoutParams, sz: dict[str, object]):
        super().__init__()
        self.p, self.sz = p, sz
        self.c = gf.Component(CELL)
        self.track_y: dict[str, float] = {}
        self.track_pts: dict[str, list[float]] = {t: [] for t in TRACKS}
        self.rail_y: dict[str, float] = {}
        self.ring_m1: dict[str, tuple[float, float, float, float]] = {}
        self.dummies: list[NR.Dummy] = []
        self.budgets: list[dict] = []   # power-path segments, for the current-density stage

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
        """Small square via stack: as many cuts as fit in ``size`` (<= 3x3)."""
        i0, i1 = _STACK.index(bot), _STACK.index(top)
        for i in range(i0, i1 + 1):
            lay = _STACK[i]
            s = max(size, TM1_MIN_W) if lay == "TopMetal1" else size
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

    def via_row(self, layer_bot: str, xc: float, yc: float, n: int, rows: int = 1) -> tuple[float, float]:
        """``n`` cuts of ``layer_bot``'s via, laid out in ``rows`` rows centred on (xc, yc).
        Returns the (x, y) span the enclosing metal must cover.  This is the count-driven via
        array the power path needs; ``vstack``'s 3x3 cap cannot carry 10 mA."""
        vl, vs, vsp, enc = _VIA[layer_bot]
        rows = max(1, rows)
        per = -(-n // rows)
        spx = per * vs + (per - 1) * vsp
        spy = rows * vs + (rows - 1) * vsp
        k = 0
        for r in range(rows):
            for i in range(per):
                if k >= n:
                    break
                k += 1
                x0 = xc - spx / 2 + i * (vs + vsp)
                y0 = yc - spy / 2 + r * (vs + vsp)
                self.rect(vl, x0, y0, x0 + vs, y0 + vs)
        return spx + 2 * enc, spy + 2 * enc

    def label(self, net: str, x: float, y: float, layer: str = "Metal1text") -> None:
        self.c.add_label(text=net, position=(_s(x), _s(y)), layer=layer)

    def vert(self, net: str, x: float, y0: float, y1: float) -> None:
        """Metal2 vertical between two Via1 pads (both drawn)."""
        self.vstack(x, y0, "Metal1", "Metal2")
        self.vstack(x, y1, "Metal1", "Metal2")
        self.v("Metal2drawing", x, y0, y1, W_M2)
        self.verticals.append((net, _s(x), _s(min(y0, y1)), _s(max(y0, y1))))

    def to_track_m3(self, net: str, x: float, y: float, step: float = 0.6) -> float:
        """Same as :meth:`to_track` but the vertical is **Metal3**.

        The pass device's gate leaves its island at the array's left edge, where the vout Metal2
        comb spine runs: a Metal2 column there merges `gate` into `vout` -- one legal polygon, so
        DRC says nothing and only LVS sees it.  Metal3 hops the spine (and the guard rings).
        """
        yt = self.rail_y.get(net, self.track_y.get(net))
        if yt is None:
            raise KeyError(f"no track or rail for net {net}")
        xx = self.alloc(net, x, y, yt, step)
        if xx != _s(x):
            self.m1h(y, x, xx)
            self.m1_claim(net, y, x, xx)
        self.vstack(xx, y, "Metal1", "Metal3", VPAD)
        self.vstack(xx, yt, "Metal1", "Metal3", VPAD)
        self.v("Metal3drawing", xx, y, yt, 0.3)
        self.verticals.append((net, _s(xx), _s(min(y, yt)), _s(max(y, yt))))
        self.track_pts.setdefault(net, []).append(xx)  # type: ignore[arg-type]
        return xx

    def to_track(self, net: str, x: float, y: float, step: float = 0.6) -> float:
        """Connect the Metal1 point (x, y) to the channel track / rail of ``net``."""
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
            *, d_top: bool, g_top: bool) -> Dev:
        """Place one lv MOS with its active's left edge at x0 and bottom at y_act."""
        cell = _mos_core(width=w, length=l, nf=nf, is_pmos=pmos, is_hv=False)
        ref = self.c << cell
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
        tab = min(GPAD, l)
        y_g = (ay1 + GATE) if g_top else (ay0 - GATE)
        py = ay1 if g_top else ay0
        for gxx in gates:
            self.rect("GatPolydrawing", gxx - tab / 2, py, gxx + tab / 2, y_g)
        gb0, gb1 = min(gates) - 0.25, max(gates) + 0.25
        self.rect("GatPolydrawing", gb0, y_g - GPAD / 2, gb1, y_g + GPAD / 2)
        self.rect("Metal1drawing", gb0, y_g - GPAD / 2, gb1, y_g + GPAD / 2)
        for gxx in gates:
            self.rect("Contdrawing", gxx - CONT / 2, y_g - CONT / 2, gxx + CONT / 2, y_g + CONT / 2)
        d.term["_gate_bar"] = (y_g, gb0, gb1)  # type: ignore[assignment]
        self.m1_claim(f"@g:{name}", y_g, gb0, gb1, GPAD)
        return d

    def strap(self, d: Dev, which: str, top: bool, ext_to: float | None = None,
              net: str | None = None) -> float:
        """Metal1 bar joining the S (even) or D (odd) columns outside the active."""
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
        grp = d.cols[0::2] if which == "S" else d.cols[1::2]
        for xx in grp:
            self.m1v(xx, d.ay0 if y_rail < d.ay0 else d.ay1, y_rail)

    def gate_pad(self, d: Dev, x: float, net: str) -> float:
        y_g, gb0, gb1 = d.term["_gate_bar"]  # type: ignore[misc]
        x0, x1 = min(gb0, x - VPAD / 2), max(gb1, x + VPAD / 2)
        self.rect("Metal1drawing", x0, y_g - GPAD / 2, x1, y_g + GPAD / 2)
        self.m1_retag(f"@g:{d.name}", net)
        self.m1_claim(net, y_g, x0, x1, GPAD)
        return y_g

    def dummy(self, name: str, w: float, l: float, pmos: bool, x0: float, y_act: float,
              rail: str, y_rail: float) -> Dev:
        """A tied-off dummy device: gate bar on the RAIL side, every column shorted to the rail.

        It is a real extracted device (measured: the IHP LVS deck does not purge a fully shorted
        MOS), so it is declared in the LVS reference -- see `netlist_ref.lvs_reference`, which
        asserts all four terminals are on one rail."""
        d = self.mos(name, w, l, 1, pmos, x0, y_act, d_top=not (y_rail < y_act), g_top=(y_rail > y_act))
        y_g, gb0, gb1 = d.term["_gate_bar"]  # type: ignore[misc]
        # ONE Metal1 blanket from the rail over the whole device: source, drain, gate bar and the
        # rail are all the same net, and separate 0.2 um ties left a 0.09 um notch against the
        # gate bar that M1.b (0.21 um) rejects.
        bx0, bx1 = _s(min(min(d.cols), gb0) - 0.16), _s(max(max(d.cols), gb1) + 0.16)
        by0 = _s(min(y_rail, d.ay0, y_g - GPAD / 2))
        by1 = _s(max(y_rail, d.ay1, y_g + GPAD / 2))
        self.rect("Metal1drawing", bx0, by0, bx1, by1)
        self.m1_retag(f"@g:{name}", rail)
        self.m1_claim_box(rail, bx0, by0, bx1, by1)
        self.dummies.append(NR.Dummy(name, "p" if pmos else "n", rail, w, l))
        return d

    # -- guard rings -------------------------------------------------------
    def ring(self, kind: str, net: str, x0: float, y0: float, x1: float, y1: float,
             gap: float = 0.14) -> tuple[float, float, float, float]:
        """A CLOSED guard ring around the box: a continuous Activ/Metal1 frame with a uniform
        contact row, the implant as a frame and (for an n-well ring) the well as a FILLED rect
        that merges with the devices' own wells.

        Drawn here rather than with `ihp.cells.guard_ring`, whose corner contact arrays violate
        Cnt.b (min. Cont space 0.18 um) at every corner — measured on a standalone ring at seven
        width/spacing combinations, 2-4 hits each.  Placing the corner contact ON the corner and
        starting each side one pitch away makes every neighbour pair axis-aligned and >= one
        pitch apart.

        The ring's Metal1 is claimed in the obstacle map, so a routing stub can never walk out
        through it.  Returns the outer implant/well bbox.
        """
        w = self.p.ring_w
        ix0, iy0, ix1, iy1 = _s(x0 - gap), _s(y0 - gap), _s(x1 + gap), _s(y1 + gap)
        ox0, oy0, ox1, oy1 = _s(ix0 - w), _s(iy0 - w), _s(ix1 + w), _s(iy1 + w)
        frame = [(ox0, oy0, ox1, iy0), (ox0, iy1, ox1, oy1),
                 (ox0, iy0, ix0, iy1), (ix1, iy0, ox1, iy1)]
        imp = "pSDdrawing" if kind == "psub" else "nSDdrawing"
        for (a, b_, c, d) in frame:
            self.rect("Activdrawing", a, b_, c, d)
            self.rect("Metal1drawing", a, b_, c, d)
            self.rect(imp, a - 0.1, b_ - 0.1, c + 0.1, d + 0.1)
        if kind == "nwell":
            # filled, so the island's devices share one well with the ring
            self.rect("NWelldrawing", ox0 - 0.31, oy0 - 0.31, ox1 + 0.31, oy1 + 0.31)
        # contacts: one on each corner, then one pitch in along every side
        cx0, cy0, cx1, cy1 = _s(ix0 - w / 2), _s(iy0 - w / 2), _s(ix1 + w / 2), _s(iy1 + w / 2)
        pts: list[tuple[float, float]] = [(cx0, cy0), (cx1, cy0), (cx0, cy1), (cx1, cy1)]
        pitch = CONT + 0.20
        n_x = max(0, int((cx1 - cx0) / pitch) - 1)
        n_y = max(0, int((cy1 - cy0) / pitch) - 1)
        step_x = (cx1 - cx0) / (n_x + 1) if n_x else 0.0
        step_y = (cy1 - cy0) / (n_y + 1) if n_y else 0.0
        for i in range(1, n_x + 1):
            pts += [(_s(cx0 + i * step_x), cy0), (_s(cx0 + i * step_x), cy1)]
        for i in range(1, n_y + 1):
            pts += [(cx0, _s(cy0 + i * step_y)), (cx1, _s(cy0 + i * step_y))]
        for (px, py) in pts:
            self.rect("Contdrawing", px - CONT / 2, py - CONT / 2, px + CONT / 2, py + CONT / 2)
        for seg in ((cy0, ox0, ox1), (cy1, ox0, ox1)):
            self.m1_claim(net, seg[0], seg[1], seg[2], w)
        for x in (cx0, cx1):
            self.m1_claim_box(net, x - w / 2, oy0, x + w / 2, oy1)
        self.ring_m1[net] = (cx0, cy0, cx1, cy1)
        return (_s(ox0 - 0.31), _s(oy0 - 0.31), _s(ox1 + 0.31), _s(oy1 + 0.31))

    # -- passives ----------------------------------------------------------
    def serpentine(self, w: float, l_total: float, segs: int, x0: float, y0: float,
                   pitch: float | None = None) -> tuple[tuple[float, float], tuple[float, float], list[float]]:
        """``segs`` vertical rhigh segments joined top/bottom by Metal1; returns the two end pads
        and the segment x list.  With ``segs`` even both ends come out at the bottom."""
        pitch = pitch or self.p.res_pitch
        seg = _s(l_total / segs)
        cell = C.rhigh(dy=seg, dx=w)
        ends = []
        xs = []
        for i in range(segs):
            ref = self.c << cell
            b = ref.bbox()
            ref.dmovex(_s(x0 + i * pitch - b.left))
            ref.dmovey(_s(y0 - b.bottom))
            p1, p2 = ref.ports["P1"].center, ref.ports["P2"].center
            ends.append((p1, p2))
            xs.append(_s(p1[0]))
        for i in range(segs - 1):
            top, bot = ends[i][0], ends[i][1]
            ntop, nbot = ends[i + 1][0], ends[i + 1][1]
            if i % 2 == 0:
                self.m1h(top[1], top[0], ntop[0], 0.3)
            else:
                self.m1h(bot[1], bot[0], nbot[0], 0.3)
        first = ends[0][1]
        last = ends[-1][1] if segs % 2 == 0 else ends[-1][0]
        return first, last, xs

    def mim(self, unit: float, x0: float, y0: float, mirror: bool = False,
            top_to: float | None = None, escape: float = 0.0) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float, float, float]]:
        """One MIM unit, Metal5 plate lower-left at (x0, y0).

        Bottom (Metal5) plate pad on the LEFT and top plate strap to the RIGHT -- ONE
        plate-connection side, so a unit array has one bus per terminal.  ``mirror`` swaps the two
        sides, which is what makes the XCOUT 2x2 array a common centroid about a central top-plate
        spine; ``top_to`` extends the top-plate strap to that x (the spine)."""
        cell = C.cmim(width=unit - MIM_BIAS, length=unit - MIM_BIAS)
        ref = self.c << cell
        b = ref.bbox()
        ref.dmovex(_s(x0 - b.left))
        ref.dmovey(_s(y0 - b.bottom))
        b = ref.bbox()
        yc = _s((b.bottom + b.top) / 2)
        sgn = -1.0 if not mirror else 1.0
        xb = _s((b.left - 1.2) if not mirror else (b.right + 1.2))
        self.vstack(xb, yc, "Metal1", "Metal5", 1.3)   # Metal1, so a shifted stub still lands
        self.h("Metal5drawing", yc, xb, (b.left + 0.3) if not mirror else (b.right - 0.3), 0.6)
        xt = _s((b.right + 2.4) if not mirror else (b.left - 2.4))
        if top_to is not None:
            xt = _s(top_to)
        self.vstack(xt, yc, "Metal1", "TopMetal1", 1.3)
        self.h("TopMetal1drawing", yc, ref.ports["PLUS"].center[0], xt, TM1_MIN_W)
        del sgn
        # The plate pad carries its own 1.3 um Metal1/Metal2 stack and a 3x3 Via1 array; claim it
        # so no routing pad lands beside it (three rounds of V1.a/V1.b/M1.b/M2.b came from that),
        # and hand the caller a Metal1 arm `escape` um clear of it to route from.
        for xp in (xb, xt):
            self.m1_claim_box(f"@mim{len(self.m1_rows)}", xp - 0.85, yc - 0.85, xp + 0.85, yc + 0.85)
        if escape > 0:
            # INWARD, under the plate: outward runs into the cell edge (round 7 shorted
            # ea_o1/fb/vss on the left-edge vss strap); under a Metal5 plate the Metal1 is free
            xb_e = _s(xb + (-escape if mirror else escape))
            xt_e = _s(xt + (escape if mirror else -escape))
            self.m1h(yc, xb, xb_e, 0.4)
            self.m1h(yc, xt, xt_e, 0.4)
            return (xb_e, yc), (xt_e, yc), (b.left, b.bottom, b.right, b.top)
        return (xb, yc), (xt, yc), (b.left, b.bottom, b.right, b.top)

    def climb(self, net: str, x: float, y0: float, y1: float, w: float = 0.3) -> None:
        """Take ``net`` from its Metal1 y up to the TopMetal1 strap at ``y1`` on a Metal2 column
        clear of every device row.  Only ever used for Iq-class currents."""
        self.vstack(x, y0, "Metal1", "Metal2", VPAD)
        self.v("Metal2drawing", x, y0, y1, w)
        self.vstack(x, y1, "Metal2", "TopMetal1", 1.3)
        self.verticals.append((net, _s(x), _s(min(y0, y1)), _s(max(y0, y1))))
        # register the landing x, or the channel track is not drawn out to it and the net splits
        if net in self.track_pts and abs(y0 - self.track_y.get(net, 1e9)) < 1e-6:
            self.track_pts[net].append(_s(x))

    # -- power path --------------------------------------------------------
    def budget(self, net: str, note: str, current_a: float, layer: str,
               width_um: float = 0.0, n_vias: int = 1) -> None:
        self.budgets.append({"net": net, "note": note, "current_a": current_a, "layer": layer,
                             "width_um": round(width_um, 4), "n_vias": int(n_vias)})

    def riser(self, net: str, xc: float, yc: float, bot: str, top: str, n: int,
              rows: int, pad_w: float, current_a: float) -> None:
        """A count-driven via stack from ``bot`` to ``top`` with pads sized for the current."""
        i0, i1 = _STACK.index(bot), _STACK.index(top)
        span_x = span_y = 0.0
        for i in range(i0, i1):
            lay = _STACK[i]
            if lay == "Metal5":
                sx, sy = self.via_row("Metal5", xc, yc, self.p.pwr_stitch, 1)
                sx, sy = sx + 2 * (TVIA_ENC_M5 - VIA_ENC), sy + 2 * (TVIA_ENC_M5 - VIA_ENC)
                self.budget(net, f"{net} Metal5->TopMetal1 stitch", current_a, "topvia1",
                            n_vias=self.p.pwr_stitch)
            else:
                sx, sy = self.via_row(lay, xc, yc, n, rows)
                self.budget(net, f"{net} riser {lay}->{_STACK[i+1]}", current_a,
                            f"via{i + 1}", n_vias=n)
            span_x, span_y = max(span_x, sx), max(span_y, sy)
        w = max(pad_w, span_y)
        lx = max(span_x, pad_w)
        for i in range(i0, i1 + 1):
            lay = _STACK[i]
            if lay == "TopMetal1":
                continue     # the strap itself is the top pad
            self.rect(lay + "drawing", xc - lx / 2, yc - w / 2, xc + lx / 2, yc + w / 2)
            if lay != bot:
                self.budget(net, f"{net} riser {lay} pad", current_a, lay.lower(), width_um=w)

    # -- checks ------------------------------------------------------------
    def check(self) -> None:
        vs = self.verticals
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                a, b = vs[i], vs[j]
                if a[0] != b[0] and abs(a[1] - b[1]) < 0.6 - 1e-6 and not (a[3] < b[2] - 0.6 or b[3] < a[2] - 0.6):
                    raise AssertionError(f"Metal2 verticals collide: {a} vs {b}")




# ------------------------------------------------------------------ build ----
# Measured operating currents (brief §8: `decks/candidate` dc_op with 0 V ammeters, 10 mA load).
I_VDD = 10.0318e-3
I_XMP = 10.0041e-3
I_VSS = 27.7e-6
I_RAIL_VDD = 37.0e-6   # what the Metal1 vdd rail carries once XMP's source goes up, not sideways


def _wf_max(groups: list[Group], W) -> float:
    """The tallest finger a row will contain, dummies included — needed before placement, because
    the rail y (and therefore the dummies' tie direction) depends on it."""
    out = 0.0
    for _g, _p, slots in groups:
        out = max(out, max(W[n] * f for n, f, _nf in slots))
        out = max(out, max(W[n] * f / nf for n, f, nf in slots))
    return out


def _place_row(b: Builder, groups: list[Group], W, L, x: float, y_act: float, pmos: bool,
               rail: str, y_rail: float, tag: str) -> tuple[dict[str, list[Dev]], list[Dev], float]:
    """Place every group of a row left to right, with `n_dummy` tied dummies at each end of each
    group.  Returns {device: [instances]}, every placed Dev (dummies included), and the x cursor."""
    p = b.p
    out: dict[str, list[Dev]] = {}
    alld: list[Dev] = []
    k = 0
    for gi, (_gname, _pattern, slots) in enumerate(groups):
        if gi:
            x += p.grp_gap
        w_dum = max(W[n] * f for n, f, _nf in slots)
        l_dum = L[slots[0][0]]
        for side in (0, 1):
            if side:
                for name, frac, nf in slots:
                    d = b.mos(name, W[name] * frac, L[name], nf, pmos, x, y_act,
                              d_top=not pmos, g_top=not pmos)
                    out.setdefault(name, []).append(d)
                    alld.append(d)
                    x = d.ax1 + p.dev_gap
            for _ in range(p.n_dummy):
                k += 1
                d = b.dummy(f"{tag}{k}", w_dum, l_dum, pmos, x, y_act, rail, y_rail)
                alld.append(d)
                x = d.ax1 + p.dev_gap
    return out, alld, x - p.dev_gap


def _row_box(devs: list[Dev], pad: float = 1.15) -> tuple[float, float, float, float]:
    """Bounding box of a placed row including its gate bars and strap / via pads."""
    ys: list[float] = []
    for d in devs:
        y_g = d.term["_gate_bar"][0]  # type: ignore[index]
        ys += [d.ay0, d.ay1, y_g - GPAD / 2, y_g + GPAD / 2, d.ay1 + STRAP + VPAD / 2,
               d.ay0 - STRAP - VPAD / 2]
    return (min(d.ax0 for d in devs) - pad, min(ys) - 0.4,
            max(d.ax1 for d in devs) + pad, max(ys) + 0.4)


def _wire_row(b: Builder, insts: dict[str, list[Dev]], net, pmos: bool, y_rail: float) -> None:
    """Drain -> its track, gate -> its track, source -> the rail (or its track)."""
    for name, ilist in insts.items():
        dn, gn, sn = net[name]
        for d in ilist:
            xr = _s(d.ax1 + 0.55)
            yd = b.strap(d, "D", not pmos, ext_to=xr, net=dn)
            b.to_track(dn, xr, yd)
            xl = _s(d.ax0 - 0.55)
            yg = b.gate_pad(d, xl, gn)
            b.to_track(gn, xl, yg, step=-0.6)
            if sn in ("vdd", "vss"):
                b.columns_to_rail(d, "S", y_rail)
            else:
                xs = _s(d.ax1 + 1.15)
                ys = b.strap(d, "S", pmos, ext_to=xs, net=sn)
                b.to_track(sn, xs, ys)


def _seg_len(l_total: float, segs: int, what: str) -> float:
    """A serpentine segment length that keeps the `rhigh` cell on grid.

    A `dy` that is not a multiple of 0.01 um makes the PDK cell's own geometry off-grid: at
    `l = 138.5 um / 4 = 34.625 um` the rule deck reported 14 OffGrid / Sal.e / Rhi.d violations
    *inside* the rhigh cell.  Rather than silently rounding (which would change the resistance and
    fail LVS), refuse — the segment count is a knob and the caller can move it.
    """
    seg = l_total / segs
    if abs(round(seg, 2) - seg) > 1e-9:
        raise AssertionError(
            f"{what}: {l_total:g} um / {segs} = {seg:g} um is not a multiple of 0.01 um; the "
            f"rhigh cell goes off-grid there — pick another segment count")
    return _s(seg)


def build_full(p: LayoutParams = LayoutParams(),
               sizing: dict[str, object] | None = None) -> tuple[gf.Component, Builder]:
    sz = {**SIZING, **(sizing or {})}
    mos, passives = NR.devices(sz)
    MD = {d.name: d for d in mos}
    W = {n: d.w_total for n, d in MD.items()}
    L = {n: d.l for n, d in MD.items()}
    net = {n: (d.drain, d.gate, d.source) for n, d in MD.items()}
    PC = {c.name: c for c in passives}
    b = Builder(p, sz)

    # ================= row A: NMOS, sources on the vss rail =================
    y_vss = 0.0
    b.rail_y["vss"] = y_vss
    b.m1_claim("vss", y_vss, -1e4, 1e4, p.rail_w)
    yA = _s(y_vss + p.rail_gap)
    instA, allA, xA_end = _place_row(b, ROW_A, W, L, 0.6, yA, False, "vss", y_vss, "A")
    boxA = _row_box(allA)
    # the ring encloses the vss rail as well: the rail is the row's own vss distribution and
    # leaves through the ring's side segments, which is a merge of one net, not a crossing
    boxA = (-1.4, min(boxA[1], y_vss - p.rail_w / 2 - 0.5), xA_end + 1.4, boxA[3])
    ringA_top = boxA[3] + p.ring_gap + 0.14 + p.ring_w + 0.25
    y_ch0 = _s(ringA_top + p.ch_margin)
    for i, t in enumerate(TRACKS):
        b.track_y[t] = _s(y_ch0 + i * p.track_pitch)
    y_ch1 = b.track_y[TRACKS[-1]] + p.ch_margin
    b.ring("psub", "vss", boxA[0], boxA[1], boxA[2], boxA[3], gap=p.ring_gap)
    _wire_row(b, instA, net, False, y_vss)

    # ================= row B: PMOS, two nwell islands, sources on the vdd rail ==========
    wfB = max(_wf_max(ROW_B_QUIET, W), _wf_max(ROW_B_FVF, W))
    yB = _s(y_ch1 + p.ring_w + 0.14 + p.ring_gap + GATE + GPAD / 2 + 0.45)
    y_vdd = _s(yB + wfB + p.rail_gap)
    b.rail_y["vdd"] = y_vdd
    b.m1_claim("vdd", y_vdd, -1e4, 1e4, p.rail_w)
    instQ, allQ, xQ_end = _place_row(b, ROW_B_QUIET, W, L, 0.6, yB, True, "vdd", y_vdd, "Q")
    # both rings plus NW.b (0.62 between two nwells on the same net) and Act.b (0.21) fit in
    # this gap: at 0.20 the two islands merged into ONE well and Act.b fired six times
    x_isl = _s(xQ_end + 2.8 + 2 * (p.ring_gap + p.ring_w) + p.isl_gap)
    instF, allF, xF_end = _place_row(b, ROW_B_FVF, W, L, x_isl, yB, True, "vdd", y_vdd, "F")
    boxQ = _row_box(allQ)
    boxQ = (-1.4, boxQ[1], _s(xQ_end + 1.4), max(boxQ[3], y_vdd + p.rail_w / 2 + 0.5))
    boxF = _row_box(allF)
    boxF = (_s(x_isl - 1.4), boxF[1], _s(xF_end + 1.4), max(boxF[3], y_vdd + p.rail_w / 2 + 0.5))
    for box in (boxQ, boxF):
        b.ring("nwell", "vdd", box[0], box[1], box[2], box[3], gap=p.ring_gap)
    _wire_row(b, instQ, net, True, y_vdd)
    _wire_row(b, instF, net, True, y_vdd)

    # ================= the pass device: own island, Metal2 combs, TopMetal1 straps ======
    y_out_band = _s(y_vdd + p.rail_w / 2 + p.blk_gap + p.ring_w + p.pwr_band_w / 2 + 1.5)
    yC = _s(y_out_band + p.pwr_band_w / 2 + 1.4 + GATE + GPAD / 2 + 0.6)
    nf = MD["XMP"].m * p.xmp_nf_mult
    xC = _s(max(0.6, boxF[2] - 1.4 - (nf + 1) * 0.52))
    dP = b.mos("XMP", W["XMP"], L["XMP"], nf, True, xC, yC, d_top=False, g_top=False)
    i_col = 2 * I_XMP / nf                    # interior diffusion columns are SHARED by 2 fingers
    src, drn = dP.cols[0::2], dP.cols[1::2]
    # the via column is `col_vias` cuts stacked in y; both the Metal1 stub and the Metal2 finger
    # must enclose it (M2.c1: Metal2 endcap enclosure of Via1 = 0.05), which is what 77 of the
    # first round's 118 violations were.
    v_span = p.col_vias * VIA + (p.col_vias - 1) * VIA_SP
    v_env = _s(v_span / 2 + 0.10)
    y_s_pad = _s(dP.ay1 + 0.15 + v_env)
    y_d_pad = _s(dP.ay0 - 0.15 - v_env)
    y_s_band = _s(y_s_pad + v_env + 1.0 + p.pwr_band_w / 2)
    for xx in src:
        b.rect("Metal1drawing", xx - 0.155, dP.ay1 - 0.1, xx + 0.155, y_s_pad + v_env)
        b.via_row("Metal1", xx, y_s_pad, p.col_vias, p.col_vias)
        b.rect("Metal2drawing", xx - 0.155, y_s_pad - v_env, xx + 0.155, y_s_band)
    for xx in drn:
        b.rect("Metal1drawing", xx - 0.155, y_d_pad - v_env, xx + 0.155, dP.ay0 + 0.1)
        b.via_row("Metal1", xx, y_d_pad, p.col_vias, p.col_vias)
        b.rect("Metal2drawing", xx - 0.155, y_out_band, xx + 0.155, y_d_pad + v_env)
    b.h("Metal2drawing", y_s_band, dP.ax0 - 0.6, dP.ax1 + 0.6, p.pwr_band_w)
    b.h("Metal2drawing", y_out_band, dP.ax0 - 0.6, dP.ax1 + 0.6, p.pwr_band_w)
    b.budget("vdd", "pass source column Metal1 riser (shared)", i_col, "metal1", width_um=0.31)
    b.budget("vout", "pass drain column Metal1 riser (shared)", i_col, "metal1", width_um=0.31)
    b.budget("vdd", "pass source column Via1 (shared)", i_col, "via1", n_vias=p.col_vias ** 2)
    b.budget("vout", "pass drain column Via1 (shared)", i_col, "via1", n_vias=p.col_vias ** 2)
    b.budget("vdd", "pass source column Metal2 finger", i_col, "metal2", width_um=0.31)
    b.budget("vout", "pass drain column Metal2 finger", i_col, "metal2", width_um=0.31)
    b.budget("vdd", "pass source Metal2 comb spine", I_VDD, "metal2", width_um=p.pwr_band_w)
    b.budget("vout", "pass drain Metal2 comb spine", I_XMP, "metal2", width_um=p.pwr_band_w)
    b.budget("vout", "pass drain diffusion contacts (shared column)", i_col, "cnt", n_vias=4)
    # `gate` leaves the array on its LEFT and drops onto the TOP channel track, which runs under
    # the vout bus: brief §3 measures gate-to-vout at 10-24x cheaper than gate-to-rail.
    xg = _s(dP.ax0 - 0.75)
    ygp = b.gate_pad(dP, xg, "gate")
    b.to_track_m3("gate", xg, ygp, step=-0.6)

    x_r = _s((dP.ax0 + dP.ax1) / 2)
    b.riser("vdd", x_r, y_s_band, "Metal2", "TopMetal1", p.pwr_riser_vias, 2, p.pwr_band_w, I_VDD)
    b.riser("vout", x_r, y_out_band, "Metal2", "TopMetal1", p.pwr_riser_vias, 2, p.pwr_band_w, I_XMP)
    b.budget("vdd", "cell Metal1 vdd rail (row-B sources + XRB, Iq only)", I_RAIL_VDD, "metal1",
             width_um=p.rail_w)
    b.budget("vss", "cell Metal1 vss rail (Iq only)", I_VSS, "metal1", width_um=p.rail_w)

    boxP = (dP.ax0 - 1.0, dP.ay0 - GATE - GPAD / 2 - 0.5, dP.ax1 + 1.0, dP.ay1 + 1.15)
    gP = b.ring("nwell", "vdd", *boxP, gap=p.ring_gap)
    # the ntap ring reaches vdd up its LEFT segment on Metal2, into the source comb's spine
    rm = b.ring_m1["vdd"]
    x_rc = _s(rm[0])
    b.vstack(x_rc, _s(dP.ay1), "Metal1", "Metal2", 0.5)
    b.v("Metal2drawing", x_rc, _s(dP.ay1), y_s_band, 0.5)
    # brief §7: a second, p-substrate ring between XMP and everything else, outside the combs
    b.ring("psub", "vss", gP[0] - 0.6, y_out_band - p.pwr_band_w / 2 - 0.6,
           gP[2] + 0.6, y_s_band + p.pwr_band_w / 2 + 0.6, gap=0.3)

    y_top = _s(y_s_band + p.pwr_band_w / 2 + 3.4)
    x_stack = max(boxF[2], gP[2] + 2.4, xA_end + 1.4)

    # ================= passives: the left column ===============================
    # Everything with a channel connection lives at x < 0, so its Metal2 riser reaches the tracks
    # without crossing a device row.  XCOUT (§below) needs no track and goes under the stack.
    r_w = _um(sz[PC["XR1"].params["w"]])
    r_l = _um(sz[PC["XR1"].params["l"]])
    rb_l = _um(sz[PC["XRB"].params["l"]])
    ccw = _um(sz[PC["XCC"].params["w"]])
    cffw = _um(sz[PC["XCFF"].params["w"]])
    if p.r_segs % 2:
        raise AssertionError("r_segs must be even: the A B B A pattern is built from pairs")
    seg_l = _seg_len(r_l, p.r_segs, "XR1/XR2")
    # XR1 / XR2: one common-centroid block, [A B B A] repeated, both centroids at the block
    # centre, with a tied dummy segment at each end.  brief §6 makes this the tightest matching
    # class in the cell (1.71 sigma) and brief §9 asks for ABBA specifically.
    order: list[str] = []
    for _ in range(p.r_segs // 2):
        order += ["XR1", "XR2", "XR2", "XR1"]
    order += ["XR1", "XR2"] * (p.r_segs % 2)
    n_cols = len(order) + 2 * p.n_dummy
    x_res1 = _s(-p.blk_gap - max(n_cols * p.res_pitch, ccw + 6.0))
    y_res = _s(y_vss - 7.0 - seg_l)
    ports: dict[str, list[tuple[tuple[float, float], tuple[float, float]]]] = {"XR1": [], "XR2": []}
    for i in range(n_cols):
        xx = _s(x_res1 + i * p.res_pitch)
        lo, hi, _ = b.serpentine(r_w, seg_l, 1, xx, y_res)
        # the rhigh end pads are Metal1: claim them, or a stub walking the port row shorts the
        # comb into itself (round 2 extracted XR2 as 212.5 + 85 + 42.5 um with `fb` in the middle)
        for k, (px, py) in enumerate((lo, hi)):
            b.m1_claim(f"@r{i}{k}", py, px - 0.45, px + 0.45, 0.9)
        if i < p.n_dummy or i >= n_cols - p.n_dummy:
            # a dummy segment: both ends shorted together and tied to vss
            b.m1v(lo[0], lo[1], hi[1], 0.3)
            b.dummies.append(NR.Dummy(f"RD{i}", "r", "vss", r_w, seg_l))
            b.m1_retag(f"@r{i}0", "vss")
            b.m1_retag(f"@r{i}1", "vss")
            b.to_track("vss", lo[0], lo[1])
            continue
        ports[order[i - p.n_dummy]].append((lo, hi, i))

    def _chain(entries, on_m2: bool):
        """Series-connect one arm's segments.  One arm links on Metal1 (offset out of the way),
        the other on Metal2 at the port y: an interdigitated comb needs two levels, or the two
        arms' links short where their spans overlap."""
        y_lo = min(e[0][1] for e in entries) - 1.0
        y_hi = max(e[1][1] for e in entries) + 1.0
        for j in range(len(entries) - 1):
            at_bot = (j % 2 == 0)
            p0, p1 = entries[j][0 if at_bot else 1], entries[j + 1][0 if at_bot else 1]
            for e, k in ((entries[j], 0 if at_bot else 1), (entries[j + 1], 0 if at_bot else 1)):
                b.m1_retag(f"@r{e[2]}{k}", f"@arm{id(entries)}")
            if on_m2:
                # Metal3, not Metal2: the arm's links run the length of the comb at the port y,
                # and the fb / lp_brk Metal2 columns that leave the comb cross exactly there --
                # round 3 extracted XR2 as vss-212.5-fb-85-$16-42.5-fb, a loop back into fb.
                b.vstack(p0[0], p0[1], "Metal1", "Metal3", VPAD)
                b.vstack(p1[0], p1[1], "Metal1", "Metal3", VPAD)
                for px in (p0[0], p1[0]):
                    b.verticals.append((f"@arm{id(entries)}", _s(px), _s(p0[1] - 0.3), _s(p0[1] + 0.3)))
                b.h("Metal3drawing", p0[1], p0[0], p1[0], 0.3)
            else:
                y = y_lo if at_bot else y_hi
                b.m1v(p0[0], p0[1], y, 0.3)
                b.m1v(p1[0], p1[1], y, 0.3)
                b.m1h(y, p0[0], p1[0], 0.3)
                b.m1_claim(f"@arm{id(entries)}", y, p0[0], p1[0], 0.3)
        k_last = 1 if (len(entries) - 2) % 2 == 0 else 0
        return ((entries[0][1], (entries[0][2], 1)),
                (entries[-1][k_last], (entries[-1][2], k_last)))

    (r1a, i1a), (r1b, i1b) = _chain(ports["XR1"], on_m2=False)
    (r2a, i2a), (r2b, i2b) = _chain(ports["XR2"], on_m2=True)
    for tag, nname in ((f"@r{i1a[0]}{i1a[1]}", "lp_brk"), (f"@r{i1b[0]}{i1b[1]}", "fb"),
                       (f"@r{i2a[0]}{i2a[1]}", "fb"), (f"@r{i2b[0]}{i2b[1]}", "vss")):
        b.m1_retag(tag, nname)
    b.to_track("lp_brk", r1a[0], r1a[1])       # XR1: lp_brk (divider top) -> fb
    b.to_track("fb", r1b[0], r1b[1])
    b.to_track("fb", r2a[0], r2a[1])           # XR2: fb -> vss
    b.to_track("vss", r2b[0], r2b[1])
    # XRB beside the divider block, equally far from XMP (brief §9: its tc1 sets every current)
    x_rb = _s(x_res1 + n_cols * p.res_pitch + 1.0)
    _seg_len(rb_l, p.rb_segs, "XRB")
    rba, rbb, _ = b.serpentine(r_w, rb_l, p.rb_segs, x_rb, y_res, pitch=1.6)
    b.to_track("vdd", rba[0], rba[1])
    b.to_track("nbias", rbb[0], rbb[1])

    # XCC (Miller) and XCFF (feed-forward): same orientation, same plate-connection side.
    # Which node is the TOP plate is NOT a layout choice: `cap_cmim` is a polarised device in the
    # LVS deck and the certified card fixes it -- nodes[0] is the top (PLUS) plate, nodes[1] the
    # Metal5 bottom (MINUS).  Round 4 followed brief §9 instead ("put the terminal that has a
    # budget on top") and LVS reported CFF and CC mismatched with fb/lp_brk and ea_o1/ea_out
    # swapped.  Swapping the plates moves the bottom-plate parasitic to the other node, i.e. it is
    # a design change, so the drawing follows the netlist and the brief's preference is recorded
    # as a re-sizing question, not applied here.
    y_cc = _s(y_res - p.mim_gap - ccw - 3.0)
    bt, tp, bbcc = b.mim(ccw, _s(x_res1 + 1.4), y_cc, escape=2.0)
    b.to_track(PC["XCC"].nodes[1], *bt)
    b.to_track(PC["XCC"].nodes[0], *tp)
    y_cff = _s(bbcc[1] - p.mim_gap - cffw - 1.0)
    bt, tp, bbff = b.mim(cffw, _s(x_res1 + 1.4), y_cff, escape=2.0)
    b.to_track(PC["XCFF"].nodes[1], *bt)
    b.to_track(PC["XCFF"].nodes[0], *tp)
    x_pass_r = _s(max(bbcc[2] + 3.2, x_rb + p.rb_segs * 1.6 + 1.0))

    # ================= XCOUT: a 2x2 common-centroid unit array under the stack ==========
    # A3 of the PLAN: `m = 4` already IS the unit array; the four certified 58 um units are drawn
    # on a common centroid about a central TopMetal1 top-plate spine, the right column mirrored so
    # the block has ONE plate-connection side per terminal.  No MIM dummy ring: brief §6 gives
    # `mim_cout_unit` no bound, and a ring of 58 um units would triple the block.
    cw = _um(sz[PC["XCOUT"].params["w"]])
    cm = _count(sz[PC["XCOUT"].params["m"]])
    cols_ = 2 if cm > 1 else 1
    rows_ = -(-cm // cols_)
    y_cout_top = _s(y_vss - 8.0)
    unit_h = _s(cw + p.mim_gap)
    pitch_x = _s(cw + 2 * p.mim_gap + 4.0)
    x_cout0 = 1.0
    vout_spine_x = _s(x_cout0 + cw + p.mim_gap + 2.0)
    cout_bot = _s(y_cout_top - rows_ * unit_h)
    vss_pads: list[tuple[float, float]] = []
    for i in range(cm):
        col, row = i % cols_, i // cols_
        mir = bool(col)
        x0 = _s(x_cout0 + col * pitch_x)
        y0 = _s(y_cout_top - (row + 1) * unit_h + p.mim_gap / 2)
        bt, _tp, _bb = b.mim(cw, x0, y0, mirror=mir, top_to=vout_spine_x)
        vss_pads.append(bt)   # PC["XCOUT"].nodes[1] == "vss"; nodes[0] == "vout" is the top plate
    x_cout_r = _s(x_cout0 + (cols_ - 1) * pitch_x + cw + 3.0)

    # ================= rails, straps, pin frame ===============================
    x_left = _s(x_res1 - 2.5)
    x_right = _s(max(x_stack + 2.0, x_cout_r + 2.0))
    y_bot = _s(min(cout_bot, bbff[1] - 3.0) - 4.0)
    b.m1h(y_vss, x_left, x_right, p.rail_w)
    b.m1h(y_vdd, x_left, x_stack, p.rail_w)
    # bottom vss rail (the vss PIN) joined to the cell's vss rail up the left edge
    b.m1h(y_bot, x_left, x_right, p.rail_w)
    b.m1v(_s(x_left + p.rail_w / 2), y_bot, y_vss, p.rail_w)
    for (xb, yb) in vss_pads:                     # XCOUT bottom plates -> the bottom rail
        b.m1v(xb, yb, y_bot, 0.6)               # the plate pad already reaches Metal1
    # vdd: the Metal1 rail climbs to the TopMetal1 strap on the left, clear of every device
    b.climb("vdd", _s(x_left + 2.6), y_vdd, y_s_band)
    b.h("TopMetal1drawing", y_s_band, x_left, x_right, p.pwr_w)
    b.budget("vdd", "vdd TopMetal1 strap (top edge)", I_VDD, "topmetal1", width_um=p.pwr_w)
    # vout: TopMetal1 from the pass-drain riser, right to the edge, down it, then over XCOUT
    b.h("TopMetal1drawing", y_out_band, dP.ax0 - 0.6, x_right, p.pwr_w)
    b.v("TopMetal1drawing", _s(x_right - p.pwr_w / 2), _s(cout_bot + 3.0), y_out_band, p.pwr_w)
    b.h("TopMetal1drawing", _s(cout_bot + 3.0), vout_spine_x, _s(x_right - p.pwr_w / 2), p.pwr_w)
    b.v("TopMetal1drawing", vout_spine_x, _s(cout_bot + 3.0), _s(y_cout_top - 1.0), p.pwr_w)
    b.budget("vout", "vout TopMetal1 strap (right edge + XCOUT bus)", I_XMP, "topmetal1",
             width_um=p.pwr_w)
    # the `vout` channel track (XMC's source, the divider sense return) joins the strap clear of
    # the stack; the vout PIN label sits at the far right edge, so the extraction's pin node is
    # the OUTPUT PIN and not the pass drain (brief §4: 0.126 Ohm -> 1.78 Ohm)
    b.climb("vout", _s(x_stack + 1.2), b.track_y["vout"], y_out_band)

    # ---------------- channel tracks + labels ----------------
    for t in TRACKS:
        xs = b.track_pts[t]
        if not xs:
            raise AssertionError(f"net {t} has no terminals")
        b.m1h(b.track_y[t], min(xs) - VPAD / 2, max(xs) + VPAD / 2)
    # Label EVERY track, not just the pins: the extractor names a net after its label, which is
    # what makes the per-net C table readable and lets the post-layout deck re-attach the MIM
    # capacitors (stripped before extraction) to `ea_out`/`ea_o1`/`fb` by name.
    for t in TRACKS:
        xs = b.track_pts[t]
        b.label(t, (min(xs) + max(xs)) / 2, b.track_y[t])
    # pin frame: vdd top (TopMetal1), vss bottom (Metal1), vout right (TopMetal1), fb/vref left
    b.label("vdd", _s(x_left + 6.0), y_s_band, "TopMetal1text")
    b.label("vout", _s(x_right - p.pwr_w / 2), _s(y_vss), "TopMetal1text")
    b.label("vss", _s((x_left + x_right) / 2), y_bot)
    b.label("vss", _s(x_left + 6.0), y_vss)
    b.label("vdd", _s(x_left + 6.0), y_vdd)
    b.check()
    return b.c, b


def build(p: LayoutParams = LayoutParams(), sizing: dict[str, object] | None = None) -> gf.Component:
    return build_full(p, sizing)[0]


def write_lvs_reference(p: LayoutParams = LayoutParams(), sizing: dict[str, object] | None = None,
                        out: str | os.PathLike | None = None, builder: Builder | None = None) -> str:
    """The LVS reference for THIS build: the certified netlist (via `netlist_ref`) plus the
    dummy devices this generator actually drew."""
    sz = {**SIZING, **(sizing or {})}
    b = builder or build_full(p, sizing)[1]
    text = NR.lvs_reference(sz, b.dummies)
    if out is not None:
        Path(out).write_text(text)
    return text


def power_budgets(p: LayoutParams = LayoutParams(), sizing: dict[str, object] | None = None,
                  builder: Builder | None = None) -> list[dict]:
    """Every current-carrying segment this build drew, as `current_density.Budget` kwargs.

    Derived from the drawn geometry and `LayoutParams`, never retyped: `layout/signoff.py` turns
    this into the blocking current-density stage (review-002 B1)."""
    b = builder or build_full(p, sizing)[1]
    return b.budgets


def main() -> None:
    ap = argparse.ArgumentParser(description=f"Generate {CELL} (gdsfactory, IHP SG13G2)")
    ap.add_argument("-o", "--out", default=str(Path(__file__).with_name(f"{CELL}.gds")))
    ap.add_argument("--params", default=None, help="JSON overrides for LayoutParams")
    ap.add_argument("--sizing", default=None, help="JSON file of sizing knobs (Design.knobs())")
    ap.add_argument("--lvs", default=None, help="also write the LVS reference netlist here")
    ap.add_argument("--power", default=None, help="also write the power-path budget JSON here")
    a = ap.parse_args()
    p = LayoutParams(**json.loads(a.params)) if a.params else LayoutParams()
    sizing = json.loads(Path(a.sizing).read_text()) if a.sizing else None
    comp, b = build_full(p, sizing)
    comp.write_gds(a.out)
    bb = comp.bbox()
    print(f"wrote {a.out}; bbox um: ({bb.left:.2f},{bb.bottom:.2f})-({bb.right:.2f},{bb.top:.2f}); "
          f"area um2: {(bb.right - bb.left) * (bb.top - bb.bottom):.0f}")
    if a.lvs:
        write_lvs_reference(p, sizing, a.lvs, builder=b)
        print("wrote", a.lvs)
    if a.power:
        Path(a.power).write_text(json.dumps(power_budgets(p, sizing, builder=b), indent=1) + "\n")
        print("wrote", a.power)


if __name__ == "__main__":
    main()
