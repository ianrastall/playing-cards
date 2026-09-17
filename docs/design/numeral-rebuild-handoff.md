# Numeral-card rebuild: technical explanation and new-session handoff

**Historical handoff, superseded by the implemented
[deck rebuild v1](deck-rebuild-v1.md).** The rebuild covers all 52 poker faces
and all 30 backs. Its [layout manifest](numeral-layout-v1.json), reusable
components, renderer, and validation report are now present. The starting
prompt and proposed steps below record the earlier state; they are not pending
work or current production instructions.

This document explains the current poker numeral-card system in enough detail
to begin a clean rebuild in a new session. It records what the files contain,
what the existing scripts actually verify, why some visually wrong cards still
passed those checks, what went wrong in earlier passes, and what a genuinely
standardized production pipeline should do differently.

The short version is this:

> The deck currently has a standardized canvas, shared perimeter, and common
> *aggregate* center. It does **not** yet have a canonical per-rank pip grid or
> a component-based renderer. Full-card image generation was asked to satisfy
> geometric requirements, but generative output treats those requirements as
> visual guidance rather than mathematical constraints. The durable solution
> is to generate or extract the artwork as reusable layers, then assemble every
> card deterministically from a layout manifest.

## Current state

The playable poker faces are under:

```text
cards/faces/french-suited/poker/<suit>/<rank>.png
```

The four active threes have been rebuilt once as professional-redo candidates
and then installed. Their generated masters and normalized candidates are in:

```text
sources/generated/poker/numerals/professional-redo/
```

The cards they replaced are recoverable from:

```text
sources/before-professional-redo/poker/<suit>/3.png
```

The first Clubs candidate is retained as `clubs-3-v1.png`. It had three
vertically centered clubs, but its lowest club was still upright. The corrected
source is `clubs-3-v2-master.png`; its lowest club has the stem pointing upward
and the lobes pointing downward, as a 180-degree counterpart of the top club.

Earlier, all ranks two through nine were registered as complete, flat images.
Their pre-registration versions are under:

```text
sources/before-numeral-rebalancing/poker/<suit>/<rank>.png
```

The registration and its later wraparound repair are documented in:

- `docs/design/numeral-rebalancing.json`
- `docs/design/numeral-rebalancing-repair.json`
- `docs/design/numeral-rebalancing.md`

The active image inventory is tracked by `catalog.json` and verified by
`scripts/catalog.py`. At the time of this handoff, the catalog contains 82 PNG
assets and passes its ID, hash, dimension, and inventory checks.

## The physical image space

Every playable face is a 750 × 1050 RGB PNG at nominal 300 dpi. This is a 5:7
portrait canvas.

The software uses zero-based pixel coordinates:

- top-left pixel: `(0, 0)`
- bottom-right pixel: `(749, 1049)`
- rounded registration anchor: `(375, 525)`
- exact continuous geometric center: `(374.5, 524.5)`

That last distinction matters. An even-sized raster has no single center pixel.
Its true half-turn center lies between four pixels. The existing detector rounds
the measured continuous center to `(375, 525)`, which is convenient for QA,
but exact 180-degree geometry should be defined around `(374.5, 524.5)`.

For a canvas of width `W = 750` and height `H = 1050`, exact pixel-coordinate
rotation through 180 degrees is:

```text
x' = (W - 1) - x = 749 - x
y' = (H - 1) - y = 1049 - y
angle' = (angle + 180) mod 360
```

This is not the same as mapping `(x, y)` to `(750 - x, 1050 - y)`. The `-1`
is required by zero-based raster coordinates.

## The conceptual layers of a card

The current PNGs are flattened, but they should be understood as four logical
layers:

1. **Shared perimeter** — ivory edge, gold beadwork, black botanical band,
   flowers, berries, and inner gold boundary.
2. **Corner cartouches** — top-left rank/suit and the complete bottom-right
   counterpart rotated 180 degrees.
3. **Inner field** — pale ivory ground with champagne-gold floral scrollwork.
4. **Central pips** — ornate suit silhouettes containing flowers, leaves,
   berries, and one turquoise jewel apiece.

