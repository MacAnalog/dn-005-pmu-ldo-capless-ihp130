# 2026-09-04 — an unused placeholder still has to bind, and a lint that guards one frozen dir guards one frozen dir

KIND: journal entry | type: procedural | status: live

**Observation.** Review-002 m5 said `VOUT_THRESH: 1.14` in the candidate's `analyses/dropout.yaml`
was a declared bench condition the bench ignores — true — and it was deleted. That made
`ldo.dut.Design.deck()` raise `AssembleError: unresolved placeholders ['VOUT_THRESH']` for
**every** candidate bench, so `decks/candidate/` could no longer be rebuilt or re-certified at
all. Nobody noticed for a whole review round.

Two independent reasons.

1. **A placeholder in a comment is still a placeholder.** The LDO class dropout template kept
   `${VOUT_THRESH}` in its `**` header, explaining why the legacy threshold criterion was wrong,
   and analog-db's `assemble()` scans the *rendered* text — comments included — before this
   repo's builder strips them. A parameter the bench genuinely ignores still has to be bound.
2. **`deck_rebuild` only looked at `decks/reference/`.** The one lint that would have caught it
   was hard-coded to a single frozen dir while `harness.yaml` declares two, so the reference
   stayed green through a candidate that could not be built.

**Rule.** A repo invariant is written over the *set* the config declares (`frozen:`), never over
one member of it. And when a review says "remove it or wire it through", removing it is only the
cheaper option if you rebuild the artefact afterwards — deletion is a change to the build.

**Fixed here.** The binding is restored with the reason written beside it (the fix that removes
it for good belongs in the analog-db template), and `scripts/lint.py::deck_rebuild` now iterates
`L.h.frozen`. `certify()` also builds every deck *before* unlinking the old ones, so a builder
that raises half way through can no longer leave a frozen dir short of benches.
