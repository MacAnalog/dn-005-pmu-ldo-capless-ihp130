"""003 — the figures. Every one is regenerated from the JSON the runs wrote, with the spec bound
drawn on it (`.claude/skills/findings-as-plots`): a number in prose is a claim, a number on a
plot with its box is a finding.

    uv run --no-sync python experiments/003-sizing/figs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT, FIGS = HERE / "out", HERE / "figs"
FIGS.mkdir(parents=True, exist_ok=True)

CORNERS = ("tt", "ss", "ff", "sf", "fs")
TEMPS = (-40, 27, 125)
MARK = {"tt": "o", "ss": "s", "ff": "^", "sf": "D", "fs": "v"}


def _style(ax, title: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.tick_params(labelsize=8)


def corner_figs() -> None:
    d = json.loads((OUT / "corners.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    for ax, (key, bound, label, unit) in zip(axes, [
            ("i_q_ua", 50, "S5 quiescent current", "µA"),
            ("v_undershoot_mv", 150, "S7 load-step undershoot", "mV"),
            ("pm_loop_deg", 60, "S8 loop phase margin (1 mA)", "deg")]):
        for c in CORNERS:
            ys = [d[f"{c} {t:g} C"][key] for t in TEMPS]
            ax.plot(TEMPS, ys, marker=MARK[c], label=c, linewidth=1.4, markersize=5)
        ax.axhline(bound, color="crimson", linestyle="--", linewidth=1.4)
        lo, hi = ax.get_ylim()
        if key == "pm_loop_deg":      # >= bound: shade below
            ax.axhspan(lo, bound, color="crimson", alpha=0.08)
        else:                          # <= bound: shade above
            ax.axhspan(bound, max(hi, bound * 1.05), color="crimson", alpha=0.08)
        ax.annotate(f"spec {'≥' if key == 'pm_loop_deg' else '≤'} {bound} {unit}",
                    (TEMPS[0], bound), textcoords="offset points", xytext=(2, 4),
                    color="crimson", fontsize=8)
        _style(ax, label, f"{key} ({unit})")
        ax.set_xlabel("temperature (°C)", fontsize=9)
        ax.set_xticks(TEMPS)
    axes[0].legend(fontsize=8, ncol=5, loc="upper left", frameon=False)
    fig.suptitle("003 — design of record over 5 MOS corners × −40/27/125 °C  "
                 "(S5 binds at ff/125, S7 at ss/−40; S8 never binds)", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIGS / "corners.png", dpi=150)
    print("wrote", FIGS / "corners.png")


def cliff_fig() -> None:
    """The c_ff_w sweep of README §2 — the cliff, and what the optimizer could see instead."""
    w = [3, 4, 5, 6, 7, 8, 8.5, 9, 9.2, 9.4, 9.5, 10, 11, 12]
    under = [112.20, 96.81, 98.93, 101.04, 103.05, 104.85, 105.67, 106.44, 106.73, 107.02,
             201.26, 225.31, 221.85, 252.57]
    pm = [62.09, 63.75, 65.76, 68.00, 70.30, 72.42, 73.33, 74.09, 74.34, 74.50, 74.57, 74.76,
          74.14, 72.22]
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.plot(w, under, marker="o", color="#1f77b4", linewidth=1.6, label="S7 undershoot (mV)")
    ax.axhline(150, color="crimson", linestyle="--", linewidth=1.4)
    ax.axhspan(150, 270, color="crimson", alpha=0.08)
    ax.annotate("spec ≤ 150 mV", (3.1, 152), color="crimson", fontsize=8)
    ax.axvspan(9.4, 9.5, color="black", alpha=0.10)
    ax.annotate("cliff\n9.4 → 9.5 µm", (9.45, 165), ha="center", fontsize=8)
    ax.annotate("optimizer's winner\n(9.415 µm)", (9.415, 107), textcoords="offset points",
                xytext=(-70, -28), fontsize=8,
                arrowprops=dict(arrowstyle="->", linewidth=0.9))
    ax.annotate("design of record\n(8 µm, 19 % margin)", (8, 104.85), textcoords="offset points",
                xytext=(-30, -42), fontsize=8, color="darkgreen",
                arrowprops=dict(arrowstyle="->", linewidth=0.9, color="darkgreen"))
    _style(ax, "003 §2 — the feed-forward MIM cliff the optimizer could not see",
           "v_undershoot_mv")
    ax.set_xlabel("c_ff_w, feed-forward MIM side (µm)", fontsize=9)
    ax2 = ax.twinx()
    ax2.plot(w, pm, marker="s", color="#999999", linewidth=1.2, markersize=4,
             label="S8 phase margin (deg)")
    ax2.set_ylabel("pm_loop_deg (smooth through the cliff)", fontsize=8, color="#666666")
    ax2.tick_params(labelsize=8, colors="#666666")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(FIGS / "cff_cliff.png", dpi=150)
    print("wrote", FIGS / "cff_cliff.png")


def points_fig() -> None:
    """reference → control → record, each spec as a fraction of its bound (1.0 = at the limit)."""
    rows = json.loads((OUT / "points_all.md").with_suffix(".json").read_text())
    names = list(rows)
    specs = [("i_q_ua", 50, "S5 Iq"), ("load_reg_mv", 5, "S2 load reg"),
             ("line_reg_mv", 2, "S3 line reg"), ("v_dropout_mv", 200, "S4 dropout"),
             ("v_undershoot_mv", 150, "S7 undershoot")]
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    width = 0.8 / len(names)
    for i, nm in enumerate(names):
        vals = [(rows[nm][k] or 0) / b for k, b, _ in specs]
        ax.bar([x + i * width for x in range(len(specs))], vals, width, label=nm[:42])
    ax.axhline(1.0, color="crimson", linestyle="--", linewidth=1.4)
    ax.annotate("spec bound", (-0.4, 1.03), color="crimson", fontsize=8)
    ax.set_xticks([x + 0.4 - width / 2 for x in range(len(specs))])
    ax.set_xticklabels([s[2] for s in specs], fontsize=8)
    _style(ax, "003 §1 — every 'lower is better' spec as a fraction of its bound (tt / 27 °C)",
           "measured / bound")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIGS / "points.png", dpi=150)
    print("wrote", FIGS / "points.png")


if __name__ == "__main__":
    corner_figs()
    cliff_fig()
    try:
        points_fig()
    except Exception as exc:  # noqa: BLE001
        print("points_fig skipped:", exc, file=sys.stderr)
