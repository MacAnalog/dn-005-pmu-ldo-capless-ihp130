"""003 — sizing: drive the frozen class benches of the candidate through `spicexplorer-optimize`.

Decks are BUILT from `lab.dut.CANDIDATE` with NO overrides, so every knob is defined exactly once
(the sizing.yaml `.param` default) and the optimizer's by-name `.param` rewrite hits the live
line. The project YAML's `dut_params` are the sizing knobs (SI units), `init` = the hand point
(seeded as trial 0), `target_specs` = the S1-S8 box with margin + S8 at 0.1/10 mA; the objective
is the quiescent current (S5, minimize with log reward for headroom).

    LDO_EXP=003 uv run --no-sync python experiments/003-sizing/run_opt.py --budget 120 --workers 8
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lab import config as C  # noqa: E402
from lab.dut import CANDIDATE  # noqa: E402
from spicexplorer_core.eng import parse_value  # noqa: E402

OPT = C.WORK / "opt"
SEARCH = {  # knob -> (min, max) in sizing.yaml syntax; everything else is frozen at its default
    "r_bias_l": ("50u", "200u"), "x_dut_xmb1_w": ("0.8u", "3u"), "x_dut_xmt_w": ("4u", "20u"),
    "x_dut_xm1_w": ("4u", "20u"), "x_dut_xm3_w": ("0.5u", "3u"), "x_dut_xm5_w": ("1u", "6u"),
    "x_dut_xm6_w": ("2u", "12u"), "c_comp_w": ("26u", "73u"), "c_ff_w": ("4u", "11u"), "x_dut_xmc_w": ("4u", "30u"),
    "x_dut_xmc_l": ("0.13u", "0.6u"), "x_dut_xms_w": ("1u", "8u"), "x_dut_xms_l": ("0.3u", "2u"),
    "x_dut_xmp_m": ("10", "50"), "x_dut_xmp_l": ("0.13u", "0.25u"), "x_dut_xma_w": ("0.5u", "8u"),
    "x_dut_xmcp_w": ("1u", "20u"),
}
INTEGER = {"x_dut_xmp_m"}
# (name, testbench, sim_type, goal, target, range, tolerance, weight, reward)
SPECS = [
    ("i(i_supply)", "dc_op", "op", "minimize", 30e-6, 50e-6, 0.0, 2.0, "log"),      # S5 objective
    ("v(vout_dc)", "dc_op", "op", "exact", 1.2, 0.5, 0.02, 1.0, "none"),            # S1 (+/-24 mV box, 20 used)
    ("load_reg", "load_regulation", "dc", "minimize", 4e-3, 10e-3, 0.0, 1.0, "none"),   # S2 <= 5 mV
    ("line_reg", "line_regulation", "dc", "minimize", 1.5e-3, 5e-3, 0.0, 1.0, "none"),  # S3 <= 2 mV
    ("v_dropout", "dropout", "dc", "minimize", 0.17, 0.3, 0.0, 1.0, "none"),            # S4 <= 200 mV
    ("psrr_vdd_db", "psrr", "ac", "exceed", 43.0, 40.0, 0.0, 1.0, "none"),              # S6 >= 40 dB
    ("v_undershoot", "tran_load_step", "tran", "minimize", 0.12, 0.3, 0.0, 1.5, "none"),  # S7 <= 150 mV
    # S8 at 1 / 0.1 / 10 mA. The three benches all `print` the same `pm_loop` name and the
    # optimizer keys specs by name, so each is read through the Tier-1 registry recipe
    # {meas: pm, out: tloop} on the saved loop-gain wave -- the same 180 - phi0 + phi_ugf the
    # bench's own meas computes (validated on the smoke run: recipe == deck pm_loop).
    ("pm_loop_1m", "ac_loopgain", "ac", "exceed", 63.0, 60.0, 0.0, 1.0, "none"),
    ("pm_loop_lo", "ac_loopgain_lo", "ac", "exceed", 63.0, 60.0, 0.0, 1.0, "none"),
    ("pm_loop_hi", "ac_loopgain_hi", "ac", "exceed", 63.0, 60.0, 0.0, 1.0, "none"),
]
RECIPES = {"pm_loop_1m": {"meas": "pm", "out": "tloop"}, "pm_loop_lo": {"meas": "pm", "out": "tloop"},
           "pm_loop_hi": {"meas": "pm", "out": "tloop"}}
BENCHES = sorted({s[1] for s in SPECS})


def write_project(budget: int, seed: int) -> Path:
    decks = OPT / "decks"
    decks.mkdir(parents=True, exist_ok=True)
    for b in BENCHES:
        (decks / f"{b}.spice").write_text(CANDIDATE.deck(b))
    knobs = CANDIDATE.knobs()
    dut_params = []
    for name, default in knobs.items():
        if name in SEARCH:
            lo, hi = SEARCH[name]
            dut_params.append({"name": name, "min_val": float(parse_value(lo)), "max_val": float(parse_value(hi)),
                               "init": float(parse_value(default)), "is_integer": name in INTEGER})
        else:
            dut_params.append({"name": name, "freeze": True, "val": float(parse_value(default))})
    specs = [dict(name=n, testbench=tb, sim_type=st, goal=g, target=t, range=r, tolerance=tol, weight=w,
                  reward_type=rw, enable=True, **({"measurement": RECIPES[n]} if n in RECIPES else {}))
             for n, tb, st, g, t, r, tol, w, rw in SPECS]
    doc = {"project": {
        "name": "ldo_ihp_capless sizing (003)", "description": "experiments/003-sizing", "simulator": "ngspice", "save_sim": False, "parallel_sim": True,
        "ws_root": str(decks), "netlist": "dc_op.spice", "outdir": "run", "tech_spec": {"name": "ihp-sg13g2", "constraints": {}},
        "dut_params": dut_params,
        "testbenches": [{"name": b, "params": [], "netlist": f"{b}.spice", "enable": True,
                         "description": f"frozen class bench {b} built by lab.dut.CANDIDATE"} for b in BENCHES],
        "optimizer_config": {"type": "nevergrad", "random_seed": seed, "budget": budget, "name": "NGOpt",
                             "seed_from_init": True,
                             "lin_variable_bounds": {"min": 0, "max": 100}, "log_variable_bounds": {"min": 1, "max": 100},
                             "target_specs": specs}}}
    p = OPT / "project_setup.yaml"
    p.write_text(yaml.safe_dump(doc, sort_keys=False))
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=120)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--outdir", default="run")
    a = ap.parse_args()
    p = write_project(a.budget, a.seed)
    print("project:", p, "\nknobs searched:", sorted(SEARCH), flush=True)
    cmd = [sys.executable, "-m", "spicexplorer.optimization.run_project", str(p), "--budget", str(a.budget),
           "--workers", str(a.workers), "--outdir", a.outdir, "--no-timestamp", "--quiet"]
    log = OPT / f"{a.outdir}.log"
    with log.open("w") as fh:
        rc = subprocess.call(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=str(OPT))
    tail = log.read_text().splitlines()
    best: dict[str, object] = {}
    for ln in tail:  # "[spicexplorer-optimize] best score -0.81" / "best knobs: {...}" / "best metrics: {...}"
        m = re.match(r"\[spicexplorer-optimize\] best (score|knobs|metrics):? (.*)$", ln.strip())
        if m:
            best[m.group(1)] = json.loads(m.group(2)) if m.group(2).startswith("{") else float(m.group(2))
    (OPT / f"{a.outdir}_best.json").write_text(json.dumps(best, indent=1) + "\n")
    print("\n".join(tail[-6:]))
    return rc


if __name__ == "__main__":
    sys.exit(main())
