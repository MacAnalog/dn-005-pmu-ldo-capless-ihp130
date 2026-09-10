"""Build (and execute) notebooks/ldo_walkthrough.ipynb.

The notebook is generated, not hand-edited, so it cannot drift from the repo and so no host path
can be baked into it: every cell resolves paths from the repo root at run time and prints only
scorecards and verdicts. Run from the repo root:

    uv run --no-sync python notebooks/make_walkthrough.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
NB = HERE / "ldo_walkthrough.ipynb"
# `.venv/bin/python -m ipykernel install --user --name ldo-ihp130` registers it once per host.
KERNEL = os.environ.get("LDO_KERNEL", "ldo-ihp130")

MD = nbf.v4.new_markdown_cell
CODE = nbf.v4.new_code_cell

CELLS = [
    MD("""# A capless low-Iq LDO in IHP SG13G2 — walkthrough

**Read `doc/target-spec.md` first**: this notebook does not define anything, it *reads* the
artefacts the experiments certified. The rule of the repo is that a number which has not passed
the frozen bench definitions is a claim, so every figure below comes from a scorecard JSON that a
simulation wrote.

1. the acceptance box (S1–S8) and the certified reference it is measured against
2. the design of record and what it cost to get there (experiment 003)
3. corners: which spec actually binds, and why it is a bias problem rather than a sizing one
4. the layout, and what extraction costs (experiment 005)"""),

    CODE("""import json, os
from pathlib import Path

# The repo root, found from the notebook's own location -- never an absolute host path.
REPO = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "harness.yaml").is_file())
os.chdir(REPO)

from spicexplorer_harness import load, violations
H = load(REPO)
print(H.goal)"""),

    MD("""## 1. The acceptance box

`harness.yaml` holds the machine twin of `doc/target-spec.md`; `make lint` refuses to let the two
drift, so this table IS the spec."""),

    CODE("""import pandas as pd
# H.spec rows are SpecRow dataclasses, not dicts.
box = pd.DataFrame([{"spec": s.label, "key": s.key, "bound": f"{s.op} {s.bound}",
                     "unit": s.unit or ""} for s in H.spec])
box"""),

    MD("""## 2. Reference vs the design of record

The reference (`ldo_005_buffered_ref`) was certified at **its own** committed operating point —
3.3 V thick-oxide devices, 1.6 V out, 1 µF external capacitor — because no analog-db LDO binding
runs at this challenge's conditions. It is therefore a yardstick for regulation and PSRR only, not
a competitor; `doc/journal/reference-is-not-at-the-target-point.md` has the reasoning."""),

    CODE("""ref = json.loads(Path("decks/reference/scorecard.json").read_text())
cand = json.loads(Path("signoff/prelayout/decks/scorecard.json").read_text())
keys = [s.key for s in H.spec]
cmp = pd.DataFrame({
    "reference (3.3 V, 1 uF)": {k: ref["scorecard"].get(k) for k in keys},
    "design of record (1.5 V, on-chip)": {k: cand["scorecard"].get(k) for k in keys},
    "bound": {s.key: f"{s.op} {s.bound}" for s in H.spec},
}).round(3)
print("reference violations:", len(ref["violations"]))
print("candidate violations:", len(cand["violations"]))
cmp"""),

    MD("""The headline of the challenge was to match the reference's load/line regulation and 1 kHz
PSRR at **≤ 50 µA** of quiescent current. The record does it at **36.3 µA — 4.8 % of the
reference's 759 µA** — while also improving regulation, PSRR and phase margin, at 1.5 V into an
on-chip 21 pF instead of 3.3 V into 1 µF."""),

    CODE("""cur = {"reference": ref["scorecard"]["i_q_ua"], "design of record": cand["scorecard"]["i_q_ua"]}
print(f'quiescent current: {cur["reference"]:.1f} uA -> {cur["design of record"]:.2f} uA '
      f'({cur["design of record"] / cur["reference"] * 100:.1f} % of the reference)')
for k in ("load_reg_mv", "line_reg_mv", "psrr_1k_db", "pm_loop_deg"):
    a, b = ref["scorecard"][k], cand["scorecard"][k]
    print(f'{k:15s} {a:9.3f} -> {b:9.3f}')"""),

    MD("""## 3. The design of record, device by device

The sizing point is not stored in this notebook or in the layout generator: it is the `default:`
fields of the circuit's `sizing.yaml`, so a bare `ldo.dut.CANDIDATE`, the frozen decks, the
schematic of record and the GDS all render the same numbers by construction."""),

    CODE("""import yaml
