"""The case `review-002` **M8** asked for: a collision that only `stub_clear` prevents.

M8: "The Metal1 short reproduces only when *both* committed changes are reverted. Reverting
`stub_clear` alone (leaving the two-directional column search) still gives 0 rule violations and a
matched netlist at the record sizing. So no committed sizing exercises the obstacle map ... a
regression that no case exercises will rot."

These tests build the collision by hand, so it does not depend on a sizing point ever producing
it. They import `layout/router.py` only — no gdsfactory, so they run in the repo venv under
`make test`.

Run them directly (``uv run --no-sync python layout/test_builder.py``) or under pytest; the
sign-off driver runs them as its first, blocking stage, so the guard is exercised every round.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from router import ObstacleMap  # noqa: E402

Y = 4.0          # the y two neighbouring devices share for their gate bars
GATE_BAR = 0.5   # gate-bar height


def _map_with_a_neighbours_gate_bar() -> ObstacleMap:
    """`vref`'s terminal is at x = 3.0, its own column is taken by `ea_n`, and `fb`'s gate bar
    occupies x in [1.2, 2.6] at the same y -- i.e. the preferred direction of the walk.

    The *column* check accepts x = 2.4 (no Metal2 there); only the Metal1 stub the walk would drag
    across the gate bar can refuse it. This is the LDO 005 failure exactly: a 50 nm length change
    in another row pushed XM2's gate stub through XM1's gate bar, and DRC reported 0 violations on
    a shorted netlist.
    """
    m = ObstacleMap()
    m.m1_claim("fb", Y, 1.2, 2.6, GATE_BAR)
    m.verticals.append(("ea_n", 3.0, 0.0, 10.0))   # the terminal's own column is busy
    return m


def test_stub_clear_refuses_a_stub_that_crosses_a_foreign_gate_bar():
    m = _map_with_a_neighbours_gate_bar()
    assert m.stub_clear("vref", Y, 3.0, 3.0)          # no walk: nothing crossed
    assert not m.stub_clear("vref", Y, 3.0, 2.4)      # walks INTO the bar
    assert not m.stub_clear("vref", Y, 3.0, 0.6)      # walks straight THROUGH it
    assert m.stub_clear("fb", Y, 3.0, 0.6)            # same net: a merge, not a short
    assert m.stub_clear("vref", Y + 1.2, 3.0, 0.6)    # a different row is not blocked


def test_alloc_turns_round_instead_of_marching_into_the_neighbour():
    """With the preferred direction blocked by Metal1 only, `alloc` must come back the other way."""
    m = _map_with_a_neighbours_gate_bar()
    x = m.alloc("vref", 3.0, Y, 10.0, step=-0.6)      # preferred direction is LEFT, into `fb`
    assert x > 2.6 + 0.28, f"alloc returned {x}: the stub would cross fb's gate bar"
    assert x != 3.0, "x = 3.0 is taken by ea_n's Metal2 column"
    assert m.stub_clear("vref", Y, 3.0, x)


def test_without_stub_clear_the_allocator_would_short_the_two_nets():
    """The regression itself: with the Metal1 check disabled, the same call returns a column whose
    stub lands on `fb` -- a short DRC cannot see, because the two Metal1 shapes merge."""
    m = _map_with_a_neighbours_gate_bar()
    m.stub_clear = lambda *a, **k: True  # type: ignore[method-assign]
    x = m.alloc("vref", 3.0, Y, 10.0, step=-0.6)
    assert abs(x - 2.4) < 1e-9, "the unguarded walk should take the first free Metal2 column"
    assert not _map_with_a_neighbours_gate_bar().stub_clear("vref", Y, 3.0, x)


def test_column_free_still_keeps_two_nets_off_one_metal2_column():
    m = ObstacleMap()
    m.verticals.append(("fb", 3.0, 0.0, 10.0))
    assert not m.column_free("vref", 3.0, 4.0, 6.0)
    assert not m.column_free("vref", 3.4, 4.0, 6.0)   # inside the 0.6 um pad+space pitch
    assert m.column_free("vref", 3.6, 4.0, 6.0)
    assert m.column_free("fb", 3.0, 4.0, 6.0)         # same net shares its own column
    assert m.column_free("vref", 3.0, 20.0, 30.0)     # no y overlap


def test_alloc_raises_with_a_hint_when_nothing_fits():
    m = ObstacleMap()
    m.m1_claim("fb", Y, -100.0, 100.0, GATE_BAR)
    try:
        m.alloc("vref", 0.0, Y, 10.0)
    except AssertionError as exc:
        assert "widen dev_gap" in str(exc)
    else:
        raise AssertionError("alloc should have refused every column")


def main() -> int:
    fails = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
            print(f"  ok   {name}")
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"  FAIL {name}: {type(exc).__name__}: {exc}")
    print(f"{'FAILED' if fails else 'passed'}: {fails} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
