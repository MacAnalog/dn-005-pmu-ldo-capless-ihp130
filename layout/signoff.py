"""005 — layout sign-off driver: guards -> GDS -> current density -> DRC -> LVS -> PEX.

Every stage is the platform's own runner (`spicexplorer_signoff`, `spicexplorer_layout`); this
file only sequences them and writes the verdicts a reviewer reads. Two interpreters are
involved and the split is not cosmetic:

* ``gen_ldo.build`` needs **gdsfactory + ihp-gdsfactory** -> `$LDO_GF_PYTHON`
  (default ``~/miniconda3/envs/ai_env/bin/python``); it is run as a subprocess.
* DRC / LVS / PEX are KLayout runsets + kpex, driven from THIS interpreter through
  `spicexplorer_signoff` (which finds its own klayout/kpex executables via `$PDK_ROOT`).

  ``SIGNOFF_PYTHON``, if set, must name an interpreter that can import **both ``docopt``**
  (the PDK's ``run_lvs.py`` imports it) **and the layout API**. Leaving it unset resolves
  `pdk.runner_python()` to this checkout's venv, which has both. An interpreter missing
  ``docopt`` gives ``matched=False``, an empty run directory and an empty ``reason`` -- the
  ``ModuleNotFoundError`` traceback IS in the returned log, but `run_lvs` does not promote a
  non-zero exit into ``reason``, so a caller that records only ``matched``/``reason`` (this
  file did) reports a mismatch with no cause. Platform follow-up:
  doc/journal/run-lvs-swallows-its-own-traceback.md (review-002 m7).

The engine of record is therefore **KLayout** (IHP SG13G2 runsets) for DRC/LVS and **kpex**
(2.5D) for extraction -- not magic/netgen.

Two PDK-runset quirks are handled here, both journalled:

1. **kpex cannot read a 2-node ``rhigh``.** The standalone IHP LVS deck extracts the poly
   resistor as a 2-terminal device, but kpex's bundled copy
   (``rule_decks/custom_reader.lvs``: ``'Poly resistor should have 3 nodes'``) extracts it as
   3-terminal (two ports + substrate, connected to pwell). The LVS schematic and the PEX
   schematic therefore differ by that third node -- :func:`pex_schematic` adds it.
2. **kpex cannot extract IHP MIM caps** -- ``strip_mim_for_pex`` removes the MIM device layers
   and the C cards; the schematic MIM capacitors are spliced back for the benches.

Two stages exist because `review-002` said "silence from a check that did not run is not
evidence":

* **guards** — `layout/test_builder.py`, the case M8 asked for: a Metal1 stub collision that only
  the obstacle map prevents.  It runs first and blocks, so the guard is exercised every round.
* **current density** — `spicexplorer_signoff.current_density` over the budget list the
  GENERATOR emits from its own drawn geometry (`gen_ldo.power_budgets`), never a retyped table.
  Electromigration is not a rule-deck check and not a connectivity check, so without this stage a
  cell can pass DRC, LVS, PEX and every bench at 12-28x over the metal limit — which the cell of
  record did (B1, `doc/journal/metal-current-density-is-nobodys-check.md`).

    LDO_EXP=005 uv run --no-sync python layout/signoff.py --all
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ldo import config as C  # noqa: E402

CELL = "ldo_ihp_capless"
GEN = Path(__file__).resolve().parent / "gen_ldo.py"
GF_PYTHON = os.environ.get("LDO_GF_PYTHON", str(Path.home() / "miniconda3/envs/ai_env/bin/python"))
WORK = C.WORK / "layout"


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print("  $", " ".join(str(c) for c in cmd)[:160], flush=True)
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)


# ---------------------------------------------------------------- build ----

def guards() -> dict:
    """The generator's own regression case (review-002 M8).  A blocker: a router guard that no
    case exercises rots, and this one is the difference between a shorted netlist and a clean
    one."""
    r = _run([sys.executable, str(Path(__file__).resolve().parent / "test_builder.py")])
    ok = r.returncode == 0
    print(" ", (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else "")
    return {"passed": ok, "log": (r.stdout + r.stderr)[-2000:]}


def current_density(power_json: Path) -> dict:
    """Score every current-carrying segment the generator drew against the PDK's own limits."""
    from spicexplorer_signoff.current_density import Budget, check_current_density, limit_for

    rows = json.loads(power_json.read_text())
    r = check_current_density([Budget(**d) for d in rows], pdk="ihp-sg13g2")
    table = []
    for d in rows:
        lim = limit_for(d["layer"], width_um=d["width_um"], n_vias=d["n_vias"])
        table.append({**d, "limit_a": lim[0] if lim else None, "rule": lim[1] if lim else None,
                      "over": round(d["current_a"] / lim[0], 4) if lim else None})
    worst = max((t["over"] for t in table if t["over"] is not None), default=None)
    print(f"  current density: passed={r.passed} checked={r.n_checked} worst={worst}")
    return {"passed": bool(r.passed), "n_checked": int(r.n_checked),
            "n_violations": int(r.n_violations), "worst_over": worst,
            "reason": r.reason, "segments": table,
            "violations": [v.__dict__ for v in r.violations]}


