# Design 2

[All designs](../../README.md) · [Gallery](index.html) · [Finished backs](cards/backs/)

The approved PNGs live in `cards/backs/<format>/<color>.png` in this folder.
They are permanent source assets, separate from ignored build output.
There are no finished Design 2 faces yet.

Run the commands below from `designs/design2/`.

Thirty trim-size backs: five border colors in all six formats, including Tarot.
The gold looping ornaments have been replaced with small Chinese-inspired
floral sprigs. Every color uses the same centered artwork and frame.

Open `index.html`. Scroll over the card or press the left/right arrow keys to
cycle colors in a fixed position. Buttons, a format selector and optional
center guides are also available. Use each PNG at its natural aspect ratio;
different formats intentionally have different proportions.

## Geometry

| Format | Pixels | Trim inches | Center pixel coordinates |
| --- | --- | --- | --- |
| Poker | 750 x 1050 | 2.5 x 3.5 | (374.5, 524.5) |
| Bridge | 675 x 1050 | 2.25 x 3.5 | (337, 524.5) |
| European Standard | 696 x 1074 | 2.32 x 3.58 | (347.5, 536.5) |
| Jumbo | 1050 x 1500 | 3.5 x 5 | (524.5, 749.5) |
| Travel | 525 x 750 | 1.75 x 2.5 | (262, 374.5) |
| Tarot | 825 x 1425 | 2.75 x 4.75 | (412, 712) |

All PNGs are RGBA at nominal 300 ppi with the collection's 3.5 mm corner alpha,
antique-white #FAEBD7 paper ground and exact half-turn symmetry. The outside
paper margin is 23/750 of the card width; the floral border is 50/750 of the
width on all four straight sides. Each format's five variants are identical
outside the border-color mask. The central roundel remains proportional;
surrounding patterned bands adapt to the available height.

`manifest.json` records file hashes, palettes, layout and source registration.
`registration-audit.json` records independent saved-file checks, including
zero measured center error in all 30 outputs. `prompts.json` preserves the
built-in image-generation edit prompt (under `sources/generated/design2-registered-v1/`). The repository can reproduce the set:

```text
node scripts/register_design2.mjs
python scripts/audit_design2_registration.py --build
```

The renderer writes to `build/design2-registered-v1/` for review. It does not
overwrite the approved cards. To check the permanent set, run:

```text
python scripts/audit_design2_registration.py
python ../../scripts/catalog.py --check
```

Choose one back color for a physical deck. This package includes no faces,
bleed, cutting guides or imposed sheets. The prior Design 1 decks, including
its completed Tarot release, are unchanged.

Source studies and earlier candidates are preserved in `sources/generated/`;
registration plates and masks live in `sources/components/`. Notes live in
`docs/design/`. The final manifest paths are relative to this design folder.
The image renderer needs Node.js and ImageMagick on PATH; audits need the Python
dependencies from `../../requirements.txt`. Licensed under [MIT](../../LICENSE).
