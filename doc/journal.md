# Journal — index

KIND: REFERENCE (index; `make lint` keeps it complete, newest first)

| date | entry | type | status | hook |
|---|---|---|---|---|
| 2026-09-04 | [plain-fvf-gate-ceiling.md](journal/plain-fvf-gate-ceiling.md) | semantic | live | a plain FVF caps the pass gate at vout, so the pass device leaks 80–470 µA at ff/hot and regulation is lost; a PMOS SF/SSF buffer rings, the double-mirror fold fixes it |
| 2026-09-04 | [fvf-gate-cap-is-slew.md](journal/fvf-gate-cap-is-slew.md) | semantic | live | 5 pF at the FVF pass gate turned a 65 mV load step into 553 mV: the sink slews it alone; damp with L, not C |
| 2026-09-04 | [analog-db-has-no-overlay-root.md](journal/analog-db-has-no-overlay-root.md) | procedural | live | load_circuit reads only its own root and assemble() has no temp arg; lab.dut resolves circuits/<id>/ locally and rewrites the one generated .temp line |
| 2026-09-04 | [lab-venv-lacks-the-physical-lanes.md](journal/lab-venv-lacks-the-physical-lanes.md) | procedural | live | gmid/layout/signoff were not in the template venv; added as path sources, gdsfactory stays in a second interpreter |
| 2026-09-04 | [template-gaps-t8.md](journal/template-gaps-t8.md) | procedural | live | nine template gaps from the T8 instantiation (uv transitive sources, spec tokens, vendor names in class-template comments, wrapper title line, batch() signature, log row name…) + the generic lab code to promote |
| 2026-09-04 | [reference-is-not-at-the-target-point.md](journal/reference-is-not-at-the-target-point.md) | semantic | live | ldo_005 is hv/3.3 V/1.6 V/1 µF; only S2/S3/S5/S6/S8 are quotable, S4/S7 come from the literature until a re-based reference (exp 002) |
| 2026-09-01 | [gap-as-signal.md](journal/gap-as-signal.md) | procedural | live | a trap that bites twice becomes a lint |
