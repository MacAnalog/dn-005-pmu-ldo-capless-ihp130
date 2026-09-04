"""The simulator lane: run one deck TEXT through the platform's ngspice wrapper.

`run(deck, tag)` writes the deck under `WORK/decks/`, simulates it with
`spicexplorer_core.spice_engine.NGSpice_Wrapper` into its own `WORK/runs/<tag>/` directory,
scans the ngspice log for the errors ngspice reports WITHOUT a non-zero exit (a failed
operating point leaves a rawfile full of zeros and exit code 0), and parses the deck's
`print` scalars out of the log with the same regex the analog-db tier uses
(`spicexplorer_analog_db.runner.parse_measures`). Nothing here is design-specific.

`preflight()` (`make doctor`) is a one-device `.op` through the same path; the lane is alive
only when a scalar comes back parsed from the log -- rawfile presence proves nothing.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from spicexplorer_analog_db.runner import parse_measures

from . import config as C


class SimError(RuntimeError):
    """ngspice reported a fatal condition, or the run produced no parseable measure."""


def deck_hash(text: str) -> str:
    """Stable 12-hex identity of a deck -- the ledger's provenance key."""
    return hashlib.sha256(text.encode()).hexdigest()[:12]


@dataclass
class RunResult:
    tag: str
    rundir: Path
    deck_path: Path
    log_path: Path | None
    raw_path: Path | None
    wall: float
    measures: dict[str, float] = field(default_factory=dict)
    failed: list[str] = field(default_factory=list)   # `meas` names ngspice reported as failed

    @property
    def log(self) -> str:
        return self.log_path.read_text(errors="replace") if self.log_path else ""


# The lines ngspice prints for failures it does not exit non-zero on, plus the analog-db
# runner's fatal signatures. Any hit is a failed run, whatever the rawfile says.
_FATAL = (
    "doAnalyses: iteration limit reached",
    "Transient solution failed",
    "singular matrix",
    "no such vector",
    "Unknown model type",
    "could not find a valid modelname",
    "simulation interrupted",
    "cannot open",
    "Error: Library file",
    "fatal",
)
_FATAL_RX = re.compile("|".join(re.escape(s) for s in _FATAL), re.IGNORECASE)


def _safe(tag: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", tag)


def run(deck: str, tag: str) -> RunResult:
    """Simulate `deck` (a complete ngspice deck: a `*` title line first, its own `.control`
    block) under `WORK/runs/<tag>/`; return the parsed measures; raise `SimError` on a failed run."""
    from spicexplorer_core.spice_engine import NGSpice_Wrapper

    tag = _safe(tag)
    decks, runs = C.WORK / "decks", C.WORK / "runs"
    decks.mkdir(parents=True, exist_ok=True)
    deck_path = decks / f"{tag}.spice"
    deck_path.write_text(deck)
    # The wrapper wipes its output folder on first construction and refuses a netlist that
    # lives inside it -- hence decks/ beside runs/, never within.
    out = runs / tag
    kw = {"path_to_simulator": Path(C.NGSPICE)} if C.NGSPICE else {}
    t0 = time.perf_counter()
    w = NGSpice_Wrapper(netlist_filename=deck_path, output_folder=out, testbench_name=tag, **kw)
    res = w.run(label=tag)
    wall = time.perf_counter() - t0
    r = RunResult(tag=tag, rundir=out, deck_path=deck_path,
                  log_path=Path(res.log_path) if res.log_path else None,
                  raw_path=Path(res.raw_path) if res.raw_path else None, wall=wall)
    (out / "wall.txt").write_text(f"{wall:.3f}\n")
    log = r.log
    bad = [ln for ln in log.splitlines() if _FATAL_RX.search(ln)]
    if bad:
        raise SimError(f"{tag}: simulator error\n  " + "\n  ".join(bad[:8]))
    r.measures, r.failed = parse_measures(log)
    if not r.measures and not r.failed:
        raise SimError(f"{tag}: no measure parsed from the log ({r.log_path})\n{_tail(log)}")
    return r


def _tail(s: str, n: int = 30) -> str:
    lines = [ln for ln in s.splitlines() if ln.strip()]
    return "\n".join(lines[-n:])


def preflight() -> dict:
    """Cheap 'is the lane alive?' probe -- what `make doctor` reports."""
    info = {"lane": "native ngspice via NGSpice_Wrapper", "ngspice": C.NGSPICE or "ngspice (PATH)",
            "pdk": C.PDK, "work": str(C.WORK), "ok": False, "note": ""}
    deck = f"""* lane preflight (the wrapper's editor wants a `*` title line first)
.lib {C.MOS_LIB_LV} mos_tt
vd d 0 0.75
vg g 0 0.6
xm1 d g 0 0 sg13_lv_nmos w=1u l=0.13u ng=1 m=1
.control
set filetype=ascii
op
let id_ua = -i(vd)*1e6
print id_ua
write
quit
.endc
.end
"""
    try:
        r = run(deck, "_preflight")
        info["ok"] = r.measures.get("id_ua", float("nan")) > 0
        info["note"] = f"id_ua={r.measures.get('id_ua')} in {r.wall:.2f} s; log {r.log_path}"
    except Exception as exc:  # noqa: BLE001 - reported, not raised
        info["note"] = str(exc)[:600]
    return info


if __name__ == "__main__":  # `make doctor`
    info = preflight()
    print(json.dumps(info, indent=2))
    sys.exit(0 if info["ok"] else 1)
