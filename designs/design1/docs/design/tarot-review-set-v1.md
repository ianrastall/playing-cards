# Design 1 Tarot — component prompts and representative review set

## Scope and decision status

Revised for the user's reusable-asset workflow and request to retain Design 1's
small rank/symbol side panels. Earlier supplied prompts were references, not a
record of user approval. Latin ornamental Cups, Coins, Swords, and Batons remain
the working direction: 40 ace/number cards, 16 courts, and 22 trumps including
the Fool, without French Jokers. Palette, labels, numbering, and upright-art
conventions below remain proposals for visual review.

Use the [component/layout contract](tarot-component-layout-v1.md) and
[palette manifest](tarot-palette-manifest-v1.json). New component paths describe
planned outputs, not existing files. This brief does not implement a renderer.

The review deliverable is four **composited cards**, not four generated cards:

| Card | Inputs | Test |
| --- | --- | --- |
| The Empress | Original figure composition | Attributes, paired trump indices, full title |
| Queen of Cups | Original figure composition; Cups index glyph | Court attributes, suit/rank index |
| Ace of Swords | Straight sword; separate crown and foliage | Sparse reuse, halos, side panels |
| Ten of Swords | Ten sword instances from the same component family | Dense positioning, count, crossings |

## Shared art direction

- William Morris ornament, Alphonse Mucha figure/line composition, Persian
  Safavid textile and metalwork influences. Safavid is an artistic influence,
  not a claim about a figure's historical identity.
- Antique ivory `#FAEBD7`, matte antique-gold ornament, madder-red flowers,
  olive foliage, restrained turquoise. No neon, glossy foil, or heavy shadows.
  The compositor supplies exact ground/frame colors; review generated accents.
- Generate artwork only. Frame, panels, indices, titles, background tracery,
  and rounded corners are separate components.
- Finished cards: 825 × 1425 px, 11:19, 300 ppi, 3.5 mm rounded corner alpha.
  Individual asset canvases follow their subjects; a sword sprite is not an
  11:19 card. Retain high-resolution sources sufficient for the largest placement.
- Prepared masters require clean RGBA, including open holes. Prefer transparent
  generation; if extraction is needed, use flat ivory and inspect the edges.
  No baked rectangular ivory patch or halo may remain on a component.
- Figure compositions fit a tall guide with outer roughly 8% initially clear,
  extra clearance for upper-left/lower-right panels, and a lower title band.
  Final measured frame/panel masks, not this approximate margin, govern fit.
- No lettering, numbers, French suit signs, frame, border, baked corner radius,
  all-over tracery, paper texture, watermark, signature, photography, or modern
  clothing in generated art. Local engraving on a blade or robe is allowed.
- Apply the existing front-tracery-v3 in open space, masked away from artwork,
  panels, and labels. Do not regenerate the background with every component.

## Generate reusable components first

Append shared art direction to the subject prompts below. Generate each asset
separately. Use the accepted first sword and established Design 1 art as visual
references for subsequent variants. Save exact prompts, references, and hashes.
Do not generate a contact sheet to cut apart, a finished number card, or a
prewoven Ten. Generate additional variants only after a layout demonstrates need.

### S1 — straight sword

> One isolated complete upright double-edged straight sword, point up, pommel
> down, with a vertically symmetrical silhouette. William Morris ornament,
> Mucha clean contour, Persian Safavid-inspired metalwork. Finely engraved steel
> blade with restrained turquoise detail; antique-gold hilt and pommel with fine
> arabesque. Matte hand-printed appearance, crisp silhouette, gentle shading.
> Entire sword visible with padding beyond tip, guard, and pommel. Transparent
> background. No crown, wreath, flowers, ribbon, detached ornament, lettering,
> numbers, border, scene, cast shadow, or other sword.

Keep the sword bare so Ace furniture does not appear on every numbered pip.
Record a deliberate registration anchor; do not detect incidental turquoise dots.

### S2 — curved sword

> One isolated complete slender curved sword with one continuous gently arcing
> blade, one guard, and one pommel, suitable for an ornamental woven arrangement.
> Match the supplied straight sword reference in steel, turquoise details,
> antique-gold hilt, engraving, line weight, and matte finish. Show the full
> silhouette with padding, without perspective foreshortening. Transparent
> background. No second sword, crossing, flowers, crown, lettering, border,
> scene, or cast shadow.

Prototype placement before generating more. Rotation and recorded mirroring may
supply partners if engraving and lighting remain credible. If needed, generate
S3 as an opposite-handed curve and/or S4 as a tighter curve using accepted
references. These are optional variants, not four mandatory generations. Do not
stretch the straight blade nonuniformly to manufacture a curve.

### O1 — Ace crown

> One isolated small open antique-gold crown, front view, inspired by Safavid
> metalwork and Mucha contour, matching the supplied sword's engraving and matte
> finish. Restrained turquoise jewels, clear central opening, complete silhouette,
> balanced detail, generous padding. Transparent background. No sword, head,
> figure, text, border, background scene, or cast shadow.

