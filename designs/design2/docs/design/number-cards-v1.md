# Design 2 number cards

All 36 Poker number cards, ranks 2 through 10 in four suits, are composed and
saved under `cards/faces/french-suited/poker/<suit>/<rank>.png`.
Each is 750 × 1050 RGBA at nominal 300 DPI, with the existing rounded silhouette.

[Browse and turn the cards](../../number-cards.html) ·
[Spades preview](number-cards-v1-spades.jpg) ·
[Hearts preview](number-cards-v1-hearts.jpg) ·
[Diamonds preview](number-cards-v1-diamonds.jpg) ·
[Clubs preview](number-cards-v1-clubs.jpg)

## Artwork and spacing

The existing transparent lotus pips are uniformly resized and registered by
their turquoise jewel. Very faint or disconnected exterior alpha is removed
from derived components; original masters are preserved. The artwork is not
regenerated, recolored or redrawn, and each rank uses one repeated component
per suit. More crowded ranks use smaller pips.

The approved open frame leaves a plain antique-white center. Ornament stays
in the outer lotus band, with opposing serif rank/suit indices. All pip ink
fits inside the verified 510 × 830 pixel clear layout rectangle, with no
overlapping symbols. Black suits use Lamp Black; red suits use Madder Lake.

## Reversibility

- Ranks 2, 4, 6, 8 and 10 are pixel-identical under a 180-degree rotation,
  including their frames, indices and pips: 20 exactly reversible cards.
- Ranks 3, 5, 7 and 9 have paired surrounding pips and one upright center pip.
  Only that central pip differs after rotation: 16 center-only exceptions.
- On a center row, the left outer pip is upright and the right outer pip is
  inverted, so they exchange exactly under a half-turn.
- Seven uses a centered 2–3–2 arrangement rather than an offset seventh pip.
  Nine uses a balanced 3 × 3 arrangement. Eight has four rows of two; ten
  adds two staggered center-column pips to that arrangement.

These choices prioritize the user's request for symmetry wherever possible
while keeping each suit emblem intact. A directional center pip is not
distorted or duplicated to force an odd card into exact rotational symmetry.

## Files and verification

[The manifest](number-cards-v1.json) records every component, anchor, scale
bound, placement, rotation, source hash and output hash. Prepared pip and index
rasters live in `sources/components/number-cards-v1/`. The indices use Times
New Roman Bold, rasterized once; the font file is not distributed.

[The audit](number-cards-v1-audit.json) counts visible connected pip silhouettes
in saved card pixels independently of the layout metadata. It also checks
nonoverlap, field and index containment, unchanged perimeter pixels, exact
alpha, dimensions, DPI, paired positions, source hashes and full-image
half-turn comparisons. All pre-existing Design 2 image hashes are preserved.
Four suit sheets and the full-size ten of Spades were visually inspected.

From the repository root:

```text
python designs/design2/scripts/build_number_cards.py
python designs/design2/scripts/build_number_cards.py --apply
python designs/design2/scripts/audit_number_cards.py --active
python scripts/catalog.py --check
```

The default build stages files and review sheets. `--apply` audits before
installation and refuses to replace different existing artwork. The reusable
frame templates support other sizes; this release contains the 36 Poker faces.
