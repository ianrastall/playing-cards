# Design 1: five face formats and palette-aware frames

The active inventory is 270 faces and 30 backs. Each of Poker, Jumbo, Travel,
Bridge, and European Standard has 52 suited cards and two Jokers.
Tarot still has backs only.

Jumbo, Travel, and Bridge are composed at their native canvas sizes from the
saved pip masters, indices, frame, Joker components, and preserved court
paintings. They do not read flattened active Poker cards. Their pip spacing is
mapped from the established layout and quantized around the exact new center.
Pip proportions are preserved, using the smaller axis scale to fit each frame.
The border and index-panel geometry are resized to the new aspect ratio.

The court paintings are reused from preserved source artwork and fitted within
the new shared frame. Their faces are not newly generated illustrations.
Poker retains its registered pip components and placements.
The [King registration correction](king-registration-v2.md) additionally
centers the painted King interiors before their center-jewel overlay.

European Standard is a Lanczos resize of the newly composed Bridge export,
with the established 3.5 mm physical corner mask reapplied. This intentionally
allows the slight aspect change from 675 x 1050 to 696 x 1074 requested for
this format. Pixel-exact half-turn equality is guaranteed for declared native
two-way faces and backs; European interpolation may differ by a channel level.

## Palette and filigree

Spades, clubs, and the black Joker use Lamp Black frames. Hearts, diamonds,
and the red Joker use Madder Lake frames. Each back uses its own named frame
palette. The palette function changes dark neutral ground and source blue
chroma without moving the artwork; luminous gold, ivory, red flowers and
chromatic green foliage are protected. These are digital pigment-inspired
choices, not measured historical ink colors.

The [gilded vine tracery template](front-tracery-v3.md) supplies fine arabesque
scrollwork and acanthus leaves in a light antique-gold printer's-ink treatment.
It uses the approved generated ornament at 26% opacity, reduced a further 15%
in scale for finer granularity. The saved source and template settings live in
`sources/components/front-tracery-v3/` and are included in render provenance.

The texture appears on aces, number cards, and Jokers. Its halves match under
a half-turn, with a narrow blend through the center to avoid a hard seam or
darkened overlap. Artwork silhouettes mask it to leave clear ivory halos.
Dense court paintings are unchanged inside the frame.

## Reproduction and checks

```text
python scripts/expand_faces.py --stage
python scripts/expand_faces.py --check
python scripts/expand_faces.py --apply
python scripts/expand_faces.py --check --active
python scripts/catalog.py --check
python -m unittest discover -s scripts -p "test_*.py"
```

The established `rebuild_deck.py --stage/--check/--apply` commands route to the
current renderer after promotion. Historical `--prepare` creates original
Poker components and should not be used as a new-format authoring command.

`face-formats-v1.json` records source hashes, order, dimensions, native pip
centers and orientations, palette policy, and backup location. Checks verify
all exports against their render inputs, exact inventory, native pip counts,
centers, collisions, clipping, index containment, corner masks, density, and
declared reversibility. The catalog supplies final file hashes and dimensions.

All 84 pre-expansion PNGs, the prior deck configuration, and catalog are
preserved with hashes under `sources/before-face-formats-v1/`. Promotion refuses
to overwrite an active file that differs from both its preserved input and
the checked output. Generated masters remain unchanged.

Full-format review sheets are under `work/face-formats-v1/`. The small
tracked overview is `face-formats-v1-preview.jpg`.
