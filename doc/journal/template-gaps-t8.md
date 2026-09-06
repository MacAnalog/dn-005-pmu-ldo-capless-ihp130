# 2026-09-04 — template gaps hit while instantiating ldo-ihp130 (T8)

KIND: journal entry | type: procedural | status: live

Each item is a place the template made an agent work harder than it should; the fix that
belongs in `agentic-design-template` (or the platform) is named. Procedural writes — proposed,
not self-applied.

1. **`uv sync` fails on transitive platform members.** From outside the platform's uv
   workspace, `[tool.uv.sources]` paths are applied only to packages the root project names
   directly; `spicexplorer-analog-db → spicexplorer-circuitgraph` was "not found in the
   registry" until circuitgraph/netlist2xschem/waveview were added to `dependencies` as well.
   Fix: the template `pyproject.toml` should carry the full member list commented out, with
   this note.
2. **`spec_sync` tokens force unit-scaled keys.** The lint matches `f"{bound:g}"` literally in
   `doc/target-spec.md`; a bound of `1e-4` A would have to appear as `0.0001`. Fix: either
   let `spec:` rows carry a `scale`/display, or document "keys are unit-scaled" in the
   template's `harness.yaml` comment (done here).
3. **Class-template comments leak vendor names into assembled decks.** The analog-db
   `ldo/ac_loopgain` template header names a proprietary simulator's probe element; frozen
   verbatim, the deck fails the denylist. `lab.dut.Design.deck()` drops comment lines. Fix:
   analog-db templates should keep vendor names out of headers, or `assemble()` should offer
   `comments=False`.
4. **The wrapper wants a `*` title line first.** `NGSpice_Wrapper`'s editor raises
   `Expected pattern "^\*"` on a deck that starts with `.title`. Fix: document it in the
   template's `lab/sim.py` docstring (done here) or have the wrapper accept `.title`.
5. **`batch()` argument order is `(items, fn)` and the env kwarg is `env=`,** not
   `(fn, items, jobs_env=)` as the CLAUDE.md hint reads. Fix: template `lab/metrics.py` stub
   should show one real call.
6. **The experiment-log lint wants the directory name verbatim** (`001-reference`), not the
   number; the template's log header does not say so. Fix: a sample row in the template log.
7. **`experiments/_template/README.md` rows are `**Paper(s)**`/`**Hypothesis**`/`**Verdict**`
   bolded cells** — a table with those as row labels passes; a heading does not. Documented
   nowhere. Fix: say so in the template README.
8. **No analog-db LDO binding at the target conditions** (see
   `reference-is-not-at-the-target-point.md`): the template assumes a reference exists at the
   challenge's point. Fix: the template's certification step should say what to do when the
   only reference is off-point (certify as committed, split the spec table into quotable /
   literature-set rows).
9. **`make doctor` ok-criterion.** The template stub returns `ok` on lane presence; a parsed
   scalar from the log is the only honest criterion (ngspice exits 0 on a failed `.op`).
   Done here; the template stub should say it.

10. **`netlist2xschem` drops the size of a 2-node PDK primitive shipped as a subckt.**
    `XCFF a b cap_cmim w=.. l=..` has exactly two nets, so the prefix test types it `CAP` and it
    never reaches the subcircuit fallback that rescued the 3-node `rhigh`; it is then drawn with
    `devices/capa.sym` (`format="@name @pinlist @value m=@m"`) and `w`/`l` are gone. The PDK ships
    `sg13g2_pr/cap_cmim.sym` with the `rhigh` shape minus `body`. Fix: key the PDK symbol lookup on
    the model name for two-terminal kinds too, not only on `DeviceKind.SUBCKT`.
11. **A `.param` expression cannot ride in a quoted xschem attribute.** `dc {vref_val}` is emitted
    as `value="dc {vref_val}"`; xschem's tokenizer treats `{}` as its own delimiters, drops the
    attribute (`SKIPPING |"}|`, exit 0) and falls back to the symbol template's `value=3`. Fix:
    emit braced expressions unquoted, or escape them the way xschem's own writer does.

Generic code written here that belongs in the platform: `lab/sim.py` (deck text →
`NGSpice_Wrapper` with per-run dirs, fatal-string scan, `parse_measures`), `lab/dut.py`
(`Design` = analog-db binding + shadowing `.param` overrides, comment-stripped `assemble()`),
`lab/metrics.py::promote/KEYMAP` (measure → unit-scaled key) and `--certify/--check`.
