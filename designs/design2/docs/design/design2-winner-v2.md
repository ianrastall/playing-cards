# Design 2 revision 2: make the border color dominant

Superseded by the [floral replacement and registered set](design2-registered-v1.md).

The prior frame's red flowers and green leaves concealed the differences
between its five dark background colors at normal card size. This revision
replaces that frame ornament with smaller ivory/gold lotus-vine linework,
leaving much more uninterrupted color visible. Blue, green, crimson, violet,
and charcoal use more distinct digital midtones. The polychrome silk interior,
radial central flower, border width, and outer card geometry are retained.

Five edited masters were generated with the built-in image-generation tool.
Original outputs and exact prompts are in `sources/generated/design2-winner-v2/`.
The native exports and browsable gallery are in `build/design2-winner-v2/`.
The downloadable package is `build/design2-winner-v2.zip`.

Rebuild with `node scripts/export_design2_winner.mjs v2`. Pass `v1` explicitly
to reproduce the earlier frame. That earlier set is retained for provenance;
v2 is the current provisional candidate, pending visual acceptance.

There are 30 native RGBA backs: five colors by six formats, including Tarot.
Each has exact half-turn symmetry, nominal 300 ppi and the existing 3.5 mm
corner alpha. The center medallion maintains equal horizontal/vertical scale;
the surrounding bands absorb changes in format height. Pale paper reserves
use #FAEBD7. The shared interior comes from the new blue master, clipped inside
the rounded inner field so its blue corner wedges cannot leak into other colors.

All 30 exports passed source/output hash, lossless roundtrip, common-interior,
half-turn, dimension, density and independent existing-alpha-mask checks.
The revised full cards were reviewed at thumbnail scale, and the native red
card was checked for border/interior joins. The prior multicolored frame is
superseded as a design direction. Design 1 and its completed Tarot are untouched.

These are provisional trim-size backs, not bleed/cut-guide packages. The
outer frame is deliberately quieter; increasing interior density remains
a separate possible design change.
