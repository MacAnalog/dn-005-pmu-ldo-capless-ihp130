# Environment

KIND: REFERENCE (procedural gotchas; recipes that outgrow this file go to `doc/memory/procedural/`)

| item | value |
|---|---|
| PDK | **IHP SG13G2** (`ihp-sg13g2`, Apache-2.0), install `$PDK_ROOT/ihp-sg13g2`, pinned at IHP-Open-PDK commit `62c1d640dc1c91f57bc1a8e4e08e537a7a105ae8`; MOS model cards PSP 103.6, corner-lib revision 200310 (`libs.tech/ngspice/models/cornerMOS{lv,hv}.lib`) |
| simulator lane | **native ngspice-45** (`$HOME/local/bin/ngspice`, installed under `~/local/tools/ngspice_44_2/` despite the name — trust `ngspice --version`, not the path), driven through the platform's `spicexplorer_core.spice_engine.NGSpice_Wrapper` (`lab/sim.py`) |
| PDK model resolution | `SPICE_USERINIT_DIR=$PDK_ROOT/ihp-sg13g2/libs.tech/ngspice` — its `.spiceinit` puts `models/` on the ngspice `sourcepath` and loads `osdi/psp103_nqs.osdi`, `r3_cmc.osdi`, `mosvar.osdi`. Decks reference libs by bare name (`.lib cornerMOShv.lib mos_tt`) so they stay host-independent |
| corner sections | MOS `mos_tt mos_ss mos_ff mos_sf mos_fs` (each with a `_mismatch` twin); R `res_typ res_wcs res_bcs`; C `cap_typ cap_wcs cap_bcs` — bundled per corner in analog-db `circuits/<id>/pdk/ihp-sg13g2/corners.yaml` |
| device families | `sg13_lv_{n,p}mos` thin oxide, **1.5 V** rail (`_shared/pdk/ihp-sg13g2.yaml: supply.default: 1.5`); `sg13_hv_{n,p}mos` thick oxide, 3.3 V rail. The reference binding is hv/3.3 V; the target is lv/1.5 V |
| work dir | `$LDO_WORK`, else `$SX_SCRATCH/ldo-ihp130-<checkout hash>`, else `~/sx-scratch/ldo-ihp130-<hash>` — per checkout, outside the repo, never `/tmp` |
| parallel width | `LDO_JOBS` (default cpu_count − 2); ngspice is pinned single-threaded in the shared `.spiceinit` |
| experiment stamp | `LDO_EXP=NNN` |

## Gotchas

- **ngspice exits 0 after a failed operating point** and leaves a rawfile full of zeros;
  `lab.sim.run` scans the log for the fatal strings and raises `SimError`. A run with no parsed
  `print` scalar is a failure, not a zero.
- **`print` output lands in the wrapper's log file**, not on stdout: `NGSpice_Wrapper` runs
  `ngspice -b -o <log>`; `lab.sim` parses the measures out of `result.log_path` with
  analog-db's `runner.parse_measures` (same regex the analog-db tier uses).
- **`NGSpice_Wrapper` wipes its `output_folder` on first construction** in a process and refuses a
  netlist that lives inside it; `lab.sim` keeps decks in `WORK/decks/` and runs in `WORK/runs/<tag>/`.
- **The wrapper's `.noise` guard forces `.option sparse`** (KLU cannot run `.noise`); nothing to do,
  but expect the noise bench to be the slow one.
- **`.param` shadowing is the sizing seam.** analog-db's assembled deck binds every sizing knob with
  a `.param name=default`; a later `.param name=value` line wins (analog-db calls this
  "untying = shadowing"). `lab.dut.Design.deck()` appends the overrides — no line is edited.