sizing = yaml.safe_load(Path("circuits/ldo_ihp_capless/pdk/ihp-sg13g2/sizing.yaml").read_text())
dev = pd.DataFrame([{"knob": v["name"], "default": v["default"],
                     "what": v["description"].split("(")[0].strip()}
                    for v in sizing["variables"]])
dev"""),

    MD("""## 4. Corners — the finding that matters

12 of 15 corners pass. The two that do not are **S5 at ff/125 °C** and **S7 at ss/−40 °C**, and
they are one mechanism: the bias is resistor-referenced, so every branch current scales with
`rhigh`'s sheet resistance and the quiescent current spreads **2.4×** across the grid. S5 wants
less current and S7 wants more, from the same knob — which is why the next increment is a
PVT-stable bias, not more sizing (`experiments/003-sizing/README.md` §3)."""),

    CODE("""p = Path("experiments/003-sizing/out/corners.json")
if p.is_file():
    corners = json.loads(p.read_text())
    df = pd.DataFrame(corners).T[["i_q_ua", "v_undershoot_mv", "pm_loop_deg", "v_out_v"]].round(3)
    df["verdict"] = ["PASS" if not corners[i]["violations"] else "FAIL" for i in df.index]
    iq = df["i_q_ua"]
    print(f"Iq spread over the corner grid: {iq.min():.2f} - {iq.max():.2f} uA "
          f"({iq.max() / iq.min():.2f}x)")
    display(df)
else:
    print("corner data is a run artefact (experiments/*/out/ is git-ignored); regenerate with:")
    print("  LDO_EXP=003 uv run --no-sync python experiments/003-sizing/score.py --corners")"""),

    MD("""![corners](../experiments/003-sizing/figs/corners.png)

Phase margin — the thing 002 fought hardest for and the predicted corner failure — never binds:
it stays between 70.3° and 73.4° over the whole grid. The optimizer bought 12° of it while cutting
Iq, and that margin is what absorbs the corner spread."""),

    MD("""## 5. The layout, and what extraction costs

DRC 0 violations, LVS matched against the certified netlist, kpex 2.5D extraction, and then the
cell's **own** frozen benches re-run on the extracted netlist. Not a new measurement — the same
definitions, a different netlist."""),

    CODE("""p = Path("experiments/005-layout/out/scorecard.json")
if p.is_file():
    sc = json.loads(p.read_text())
    post = pd.DataFrame({"pre-layout": sc["pre"], "post-layout": sc["post"]})
    post = post.loc[[k for k in keys if k in post.index]]
    post["shift"] = (post["post-layout"] - post["pre-layout"]).round(3)
    print("post-layout violations:", len(sc["post_violations"]))
    display(post.round(3))
else:
    print("post-layout data is a run artefact; regenerate with:")
    print("  LDO_EXP=005 uv run --no-sync python layout/postlayout.py")"""),

    MD("""![layout](../experiments/005-layout/figs/ldo_ihp_capless.png)

The layout costs **9.1 mV of undershoot and 0.68° of phase margin**, and both trace to the same
place: extraction puts 28.4 fF on the pass-device gate, and in an FVF output stage every farad
there is paid at the sink's slew rate (`doc/journal/fvf-gate-cap-is-slew.md`). The cell still
passes the whole box after layout.

## What to read next

| | |
|---|---|
| the sizing run, the cliff, the corner table | `experiments/003-sizing/README.md` |
| drawing ≡ netlist | `experiments/004-schematic/README.md` |
| generator, sign-off, the DRC-invisible short it found | `experiments/005-layout/README.md` |
| every lesson, one file each | `doc/journal.md` |"""),
]


def main() -> int:
    nb = nbf.v4.new_notebook(cells=CELLS)
    # The notebook must run on THIS checkout's venv (the platform packages are editable path
    # deps there); a bare "python3" kernelspec resolves to whatever kernel the host registered
    # first and fails with ModuleNotFoundError: spicexplorer_harness.
    nb.metadata["kernelspec"] = {"name": KERNEL, "display_name": KERNEL, "language": "python"}
    NB.write_text(nbf.writes(nb))
    print("wrote", NB.relative_to(Path.cwd()) if NB.is_relative_to(Path.cwd()) else NB.name)
    r = subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook",
                        "--execute", "--inplace", str(NB)], capture_output=True, text=True)
    print((r.stdout + r.stderr)[-1200:])
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
