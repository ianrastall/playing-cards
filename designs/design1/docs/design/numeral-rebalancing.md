# Poker numerals — geometric rebalancing

The 32 poker numeral faces from two through nine were rebalanced on September 16, 2026. Tens, aces, courts, and every card back were already registered and were deliberately left unchanged.

## Registration anchor

Every ornate center pip includes a turquoise jewel. For each numeral card, the chroma-weighted centroids of all its pip jewels are averaged; this gives one layout anchor even when the rank has no single center pip. The target is pixel `(375, 525)` on the 750 × 1050 canvas, using zero-based x/y coordinates.

Each card's central artwork received only an exact whole-pixel translation. There was no generation, redrawing, scaling, interpolation, or pip modification. The final verification finds every one of the 32 layout anchors at `(375, 525)`.

## September 16 repair

The first registered export used a wrapping translation and could carry a narrow strip of bottom-edge artwork into the top of cards with a downward offset. That pass was replaced from the preserved originals with a non-wrapping integer translation: newly exposed strips remain their original pixels, and both corner cartouches remain fixed. This removes the duplicated top-edge artifact without altering the card artwork, pips, or the shared perimeter. The repair's independently checked hashes and offsets are in [numeral-rebalancing-repair.json](numeral-rebalancing-repair.json).

## Perimeter

The existing [Ten of Spades](../../cards/faces/french-suited/poker/spades/10.png) supplies the common numeral perimeter. Under the established border mask, the outer ivory edge, gold beading, dark botanical surround, and interior boundary are byte-identical across all 32 cards. The card-specific corner cartouches remain protected, retaining their own rank and suit indices.

## Preservation and checks

- Originals are retained at `sources/before-numeral-rebalancing/poker/<suit>/<rank>.png`.
- Active artwork outside the shared-border mask is verified as an exact non-wrapping integer translation of its preserved original, with exposed strips retained from that original.
- Active perimeter pixels under the mask are verified as an exact copy of the Ten of Spades template.
- The machine-readable offsets, hashes, candidate paths, and anchor measurements are in [numeral-rebalancing.json](numeral-rebalancing.json).
- `scripts/rebalance_numerals.py` stages and validates the procedure and refuses a repeated application after the report has been recorded.
