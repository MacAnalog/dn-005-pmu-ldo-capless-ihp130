"""Sheet-resistance solve on this cell's drawn `vss` return path (review-004 **F9**) — a CLI.

There is no extracted resistance to read: kpex's RC mesh is joined but its terminal/via values
are three orders out (REPORT section 5), so every series-R number in this cell is a model. A
1-D hand model is what got REPORT section 6.4 wrong: it credited the row-A ptap ring over the
whole 170 um of the return when the ring spans only x = -3.4 .. 105.6, so the first 66.6 um is
bare rail. This solves the drawn copper instead of describing it.

The solver is now `spicexplorer_layout.rail` — rasterize one drawn layer, keep the 4-connected
component the pin touches, and solve the grid in which each edge is one square of sheet metal —
and the sheet resistances and GDS layer numbers it uses come from the platform's tech config for
`$PDK`, not from a table in this repo. What is left here is this cell's command line.

    uv run --no-sync python layout/rail_solve.py <gds> --pin -70,-134 --probe far=96.5,2.15
    uv run --no-sync python layout/rail_solve.py --selftest
"""
from __future__ import annotations

import argparse
import os
import sys

from spicexplorer_core.tech import Tech
from spicexplorer_layout.rail import (
    component_touching,
    rasterize_layer,
    selftest as _selftest,
    solve_sheet_resistance,
)

CELL = "ldo_ihp_capless"


def selftest() -> int:
    """A 10 um x 1 um bar is 10 squares end to end — the solver against an analytic value."""
    got, want = _selftest()
    err = (got - want) / want
    print(f"bar 9.9x1 um: solved {got:.4f} Ohm, analytic {want:.4f}, error {err * 100:+.2f} %")
    return 0 if abs(err) < 0.01 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("gds", nargs="?")
    ap.add_argument("--cell", default=CELL)
    ap.add_argument("--layer", default="Metal1")
    ap.add_argument("--pitch", type=float, default=0.1)
    ap.add_argument("--pdk", default=os.environ.get("PDK", "ihp-sg13g2"))
    ap.add_argument("--pin", default="", help="x,y (or x0,y0,x1,y1) of the pin, um")
    ap.add_argument("--probe", action="append", default=[], help="name=x,y (um), repeatable")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    tech = Tech.builtin(a.pdk)
    r = rasterize_layer(a.gds, a.cell, a.layer, a.pitch, tech=tech)
    pin = r.box([float(t) for t in a.pin.split(",")])
    r.mask = component_touching(r.mask, (pin[0], pin[2]))
    print(f"{a.layer}: {r.mask.sum()} cells on the pin's component at {a.pitch} um")
    probes = {}
    for spec in a.probe:
        name, _, xy = spec.partition("=")
        probes[name] = r.box([float(t) for t in xy.split(",")])
    got = solve_sheet_resistance(r.mask, tech.sheet_resistance(a.layer), pin, probes)
    for k, v in sorted(got.items()):
        print(f"  R(pin -> {k}) = {v:.3f} Ohm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
