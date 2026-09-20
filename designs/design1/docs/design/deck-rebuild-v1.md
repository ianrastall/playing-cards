# Deck rebuild v1

**Follow-up:** [Poker completion v2](poker-completion-v2.md) replaces the back
cartouches with a dedicated panel-free template, adds both Jokers, and builds
the poker release/print variants. This page preserves the initial rebuild design.

Implemented 2026-09-17 for all **52 poker faces and 30 backs**. This replaces
the earlier rounded-centroid registration system. The original 82 images,
catalog, configuration, and SHA-256 inventory are preserved under
`sources/before-deck-rebuild-v1/`.

## Fixed geometry

- Poker: 750 x 1050 pixels, nominal 300 dpi, 2.5 x 3.5 inch trim.
- Exact center: (374.5, 524.5), using zero-based pixel-center coordinates.
  This is (375, 525) measured from the outside edges of the canvas.
- Other formats keep the dimensions in `deck.json`; their anchors are
  `((width-1)/2, (height-1)/2)`.
- Antique-white ground: RGB (250, 235, 215), `#FAEBD7`.
- Outer corner radius: 3.5 mm, or approximately 41.3386 pixels at 300 dpi.
  One deterministic antialiased alpha mask is reused per format.
- Active exports are **RGBA**, superseding the previous RGB-only convention.
  The rounded silhouette is in the file. Consumers must preserve alpha and
  must not add a separate CSS corner radius or crop the image independently.

The illustrated court and back fields retain their painted ivory ornaments.
The shared card ground, outer margins, and index-panel ground use antique white.

## Artwork and assembly

The built-in image-generation tool produced four transparent suit masters and
two frame components. The exact prompts are in
`sources/generated/deck-rebuild-v1/prompts.json`; all generated masters are
saved alongside it. No external image API was used.

A generated frame quarter is reused by reflection to form a centered,
seam-continuous perimeter. One extracted generated cartouche supplies both
opposing panels. The resulting frame is pixel-identical under a half-turn.
Every face and back of a format uses the same frame pixels, excluding only
the variable index/medallion ink. Other formats derive their shared frame once
from the poker component and apply their own physical corner mask.

The four suit masters are sized and registered once for each rank. Final
assembly uses integer translations and exact 180-degree sprite rotations.
The central turquoise jewel is an extracted reusable component with reciprocal
illumination; replacing its translucent interpolation fringe prevents the
underlying artwork from shifting the measured centroid. The measured jewel
centers equal their manifest coordinates to within numerical precision.

The original court portraits remain the source illustrations. Their inner
fields are fitted vertically around the fixed center to exclude the legacy
bottom gold rule, then receive the shared jewel, frame, and indices. The
portraits themselves retain the original independently painted opposing poses;
the court illustrations are not claimed to be pixel-exact half-turn repeats.

Each back uses its preserved Prussian Blue source, registered around its red
central bead and enlarged 2.5% to keep its former frame out of the new aperture.
The lower pattern is the exact half-turn of the upper. The existing palette
recipes supply the five color variants. Former index panels carry small floral
medallions on backs. All 30 completed backs are pixel-exact under a half-turn.

## Numeral system

The executable specification is [numeral-layout-v1.json](numeral-layout-v1.json).
It contains individual coordinates, angles, component bounds, anchors, and
component hashes for every suit and rank from Ace through Ten.

| Rank | Layout | Reversibility |
| --- | --- | --- |
| Ace | One central emblem | One-way |
| 2 | Center-column upper/lower pair | Exact half-turn |
| 3 | Center-column upper/center/lower | One-way center pip |
| 4 | Two upper and two lower side pips | Exact half-turn |
| 5 | Four outer pips and center | One-way center pip |
| 6 | Two columns of three; opposite midline rotations | Exact half-turn |
| 7 | Six side pips and one offset upper-center pip | Intentionally one-way |
| 8 | Two columns of four | Exact half-turn |
| 9 | Three-by-three, opposite outer midline rotations | One-way center pip |
| 10 | Four side rows and upper/lower center pair | Exact half-turn |

Seven retains the traditional offset pip. Its arithmetic mean is intentionally
above the card center; the common canvas/frame anchor remains fixed. No hidden
whole-card translation is used to force that mean to the center.

## Reproduce and verify

With the existing Pillow and NumPy requirements installed:

```text
python scripts/rebuild_deck.py --stage
python scripts/rebuild_deck.py --check
python -m unittest discover -s scripts -p test_rebuild_deck.py
python scripts/rebuild_deck.py --apply
python scripts/rebuild_deck.py --check --active
python scripts/catalog.py --check
```

`--stage` uses the saved components; it does not call image generation.
`--prepare` rebuilds components from the saved generated masters and rasterizes
indices using Windows Times New Roman Bold. Normal rendering uses the saved
index rasters and has no system-font dependency. Use a new version directory
for future artwork revisions instead of overwriting these approved components.

Validation checks dimensions, alpha masks, shared frame pixels including
cartouche contours, containment of index ink, exact per-pip jewel locations,
pip count, overlap/clipping, source component hashes, exact counterpart pixels,
and full-card half-turn equality for two-way numeral ranks and all backs.
It also reproduces each output and checks equality with its expected pixels.
The machine report is [deck-rebuild-v1-report.json](deck-rebuild-v1-report.json).

Visual review covered every rank contact sheet and all 30 backs, with individual
full-resolution checks of representative pips, crowded Tens, Aces, court
portraits, frame joins, and a poker back. Before/after sheets and rank previews
are generated under `work/deck-rebuild-v1/previews/`.

The older alignment/rebalancing scripts document historical workflows and must
not be reapplied to this deck. Their aggregate-centroid rules and assumptions
about original back pixels no longer describe these exports.

These remain trim-size digital artworks, without printer-specific bleed,
imposition, or physical color proofing. For opaque print placement, composite
the alpha over the chosen paper/background color and use catalog trim inches.
