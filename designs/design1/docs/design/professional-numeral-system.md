# Professional numeral-face system

**Current implementation:** [Deck rebuild v1](deck-rebuild-v1.md) and
[the exact layout manifest](numeral-layout-v1.json) supersede the historical
rules below, including RGB-only output, rounded aggregate centering, and
suit-specific optical position changes. All 52 faces and 30 backs have been
rebuilt from shared geometry and components.

## Historical pre-rebuild standard

This is the production standard for the French-suited poker numerals in this
deck. It describes a consistent visual language, not a claim that every
manufacturer uses identical dimensions or pip coordinates.

## Non-negotiable invariants

- Canvas: 750 × 1050 px, RGB, 300 dpi.
- The outer botanical perimeter, inner gold rules, and both corner cartouches
  are fixed artwork. They are not to be regenerated, scaled, or repositioned
  while a numeral face is being registered.
- The decorative inner rule immediately below the top botanical frame is an
  intentional part of that frame; it is not a duplicate pip or an artifact.
- Each rank has exactly as many central suit pips as its value.
- The chroma-weighted mean of the turquoise pip-jewel centers is the deck's
  layout anchor. Every numeral face is registered to `(375, 525)`.
- Pips remain the existing illustrated suit motifs. Registration uses only
  whole-pixel placement; it must not redraw, stretch, blur, or recolor them.

## Rank topology

The topology, rather than an arbitrary percentage grid, is what makes a
numeral card immediately legible. Coordinates may be optically tuned for the
different footprints of the ornate spade, heart, diamond, and club motifs,
provided the overall anchor remains fixed.

| Rank | Layout topology | Rotational policy |
| --- | --- | --- |
| 2 | Two pips on the center column | Two-way |
| 3 | Two on the center column plus a central pip | Intentionally one-way for directional suits |
| 4 | Two upper and two lower side pips | Two-way |
| 5 | Four corners plus a central pip | Intentionally one-way for directional suits |
| 6 | Two columns of three | May be one-way when the midline pips are upright |
| 7 | Two upper sides, one upper-center, two lower-mid sides, two lower sides | Intentionally one-way; spacing is optically balanced around the common anchor |
| 8 | Two columns of four | Two-way in this deck |
| 9 | Three rows of three | Intentionally one-way for directional suits |
| 10 | Four side rows plus an upper/lower center pair | Two-way |

"Two-way" means exact 180-degree rotational correspondence of both pip
location and orientation. It does not imply mirror symmetry across a vertical
or horizontal axis. One-way numeral faces are a deliberate traditional choice,
not a defect, but their asymmetry must be balanced around the shared layout
anchor.

## Professional acceptance checks

1. Confirm one clean botanical top frame and one clean inner gold rule; do not
   mistake the latter for a duplicated image.
2. Confirm the two rank/suit cartouches remain upright at top-left and rotated
   180 degrees at bottom-right.
3. Confirm the pip count, rank topology, and intended orientations.
4. Confirm the shared layout anchor is `(375, 525)`.
5. Confirm the border-mask pixels are byte-identical to the numeral template.
6. Inspect full size and at print-scale for accidental doubled edges, seams,
   repeated rows, clipping, or unwanted interpolation.

The machine-verifiable centering and border procedure is implemented in
[`scripts/rebalance_numerals.py`](../../scripts/rebalance_numerals.py). Its
preserved originals and repair hashes provide the audit trail for the current
faces.

For the complete explanation of the existing implementation, its limitations,
the Club Three orientation failure, and the recommended component-based rebuild,
see [numeral-rebuild-handoff.md](numeral-rebuild-handoff.md).
