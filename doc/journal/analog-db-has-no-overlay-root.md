# 2026-09-04 — analog-db has no overlay root: a candidate circuit cannot be bound from outside its tree

KIND: journal entry | type: procedural | status: live

**Symptom.** `spicexplorer_analog_db.model.load_circuit(id)` resolves only
`paths.circuits_root()/<id>` (the submodule's own `circuits/`, or the whole root moved by
`$SPICEXPLORER_ANALOG_DB`). A design repo that wants to bind a NEW circuit to the class benches
(`assemble()`) therefore has to either write into the platform submodule — forbidden here, another
agent owns that checkout — or bypass the loader.

**What was done (minimum, local).** `assemble(circuit, …)` takes a `Circuit` object, and
`Circuit(id=, dir=, manifest=)` is a plain frozen dataclass whose methods read
`datasheet.yaml`, `analyses/<id>.yaml`, `pdk/<pdk>/{sizing,corners}.yaml`, `pdk/<pdk>/netlist.spice`
under `dir`. So `lab.dut.circuit(id)` now resolves `circuits/<id>/circuit.yaml` in THIS repo first
and builds the `Circuit` itself; the analog-db root stays the fallback (the reference still comes
from there). The candidate directory is an exact analog-db circuit directory, hand-lowered
(`abstract/netlist.spice` + `pdk/ihp-sg13g2/netlist.spice` kept in step by hand — there is no
`analog-db generate` for a local dir either).

**Platform function that is missing** (for the template lane to promote): an overlay/search-path
for circuit roots — `load_circuit(id, roots=[…])` or `SPICEXPLORER_ANALOG_DB_EXTRA`, plus
`assemble(…, temp=)` (see below). Until then every design repo re-implements this 6-line resolver.

**Second gap, same seam.** `assemble()` takes the simulation temperature from the datasheet's
`default_conditions.temp` only; a corner table (-40/27/125 °C) needs a per-deck temperature.
`lab.dut.Design.temp` rewrites the ONE generated `.temp` line at build time (asserting there is
exactly one) — a generator-level substitution, not a text edit of a frozen deck; the reference's
`design.json` has no `temp` key so its decks are byte-identical (`make check` still passes).
