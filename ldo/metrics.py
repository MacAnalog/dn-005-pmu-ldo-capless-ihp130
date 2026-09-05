"""Fast scorecard: build every bench deck, simulate, map measures to spec keys, check the box,
log the row. Also the reference certification (`--certify`), the drift check (`--check`,
second half of `make check`) and the plain baseline print (`--baseline`).

The measurement definitions are the analog-db LDO class benches; this module only maps their
`print`ed measures onto the unit-scaled spec keys of harness.yaml (`KEYMAP`, documented in
doc/benches.md) and adds nothing of its own.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

from spicexplorer_harness import batch, log_run, violations

from . import config as C
from . import sim
from .dut import REFERENCE, Design

# (bench, ngspice measure) -> (spec/report key, scale). Anything not listed is kept raw under
# "<bench>.<measure>" in the per-bench record but not promoted to a scorecard column.
KEYMAP: dict[tuple[str, str], tuple[str, float]] = {
    ("dc_op", "vout_dc"): ("v_out_v", 1.0),
    ("dc_op", "i_supply"): ("i_q_ua", 1e6),
    ("load_regulation", "load_reg"): ("load_reg_mv", 1e3),
    ("line_regulation", "line_reg"): ("line_reg_mv", 1e3),
    ("dropout", "v_dropout"): ("v_dropout_mv", 1e3),
    ("psrr", "psrr_vdd_db"): ("psrr_1k_db", 1.0),
    ("tran_load_step", "v_undershoot"): ("v_undershoot_mv", 1e3),
    ("tran_load_step", "t_transient"): ("t_transient_us", 1e6),
    ("ac_loopgain", "pm_loop"): ("pm_loop_deg", 1.0),
    ("ac_loopgain", "loopgain_db"): ("loopgain_db", 1.0),
    ("ac_loopgain", "ugf_loop"): ("ugf_loop_khz", 1e-3),
    ("ac_loopgain", "gm_loop_db"): ("gm_loop_db", 1.0),
    ("ac_loopgain", "ms_peak"): ("ms_peak_db", 1.0),
    ("ac_loopgain", "tloop_ph_dc"): ("tloop_ph_dc_deg", 1.0),
    ("loop_stability", "zout_peak_db"): ("zout_peak_db", 1.0),
    ("noise", "vn_out_rms"): ("vn_out_urms", 1e6),
    ("tran_line_step", "v_line_pp"): ("v_line_pp_mv", 1e3),
    # candidate-only twins (circuits/ldo_ihp_capless): report-only PSRR at 1 MHz and the S8
    # sign-off at the light/heavy load (harness.yaml spec_notes)
    ("psrr_1m", "psrr_vdd_db"): ("psrr_1m_db", 1.0),
    ("ac_loopgain_lo", "pm_loop"): ("pm_loop_lo_deg", 1.0),
    ("ac_loopgain_lo", "ugf_loop"): ("ugf_loop_lo_khz", 1e-3),
    ("ac_loopgain_lo", "gm_loop_db"): ("gm_loop_lo_db", 1.0),
    ("ac_loopgain_hi", "pm_loop"): ("pm_loop_hi_deg", 1.0),
    ("ac_loopgain_hi", "ugf_loop"): ("ugf_loop_hi_khz", 1e-3),
    ("ac_loopgain_hi", "gm_loop_db"): ("gm_loop_hi_db", 1.0),
}
COLS = ("v_out_v", "i_q_ua", "load_reg_mv", "line_reg_mv", "v_dropout_mv", "psrr_1k_db",
        "v_undershoot_mv", "t_transient_us", "pm_loop_deg", "loopgain_db", "ugf_loop_khz",
        "gm_loop_db", "ms_peak_db", "zout_peak_db", "vn_out_urms", "v_line_pp_mv")
# The candidate's scorecard: the spec columns first, then the sign-off twins and report-only extras.
COLS_CANDIDATE = ("v_out_v", "i_q_ua", "load_reg_mv", "line_reg_mv", "v_dropout_mv", "psrr_1k_db",
                  "v_undershoot_mv", "pm_loop_deg", "pm_loop_lo_deg", "pm_loop_hi_deg", "loopgain_db",
                  "ugf_loop_khz", "gm_loop_db", "ms_peak_db", "psrr_1m_db", "t_transient_us",
                  "vn_out_urms", "v_line_pp_mv")

# Drift tolerances for `--check`: ngspice is deterministic for a fixed binary + models, so
# these are the spec's own resolution, not run-to-run spread.
TOL: dict[str, tuple[str, float]] = {
    "v_out_v": ("abs", 0.002), "i_q_ua": ("rel", 0.005), "load_reg_mv": ("rel", 0.01),
    "line_reg_mv": ("rel", 0.01), "v_dropout_mv": ("abs", 12.0), "psrr_1k_db": ("abs", 0.05),
    "v_undershoot_mv": ("rel", 0.02), "pm_loop_deg": ("abs", 0.5), "loopgain_db": ("abs", 0.1),
    "ugf_loop_khz": ("rel", 0.01), "vn_out_urms": ("rel", 0.01),
}


def promote(bench: str, measures: dict[str, float]) -> dict[str, float]:
    out = {}
    for meas, val in measures.items():
        key, scale = KEYMAP.get((bench, meas), (f"{bench}.{meas}", 1.0))
        out[key] = val * scale if isinstance(val, (int, float)) else val
    return out


def run_decks(decks: dict[str, str], tag: str, *, record: bool = True) -> tuple[dict, dict]:
    """Simulate {bench: deck} in parallel; return (scorecard values, per-bench records)."""

    def one(bench: str) -> tuple[str, dict]:
        t0 = time.perf_counter()
        rec: dict = {"bench": bench, "deck": decks[bench]}
        try:
            r = sim.run(decks[bench], f"{tag}__{bench}")
            rec.update(status="ok", measures=r.measures, failed=r.failed, wall=r.wall,
                       log=str(r.log_path))
        except sim.SimError as exc:
            rec.update(status="sim_error", error=str(exc)[:800], measures={}, failed=[],
                       wall=time.perf_counter() - t0)
        return bench, rec

    records = dict(batch(list(decks), one, env=C.H.jobs_env, on_error="raise"))
    values: dict = {}
    for bench, rec in records.items():
        if rec["status"] == "ok":
            values.update(promote(bench, rec["measures"]))
            values.update({promote(bench, {m: float("nan")}).popitem()[0]: float("nan")
                           for m in rec["failed"]})
        if record:
            log_run(C.H, f"{tag}__{bench}", {"bench": bench, "status": rec["status"]},
                    kind="bench", deck=rec["deck"], wall=rec["wall"])
    return values, records


def evaluate(design: Design, tag: str, *, record: bool = True, benches=None) -> dict:
    """Every declared bench of `design`; one ledger row per evaluate (plus one per bench)."""
    benches = list(benches or design.benches())
    decks = {b: design.deck(b) for b in benches}
    t0 = time.perf_counter()
    values, records = run_decks(decks, tag, record=record)
    viol = violations(C.H.spec, values)
    row = dict(values)
    if record:
        row = log_run(C.H, tag, values, deck="".join(decks[b] for b in benches),
                      wall=time.perf_counter() - t0, violations=viol, design=design.as_dict(),
                      extra={"benches": {b: r["status"] for b, r in records.items()}})
    row["_records"] = records
    row["_violations"] = viol
    return row


# ------------------------------------------------------------------ reference -----

def frozen_decks() -> dict[str, str]:
    """The frozen reference benches, EXACTLY as certified (bytes, not a rebuild)."""
    return {p.stem: p.read_text() for p in sorted(C.REF_DIR.glob("*.spice"))}


def certified() -> dict:
    return json.loads((C.REF_DIR / "scorecard.json").read_text())


def certify(design: Design = REFERENCE, tag: str = "reference_certify", out: Path | None = None) -> dict:
    """Write <out>/{<bench>.spice, design.json, scorecard.json} (default decks/reference/);
    `make freeze` afterwards. A candidate certifies into decks/candidate/ the same way."""
    out = C.REF_DIR if out is None else Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.spice"):
        old.unlink()
    decks = {b: design.deck(b) for b in design.benches()}
    for b, text in decks.items():
        (out / f"{b}.spice").write_text(text)
    values, records = run_decks(decks, tag)
    log_run(C.H, tag, values, deck="".join(decks.values()), violations=violations(C.H.spec, values),
            design=design.as_dict(), extra={"benches": {b: r["status"] for b, r in records.items()}})
    doc = {
        "circuit": design.circuit, "pdk": design.pdk, "corner": design.corner,
        "design": design.as_dict(),
        "scorecard": {k: v for k, v in values.items() if isinstance(v, float) and not math.isnan(v)},
        "bench_measures": {b: r.get("measures", {}) for b, r in records.items()},
        "bench_status": {b: r["status"] for b, r in records.items()},
        "violations": violations(C.H.spec, values),
        "provenance": {"tag": tag, "t": time.strftime("%Y-%m-%dT%H:%M:%S"), "lane": sim.preflight()["lane"]},
    }
    (out / "design.json").write_text(json.dumps(design.as_dict(), indent=1) + "\n")
    (out / "scorecard.json").write_text(json.dumps(doc, indent=1) + "\n")
    return doc


def drift(measured: dict) -> list[tuple[str, float, float, str]]:
    out, ref = [], certified()["scorecard"]
    for k, (mode, tol) in TOL.items():
        want, got = ref.get(k), measured.get(k)
        if want is None:
            continue
        if got is None or (isinstance(got, float) and math.isnan(got)):
            out.append((k, float("nan"), float(want), "NOT MEASURED"))
            continue
        d = abs(got - want)
        limit = tol * abs(want) if mode == "rel" else tol
        if d > limit:
            out.append((k, float(got), float(want), f"|delta| {d:.4g} > {tol:g} {'rel' if mode == 'rel' else 'abs'}"))
    return out


def table(rows: dict[str, dict], cols=COLS) -> str:
    """A markdown findings table. Prose is interpretation; THIS is the finding."""
    head = "| cell | " + " | ".join(cols) + " | verdict |"
    out = [head, "|" + "---|" * (len(cols) + 2)]
    for name, v in rows.items():
        cells = ["-" if not isinstance(v.get(c), (int, float)) or math.isnan(v[c]) else f"{v[c]:.4g}"
                 for c in cols]
        viol = v.get("_violations", violations(C.H.spec, v))
        out.append(f"| {name} | " + " | ".join(cells) + f" | {'PASS' if not viol else f'FAIL ({len(viol)})'} |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ldo.metrics")
    ap.add_argument("--certify", action="store_true", help="(re)certify the reference into decks/reference/")
    ap.add_argument("--check", action="store_true", help="exit 1 if the frozen reference drifted")
    ap.add_argument("--baseline", action="store_true", help="simulate the frozen decks and print the scorecard")
    a = ap.parse_args(argv)
    if a.certify:
        doc = certify()
        print(table({"reference (certified)": {**doc["scorecard"], "_violations": doc["violations"]}}))
        print("\nbench status:", doc["bench_status"])
        return 0
    if not (C.REF_DIR / "scorecard.json").exists():
        print("no reference certified yet: `python -m ldo.metrics --certify`, then `make freeze`")
        return 1
    decks = frozen_decks()
    values, records = run_decks(decks, "reference_check")
    values["_violations"] = violations(C.H.spec, values)
    log_run(C.H, "reference_check", {k: v for k, v in values.items() if not k.startswith("_")},
            deck="".join(decks.values()), violations=values["_violations"],
            extra={"benches": {b: r["status"] for b, r in records.items()}})
    print(table({"reference (frozen decks)": values}))
    bad = [b for b, r in records.items() if r["status"] != "ok"]
    if bad:
        print("\nbenches that did not run:", bad)
    if a.check:
        d = drift(values)
        if d or bad:
            print("\nDRIFT against decks/reference/scorecard.json:")
            for k, got, want, why in d:
                print(f"  {k:16s} got {got:.6g}  certified {want:.6g}  ({why})")
            print("\nFIX: the simulator, the PDK models, the analog-db submodule or the deck moved; "
                  "re-certify deliberately (`python -m ldo.metrics --certify && make freeze`) "
                  "and re-measure every A/B that was scored before")
            return 1
        print("\nreference reproduces its certified scorecard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
