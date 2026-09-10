# The front door.  `make help` lists everything.  The generic harness (lint, pack,
# runs, freeze) is the platform's spicexplorer-harness driven by harness.yaml;
# ldo/ and scripts/ hold only what is specific to this design.

# Prefer the checkout's own venv (uv sync creates it); fall back to python3.
PY ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
HARNESS := $(PY) -m spicexplorer_harness.cli --repo .
ARGS ?=

help:  ## list every target
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

init:  ## set up this checkout: .sx/platform -> $$SX_ROOT/spicexplorer-platform, the .sx/skills library + agent/skill links, uv sync
	@test -n "$(SX_ROOT)" || { echo "SX_ROOT is not set: export SX_ROOT=<your spicexplorer-workspace checkout> (the lab puts it in ~/.sx_env)"; exit 2; }
	@test -f "$(SX_ROOT)/spicexplorer-platform/packages/spicexplorer-harness/pyproject.toml" || { echo "SX_ROOT=$(SX_ROOT) holds no spicexplorer-platform/ checkout"; exit 2; }
	@mkdir -p .sx && ln -sfn "$(SX_ROOT)/spicexplorer-platform" .sx/platform
	@git submodule update --init --recursive .sx/skills
	@.sx/skills/bin/sx-link . --set design
	@uv sync
	@echo "init OK: .sx/platform -> $$(readlink .sx/platform); $$(ls .claude/agents | wc -l) agents + $$(ls .claude/skills | wc -l) skills linked from .sx/skills; next: make doctor"

template-status:  ## which template version this design was cut from (.sx/template-version) and what minor updates exist since
	@$(PY) scripts/template_update.py status

template-update:  ## propagate the template's MINOR updates into this design (three-way merge; nothing committed). VER=1.03 to pick one
	@$(PY) scripts/template_update.py update $(VER)

skills-update:  ## move .sx/skills (the shared agent/skill library) to its main, re-link, and stage the pin — then commit it
	@git -C .sx/skills fetch -q origin main && git -C .sx/skills checkout -q origin/main
	@.sx/skills/bin/sx-link . --set design
	@git add .sx/skills .claude
	@echo "skills @ $$(git -C .sx/skills rev-parse --short HEAD): $$(ls .claude/agents | wc -l) agents + $$(ls .claude/skills | wc -l) skills linked; staged — commit the pin: git commit -m 'skills: bump .sx/skills to $$(git -C .sx/skills rev-parse --short HEAD)'"

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

sign:  ## verifier re-measures a frozen dir and signs it if it reproduces (DIR=decks/reference AUTHOR=<designer> VERIFIED_BY=<you>)
	@$(PY) -m ldo.sign $(DIR) --author "$(AUTHOR)" --verified-by "$(VERIFIED_BY)"

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

.PHONY: template-status template-update help init skills-update lint check baseline pack runs freeze doctor fig-layout clean
