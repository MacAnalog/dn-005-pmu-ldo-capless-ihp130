# 2026-09-04 — a plain FVF cannot turn its pass device off: the gate is capped at vout

KIND: journal entry | type: semantic | status: live

**Observation** (ledger `003_corners_hand_*`, `003_leak_*`, `003_probe4/5/6_*`; experiment 002 §2b, tables 3–5).
The FVF + two-stage error amp that passes the whole box at tt/27 °C loses regulation at every hot or
fast corner: v_out 1.256 V at ff/27, 1.306 V at tt/125, 1.368 V at ff/125 with the load at its
0.1 mA minimum. The control PMOS's source is the output, so the pass gate can never go above
vout − Vsd,sat ≈ vout: the pass device always sees Vsg ≥ Vin − Vout = 0.3 V. For the 400 µm /
0.15 µm pass device that is 15.6 µA at tt/27 (harmless) but 163 µA at tt/125, 80 µA at ff/27 and
472 µA at ff/125 — more than the load, so the outer loop has nothing left to regulate with.

**Rule.** With an FVF output stage, check the pass device's Vsg = Vin − Vout leakage at ff/125 °C
against the minimum load before anything else; if it is larger, the gate driver must be able to
reach vdd. Two ways were measured here:

- a PMOS source follower / super-source follower between control device and pass gate
  (`engur2023`'s buffer) restores the range but adds a pole at the ~1 pF gate and rang for the
  whole 7 µs bench window at every damping tried;
- a **double-mirror fold** — control-device current into an NMOS diode, mirrored into a PMOS
  diode, mirrored again onto the gate as a pull-up, constant sink still pulling down — gives the
  gate the full vss + Vds,sat … vdd − Vsd,sat range, keeps the FVF's transient pull-up current and
  the sink's pull-down slew, and adds only diode (low-impedance) nodes, so it does not ring. Cost:
  the control current is drawn twice more (≈ 9 µA here); keep the fold mirrors narrow (wider
  mirrors slowed the gate: undershoot 74 → 142 mV at 2× widths).

**Corollary.** "Meets the box at tt/27" is not evidence for an FVF regulator; the ff/125 light-load
op point is the first corner to run, and it is cheap (one dc_op bench).
