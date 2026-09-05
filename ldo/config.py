"""Paths and knobs. Everything is overridable via environment variables.

The simulation lane is native ngspice + the open IHP SG13G2 PDK, driven through the
platform's `NGSpice_Wrapper` (see `ldo.sim`). Nothing here is under NDA: decks, models and
logs may all be committed and published verbatim.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from spicexplorer_harness import load as _load

REPO = Path(__file__).resolve().parents[1]
H = _load(REPO)          # harness.yaml: spec, ledger, frozen dirs, env-var names

# ------------------------------------------------------------- work dirs ----
# Simulation runs land here, one subdir per tag, NAMESPACED PER CHECKOUT (repo dir name +
# path hash) so parallel sessions in separate worktrees never clobber each other. Never
# inside the repo, never under /tmp: `$LDO_WORK`, else `$SX_SCRATCH/…`, else `~/sx-scratch/…`.
_ns = f"{REPO.name}-{hashlib.sha1(str(REPO).encode()).hexdigest()[:6]}"
_scratch = Path(os.environ.get("SX_SCRATCH") or (Path.home() / "sx-scratch"))
WORK = Path(os.environ.get("LDO_WORK", _scratch / f"ldo-ihp130-{_ns}"))

# ------------------------------------------------------------------ PDK -----
PDK = "ihp-sg13g2"
# The ngspice binary the platform wrapper should use; empty = whatever `ngspice` is on PATH.
# The PDK's own `.spiceinit` (via $SPICE_USERINIT_DIR) puts the model libs on the sourcepath
# and loads the OSDI objects, so decks reference libs by bare name.
NGSPICE = os.environ.get("LDO_NGSPICE", "")
MOS_LIB_LV = "cornerMOSlv.lib"      # sg13_lv_{n,p}mos  (1.5 V thin oxide) -- the target family
MOS_LIB_HV = "cornerMOShv.lib"      # sg13_hv_{n,p}mos  (3.3 V thick oxide) -- the reference's family
CORNER_NOM = "tt"                   # analog-db generic corner label -> mos_tt/res_typ/cap_typ bundle
CORNERS = ("tt", "ss", "ff", "sf", "fs")
TEMP_NOM = 27.0

# ---------------------------------------------------------------- DUT -------
# The analog-db circuit the reference is certified from; candidates bind their own id.
REF_CIRCUIT = "ldo_005_buffered_ref"
REF_DIR = REPO / "decks" / "reference"
