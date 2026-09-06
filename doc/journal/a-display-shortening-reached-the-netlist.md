# 2026-09-05 — a display shortening reached the netlist, and only a value check saw it

KIND: journal entry | type: procedural | status: live

**Observation** (experiment 006). Two of the 13 bench sheets drew a load or line step whose
netlist read

```
ILOAD vout 0 …00n 10u 20u)          # deck: Iload vout 0 pulse(0.1m 10m 1u 100n 100n 10u 20u)
```

Every topology check passed on both sheets: the instance was there, on the right nets, in the right
order. The cause was in the schematic emitter, whose `_display_value` abbreviated any attribute
value over 24 characters to its tail — a shortening intended for the *drawing* — and wrote the
result into the instance's `value=`, which is the attribute xschem netlists. Sizing symbols
(`w=x_dut_xmp_w`) are all under the threshold, so it had never shown; a transient stimulus is not.
A bench sheet built this way is not a bench: it runs, it converges, and it measures the wrong step.

**Rule.** Anything that shortens, rounds or prettifies a value for a drawing has to be *drawn*, not
*stored*. If a value has one representation, that representation is the runnable one.

**Corollary for the checks.** A round trip that proves the same devices on the same nets proves
nothing about what those devices *are*. Compare values as well as connectivity, on the benches and
not only on the cell — the cell's own sizing had a value check since experiment 004, and it was the
bench comparison, added later, that found this. The comparison is worth writing so it exits
non-zero: this one drifted on 2 of 13 sheets, and a report would have been read as noise.

**Where it lives.** `experiments/006-visual-benches/build_benches.py::compare_bench`. The emitter
fix is proposal **P4** in `$SX_SCRATCH/ldo-schematic/platform-proposal/`, applied here as a guarded
patch in `experiments/004-schematic/sch_support.py` until it lands upstream.

*Update, 2026-09-05:* it landed (`spicexplorer-platform @33850e1`), and on the way there the same
defect was measured a second time on a SIZE rather than a stimulus — the recertified cell's pass
device netlisted as `w='…xmp_nf_mult}'`. The local patch is gone; what remains in the design repo is
an assertion that the behaviour is present, and a report-only run of the stock CLI whose job is to
go red again if the truncation returns.