At present those layers cannot be independently moved without reconstructing
pixels behind them. That is the main technical reason the previous workflow
could center an entire card safely but could not enforce a precise grid for
each individual pip.

## The current border mask

`scripts/align_courts.py` defines the established shared-perimeter mask. The
principal interior rectangle is:

```text
INTERIOR = (75, 72, 675, 967)
```

The right and bottom values are exclusive. Two cartouche regions are protected:

```text
top-left:     (28, 44, 132, 290)
bottom-right: (618, 760, 722, 1008)
```

Pixels outside the interior are normally taken from the shared template, while
the cartouche rectangles are excluded so that each card keeps its own rank and
suit. The Ten of Spades currently supplies the numeral perimeter template:

```text
cards/faces/french-suited/poker/spades/10.png
```

When a generated master is normalized, its card-specific cartouches remain,
but the mask restores the common perimeter exactly. This produces byte-identical
frame pixels wherever the mask is true.

The mask does not make a generated card intrinsically identical to the template.
It simply replaces the designated perimeter pixels after generation. The seam
between preserved interior and copied frame must still be inspected visually.

## How turquoise-jewel detection works

Every ornate central pip contains a turquoise jewel. This provides a convenient
machine-detectable point near the visual center of each pip.

`scripts/rebalance_numerals.py` performs the following operations:

1. Convert RGB channels to signed integers.
2. Select pixels satisfying all three chroma conditions:

   ```text
   green - red > 18
   blue  - red > 18
   green > 65
   ```

3. Ignore the frame and cartouches by restricting the useful field to rows
   `95..954` and columns `135..614`.
4. Find 8-connected components.
5. Reject components smaller than 8 pixels or larger than 800 pixels.
6. Compute a chroma-weighted centroid for each surviving component. The weight
   is the smaller of `green-red` and `blue-red`.
7. Require the number of detected components to equal the rank.

The centroid of one jewel is:

```text
cx = sum(x * weight) / sum(weight)
cy = sum(y * weight) / sum(weight)
```

The card-level layout centroid is the arithmetic mean of every pip-jewel
centroid:

```text
card_cx = sum(cx_i) / rank
card_cy = sum(cy_i) / rank
```

The script rounds with `floor(value + 0.5)` and compares that result with
`(375, 525)`.

This detector is useful and reproducible, but it measures only the turquoise
jewels. It does not know the complete pip silhouette, its bounding box, its
orientation, or whether the botanical artwork inside two counterpart pips is
actually related by a half-turn.

## What “centered” meant in the previous pass

The earlier rebalancing made the **mean of all jewel centers** round to
`(375, 525)`. It did not establish fixed row or column coordinates for a rank.

For example, the current threes measure approximately as follows:

| Suit | Upper jewel | Middle jewel | Lower jewel |
| --- | --- | --- | --- |
| Spades | `(374.9, 297.1)` | `(374.4, 530.6)` | `(374.5, 746.2)` |
| Hearts | `(375.3, 287.2)` | `(375.1, 528.4)` | `(374.5, 758.1)` |
| Diamonds | `(375.2, 279.5)` | `(374.6, 525.5)` | `(374.7, 769.4)` |
| Clubs v2 | `(374.8, 276.9)` | `(375.0, 525.9)` | `(374.6, 771.0)` |

All four cards pass the aggregate center test. They do **not** share identical
upper, middle, and lower row coordinates. The upper row varies by about 20
pixels, and the lower row by about 25 pixels.

This is the precise difference between:

- **registration** — the complete composition is centered as a group; and
- **standardization** — corresponding pips occupy the same defined coordinates
  across all suits for a rank.

The old workflow achieved registration. The future rebuild must add
standardization.

## Why the first corrected Club Three still passed QA

The first professional-redo Club Three had these properties:

- exactly three turquoise jewels;
- all jewels close to the vertical centerline;
- an aggregate center rounding to `(375, 525)`;
- the shared perimeter copied from the numeral template.

It therefore passed every numerical check that existed.

