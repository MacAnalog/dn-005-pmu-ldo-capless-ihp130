"""003 — sizing: score the optimizer's winner through the FROZEN bench definitions.

`run_opt.py` reads nine benches through the optimizer's own recipe layer; rule 1 says a number
is a claim until it has passed `lab.metrics.evaluate` (the full 13-bench analog-db class
scorecard). This script does that, for three points and for the corner sweep:

    control  the double-mirror fold hand point of 002, pinned explicitly in CONTROL below
    raw      the optimizer's best knobs verbatim (floats in metres)
    record   the same point ROUNDED to values a layout can draw (W/L on a 10 nm grid, MIM
             sides and resistor lengths on a 0.5 um grid, integer pass-device multiplier)

Only `record` is the design of record: `gen_ldo._s` snaps geometry to a 5 nm grid and the
schematic of record carries the same numbers, so a 9.415138 um knob would make drawing,
netlist and simulation disagree in the fourth digit.

    LDO_EXP=003 uv run --no-sync python experiments/003-sizing/score.py --point record
    LDO_EXP=003 uv run --no-sync python experiments/003-sizing/score.py --corners
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lab import config as C  # noqa: E402
from lab import metrics as M  # noqa: E402
from lab.dut import CANDIDATE  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# The optimizer's best knobs (experiments/003-sizing/opt_best.json, copied from the run dir).
# Only the SEARCHED knobs are listed; everything else stays at its sizing.yaml default.
RAW_M: dict[str, float] = {
    "c_ff_w": 9.415138108419495e-06, "r_bias_l": 0.0001383319673590318,
    "x_dut_xmb1_w": 1.3876125705788644e-06, "x_dut_xmt_w": 9.999999999999999e-06,
    "x_dut_xm1_w": 9.527011164328107e-06, "x_dut_xm3_w": 2.9527790240015315e-06,
    "x_dut_xm5_w": 2.4245072126185743e-06, "x_dut_xm6_w": 5.526225290045692e-06,
    "c_comp_w": 5.385009413458311e-05, "x_dut_xmc_w": 1.576206324326544e-05,
    "x_dut_xmc_l": 3.623072853367675e-07, "x_dut_xma_w": 5.794875759567906e-06,
    "x_dut_xmcp_w": 9.023413114168818e-06, "x_dut_xms_w": 2.200000000000001e-06,
    "x_dut_xms_l": 9.517905906498067e-07, "x_dut_xmp_l": 1.3e-07, "x_dut_xmp_m": 19.0,
}
# knob -> rounding grid in um; None = integer count
GRID_UM: dict[str, float | None] = {
    "c_ff_w": 0.5, "c_comp_w": 0.5, "r_bias_l": 0.5, "x_dut_xmp_m": None,
}
DEV_GRID_UM = 0.01          # every transistor W/L: 10 nm, drawn exactly on the 5 nm layout grid.
# A 50 nm grid was tried first and is NOT usable: it rounds the pass device off the PDK minimum
# length (0.13 -> 0.15 um) and S7 goes 107 -> 248 mV (doc/journal/round-then-rescore.md).


def _um(v: float) -> float:
    return v * 1e6


def raw_point() -> dict[str, str]:
    out = {}
    for k, v in RAW_M.items():
        out[k] = f"{v:g}" if k == "x_dut_xmp_m" else f"{_um(v):.6f}u"
    return out


# One knob is NOT taken from the optimizer verbatim. `c_ff_w` (the feed-forward MIM across the
# top divider resistor) has a CLIFF between 9.4 and 9.5 um: S7 jumps 107 -> 201 mV across a 0.9 %
# change of the MIM side, and the optimizer's winner sits 15 nm from it (README §2).
# The record backs the knob off to 8 um -- 19 % of margin, and the value 002 had already
# established -- paying 2 mV of undershoot and 2.2 deg of phase margin for a point that survives
# a rounding step. Journal: doc/journal/optimizer-parks-on-cliffs.md.
BACKOFF: dict[str, str] = {"c_ff_w": "8u"}


def rounded_point() -> dict[str, str]:
    """RAW rounded onto grids a layout and a schematic can carry verbatim."""
    out = {}
    for k, v in RAW_M.items():
        g = GRID_UM.get(k, DEV_GRID_UM)
        if g is None:
            out[k] = str(int(round(v)))
            continue
        val = round(_um(v) / g) * g
        out[k] = f"{val:g}u"
    return out


def record_point() -> dict[str, str]:
    """The design of record: rounded, then backed off the cliff knob."""
    return {**rounded_point(), **BACKOFF}


# The 002 hand point, PINNED. It used to be spelled `{}` -- "whatever sizing.yaml says" -- which
# was true when 003 started and false by the time 003 ended, because 003 moved those very
# defaults onto the optimizer's winner (r_bias_l 100u -> 138.5u, x_dut_xmc_w 13u -> 15.76u and
# eight more). An empty control silently became a second copy of the record, so the 50.17 uA row
# this experiment rests on could not be reproduced without checking out 76eddd6. Values below are
# `git show 76eddd6:circuits/ldo_ihp_capless/pdk/ihp-sg13g2/sizing.yaml` (review-002 m12).
CONTROL: dict[str, str] = {
    "c_ff_w": "8u", "r_bias_l": "100u", "x_dut_xmb1_w": "1.6u", "x_dut_xmt_w": "10u",
    "x_dut_xm1_w": "8u", "x_dut_xm1_l": "0.5u", "x_dut_xm3_w": "1u", "x_dut_xm3_l": "1u",
    "x_dut_xm5_w": "2u", "x_dut_xm5_l": "0.5u", "x_dut_xm6_w": "5u", "c_comp_w": "45u",
    "x_dut_xmc_w": "13u", "x_dut_xmc_l": "0.3u", "x_dut_xma_w": "2u", "x_dut_xma_l": "0.5u",
    "x_dut_xmcp_w": "6u", "x_dut_xmcp_l": "0.5u", "x_dut_xms_w": "2.2u", "x_dut_xms_l": "1u",
    "x_dut_xmp_w": "10u", "x_dut_xmp_l": "0.13u", "x_dut_xmp_m": "20",
}

POINTS = {
    "control (002 fold hand point)": CONTROL,
    "optimizer best (raw)": raw_point(),
    "rounded (10 nm device grid)": rounded_point(),
    "design of record (rounded + c_ff_w off the cliff)": record_point(),
}


def score(name: str, knobs: dict[str, str], tag: str, corner: str = "tt",
          temp: float | None = None) -> dict:
    d = CANDIDATE.with_sizing(**knobs) if knobs else CANDIDATE
    d = d.at(corner=corner, temp=temp)
    row = M.evaluate(d, tag)
    print(f"  {name}: iq={row.get('i_q_ua'):.2f} uA  viol={len(row['_violations'])}", flush=True)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--point", choices=["control", "raw", "rounded", "record", "all"], default="all")
    ap.add_argument("--corners", action="store_true", help="the record point over 5 MOS corners x -40/27/125 C")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    if a.corners:
        rec = record_point()
        rows = {}
        for corner in C.CORNERS:
            for t in (-40.0, 27.0, 125.0):
                nm = f"{corner} {t:g} C"
                rows[nm] = score(nm, rec, f"003_record_{corner}_{t:g}C", corner=corner, temp=t)
        table = M.table(rows, cols=M.COLS_CANDIDATE)
        (OUT / "corners.md").write_text(table + "\n")
        (OUT / "corners.json").write_text(json.dumps(
            {k: {c: v.get(c) for c in M.COLS_CANDIDATE} | {"violations": v["_violations"]}
             for k, v in rows.items()}, indent=1) + "\n")
        print("\n" + table)
        return 0

    want = {"control": [0], "raw": [1], "rounded": [2], "record": [3], "all": [0, 1, 2, 3]}[a.point]
    names = list(POINTS)
    rows = {}
    for i in want:
        nm = names[i]
        rows[nm] = score(nm, POINTS[nm], f"003_{['control', 'raw', 'rounded', 'record'][i]}_tt_27")
    table = M.table(rows, cols=M.COLS_CANDIDATE)
    (OUT / f"points_{a.point}.md").write_text(table + "\n")
    (OUT / f"points_{a.point}.json").write_text(json.dumps(
        {k: {c: v.get(c) for c in M.COLS_CANDIDATE} | {"violations": v["_violations"]}
         for k, v in rows.items()}, indent=1) + "\n")
    print("\n" + table)
    print("\nrecord knobs:", json.dumps(record_point(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
