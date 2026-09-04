"""The sizing point. Decks are built from it, never text-edited.

A `Design` is an analog-db circuit binding (circuit id, PDK, corner) plus a dict of sizing-knob
overrides. `deck(bench)` renders one LDO-class bench for it through analog-db's own
`assemble()` -- class template + the circuit's generated lowered netlist + the sizing.yaml
defaults -- and appends the overrides as a `.param` block: a later `.param` shadows the
earlier definition of the same symbol (analog-db's "untying = shadowing" contract), so no
generated line is ever edited. Comment lines are dropped so a frozen deck carries only what
the simulator reads.
"""

from __future__ import annotations

import dataclasses
from functools import lru_cache
from typing import Any

from spicexplorer_analog_db.assemble import assemble
from spicexplorer_analog_db.model import load_circuit

from . import config as C


@lru_cache(maxsize=None)
def circuit(circuit_id: str):
    return load_circuit(circuit_id)


def _strip_comments(text: str) -> str:
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("*")) + "\n"


@dataclasses.dataclass(frozen=True)
class Design:
    circuit: str = C.REF_CIRCUIT
    pdk: str = C.PDK
    corner: str = C.CORNER_NOM
    # (knob, value) pairs in sizing.yaml's own units/syntax ("4.7u", "20", "1k"); a tuple so
    # the dataclass stays hashable and frozen.
    sizing: tuple[tuple[str, str], ...] = ()
    note: str = ""

    @property
    def overrides(self) -> dict[str, str]:
        return dict(self.sizing)

    def with_sizing(self, **knobs: Any) -> "Design":
        merged = {**self.overrides, **{k: str(v) for k, v in knobs.items()}}
        return dataclasses.replace(self, sizing=tuple(sorted(merged.items())))

    def benches(self) -> list[str]:
        """The circuit's declared analyses, in analog-db's order."""
        return list(circuit(self.circuit).analyses)

    def knobs(self) -> dict[str, str]:
        """Every sizing knob with its effective value (defaults + overrides)."""
        base = {v["name"]: str(v["default"])
                for v in circuit(self.circuit).sizing(self.pdk).get("variables", [])}
        unknown = set(self.overrides) - set(base)
        if unknown:
            raise KeyError(f"{self.circuit}/{self.pdk}: unknown sizing knob(s) {sorted(unknown)}")
        base.update(self.overrides)
        return base

    def deck(self, bench: str) -> str:
        """The complete runnable deck for one bench of this sizing point."""
        self.knobs()  # validate override names before rendering
        text = _strip_comments(assemble(circuit(self.circuit), bench, self.pdk, self.corner))
        body = text.rstrip()
        assert body.endswith(".end"), "assemble() contract: the deck ends with .end"
        head = body[: -len(".end")]
        over = "".join(f".param {k}={v}\n" for k, v in self.sizing)
        return (f"* {self.circuit} x {bench} x {self.pdk} x {self.corner} -- built by lab.dut.Design\n"
                + head + over + ".end\n")

    def as_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["sizing"] = self.overrides
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Design":
        return cls(circuit=d["circuit"], pdk=d["pdk"], corner=d.get("corner", C.CORNER_NOM),
                   sizing=tuple(sorted((k, str(v)) for k, v in (d.get("sizing") or {}).items())),
                   note=d.get("note", ""))


REFERENCE = Design(note="analog-db ldo_005_buffered_ref, committed IHP sizing, as certified")