But the lowest club was upright: its lobes were above and its stem below. A
correct lower counterpart must be rotated 180 degrees, with its stem above and
lobes below. Rotating a pip around its own jewel does not necessarily move the
jewel, so an orientation error can leave every centroid measurement unchanged.

That failure demonstrates that position and orientation are independent
properties. Both require separate validation.

## Registration, symmetry, reversibility, and orientation

These terms should not be used interchangeably.

### Registration

The layout is registered when its chosen aggregate anchor coincides with the
canvas anchor. Registration says nothing about individual pip rows.

### Canonical layout

A rank has a canonical layout when every suit uses the same declared pip-center
coordinates, subject only to explicitly documented optical exceptions.

### 180-degree positional symmetry

A set of pip positions is invariant under the mapping
`(x, y) -> (749-x, 1049-y)`. This is a property of the coordinate set.

### 180-degree visual reversibility

A face is visually reversible only if the pip artwork and its orientation also
map correctly. A lower spade must be the upper spade rotated 180 degrees, not a
second upright spade placed at the reciprocal location.

### One-way ranks

An odd-rank center pip occupies the geometric center and maps onto itself under
a half-turn. Hearts, spades, and clubs are directional silhouettes, so an
upright center pip becomes inverted when the card is turned. A traditional
Three, Five, or Nine with one upright center pip is therefore intentionally
one-way even when every surrounding pair is correct.

This is acceptable when declared. It is different from an accidental
orientation mismatch in a pip that is supposed to have a counterpart.

## What image generation does and does not guarantee

The recent threes were produced with the built-in image-generation editor.
Each current source master is 1060 × 1484, exactly 5:7. The prompt requested:

- exactly three pips;
- jewel centers near 29%, 50%, and 71% of the card height;
- a shared centerline;
- an upright top pip;
- an upright center pip;
- a 180-degree lower counterpart;
- a clean, uniform frame with no duplicated bands;
- preservation of the established botanical language.

The generated master was then processed deterministically:

1. Resize from 1060 × 1484 to 750 × 1050 with Lanczos resampling.
2. Detect the jewel centroids.
3. Translate the movable interior by an integer offset so the aggregate anchor
   rounds to `(375, 525)`.
4. Restore the exact shared perimeter under the border mask.
5. Save at nominal 300 dpi with trace metadata.
6. Verify pip count, aggregate anchor, dimensions, mode, and catalog integrity.

Image generation is good at preserving the artistic vocabulary and producing
clean, integrated floral fields. It is not a constraint solver. “Place this
jewel at 29%” is interpreted approximately. “Rotate the lower pip exactly” may
produce an upright pip if the image model favors visual repetition. Text and
corner marks can also drift.

Prompts remain valuable, but output must be treated as an untrusted candidate
until geometry and orientation are checked independently.

## The wraparound failure and why it happened

The first global rebalancing used `numpy.roll` to translate complete pixel
arrays. `roll` wraps pixels leaving one edge back around to the opposite edge.
For a downward shift, pixels from the bottom can reappear at the top before the
frame mask is applied. The result resembles two copies laid over each other:
thin duplicated floral or border strips near the top.

The repair replaced `roll` with a non-wrapping translation:

- destination pixels are copied only when their calculated source coordinate
  is in bounds and belongs to the movable field;
- newly exposed strips remain the corresponding pixels from the preserved
  original;
- frame pixels and protected cartouches never move;
- the shared perimeter is applied afterward.

This fixed translation-induced top-edge artifacts. It did not—and could not—
repair anomalies already painted into a source master.

## Why a layered renderer is the durable solution

The next rebuild should stop asking an image model to produce final complete
cards independently. It should separate art creation from layout mathematics.

The proposed source components are:

```text
sources/components/poker/
  frame/
    numeral-perimeter.png
  field/
    numeral-field.png
  cartouches/
    <suit>/<rank>-top-left.png
  pips/
    spades-upright.png
    hearts-upright.png
    diamonds-upright.png
    clubs-upright.png
```

The precise directory names may change, but the separation should not.

