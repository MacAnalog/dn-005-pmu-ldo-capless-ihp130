# The front door.  `make help` lists everything.  The generic harness (lint, pack,
# runs, freeze) is the platform's spicexplorer-harness driven by harness.yaml;
# ldo/ and scripts/ hold only what is specific to this design.

# Prefer the checkout's own venv (uv sync creates it); fall back to python3.
PY ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
HARNESS := $(PY) -m spicexplorer_harness.cli --repo .
ARGS ?=

help:  ## list every target
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

lint:  ## repo invariants (harness.yaml + scripts/lint.py extras); failures carry their remediation
	@$(PY) scripts/lint.py

check:  ## lint + the reference reproduces its certified scorecard
	@rc=0; $(PY) scripts/lint.py || rc=1; echo; $(PY) -m ldo.metrics --check || rc=1; exit $$rc

baseline:  ## simulate the frozen reference decks and print the scorecard
	@$(PY) -m ldo.metrics --baseline $(ARGS)

pack:  ## working-memory context pack (K="noise gain" S="symptom text")
	@$(HARNESS) pack $(K) $(if $(S),--symptom "$(S)") $(ARGS)

runs:  ## query the run ledger (ARGS="--fails" | "--best i_q_ua" | "--exp 001" | "--kind bench" | "--where circuit=ldo_005_buffered_ref")
	@$(HARNESS) runs $(ARGS)

freeze:  ## write SHA256SUMS into the frozen dirs after a deliberate certification
	@$(HARNESS) freeze

doctor:  ## is the simulation lane alive?
	@$(PY) -m ldo.sim

# The labelled layout figure.  Geometry comes from the rebuilt GDS and the annotation spec
# `layout/ldo_ihp_capless/labels.yaml`; nothing is placed by hand.  `spicexplorer_signoff.annotate`
# is a platform module that is PROPOSED, not yet merged — until it lands, point LAYOUT_ANNOTATE at
# the workspace-level runner named in the workspace layout-annotation method doc, e.g.
#   make fig-layout LAYOUT_ANNOTATE="$(PY) /path/to/annotate.py"
LAYOUT_ANNOTATE ?= $(PY) -m spicexplorer_signoff.annotate

fig-layout:  ## redraw experiments/005-layout/figs/ldo_ihp_capless_labelled*.png from the GDS + labels.yaml
	@w=$$($(PY) -c "from ldo import config; print(config.WORK)"); g="$$w/layout/ldo_ihp_capless.gds"; \
	 test -f "$$g" || { echo "no GDS at $$g — first: LDO_EXP=005 $(PY) layout/signoff.py --stages build"; exit 1; }; \
	 for v in "dark:" "white:_white"; do \
	   $(LAYOUT_ANNOTATE) "$$g" layout/ldo_ihp_capless/labels.yaml \
	     experiments/005-layout/figs/ldo_ihp_capless --base "$$w/layout/annotate_base.png" \
	     --ground "$${v%%:*}" --variant "$${v##*:}" --quantize 256 --formats png || exit 1; \
	 done

clean:  ## delete this checkout's simulation work dir + experiment output (never the ledger)
	@d=$$($(PY) -c "from ldo import config; print(config.WORK)"); echo "rm -rf $$d"; rm -rf "$$d"; rm -rf experiments/*/out/

.PHONY: help lint check baseline pack runs freeze doctor fig-layout clean
