# 2026-09-04 — a connectivity check that fails with no reason, and the reason is in the log

KIND: journal entry | type: semantic | status: live

**Observation** (review-002-capless-ldo m7). Pointing `SIGNOFF_PYTHON` at the extraction
interpreter makes the rule check work and the connectivity check fail with `matched=False`, an
empty run directory and an **empty `reason`**. The cause is a plain `ModuleNotFoundError: No
module named 'docopt'` — the PDK's `run_lvs.py` imports `docopt` — and it *is* present in the
returned log. `run_lvs` simply does not promote a non-zero exit or a traceback into `reason`, and
a caller that records only `matched` and `reason` (this repo's `layout/signoff.py` did) therefore
reports a mismatch with no cause.

**The first diagnosis was wrong in a specific way.** It was written up as "leave `SIGNOFF_PYTHON`
unset", which is true on this host and useless anywhere else: the actual requirement is that the
interpreter can import **both `docopt` and the layout API**. Host-specific advice hides a fixable
platform gap behind a local workaround.

**Rule.** When a wrapper reports a failure with an empty reason, read the raw log before writing
down a cause — and if the raw log has the cause, the finding is a wrapper bug, not an environment
quirk. Fix the reporting, then write the advice.

**Platform follow-up.** `spicexplorer_signoff.lvs.run_lvs` should set `reason` from the runner's
exit status / stderr.