def build(out: Path, sizing: Path | None = None) -> dict:
    """GDS + LVS reference + power-path budget at the sizing of record (or `sizing`)."""
    out.mkdir(parents=True, exist_ok=True)
    gds, lvs = out / f"{CELL}.gds", out / f"{CELL}_lvs.spice"
    cmd = [GF_PYTHON, GEN, "-o", gds, "--lvs", lvs, "--power", out / "power_path.json"]
    if sizing:
        cmd += ["--sizing", str(sizing)]
    r = _run(cmd)
    if r.returncode != 0 or not gds.is_file():
        raise SystemExit(f"generator failed:\n{r.stdout}\n{r.stderr}")
    m = re.search(r"area um2: (\d+)", r.stdout)
    print(" ", r.stdout.strip().splitlines()[0])
    return {"gds": str(gds), "lvs_netlist": str(lvs), "power_path": str(out / "power_path.json"),
            "area_um2": int(m.group(1)) if m else None, "sizing": str(sizing) if sizing else None,
            "stdout": r.stdout.strip()}


def render(gds: Path, png: Path) -> bool:
    r = _run([sys.executable, "-m", "spicexplorer_layout.cli", "render", str(gds), str(png)])
    ok = png.is_file()
    if not ok:
        print("  render failed:", (r.stdout + r.stderr)[-500:])
    return ok


# ------------------------------------------------------------- sign-off ----

def drc(gds: Path, out: Path, no_density: bool = True) -> dict:
    """Rule check. `no_density` skips the density/fill tables, which a standalone cell cannot
    satisfy on its own -- they are met by fill at chip assembly. The README states the flag and
    lists what those tables report when enabled (review-002 m1); pass `--density` to see them."""
    from spicexplorer_signoff.drc import run_drc
    r = run_drc(str(gds), CELL, str(out), no_density=no_density)
    print(f"  DRC: passed={r.passed} violations={r.n_violations}")
    # `DrcViolation` is not JSON-serialisable, and this line only ever runs when the list is
    # non-empty -- so a clean cell hid the bug until the first real violation (review-002 B1
    # attempt). Count per rule instead: which rules fired is what a reviewer reads.
    per_rule: dict[str, int] = {}
    hits: dict[str, list] = {}
    for v in r.violations:
        k = str(getattr(v, "rule", "?"))
        per_rule[k] = per_rule.get(k, 0) + int(getattr(v, "count", 1))
        hits[k] = [[float(x), float(y)] for x, y in (getattr(v, "locations", None) or [])][:60]
    for k, n in sorted(per_rule.items(), key=lambda kv: -kv[1]):
        print(f"    {k:18s} {n:4d}  e.g. {hits.get(k, [])[:3]}")
    return {"passed": bool(r.passed), "available": bool(r.available), "no_density": bool(no_density),
            "n_violations": int(r.n_violations), "violations_per_rule": per_rule, "hits": hits,
            "report": r.report_path, "reason": r.reason}


def lvs(gds: Path, netlist: Path, out: Path) -> dict:
    from spicexplorer_signoff.lvs import run_lvs
    r = run_lvs(str(gds), str(netlist), CELL, str(out), extra_args=["--combine_devices"])
    # The wrapper's pass flag is the runset's own verdict line; keep the raw evidence beside it.
    matched = bool(r.matched) or "Congratulations! Netlists match" in (r.log or "")
    print(f"  LVS: matched={matched}")
    return {"passed": bool(r.passed), "matched": matched, "available": bool(r.available),
            "unmatched": dict(r.unmatched or {}), "report": r.report_path,
            "netlist_sha": r.netlist_sha, "reason": r.reason}


_R_CARD = re.compile(r"^(R\S*)\s+(\S+)\s+(\S+)\s+(rhigh|rppd|rsil)\b(.*)$", re.I)


def pex_schematic(lvs_text: str, sub: str = "vss") -> str:
    """The LVS netlist as kpex's reader wants it: no C cards (MIM is stripped from the GDS too)
    and every poly resistor given its third, substrate node."""
    from spicexplorer_signoff.pex import strip_cards

    out = []
    for ln in strip_cards(lvs_text).splitlines():
        m = _R_CARD.match(ln.strip())
        out.append(f"{m.group(1)} {m.group(2)} {m.group(3)} {sub} {m.group(4)}{m.group(5)}" if m else ln)
    return "\n".join(out) + "\n"


