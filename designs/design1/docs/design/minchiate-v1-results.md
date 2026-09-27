# Design 1 Minchiate release

The active Tarot-size set now contains all 97 Minchiate faces: 40 suit pips,
16 courts, 40 trumps, and the separate unnumbered Fool. All are 825 × 1425
RGBA PNGs at nominal 300 ppi with the existing frame and rounded silhouette.

Forty-three new subject illustrations are composed with the retained suit
assets and four explicitly selected trump illustrations. The four Cavaliers
use hybrid human/horse figures; Cups and Coins use female Maids. Swords and
Batons use crossed straight pips with explicit, counted placements.

The Hanged Man retains the existing upside-down Tarot illustration following
the user's 2026-09-27 selection. This is a documented exception to historical
Minchiate iconography. Trumps I–XXXV use Roman indices, and the Fool and five
Arie have no printed number. Numeric filenames encode inventory order only.

All 97 rendered cards were visually inspected on the complete proof sheets.
The saved-PNG audit verifies exact rerendered pixels, dimensions, density,
RGBA mode, hashes, pip-instance counts, full inventory, artwork containment,
index containment, and title-band clearance. See `minchiate-v1-report.json`.
Reproduce and check with `scripts/render_minchiate.py` from the design folder.

The complete original 78-card release is preserved byte-for-byte with a hash
manifest and its original deck definition in `sources/before-minchiate-v1/`.
The collection migration checker validates both that archive and the current
replacement inventory. Historical Tarot reports remain historical records.

New illustration sources and the built-in image-generation prompts are saved
in `sources/generated/minchiate-v1/`; prepared components and their hashes are
in `sources/components/tarot/minchiate-v1/` and `minchiate-layout-v1.json`.
The completion prompts are in `completion-prompts.json`, `cavalier-prompts.json`,
and the existing `revised-trump-prompts.json` in the generated-source directory.

The catalogs and static galleries include 97 faces and five backs in Tarot
size. Release v1.2 packaging contains 102 native PNGs and 204 print variants.
