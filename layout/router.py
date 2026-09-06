"""This cell's obstacle map: the platform's map, bound to this PDK's routing rules.

The map itself — the two shorts verification cannot catch for you, and the column allocator that
avoids them — is now :class:`spicexplorer_layout.route.ObstacleMap`, and every clearance it obeys
(grid, stub width, stub clearance, column pitch, which layer is the route layer and which the stub
layer) is read from the tech config `spicexplorer_core.tech` rather than written here. The two
cases that bought those checks are unchanged and still live in this repo:

* `doc/journal/metal1-stub-shorts-are-drc-invisible.md` / `review-002` **M8** — a Metal1 stub that
  walks through a neighbour's gate bar is a short **DRC cannot see**; `layout/test_builder.py`
  builds the collision by hand so the guard is exercised without depending on a sizing point.
* `review-003` **F7** — a column through drawn metal nobody registered. The map is layer-aware:
  every vertical carries its layer and :meth:`claim_box` records any drawn rectangle.

What is left here is exactly the binding: which process, and the three method names this repo's
generator (`layout/gen_ldo.py`) and its case already call.
"""
from __future__ import annotations

import os

from spicexplorer_core.tech import Tech
from spicexplorer_layout.route import ObstacleMap as _PlatformObstacleMap

_RULES = Tech.builtin(os.environ.get("PDK", "ihp-sg13g2")).routing_rules()

#: Module constants the generator draws with; the numbers themselves come from the tech config.
GRID = _RULES.grid_um
W_M1 = _RULES.stub_width_um


def snap(v: float) -> float:
    return _RULES.snap(v)


class ObstacleMap(_PlatformObstacleMap):
    """The platform map on this PDK's rules, under the names this generator already calls."""

    def __init__(self) -> None:
        super().__init__(_RULES)

    #: Kept as an attribute because `gen_ldo.py` compares two allocated columns against it.
    M2_CLEAR = _RULES.column_pitch_um

    # The platform's names are layer-neutral (`stub`, not `m1`) — the right name for a class that
    # does not know which layer a given process calls its stub layer. These three are this
    # generator's spelling of them.
    def m1_claim(self, net: str, y: float, x0: float, x1: float, h: float | None = None) -> None:
        self.claim_stub_row(net, y, x0, x1, h)

    def m1_claim_box(self, net: str, x0: float, y0: float, x1: float, y1: float) -> None:
        self.claim_stub_box(net, x0, y0, x1, y1)

    def m1_retag(self, old: str, new: str) -> None:
        self.retag(old, new)

    @property
    def m1_rows(self) -> list[list]:
        return self.stub_rows

    def alloc(self, net, x, y0, y1, step=None, tries=80, layer="", hint=""):
        """The platform allocator, refusing in terms of THIS generator's knobs."""
        return super().alloc(
            net, x, y0, y1, step, tries, layer, hint or "widen dev_gap/grp_gap"
        )
