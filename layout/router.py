"""The generator's per-net obstacle map and column allocator — no gdsfactory, so it is testable.

`doc/journal/metal1-stub-shorts-are-drc-invisible.md`: `to_track` reaches a terminal's channel
track with a Metal2 column and bridges any x-shift with a **Metal1 stub** at the terminal's y.
Two overlapping same-layer shapes merge into one legal polygon, so a stub that walks through a
neighbour's gate bar is a short **DRC cannot see** — only LVS catches it, and only if some sizing
point happens to produce the collision.

`review-002` **M8**: the obstacle map was committed as the permanent guarantee, but reverting it
alone still gave 0 violations and a matched netlist at every committed sizing — no case exercised
it, and a regression no case exercises rots. This module is that case's home: `layout/
test_builder.py` builds the collision by hand and asserts the allocator refuses it.

`Builder` in `gen_ldo.py` derives from :class:`ObstacleMap`, so the code under test is the code
that draws.
"""
from __future__ import annotations

GRID = 0.005
W_M1 = 0.2


def snap(v: float) -> float:
    return round(round(v / GRID) * GRID, 4)


class ObstacleMap:
    """Every Metal1 feature a later stub must not run into, plus the Metal2 column allocator."""

    #: Metal2 column pitch the allocator must respect (via pad 0.38 + Metal2 space 0.21).
    M2_CLEAR = 0.6

    def __init__(self) -> None:
        self.m1_rows: list[list] = []   # [net, y0, y1, x0, x1]
        self.verticals: list[tuple[str, float, float, float]] = []  # (net, x, y0, y1)

    # -- claims ------------------------------------------------------------
    def m1_claim(self, net: str, y: float, x0: float, x1: float, h: float = W_M1) -> None:
        self.m1_rows.append([net, snap(y - h / 2), snap(y + h / 2), snap(min(x0, x1)),
                             snap(max(x0, x1))])

    def m1_claim_box(self, net: str, x0: float, y0: float, x1: float, y1: float) -> None:
        self.m1_rows.append([net, snap(min(y0, y1)), snap(max(y0, y1)), snap(min(x0, x1)),
                             snap(max(x0, x1))])

    def m1_retag(self, old: str, new: str) -> None:
        for r in self.m1_rows:
            if r[0] == old:
                r[0] = new

    # -- the two checks ----------------------------------------------------
    def stub_clear(self, net: str, y: float, xa: float, xb: float,
                   cx: float = 0.28, cy: float = 0.22) -> bool:
        """Would a Metal1 stub of ``net`` at ``y`` from ``xa`` to ``xb`` touch another net's
        Metal1?  ``cx``/``cy`` are the clearance the stub and its via pad need."""
        lo, hi = min(xa, xb) - cx, max(xa, xb) + cx
        ylo, yhi = y - W_M1 / 2 - cy, y + W_M1 / 2 + cy
        for n, y0, y1, x0, x1 in self.m1_rows:
            if n == net or y1 < ylo or y0 > yhi or x1 < lo or x0 > hi:
                continue
            return False
        return True

    def column_free(self, net: str, x: float, lo: float, hi: float) -> bool:
        """Is a Metal2 vertical of ``net`` over [lo, hi] clear of every other net's vertical?"""
        return all(v[0] == net or abs(v[1] - x) >= self.M2_CLEAR - 1e-6
                   or v[3] < lo - self.M2_CLEAR or v[2] > hi + self.M2_CLEAR
                   for v in self.verticals)

    def alloc(self, net: str, x: float, y0: float, y1: float, step: float = 0.6,
              tries: int = 80) -> float:
        """First x from ``x`` in ``step`` increments whose Metal2 vertical over [y0, y1] is free
        AND whose Metal1 stub crosses nobody.

        The search goes in the preferred direction FIRST and then the other one: a column that is
        free of Metal2 but whose stub would cross a foreign gate bar is not usable, so the walk
        has to be able to turn round instead of marching into the neighbour.
        """
        lo, hi = min(y0, y1), max(y0, y1)
        for k in range(tries):
            for s in (step, -step) if k else (step,):
                xx = snap(x + k * s)
                if self.column_free(net, xx, lo, hi) and self.stub_clear(net, y0, x, xx):
                    return xx
        raise AssertionError(f"no free Metal2 column for {net} near x={x} (widen dev_gap/grp_gap)")
