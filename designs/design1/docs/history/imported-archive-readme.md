# Card asset archive

`cards/` is the source of truth. Backs are organized by side, then size, with
pigment name in the filename: `backs/<size>/<pigment>_<size>.png`. Faces belong in
`faces/`. Keep drafts, previews, and superseded assets under `work/`.

## Color variants

Each size has ten named colors (60 assets total). Every variant is generated
directly from its corresponding Prussian Blue original. Only blue-dominant
pixels change. Pixel positions, dimensions,
alpha (where present), cream, gold, foliage, flowers, and central dots are
preserved. There is no resizing, stretching, cropping, or redrawing.

### The Printer's Palette

| Pigment-inspired name | Filename prefix | Digital appearance | Previous label |
| --- | --- | --- | --- |
| Prussian Blue | `prussian-blue` | Deep navy blue | blue |
| Madder Lake | `madder-lake` | Deep burgundy red | red |
| Viridian | `viridian` | Forest green | green |
| Manganese Violet | `manganese-violet` | Rich royal purple | purple |
| Burnt Umber | `burnt-umber` | Warm dark brown | New |
| Yellow Ochre | `yellow-ochre` | Tarnished mustard gold | New |
| Burnt Sienna | `burnt-sienna` | Orange-leaning earthy rust | New |
| Lamp Black | `lamp-black` | Soft warm charcoal | New |
| Verdigris | `verdigris` | Muted blue-green / teal | New |
| Green Earth | `green-earth` | Muted olive green | New |

These are digital interpretations named after historical pigments, not measured
reproductions of specific historical inks or printing recipes. The teal option
uses Verdigris, a historical bluish-green pigment; the existing navy takes the
Prussian Blue name. The ochre is a flat color, not a metallic print effect.

The naming references include the National Gallery of Art's
[pigment handbook](https://www.nga.gov/research/publications/artists-pigments-handbook-their-history-and-characteristics-volume-3),
the National Gallery of Australia's
[Materials of Art](https://nga.gov.au/exhibitions/materials-of-art/),
the MFA's [Verdigris](https://cameo.mfa.org/wiki/Verdigris) and
[Manganese Violet](https://cameo.mfa.org/wiki/Manganese_violet) entries, and
Daniel Smith's [earth-pigment overview](https://danielsmith.com/artists/exploring-ochres-umbers-and-siennas/).

The original 24 archive PNGs were renamed byte-for-byte: their palettes, pixels,
and file contents are unchanged. Madder Lake retains the red palette measured
from the original poker pair. The older, pre-recoloring red poker reference
remains at `../work/originals/red_poker.png`.

The rename map and original hashes are saved in
`../work/palette/filename-migration.json`. Old embedded source/color metadata
and historical working files may still use the former names; the filenames
and current validation manifest provide the authoritative labels and paths.

[View the labeled ten-color comparison](../work/palette/palette-preview.jpg).

## Dimensions

The original source PDF's dimension table (retained as
`../dimensions-reference.png`) gives rounded inch and
millimeter values that are not exact conversions of one another. These
assets follow the PDF's inch column at nominal 300 DPI, exactly matching
the existing blue canvases. Millimeters below are the exact inch conversions.
PNG stores integer pixels per meter, so readers report 299.9994 DPI for the
nominal 300 DPI setting (a negligible encoding difference).

| Size | Pixels (W x H) | Inches (W x H) | Millimeters (W x H) |
| --- | --- | --- | --- |
| Bridge | 675 x 1050 | 2.25 x 3.50 | 57.15 x 88.90 |
| European standard | 696 x 1074 | 2.32 x 3.58 | 58.928 x 90.932 |
| Jumbo | 1050 x 1500 | 3.50 x 5.00 | 88.90 x 127.00 |
| Poker | 750 x 1050 | 2.50 x 3.50 | 63.50 x 88.90 |
| Tarot | 825 x 1425 | 2.75 x 4.75 | 69.85 x 120.65 |
| Travel | 525 x 750 | 1.75 x 2.50 | 44.45 x 63.50 |

The central dot stays at its original location in each Prussian Blue design. Some
original dots are offset from the mathematical canvas center, notably Tarot;
all color copies retain those positions deliberately.

## Reproduction and checks

Run these commands from the project root (requires Pillow and NumPy), or
invoke the script by its full path:

```text
python recolor_card_backs.py --colors burnt-umber yellow-ochre
python recolor_card_backs.py --verify-archive
python recolor_card_backs.py --preview
```

Omit `--colors` to generate all nine recolored variants. The original
Prussian Blue assets are the source. The old `red`, `green`, and `purple`
CLI arguments remain supported as aliases for the new names.

Candidates are written to `work/recolored-backs/<pigment>/`. The script does
not overwrite archive files. Review candidates before copying them into the
archive. `--verify-archive` reads and checks all 60 archived cards without
changing them. `--preview` creates the labeled comparison in `work/palette/`.

`backs/validation.json` records all 60 approved assets under their current
names, with asset hashes, source hashes, dimensions, DPI, exact palette
comparisons, preservation of non-blue pixels, alpha, and central-dot patches.
Prior reports are preserved in `../work/palette/previous-validation/`.
Candidate reports also include changed-pixel counts.
Dot check boxes use zero-based top-left coordinates with
exclusive right/bottom edges; they are QA regions, not fitted dot centroids.

The script checks lossless PNG roundtrips, exact preservation outside the
blue mask, alpha preservation, and identical 11 x 11 pixel dot patches.
Per-color overviews are `../work/recolored-backs/<pigment>/<pigment>-backs-preview.jpg`;
only these previews are reduced in size, never the archive PNGs.

Palette multipliers are defined in `PALETTES` in `../recolor_card_backs.py`.
Each color is generated directly from Prussian Blue, avoiding accumulated recoloring.
