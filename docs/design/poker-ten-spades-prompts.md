# Ten of Spades — expansive numeral-card frame

Built-in image generation, September 16, 2026. The user chose the ten as the density test before continuing other ranks. The narrow lobed court/ace field crowded ten illustrated pips, so this version establishes a more expansive rounded rectangular ivory field for number cards. The user then requested light filigree to give that field definition.

![Ten of Spades](../../cards/faces/french-suited/poker/spades/10.png)

The botanical palette, small solid corner pips and miniature ace emblems continue Design 1. Dense ornament now sits in a narrow perimeter; pale champagne-gold acanthus tracery fills some of the ivory spaces. There are exactly ten central spades: four in each side column and two interleaved in the center. Five are upright and five inverted. Both corner indices read 10.

Final export: `cards/faces/french-suited/poker/spades/10.png`, 750 × 1050 at nominal 300 DPI. The untouched 1060 × 1484 generated master is retained locally at `work/numerals/spades-10-filigree-master.png`; the plain-panel comparison is at `work/numerals/spades-10-plain-panel-master.png`. Work files are Git-ignored. Export uses `scripts/export_face.py`, with aspect ratio preserved and no cropping.

This remains review artwork. Pip positions, internal ornament, filigree and frame are generative, not mathematically exact repeats. The user approved this revised numeral frame, and [all four tens are now complete](poker-wide-numerals-prompts.md). Replacing the four earlier lobed-frame twos was attempted next but image generation reached its usage limit; those files remain unchanged. Ranks 3–9 remain unmade. Courts and aces retain their existing frames.

## Prompt sequence

The broad-frame pass used the existing Two of Spades as the style reference; each subsequent edit used the immediately preceding generated image.

### Expansive numeral-card frame

```text
Use case: style-transfer.
Create a NEW NUMERAL-CARD DESIGN for the TEN OF SPADES in the existing Design 1 botanical playing-card family.
The supplied Two of Spades is a reference for PALETTE, PAINTED BOTANICAL STYLE, corner indices and the ornament inside the spade pips. Its constricted lobed center is specifically being REPLACED. The user wants a much more expansive middle area for the number cards because ten emblems need room.
OUTPUT: one complete flat poker card, exact 5:7 portrait proportions, requested 750x1050 pixels. Full card fills image, ivory rounded outer corners, no mockup or background outside card.
NEW NUMBER-CARD FRAME:
Keep the thin warm-ivory card edge and outer gold-beaded rectangular border from the reference. Keep the exquisite near-black floral band with antique-gold and olive acanthus leaves, red berries, and ivory blossoms tipped madder red.
Confine this botanical ornament to a NARROW, EVEN PERIMETER BAND, about 8-10% of card width along each side and about 6-8% card height at top/bottom. The result must still be lush and detailed in that narrow band, clearly belonging to the original deck.
The interior is now a LARGE OPEN WARM IVORY ROUNDED RECTANGLE with a delicate double gold hairline. Its sides are nearly straight, reaching approximately x=12% and x=88% of the card, and top/bottom y=8% and y=92%. The open field occupies most of the card. Remove the old scalloped/lobed constriction, all large inward-facing leaves, the lateral pointed floral medallions, large corner blossoms protruding into the center, and the large central top/bottom palmettes. Do not place any botanical curls or flowers in the ivory pip field. Only the TEN suit emblems belong there.
Retain the familiar ivory top-left and bottom-right corner index cartouches, nestled in the perimeter. Indices black serif "10" on one line over a solid small black spade, entire pair rotated 180 degrees in the bottom-right. Keep readable bold index size and make 10 fit elegantly inside its cartouche. Small corner suit marks remain solid.
TEN CENTRAL PIPS:
Exactly TEN identical-size ornate BLACK spades, each a miniature of the reference's central ornate spades: sharp spade silhouette, short flared stem, fine gold outline, gold/olive curling foliage, red-tipped ivory flowers, red berries, central ivory rosette with tiny turquoise jewel. Retain black ground. Rich detailed printed botanical illustration, not plain silhouettes.
Make these pips large enough to appreciate their art: approximately 13% card width and 12% card height (about 98x126px at 750x1050), all ten the same size.
Traditional poker TEN arrangement, FOUR equally spaced pips in each of TWO side columns, plus TWO interleaved center pips:
Left column x=33% at y=24%,41%,59%,76%.
Right column x=67% at y=24%,41%,59%,76%.
Center column x=50% at y=32.5% and y=67.5%.
Visual row counts 2,1,2,2,1,2 = exactly TEN. Clearly straight side columns, even row spacing, generous ivory clearance around and between every pip.
Top five pips upright (tip up, stem down). Bottom five are their 180-degree rotated counterparts (stem up, tip down), including interior ornament. Symmetric upper/lower arrangement. The exact center of card remains blank ivory.
No extra central jewel, flower, suit symbols, letters or labels between pips. Only two corner '10' indices and ten central ornate spades. No A or 2.
DESIGN GOAL: a spacious practical TEN with readily countable beautiful miniaturized ace pips, surrounded by the established dark/gold/red botanical vocabulary concentrated into a slender frame. This wider rounded-rectangle number-card field is intentional, replacing the old court/ace lobed frame. Produce the redesigned card, not a slight resizing of the old card.
```

