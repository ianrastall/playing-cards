# Deck rebuild brief

**Status:** The user subsequently authorized execution, including all backs.
The implemented result is documented in [deck rebuild v1](deck-rebuild-v1.md).
The remainder of this brief preserves the pre-rebuild audit and open questions
as they stood before that authorization.

Recorded 2026-09-17 from the user's current request and a read-only audit of
the existing artwork. This document separates that request from historical
instructions and implementation proposals. It does not claim that the rebuild
has been implemented or that proposed values have been approved.

## Requirements from the current user request

- Cards must be pixel-perfect in their shared geometry. Switching between
  cards of the same format must not shift the outline, border, or center anchor.
- A visible central dot must occupy the same exact coordinates on every card
  that has one. Cards without a visible center feature still use that anchor;
  they do not acquire an extra dot or pip just to make it visible.
- Number cards need a defined system for pip positions, counts, rotations,
  and configuration. Each rank's corresponding positions must be consistent
  across suits.
- Borders must be uniform. The user prefers image generation or partial-image
  generation for changes to border artwork.
- Card ground is antique white. Outer corners must have one specific rounding.
- These requirements take precedence over conflicting statements in the
  supplied documents. Historical prompts and the handoff's suggested next-session
  instructions are reference material, not an independent request to execute.

The immediate work here is preparation for the rebuild. No existing image has
been generated, altered, or replaced as part of this audit.

## What the current files establish

The supplied dimensions image and `deck.json` agree on poker trim size:
2.5 x 3.5 inches. The existing poker images are 750 x 1050 pixels, giving
300 pixels per inch at that size. Other formats have their own dimensions;
pixel-coordinate equality is evaluated within a format.

In zero-based coordinates measured at pixel centers, the exact poker canvas
center is **(374.5, 524.5)**. In coordinates measured from the outside edges of
the canvas, that same point is **(375, 525)**. The old detector's rounded pixel
index `(375, 525)` is a third convention and must not be confused with either.

Recommended rebuild convention: use the exact geometric center and explicitly
declare the coordinate basis in the layout data. For pixel-center coordinates,
a half-turn maps `(x, y)` to `(749 - x, 1049 - y)`.

The supplied numeral documents do not contain a frozen per-rank coordinate
system. The Three positions in the handoff are explicitly illustrative. The
older professional system allows suit-specific optical tuning, which is too
permissive for the requested fixed positions.

The reference research in `docs/reference/Playing Card Design Standards.md`
mentions **3.5 mm** outer corner radius. At 300 pixels per inch this is
approximately **41.3386 pixels**. This is a candidate supported by the local
reference, not an established project setting or a verified universal standard.
It is not exactly 1/8 inch. The dimensions image does not specify a radius.

No exact antique-white color value was found in the inspected design/configuration
files. The color name is a user requirement; choosing a particular RGB value
still requires a concrete color sample. The current references also use
"ivory" and "warm ivory," which do not establish numerical equality.

## Audit evidence from the current working tree

`python scripts/catalog.py --check` passes for 82 PNGs. This checks inventory,
identity, hashes, and dimensions; it does not establish the requested geometry.

The existing jewel detector gives these middle-pip centers for the Threes:

| Suit | Measured x | Measured y |
| --- | ---: | ---: |
| Spades | 374.3626 | 530.6042 |
| Hearts | 375.1208 | 528.4134 |
| Diamonds | 374.6138 | 525.5211 |
| Clubs | 374.9502 | 525.8741 |

All four pass the old rounded **aggregate** test. The middle dots are not at
the same location. Upper rows vary by about 20 pixels; lower rows by about
25 pixels. The court detector likewise reports slightly different unrounded
dot centers although every court rounds to `(375, 525)`.

Under the existing 223,349-pixel shared-border mask, all four Threes match
the Ten of Spades exactly. However, the other Tens differ from that template
at 217,957 pixels (Hearts), 219,261 pixels (Clubs), and 221,497 pixels (Diamonds).
The sampled Spades court and ace borders also differ from the numeral template.
The existing frame guarantee therefore does not cover the entire deck.

That mask excludes the corner index panels and most of the interior. Passing
it does not prove identical panel outlines, all inner rules, or all border
geometry. Existing separate court/ace/numeral frame templates cannot be taken
as evidence of one deck-wide frame.

