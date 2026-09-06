# 2026-09-05 — a green gate on a drawing that had collapsed

KIND: journal entry | type: procedural | status: live

**Observation** (experiment 004). The candidate deck was recertified mid-task (`bf3a4f8`, "the
certified deck is the drawn device set"): `XR1` became `XR1_1..8`, `XM1` became `XM1A`/`XM1B`, `XMS`
became `XMSA`/`XMSB`, and so on. The block decomposition
(`circuits/ldo_ihp_capless/xschem/ldo_ihp_capless.blocks.json`) names its members **by device
reference**, so three of the five blocks now listed devices that no longer existed.

`BlockAnnotationSet.load` drops a member it cannot find and says nothing. The hierarchy came out
with **two** blocks instead of five, the other 38 devices loose on the top sheet — and both gates
stayed green:

```
blocks: 2      equivalent: true   components 50/50   nets 33   vacuous: false
                                   parameters 239 compared over 50 devices -> OK
```

Which is correct, and useless. `compare_netlists` proves what the drawing *means*; the block
decomposition is what makes it *readable*, and nothing was measuring that. The drawing was still the
certified netlist and no longer the drawing of record.

**Rule.** When an artefact has a structure the reader depends on, assert the structure beside the
meaning, and assert it against the same source of truth. Concretely, for a hierarchy:

- every annotated device must exist in the ingested circuit — an unknown name is a finding, not a
  silent drop;
- every device must be either in a block or one of a short list of **declared** cell-level devices
  (here `VREF`, `VLP`, `XCOUT`), so a new loose device is a finding too;
- as many blocks must form as were declared.

All three exit non-zero. `experiments/004-schematic/build_sch.py::check_block_coverage`.

**Corollary.** A device-name list is a brittle join to a netlist that is allowed to be re-certified.
It is still the right contract — names are what a reviewer reads — but it needs the assertion above
to make a rename loud instead of silent. The upstream half is proposal **P8**: the annotation loader
should fail closed on a member it cannot resolve.