Each pip should be an RGBA asset with a transparent exterior and a known anchor
at its turquoise jewel. A lower counterpart should be created by rotating the
approved upright asset exactly 180 degrees in code. It should not be generated
again independently.

The empty inner field should exist as its own fixed layer. This eliminates the
need to reconstruct floral background whenever a pip moves. The perimeter and
cartouches should likewise be composed from fixed assets.

Once these components exist, a renderer can produce all numeral faces from
data. Generative tools may help create or clean the component artwork, but the
final placement, rotation, count, and assembly become deterministic.

## Proposed layout manifest

Create a versioned JSON file such as:

```text
docs/design/numeral-layout-v1.json
```

The manifest should contain canvas geometry, exact continuous coordinates,
rotation, z-order, and the intentional one-way/two-way policy. A simplified
Three entry could look like this:

```json
{
  "canvas": [750, 1050],
  "continuous_center": [374.5, 524.5],
  "rank": 3,
  "reversibility": "intentional-one-way-center-pip",
  "pips": [
    {"id": "upper",  "center": [374.5, 304.5], "rotation": 0},
    {"id": "center", "center": [374.5, 524.5], "rotation": 0},
    {"id": "lower",  "center": [374.5, 744.5], "rotation": 180}
  ]
}
```

Those row values are an illustrative starting proposal, not yet an approved
standard. Their important property is that upper and lower are exact reciprocal
positions around `(374.5, 524.5)`. The values should be visually reviewed at
full size before the manifest is frozen.

The same coordinates should apply to every suit for that rank. Pip silhouettes
may have different widths or heights, but their jewel anchors should land on
the declared points. If optical compensation is necessary, it must be a named,
measured exception rather than an accidental result of separate generations.

## Rank topology and reversibility policy

The current intended topologies are:

| Rank | Topology | Policy |
| --- | --- | --- |
| 2 | center column, one upper and one lower | two-way |
| 3 | center column, upper/center/lower | one-way center pip |
| 4 | two upper and two lower side pips | two-way |
| 5 | four reciprocal outer pips plus center | one-way center pip |
| 6 | two columns of three | policy must explicitly define the midline pair |
| 7 | paired outer pips plus one offset center-column pip | intentionally one-way |
| 8 | two columns of four | two-way in this deck |
| 9 | eight reciprocal outer pips plus center | one-way center pip |
| 10 | four reciprocal side pairs plus one center-column pair | two-way |

The Six requires special care. Two pips placed on the horizontal midline swap
left-to-right under a half-turn. Exact reversibility requires their orientation
and artwork to swap correctly as a pair. Simply making both upright creates a
one-way face.

The Seven also needs an explicit design decision. Traditional layouts often
place one unpaired pip above center, producing a deliberately one-way and
visually top-heavy topology. If this deck keeps that tradition, row spacing
must still be chosen so the full composition is optically balanced. If the deck
instead prioritizes strict center-of-mass registration, that choice must be
recorded in the manifest.

## Recommended renderer behavior

The future renderer should:

1. Load the approved fixed field and frame.
2. Load the rank/suit cartouche asset.
3. Load one approved upright pip sprite for the suit.
4. Rotate sprites in code for entries whose manifest angle is 180 degrees.
5. Place each sprite by its jewel-anchor coordinate, not by its bounding-box
   corner.
6. Use alpha compositing with no resampling when the sprite is already at its
   approved final scale.
7. Composite the shared frame last, while preserving the cartouche regions.
8. Embed source hashes, manifest version, rank, suit, and component versions in
   PNG metadata.
9. Write to a staging directory first.
10. Promote to `cards/` only after automated and visual checks pass.

If a pip needs scaling, scale the component master once, approve that version,
and then reuse the approved raster. Repeated per-card scaling can introduce
small outline and jewel differences.

## Required automated checks

The new pipeline should fail rather than merely warn when any of these checks
does not pass:

### File-level checks

- size exactly 750 × 1050;
- RGB output;
- nominal 300 dpi;
- expected rank and suit path;
- catalog entry and hash current.

### Content checks