### Upper center pip placement correction

```text
Use case: precise-object-edit.
Edit this new wide-panel TEN OF SPADES. Preserve the entire 1060x1484 full card, frame, colors, ornament, typography, corner indices, pip sizes and all ten pip designs.
ONE PRECISE LAYOUT CORRECTION ONLY:
The upright spade on the central vertical axis in the upper half is currently too LOW, below the second pair of side-column spades. Move ONLY that central upper spade UPWARD by about 180 pixels. Its center should be exactly halfway vertically between the first (top) pair and the second pair of side-column spades, at approximately (530,410) on the 1060x1484 canvas.
Keep this moved pip upright, including its floral decoration. Leave clean matching ivory where it used to be. The moved spade must have ivory clearance from the two upper side pips and the two second-row side pips.
Do NOT move or resize the other nine pips. Do NOT add a pip. There must still be exactly TEN central ornate spades: four in the left column, four in the right, one in the upper center BETWEEN first and second rows, and one in the lower center BETWEEN third and fourth rows.
The correct sequence of horizontal rows from top to bottom is: TWO upright, ONE upright centered, TWO upright, TWO inverted, ONE inverted centered, TWO inverted.
Preserve the new broad rounded-rectangular ivory playing field and narrow botanical perimeter exactly. Do not restore the old lobed frame.
Output exactly the same full canvas and proportions as this input: 1060x1484, 5:7 portrait. This is just moving the ONE upper central spade to its correct position, everything else unchanged.
```

### Pale ivory-panel filigree

```text
Use case: precise-object-edit.
Edit this wide-panel TEN OF SPADES playing card. The user likes the new expansive ivory panel and asks for LIGHT SUGGESTIONS OF FILIGREE to add definition to its ivory background.
CHANGE ONLY THE IVORY BACKGROUND INSIDE THE LARGE INNER PANEL:
Add extremely delicate, pale champagne-gold and warm ivory tone-on-tone filigree. Fine, lightly suggested acanthus tendrils and graceful curling botanical hairlines from the same visual vocabulary as the existing golden foliage. Keep it airy, restrained, luminous and subtle, as a barely visible blind-embossed or pale engraved pattern in fine stationery.
Let sparse curling tracery drift gently along the inner margins and through the broad open ivory spaces, with soft hints of balanced ornament in the gap at the card's center. The filigree should add surface definition and depth, not make the background busy. Mostly unmarked ivory with ample breathing space. Very low contrast, about 5–10 percent darker than the ivory. Hairline strokes rather than broad colored leaves. No dark outlines, strong shadows or distressed paper.
CRITICAL: preserve a small clear ivory halo around every spade so the pip silhouettes remain crisp and separated from the background. Do not draw flower rosettes, turquoise gems, diamonds or any freestanding symbol that could be mistaken for another pip in the background. No new central medallion, standalone emblem or text. Do not make a dense all-over wallpaper.
KEEP EVERYTHING ELSE EXACTLY AS SHOWN: all TEN ornate spade pips at their existing positions and size; their gold/olive foliage, ivory/red flowers, red berries, turquoise jewels and black grounds; the five upright upper pips and five inverted lower pips; both black serif '10' corner indices and solid small corner spades; the wide rounded rectangular ivory field boundary with thin double gold line; the narrow dark botanical perimeter; the outer gold beads, ivory edge, corner shapes and full-card composition. Do not relocate any pip or redesign the border.
The traditional ten arrangement remains FOUR in each side column, TWO in the center column, with upper central pip BETWEEN first and second side rows and lower central pip BETWEEN third and fourth side rows. Exactly ten, no additional suit signs.
Output ONE complete flat card at 1060 x 1484 pixels, exact 5:7 portrait, same proportions as the input. Only add the subtle background filigree inside the ivory panel.
```