All five inspected poker backs are RGB, as are the current poker faces.
Rounded artwork painted into an RGB rectangle does not itself provide a
transparent rounded card silhouette for software use.

The working tree already contains modified Threes/catalog and deleted source
archives. Several master/backup paths described by the handoff are absent.
Those pre-existing changes were left intact. Future work must check actual
source availability instead of assuming the handoff's recovery paths exist.

## Proposed production approach

1. Define one format-specific outline, center, corner mask, and ground asset.
   Reuse them with identical dimensions and sampling on every export. A digital
   alpha mask and a print trim specification can express the same outline.
2. Establish a common frame master, including fixed inner rules and index-panel
   shapes. Use image generation or partial-image generation when its artwork
   needs revision, following the user's preference. Normalize and inspect the
   master once, then reuse it unchanged. Independent full-card generations
   cannot guarantee identical border pixels.
3. Keep changing rank/suit marks separate from their fixed panel backgrounds.
   Use fixed placement and generate the opposing index by a half-turn of the
   complete index group.
4. Create reusable artwork components and a fixed empty field. Register the
   central feature to a declared local anchor. If the central dot itself must
   have identical shape as well as position, reuse the same dot component.
5. Encode per-rank pip positions and angles in a versioned manifest shared
   by all suits. Define each suit's component dimensions and local jewel anchor
   once at each required size; do not resize separately for individual cards.
6. Rotate paired pips exactly 180 degrees during assembly, including their
   internal flowers and foliage. Place components deterministically. Exact
   placement must be designed into the components: moving arbitrary existing
   jewels with fractional centroids by whole pixels cannot make them identical.
7. Produce staged proof cards and compare all four suits together. The Threes
   are a useful first proof because their center and opposing pair expose the
   failures already measured. This is a proposed sequence, not authorization
   derived from the handoff's embedded prompt.

The antique-white ground can sit beneath ornamental layers. A fixed ground
does not mean every decorated pixel must have the same color.

## Numeral rules still requiring a concrete specification

Retain the references' rank topologies as the starting point: 2 and 3 on the
center column; 4 as two upper/two lower side pips; 5 adds a center; 6 has two
columns of three; 7 has six side pips and an offset center-column pip; 8 has
two columns of four; 9 uses the older document's three-by-three arrangement;
10 has four side rows and an upper/lower center pair.

Exact coordinates, component sizes, and clearances remain to be designed.
There is no approved manifest to copy verbatim.

- Six: choose whether its middle left/right pips are reciprocal rotations or
  both upright. The older document allows a one-way Six; the handoff leaves
  the policy open.
- Seven: an offset unpaired pip added to three reciprocal pairs cannot have
  its arithmetic mean at the geometric center. Preserving that topology and
  forcing the mean to center would require moving some side positions away
  from reciprocal symmetry. A fixed card anchor does not require a symmetric
  pip arrangement or a centered arithmetic mean for this one-way rank.
- Nine: the handoff's "eight reciprocal outer pips plus center" does not by
  itself specify a three-by-three grid. Preserve the explicit older topology
  as the starting point and specify rotations for its midline pair.
- Three, Five, Seven, and Nine may intentionally be one-way. Reusing a rotated
  counterpart for paired pips does not make a directional center pip reversible.

For the initial visual proof, make the outstanding choices concrete together:
frame master, antique-white sample, outer corner radius/mask, Three coordinates,
and component sizes. Do not silently treat illustrative or generic reference
values as approved design values.

## Acceptance criteria for the rebuild

- Zero placement drift for declared anchors and zero shape changes in reused
  components at a given approved size. Rounded centroid equality is insufficient.
- Exact shared pixels for the complete invariant frame and panel backgrounds,
  plus the same outer silhouette mask. Compare all face families, including Tens.
- Each pip matches its declared point, size, and rotation; counts match rank.
  Validate orientation independently from jewel position.
- Pair transforms match the approved component's actual rotated pixels.
- Ground, canvas, output scale, and color handling are consistent.
- Review same-size card switching, full-resolution overlays, rank contact sheets,
  half-turn previews where applicable, and print-size readability. Inspect
  seams and clipping as well as numerical measurements.
- Preserve the current inputs and hashes before any eventual replacement;
  refresh the catalog only when assets actually change.

Exact assembly is the primary geometric guarantee. Color-based jewel detection
is a secondary check whose measurement tolerance must be documented separately;
that tolerance is not permission to introduce placement drift.