def pex(gds: Path, lvs_netlist: Path, out: Path, mode: str = "CC") -> dict:
    from spicexplorer_signoff.pex import run_pex, strip_mim_for_pex

    pex_gds = gds.with_name(f"{CELL}_pex.gds")
    strip_mim_for_pex(gds, pex_gds)
    sch = gds.with_name(f"{CELL}_pex_schematic.spice")
    sch.write_text(pex_schematic(lvs_netlist.read_text()))
    r = run_pex(pex_gds, CELL, sch, out, mode=mode)
    print(f"  PEX: ok={r.ok} n_C={r.n_c} n_R={r.n_r}")
    top = sorted(((v, k) for k, v in (r.per_net_c_ff or {}).items()), reverse=True)[:12]
    return {"ok": bool(r.ok), "available": bool(r.available), "mode": r.mode,
            "netlist": r.netlist_path, "n_c": int(r.n_c), "n_r": int(r.n_r),
            "per_net_c_ff": {k: round(v, 3) for v, k in top}, "reason": r.reason,
            "log_tail": (r.log or "")[-1500:] if not r.ok else ""}


def _snapshot(iter_dir: Path, out: Path, rec: dict, note: str, detail: str) -> None:
    """Record the round -- generator, render, per-rule DRC counts + hits, verdicts, knobs."""
    from spicexplorer_layout.iterations import snapshot

    drc = rec.get("drc")
    if drc:
        drc = {"passed": drc["passed"], "n_violations": drc["n_violations"],
               "violations": [{"rule": k, "count": v, "locations": drc.get("hits", {}).get(k, [])}
                              for k, v in (drc.get("violations_per_rule") or {}).items()]}
    e = snapshot(iter_dir, note=note or "(no note)", detail=detail,
                 gen_path=GEN, gds=(out / f"{CELL}.gds") if (out / f"{CELL}.gds").is_file() else None,
                 params={"area_um2": (rec.get("build") or {}).get("area_um2"),
                         "current_density_worst_over": (rec.get("current_density") or {}).get("worst_over")},
                 drc=drc, lvs=rec.get("lvs"), pex=rec.get("pex"),
                 area_um2=(rec.get("build") or {}).get("area_um2"), keep_gds=False)
    print("snapshot:", e.id)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(WORK))
    ap.add_argument("--stages", default="guards,build,render,cd,drc,lvs,pex")
    ap.add_argument("--sizing", default=None, help="JSON sizing overrides (a second sizing point)")
    ap.add_argument("--snapshot", default=None, help="iterations dir to record this round into")
    ap.add_argument("--note", default="", help="the round's one-line headline for the snapshot")
    ap.add_argument("--detail", default="", help="the round's long-form notes for the snapshot")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--pex-mode", default="CC", choices=["CC", "RC", "R"],
                    help="PEX policy: CC in the loop, RC once for the report")
    ap.add_argument("--density", action="store_true",
                    help="run the density/fill rule tables too (review-002 m1)")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    stages = a.stages.split(",")
    rec: dict = {}
    gds, netlist = out / f"{CELL}.gds", out / f"{CELL}_lvs.spice"

    if "guards" in stages:
        print("guards:")
        rec["guards"] = guards()
        if not rec["guards"]["passed"]:
            (out / "signoff.json").write_text(json.dumps(rec, indent=1) + "\n")
            raise SystemExit("router guards failed — see layout/test_builder.py")
    if "build" in stages:
        print("build:"); rec["build"] = build(out, Path(a.sizing) if a.sizing else None)
    if "render" in stages:
        print("render:"); rec["render"] = render(gds, out / f"{CELL}.png")
    if "cd" in stages:
        print("current density:")
        rec["current_density"] = current_density(out / "power_path.json")
        if not rec["current_density"]["passed"]:
            (out / "signoff.json").write_text(json.dumps(rec, indent=1) + "\n")
            raise SystemExit("current-density stage failed — a segment is over the process limit")
    if "drc" in stages:
        print("drc:"); rec["drc"] = drc(gds, out / "drc", no_density=not a.density)
    if "lvs" in stages:
        print("lvs:"); rec["lvs"] = lvs(gds, netlist, out / "lvs")
    if "pex" in stages:
        print("pex:"); rec["pex"] = pex(gds, netlist, out / f"pex_{a.pex_mode.lower()}"
                                        if a.pex_mode != "CC" else out / "pex", mode=a.pex_mode)

    (out / "signoff.json").write_text(json.dumps(rec, indent=1) + "\n")
    print("\nwrote", out / "signoff.json")
    if a.snapshot:
        _snapshot(Path(a.snapshot), out, rec, a.note, a.detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())