- detected jewel count equals rank;
- every detected jewel is assigned to exactly one manifest point;
- every jewel is within an agreed tolerance of that point;
- no extra turquoise component exists in the field;
- cartouche rank and suit are correct by visual inspection until a reliable
  detector exists.

### Layout checks

- aggregate continuous centroid agrees with the manifest expectation;
- corresponding suits use the same rank coordinates;
- reciprocal pip locations satisfy `x' = 749-x`, `y' = 1049-y`;
- rows and columns are checked individually, not inferred from the mean.

### Orientation checks

- deterministic lower sprites are pixel-identical to the approved upper sprite
  after a 180-degree transform when exact pairing is required;
- directional silhouette checks are explicit: spade point, heart point, and
  club stem must face the declared direction;
- odd center pips are marked intentionally one-way rather than accidentally
  treated as reversible.

### Frame checks

- pixels under the border mask are identical to the approved template;
- cartouche regions are excluded from the shared-frame comparison;
- no repeated row, wraparound strip, seam, or clipped ornament appears near
  any interior boundary.

### Visual checks

- full-resolution inspection of every card;
- contact sheet grouped by rank so all four suits can be compared directly;
- 180-degree preview for every nominally two-way rank;
- print-scale preview to judge optical balance and pip crowding;
- before/after sheet whenever an active card is replaced.

## Staging and preservation rules

Use three distinct levels of files:

```text
sources/   immutable or versioned masters and pre-change backups
work/      disposable candidates, previews, masks, and contact sheets
cards/     active playable assets only
```

Before replacing any active face:

1. Copy it to a versioned `sources/before-...` location.
2. Record its SHA-256 hash.
3. Build the replacement under `work/` or a versioned generated-source folder.
4. Verify the complete rank before promotion.
5. Replace active cards only after all four suits pass.
6. Refresh and check `catalog.json`.
7. Run `git diff --check`.

Never reuse an unversioned filename for two materially different generated
masters. The Club Three correction demonstrates why `v1` and `v2` history is
valuable.

## Suggested order for the rebuild

The next session should not immediately generate the Fours. It should first
build the component and rendering system using the Threes as the proof rank.

Recommended order:

1. Freeze the current active Threes as visual references.
2. Create or extract one transparent upright pip master for each suit.
3. Create one approved empty numeral field and one shared perimeter asset.
4. Define and approve the exact Three coordinates in the layout manifest.
5. Render all four Threes from components.
6. Confirm exact shared coordinates and the correct lower rotations.
7. Compare the rendered Threes with the current visual references.
8. Once the renderer is trustworthy, encode ranks 2 and 4 through 10 one rank
   at a time.

This is slower at the beginning and dramatically safer afterward. Once the
four suit sprites and shared layers exist, rebuilding a rank becomes a data and
QA task rather than four independent image-generation tasks.

## New-session starting prompt

The following can be pasted into a new Codex session:

```text
We are rebuilding the poker numeral faces under a deterministic, deck-specific
standard. Read docs/design/numeral-rebuild-handoff.md completely before making
changes, then inspect docs/design/professional-numeral-system.md and the existing
scripts it references.

Begin with the Threes as the proof rank. Do not generate or replace the Fours
yet. Treat the current active Threes and the masters under
sources/generated/poker/numerals/professional-redo/ as visual references, not
as geometric ground truth. Build a layered workflow with a fixed empty field,
shared frame, protected cartouches, and reusable transparent pip components.
Define exact per-pip coordinates and orientations in a versioned JSON layout
manifest. Compose lower counterpart pips by deterministic 180-degree rotation,
not independent generation. Validate every individual jewel coordinate,
orientation, frame pixel, dimension, and catalog hash. Stage and visually
inspect all four suits together before replacing active cards. Preserve every
prior active file under a versioned sources/before-* path.
```

## Final principle

The artwork and the geometry should no longer be solved by the same operation.

Art tools should create approved components. Code should place them. A manifest
should define the standard. Automated checks should prove the measurable parts,
and full-size visual review should catch what centroids and hashes cannot.

That separation is what will turn the deck from a sequence of individually
plausible images into a coherent production system.