### O2 — foliage sprig

> One isolated elegant laurel-and-palm ornamental sprig, olive leaves, small
> madder-red flowers, fine matte antique-gold stems, William Morris botanical
> drawing and Mucha contour. Slender gently curving silhouette, complete stem
> and leaves, generous padding. Match the supplied sword/crown palette.
> Transparent background. No sword, crown, vase, lettering, border, or shadow.

Place copies for the Ace; record any mirroring. Reuse small sprigs between dense
pips only after confirming they leave the sword count readable.

### Index glyphs — prepare separately

Prepare a simplified sword silhouette derived from S1 and a lidded-chalice glyph
for Cups with consistent optical weight. Later Batons and Coins use a staff and
disc. These are reusable ink shapes, not painting thumbnails or platform emoji.
Keep the chalice glyph and Queen's painted vessel recognizably related. Prepare
the proposed open five-point trump star separately. Typeset all rank labels
outside image generation using recorded font inputs.

## Generate two original figure compositions

Use the shared direction and accepted visual references. Keep faces, hands,
identifying attributes, and foreground ornaments clear of panel/title masks.

### F1 — The Empress

> An original ornamental tarot Empress composition: a calm dignified crowned
> empress seated on a cushioned throne, frontal or three-quarter, occupying the
> central part of a tall portrait field. Flowing Safavid-inspired patterned robes
> in madder red and olive with fine gold arabesque; a diadem of small stars; one
> slender upright scepter held clearly; beside her a heraldic roundel bearing
> the Venus sign. Ripe golden wheat, madder-red flowers, and olive foliage at the
> base. Restrained turquoise jewels. Mucha contours and gentle shading, Morris
> floral discipline, matte gold detail. Isolated figure, throne, and foreground
> plants; no landscape. Clear space especially at upper left, lower right, and
> below the plants for separately assembled panels and title. No frame, panel,
> title, number, lettering, or all-over background pattern.

The Venus sign is an iconographic attribute; inspect/correct it separately if
needed. Proposed side indices: `3` over the trump star; lower interior title:
`THE EMPRESS`. This supersedes the earlier `III` top-cartouche proposal.

### F2 — Queen of Cups

> An original ornamental Queen of Cups composition: a gracious crowned queen
> seated frontally on an ornamented throne in a tall portrait field. She holds
> one prominent ornate lidded golden chalice with a clear cup silhouette.
> Safavid-inspired gown in madder red, olive, and fine gold arabesque; crown
> with small turquoise jewels. Stylized water, scalloped waves, madder-red
> water-lilies, and olive pads at the base. Mucha contours and soft shading,
> Morris ornament, matte gold detail. Isolated figure, throne, and low water
> ornament; no surrounding landscape. Clear space especially at upper left,
> lower right, and below the water ornament for separately assembled panels and
> title. No frame, panel, lettering, numbers, or all-over background pattern.

Proposed indices: `Q` over the Cups glyph; lower title: `QUEEN OF CUPS`.
Sixteen courts and twenty-two trumps still need distinct compositions; do not
cut figures into generic body parts merely to increase reuse.

## Assemble the Ace and Ten through code

**Ace of Swords:** place one S1 upright on the center axis, O1 at the tip, and
O2 sprigs as separate instances. Use Lamp Black frame and paired `A`/sword
indices. Apply masked tracery to open space. Record placements, halos, and
clearances. Crown and foliage are furniture, not additional suit-emblem pips.

**Ten of Swords:** prototype a balanced lattice of exactly ten complete sword
instances. A candidate is two central straight swords plus eight curved swords
in four opposed pairs; this is a layout experiment, not a claim to replicate a
historical pack. Use explicit crossing masks wherever blades weave. Keep each
blade traceable from tip to hilt. Start bare and add sparse ornament only once
the count reads clearly. Use Lamp Black frame and paired `10`/sword indices.
Apply tracery only to available open space. Record every placement and crossing;
review normal and annotated views. Never ask image generation to count ten swords.

Both cards use the same sword **family**, not necessarily the same blade shape.
Reposition or select an existing variant before requesting additional artwork.

## Review before scaling

- Inspect all four framed composites at native and intended print size beside
  Design 1; compare panels, typography, frame, and palette.
- Include separate panel specimens for `10`, Knight `N`, and a two-digit trump.
- Check Empress attributes, Queen's chalice and hands, one Ace sword, ten
  traceable swords, and all interlace crossings.
- Verify alpha extraction, no ivory rectangles, clear halos, no stray lettering,
  and no frame/panel/title collisions.
- Verify manifest counts and reproducible placements. Test exact half-turn
  equality only for explicitly reversible cards, not upright figures.
- Record decisions on colors, labels, numbering, reversibility, and variants
  before expanding to the remaining suits, ranks, and figures.

This is the authoring brief. The subsequent four-card prototype is documented
in [review results](tarot-review-v1-results.md), including exact generation
prompts and saved placements. Its staged faces are outside the active catalog.
