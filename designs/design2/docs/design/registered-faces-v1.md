# Registered Poker faces

The 18 approved court, ace, and Joker masters now have finished 750 × 1050
RGBA exports at 300 ppi. Together with the existing 36 numerals, they form
a complete 54-face Poker deck.

Every export uses the existing numeral frame and silhouette. The compositor
maps the painted central turquoise stone to `(374.5, 524.5)`, replaces the
generated outside border with the shared frame, and rebuilds the opposing
indices inside the same panels. Border pixels outside the central field and
index panels are identical to the number cards of the matching color.

The twelve courts and two Jokers use a continuous upper half rotated around
that center to form the lower half. They are exactly equal under a 180-degree
turn. The four aces preserve their upright suit silhouettes; their central
stone centroids are within 0.011 pixels of the same anchor after resampling.
The 36 numeral faces, 30 backs, and 12 blank frames were preserved.

Original generated artwork is unchanged under `sources/generated/` and remains
available in the source-master gallery. Use `cards/faces/french-suited/poker/`
for the balanced finished deck.

From the Design 2 folder:

```text
python scripts/register_face_masters.py
python scripts/register_face_masters.py --check
python scripts/register_face_masters.py --apply
python scripts/register_face_masters.py --check --active
```

`registered-faces-v1.json` records source/output hashes, measured anchors, and
frame provenance. `registered-faces-v1-audit.json` checks saved pixels, shared
borders, centers, opposing indices, density, alpha, and half-turn symmetry.
The reproducible staging proof sheets are in `work/registered-faces-v1/`.
