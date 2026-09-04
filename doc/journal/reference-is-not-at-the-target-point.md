# 2026-09-04 — the certified reference does not operate at the challenge's point

KIND: journal entry | type: semantic | status: live

`ldo_005_buffered_ref`'s IHP binding is thick-oxide (`sg13_hv_*`) at **3.3 V**, regulates to
**1.6 V**, and every AC/transient bench hangs **1 µF external** on `vout`. The challenge is
1.5 V / 1.2 V / capless on `sg13_lv_*`. Certified as committed (ledger tag `reference_certify`,
`decks/reference/scorecard.json`): load_reg 1.274 mV, line_reg 4.32 mV, i_q 758.7 µA, PSRR
44.53 dB at 1 kHz, PM 46.39°, dropout 169.7 mV at 1 mA, undershoot 1.96 mV into 1 µF.

Consequences: S2/S3/S5/S6/S8 are quotable yardsticks (regulation and loop numbers are set by
loop gain and topology, not by Cout); S4 and S7 are **not** — dropout follows the pass-device
family and undershoot follows Cout, so their bounds come from the literature until a re-based
reference (lv devices, on-chip Cout, own analog-db binding) is certified as experiment 002.
Also: the shadowing probe `vref_val=0.6` moves vout to 1.206 V at 689 µA on the committed
sizing — the circuit regulates at 1.2 V, but that is not a re-base, only the divider.
