# Design 1 Tarot — reusable components and layout contract

## Authority and scope

The user requested reusable assets with deterministic positioning, following
Design 1's other sets, and retention of the small rank/symbol side panels.
These are requirements. Earlier supplied documents are references, not evidence
of approval of each proposed convention. Latin ornamental art direction,
index abbreviations, trump numbering, and upright artwork are working proposals.
This specifies the Tarot renderer contract; current French-face scripts do not
implement Tarot. The four-card prototype in `scripts/tarot_review.py` now
implements the review subset; see [results](tarot-review-v1-results.md) and
[saved placements](tarot-review-layout-v1.json). Full-deck support remains future work.

## Retain the frame and paired panels

Adapt the existing botanical frame and panel geometry to 825 × 1425 using the
same approach as the native Design 1 formats. Inspect the result at Tarot size.
The panels are upper left and lower right upright; the lower-right index is
an exact 180-degree rotation of the upper-left index, so it reads on the left
from either end. This does not require reversible central artwork. Preserve
panel ornament and rank-above-symbol order in the reader's orientation.

`rebuild_deck.frame_for` supplies frame, field, and panel masks;
`expand_faces.index_layer` supplies the existing French placement/pairing
example. Reuse the geometry and pairing principle, but create Tarot glyphs
and typeset new labels. Fit proportionally to measured panel interiors. Do not
stretch flattened French indices or turn the side panel into a full title.

## Proposed index vocabulary

This is a custom deck convention for review, not a universal Tarot standard.
A panel contains a **rank or number plus symbol**; it need not always be a letter.

| Cards | Upper label | Lower symbol |
| --- | --- | --- |
| Each suit's Ace | A | Sword, baton, lidded cup, or coin |
| Each suit's 2–10 | 2–10 | Same suit glyph |
| Page | P | Same suit glyph |
| Knight | N | Same suit glyph |
| Queen | Q | Same suit glyph |
| King | K | Same suit glyph |
| Fool | 0 | Shared open five-point star |
| Other trumps | 1–21 | Same trump star |

`N` keeps Knight distinct from King in a one-letter panel. The star marks the
trump group, not a fifth minor suit; keep it visibly distinct from Coins.
Numbers distinguish individual trumps. This covers 56 unique suit/rank pairs
and 22 unique trump/number pairs.

Use compact Arabic digits in panels, including `3` for the Empress. Put full
court/trump titles in a separate lower interior band: `THE EMPRESS` and
`QUEEN OF CUPS` in the review set. Aces/numbers need no full title. Do not add
another top number cartouche. Record the final trump order and all 22 title
spellings in the production manifest before full-deck rendering; do not silently
mix numbering conventions. `0` and `1–21` remain review proposals.

Record font file/hash, size, tracking, baseline, ink, and bounds. Match Design 1's
serif character and index weight. Use simplified suit/star shapes at consistent
optical weight, with source, anchor, and hash; avoid painting thumbnails and
platform emoji. Verify `10`, `N`, and `21` at print size. Fit long titles without
horizontal letter distortion.

## Component families

- Swords: straight blade, one curved blade initially, optional opposite/tighter
  curve when needed; separate crown and foliage for Ace furniture.
- Batons: staff master; optional variant for crossings; separate foliage.
- Cups: lidded chalice master; separate decorative furniture.
- Coins: disc master; separate decorative furniture where useful.
- Shared: botanical frame/masks, tracery, typography, index glyphs, title style,
  final rounded-corner alpha.
- Figures: sixteen distinct court paintings and twenty-two distinct trump
  compositions, all using the shared assembly system.

A family can contain multiple images. Generate once, then position instances.
Record mirroring and check asymmetric engraving/light. Preserve aspect ratio;
material shape changes require named variants, not arbitrary stretching.
Keep raw generations separate from prepared RGBA. Component records include ID,
source/component paths, dimensions, local anchor, visible bounds, SHA-256, exact
prompt/reference provenance, and allowed transforms. Deliberately register
anchors; do not infer them from incidental turquoise jewels.

## Positioning manifest to implement

Follow `numeral-layout-v1.json`'s zero-based pixel-center convention. Canvas:
`[825, 1425]`; center: `[412, 712]`, or `[412.5, 712.5]` from outer edges.
Component-local anchors and card target centers use the same coordinate basis.
Before staging, create a machine-readable Tarot layout manifest with:

| Record | Required fields |
| --- | --- |
| Canvas | Size, coordinate basis, center, ground, dpi, corner radius |
| Components | IDs, paths, dimensions, anchors, bounds, hashes, provenance |
| Frame | Source hashes, resize policy, field/panel/title masks and padding |
| Card | Stable ID, suit/group, rank/title, explicit trump number |
| Instances | Unique ID, component ID, role, target center, uniform scale, rotation, mirror flag, z order |
| Crossings | Sword instance IDs, local mask paths/hashes, over/under relation |
| Labels | Glyph/text, font metadata, bounds, paired transform, title bounds |
| Validation | Expected emblem count, reversibility, allowed overlap pairs |

Resolve numeric placements from actual components during prototyping. Record
pixel quantization and resampling policies; repeated renders must reproduce the
same pixels. Transform about each local anchor onto its recorded target center.
Store final positions; no undocumented manual shifts after rendering.

A complete sword counts as one semantic instance even when several masks split
its pixels at crossings. Crossing fragments never increment pip count. Global
z order alone cannot represent an alternating weave: use explicit local masks.
An annotated overlay should label each sword and trace its path. Ten manifest
entries can hide behind one another, so visual counting is also required.

## Assembly and verification

1. Validate hashes. Derive occupied masks from transformed art and keep-out masks
   from the frame, panels, and title band.
2. Fill exact ivory. Apply existing faint gold tracery only in allowed open
   field space, excluding panels, labels, and expanded artwork halos.
3. Composite artwork and furniture in recorded order with crossing masks.
4. Composite frame, paired indices, and court/trump title. Artwork must clear
   these areas rather than relying on the frame to hide clipping.
5. Apply the 3.5 mm silhouette once. Save native RGBA to a separate Tarot staging
   area, along with normal and annotated review sheets.
6. Verify geometry, alpha, glyph containment, spelling/legibility, semantic and
   visible count, hashes, permitted overlaps, and reproduction. Test exact
   half-turn equality only on explicitly reversible composites.

Promote checked, review-approved output through a future Tarot-aware catalog
path. Preserve existing French faces and Tarot backs. `expand_faces.py` is a
reference for the compositor approach, not a working Tarot generation command.
