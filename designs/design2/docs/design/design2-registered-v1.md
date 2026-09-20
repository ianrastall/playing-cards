> Approved native files now live in `cards/backs/` within `designs/design2/`.
> Paths and commands below are relative to this design folder. Earlier build
> output remains available for provenance; it is not the permanent asset location.

# Design 2: floral replacement and exact registration

The small ochre interlocking-circle ornaments have been replaced with delicate
peony-like floral sprigs. The selected silk interior, eightfold central flower,
and pale floral border linework remain the design language. The artistic edit
used the built-in image-generation tool; the raw master and exact prompt are
saved in `sources/generated/design2-registered-v1/`.

## One source of geometry

All five palettes now derive from one registered artwork plate and one border
color mask per format. The previous independent color-generation masters are
not used. Palette changes affect only the color mask; artwork positions,
ornament contours, outer paper margin, outlines, alpha and center never change.
The readable midtone palette from revision 2 is retained as explicit RGB values.

The painted central floral disk was measured by comparing its local pixels
under a half-turn, with a coarse search followed by a 0.05-pixel refinement.
The measured source anchor is (530.1, 734.6), in zero-based pixel coordinates.
The whole artwork is registered through that anchor before reciprocal
construction. It is not concealed by an added center jewel.

All native outputs are exactly equal to their own 180-degree rotation. The
central roundel keeps proportional scaling; outer patterned bands absorb the
format-height differences, so Tarot's satellite medallions are taller.

## Shared layout

The outside paper margin is 23/750 of card width. The floral border band is
50/750 of card width, equal on all four straight sides. Each size's five
colors share its exact placement, frame pixels, color mask and corner alpha.
The physical silhouette remains the collection's 3.5 mm radius at 300 ppi.

| Format | Native pixels | Exact center pixel coordinates | Border band px |
| --- | --- | --- | --- |
| Poker | 750 x 1050 | (374.5, 524.5) | 50 |
| Bridge | 675 x 1050 | (337, 524.5) | 45 |
| European Standard | 696 x 1074 | (347.5, 536.5) | 46.4 |
| Jumbo | 1050 x 1500 | (524.5, 749.5) | 70 |
| Travel | 525 x 750 | (262, 374.5) | 35 |
| Tarot | 825 x 1425 | (412, 712) | 55 |

The band widths are registered design coordinates; the painted rules retain
their common fine handmade contours and antialiasing. Actual contour pixels
are identical between palettes apart from the recolored ground/edge mixtures.

## Reproduction and verification

```text
node scripts/register_design2.mjs
python scripts/audit_design2_registration.py --build
```

The Node renderer uses ImageMagick for PNG decoding/encoding and preserves the
source master. It records all source/output hashes and geometry. The separate
Pillow/NumPy audit reads the saved PNGs, verifies exact palette mapping and
unchanged pixels outside the color mask, compares alpha to the existing deck
implementation, checks all dimensions and density, and measures the painted
gold/red center inside a local disk. All 30 center errors were zero pixels.

The image-generation result was visually checked for removal of the loops;
native Poker and Tarot exports were inspected. The browser viewer was tested
with color buttons, wheel cycling, arrow keys, Tarot selection and center
guides. The rendered image rectangle stayed unchanged during palette swaps.

## Deliverables

- `build/design2-registered-v1/backs/<format>/<color>.png`: 30 trim-size RGBA backs.
- `build/design2-registered-v1/index.html`: fixed-position wheel/keyboard viewer.
- `build/design2-registered-v1/manifest.json`: hashes and complete geometry.
- `build/design2-registered-v1/registration-audit.json`: independent results.
- `build/design2-registered-v1.zip`: the complete native package.
- `sources/components/design2-registered-v1/`: shared plates, masks and layout.

This approved set supersedes the earlier Design 2 export candidates. It is now
included in the collection catalog and the Design 2 local catalog. Permanent
assets are in `cards/backs/`; `manifest.json`, `registration-audit.json`, and
`index.html` at the design root describe and display those assets. Run the audit
without `--build` to verify the permanent set. Design 1 has its own catalog.
The package contains native backs, not bleed/cut-guide files or faces. Different
formats intentionally have different aspect ratios; palette swaps within a
format are the pixel-registered comparisons.
