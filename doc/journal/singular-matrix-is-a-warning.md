# 2026-09-04 — "singular matrix" is what ngspice prints while converging, not proof it failed

KIND: journal entry | type: procedural | status: live

**Observation** (experiment 005 §3). Seven of the 13 post-layout benches came back NaN with
`sim_error`. Their logs contained every measure they were asked for. The only fatal line was
`Warning: singular matrix:  check node xdut.n_37` — one occurrence, during the gmin/source
stepping ngspice does on its way to an operating point, on an extracted netlist whose resistor
taps carry hundreds of sub-fF capacitances to substrate. The analysis then converged and printed
`pm_loop = 71.7`, `loopgain_db = 49.9`, and the rest.

`lab.sim._FATAL` contains the substring `"singular matrix"` and `lab.sim.run` raises `SimError`
on any line that matches, so the results were thrown away while sitting in the file. The strict
scan exists for a real reason — ngspice exits 0 after a failed operating point and leaves a
rawfile full of zeros — but the discriminator it uses is wrong for this one string.

**Rule.** The question "did this run fail?" is answered by **whether the measures parsed**, not by
whether a warning appeared. Keep the fatal scan, but let a line that is prefixed `Warning:` be
overridden by a successful parse; a line that is not (`Transient solution failed`,
`doAnalyses: iteration limit reached`, `singular matrix` as a bare error) still fails the run.

**Proposed diff to `lab/sim.py`** — procedural code is human-reviewed (CLAUDE.md rule 10), so this
is a proposal, not an applied change. In `run()`, after `bad = [...]`:

```python
    r.measures, r.failed = parse_measures(log)
    # A `Warning:`-prefixed fatal string is advisory: ngspice prints `Warning: singular matrix`
    # while gmin-stepping to an operating point and then converges. It only condemns the run if
    # nothing parsed.
    hard = [ln for ln in bad if not re.match(r"\s*warning\s*:", ln, re.I)]
    if hard or (bad and not r.measures):
        raise SimError(f"{tag}: simulator error\n  " + "\n  ".join((hard or bad)[:8]))
    if not r.measures and not r.failed:
        raise SimError(f"{tag}: no measure parsed from the log ({r.log_path})\n{_tail(log)}")
```

**Interim.** `layout/postlayout.py:run_tolerant()` applies exactly this rule locally and labels
such benches `ok (benign singular-matrix warning)` in `bench_status`, so the scorecard says which
rows needed it rather than hiding it.
