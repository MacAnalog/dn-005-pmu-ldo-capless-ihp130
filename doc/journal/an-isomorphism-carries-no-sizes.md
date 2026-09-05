# 2026-09-05 — a wiring-preserving isomorphism says nothing about the sizes

KIND: journal entry | type: procedural | status: live

**Observation** (experiment 004, review-002 finding M3). `compare_netlists` matched the certified
cell against the drawing's netlist — **25 components and 15 nets under a wiring-preserving
isomorphism**, non-vacuous — while the drawing carried

```
VREF vref vss 3                      # certified: dc {vref_val}, i.e. 0.6 V
XCFF lp_brk fb  cap_cmim m=1         # certified: w=c_ff_w   l=c_ff_w    (8 um)
XCC  ea_out ea_o1 cap_cmim m=1       # certified: w=c_comp_w l=c_comp_w  (54 um)
XCOUT vout vss cap_cmim m=c_out_m    # certified: w=c_out_w  l=c_out_w   (58 um)
```

A `cap_cmim` with no `w`/`l` falls back to the model library's own 7 µm × 7 µm ≈ 74 fF, so the
drawing that "is" the design of record silently states 74 fF where the design has 0.1 pF, 4.4 pF
and 4 × 5 pF, and regulates against 3 V instead of 0.6 V. The graph comparison cannot see any of
it: it compares devices, models and connectivity, which is what it is for.

**Rule.** Topology equivalence is half a proof. After it, join the two netlists device by device
and compare **every parameter by NUMBER** — resolve the symbols against the deck's own `.param`
bindings, normalise the SI suffixes, then compare. Two rules keep that honest:

- **Never default `w` or `l`.** A device whose size is absent from the drawing is a failure, not
  a device at its model default — the default is exactly the drift being looked for. Only a
  no-op count may be defaulted (`m`, `ng`, `nf` → 1; the SG13G2 poly resistor's bend count
  `b` → 0), and only to the value the model library itself declares.
- **Join on the name set first.** The failure mode here is "matched fine, parameters gone", so a
  device present on one side only has to be its own finding rather than something the join
  quietly drops.

**Where it lives.** `experiments/004-schematic/build_sch.py::check_parameters`, run on every
build and re-runnable against any drawing with `--check-sch`. The step now **exits non-zero** on
a skipped device, a vacuous or failed equivalence, or one drifted parameter.

**Update, 2026-09-05.** Both gaps below are fixed upstream (`spicexplorer-platform @1775a67`): a
two-terminal PDK primitive now resolves to its own PDK symbol, and a braced value now survives the
attribute round trip. The parameter assertion reads **114 of 114 rows green** on the schematic of
record, with `VREF` at 0.6 V. The rule above is unchanged, and so is the corollary at the end.

**Two platform gaps it found, both siblings of the resistor bug**
(`prefix-precedence-drops-drawable-devices.md`), both since FIXED upstream:

1. **A 2-node PDK primitive shipped as a subckt loses its size.** `cap_cmim` has exactly two
   nets, so the prefix test in `spicexplorer_netlist2xschem/ingest.py` succeeds and the instance
   is typed `CAP` — it never reaches the subcircuit fallback that rescued the 3-node `rhigh`.
   `mapping._GENERIC_SYMREF[CAP]` then picks `devices/capa.sym`, whose `format` is
   `@name @pinlist @value m=@m`, and `emit._device_attrs`'s two-terminal branch writes only
   `value` + `m`. The PDK ships `sg13g2_pr/cap_cmim.sym` with
   `format="@spiceprefix@name @pinlist @model w=@w l=@l m=@m"` — the same shape as `rhigh.sym`
   minus the `body` — but there is no `_PDK_SUBCKT_SYMREF`-style entry for it, and the lookup is
   keyed on `DeviceKind.SUBCKT` only. The fix is a model-keyed symbol lookup for two-terminal
   kinds too, not a new symbol.
2. **A braced expression cannot survive a quoted xschem attribute.** `emit._fmt_value` quotes any
   value containing a space, so `dc {vref_val}` is written as `value="dc {vref_val}"`. xschem's
   own tokenizer treats `{}` as its attribute delimiters, trips on the brace inside the quotes
   (`SKIPPING |"}|` on stderr, exit status still 0) and falls back to the `vsource.sym` template
   default — which is `value=3`. `VLP`'s `dc 0` has no braces and round-trips fine. Any source
   whose value is a `.param` expression is affected.

**Corollary for the claim.** With a parameter check in place the honest statement is that the
drawing **cannot drift unnoticed**, not that it cannot drift: the netlist stays the design of
record, and the drawing is evidence only for as long as the check is green.
