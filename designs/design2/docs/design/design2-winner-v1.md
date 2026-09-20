# Design 2 provisional winner: silk backs

Superseded by [revision 2](design2-winner-v2.md), which makes the identifying
border colors more visible at normal card size.

The user selected the final silk prototype with the radial circular center,
accepted its current density, and clarified that the five named colors belong
in the solid ground of the outer floral frame. Tarot is one of six formats.
This version implements that direction as a provisional winner.

## Artwork and exports

- ImageGen masters and exact prompts: `sources/generated/design2-winner-v1/`.
- Thirty native backs: `build/design2-winner-v1/backs/<format>/<color>.png`.
- Comparison/gallery: `build/design2-winner-v1/index.html`.
- Download: `build/design2-winner-v1.zip`.
- Reproducible format export: `node scripts/export_design2_winner.mjs v1`.

The five colors are Prussian Blue, Verdigris, Madder Lake, Manganese Violet,
and Lamp Black. The background behind the outer border flowers carries the
named color. Red/ivory flowers, jade foliage, ochre ornament, and the silk
interior retain their shared palette. The generation tool made the artistic
border changes. Original generated files are retained without modification.

The export uses the Prussian Blue proof's interior for every color, so the
shared interior is exactly identical within each format. Native dimensions
come from `deck.json`: Poker 750 x 1050; Bridge 675 x 1050; European Standard
696 x 1074; Jumbo 1050 x 1500; Travel 525 x 750; Tarot 825 x 1425.

## Geometry and verification

The export registers the border to Design 1's approximate outer/inner edge
positions: x=23/73 and y=16/70 at Poker size, scaled for other formats.
The central roundel is registered at the exact output center and receives
equal horizontal/vertical scaling. Additional format height is distributed
through the upper/lower patterned bands; satellite medallions can therefore
become more oval in Tarot. This is provisional fitting, not a native redraw.
Warm near-white paper/ivory reserves are normalized to antique white #FAEBD7.
Ink edges are feathered rather than thresholded to preserve linework.

Every native output is RGBA, nominal 300 ppi, with exact 180-degree pixel
symmetry. The alpha coverage matches the existing collection's supersampled
3.5 mm corner mask. The master upper half is reused under a half-turn;
odd-height center rows receive reciprocal paired pixels.

Checks passed for all 30 PNGs: lossless save/reload, dimensions, density,
source hash stability, shared interior equality, full half-turn equality,
and an independent comparison against the repository's existing corner-mask
implementation. Native Poker, Travel, and Tarot samples were visually checked.
`manifest.json` in the export records all output and source hashes.

This is a separate provisional Design 2 back set. It does not replace Design 1,
change its active catalog, or alter the completed Design 1 Tarot release.
These exports are trim-size PNGs; this package contains no bleed/cut-guide
variants or face cards. More density remains a future design option.
