# Poker aces — generation prompts

Mode: built-in `image_gen` (imagegen skill), September 15, 2026.

The user requested ornate botanical treatment for every ace and a larger Spades emblem. These are the final revision prompts. Each output is retained untouched under `sources/generated/poker/aces/`; deterministic export and alignment are documented in `aces.md`.

## Initial Spades reference

The first Spades image supplied the reference for the enlarged version below. Its prompt was:

```text
Use case: style-transfer. Design the ACE OF SPADES for this existing botanical playing-card deck.
IMAGE 1: aligned King of Spades, primary reference for exact framing, card proportions, corner index cartouches, line quality and palette.
IMAGE 2: Lamp Black back, supporting reference for floral ornament and palmette/rosette/acanthus vocabulary.
OUTPUT: ONE flat full-card PNG, 5:7 portrait poker proportions, request 750 x 1050 pixels. Full card fills canvas, no perspective, mockup or external background.
KEEP THE APPROVED FRAME: replicate image 1's thin warm-ivory card edge, small rounded corners, uninterrupted rectangular gold-beaded border and narrow near-black floral perimeter band, same small red-tipped ivory blossoms, gold/olive scrolling acanthus, red berries, same positions/scale. Same decorative ivory index cartouches top-left and bottom-right. Same large ivory-and-gold lobed interior cartouche shape surrounded by dark botanical ornament. The common palette is antique gold, warm ivory, muted olive, madder flower accents and a near-black field. No new back-color theme.
REMOVE THE COURT FIGURE ENTIRELY: no person, head, face, hands, crown, clothing, weapons or diagonal sash. In place of the figure create an open warm-IVORY central field inside the existing lobed cartouche, with delicate fine gold/olive botanical scrolls hugging only its outer edges. Keep center uncluttered and spacious.
CENTRAL ACE: exactly ONE large ornate BLACK SPADE silhouette centered at x=50%,y=50%, occupying about 42% of card width and 36% of height (at 750x1050 about x=217..533 and y=336..714). Clear conventional pointed spade outline with two rounded shoulders and distinct short flared stem. The silhouette must remain overwhelmingly readable as a black spade. Fine antique-gold/ivory botanical ornament INSIDE the black silhouette: balanced curling acanthus, small palmettes and restrained red-tipped ivory flowers, adapted directly from supplied back pattern. Within this single emblem, put ONE small eight-petal ivory rosette with a tiny turquoise/blue-green central jewel at the exact canvas center (375,525 in target raster). This jewel is a registration anchor like the court-card central flower. Tasteful gold double hairline along spade outline. Do not draw a second inverted spade, no extra large suit symbols, no pseudo-letters inside the spade. Surrounding blank ivory separates emblem from dense border.
INDICES: bold clear BLACK serif 'A' above solid BLACK small SPADE in the same top-left ivory cartouche as the king, exact 180-degree rotated A/spade pair bottom-right. Same letter cap height and stroke weight as K. Exactly two A characters. No K, Q, J. No other text: no title, names, company, logo, dates, tax wording, ribbon labels, watermark or signature.
ORIENTATION: the single main spade is upright, vertically bilateral in its ornament. The outer framing and two index panels are arranged double-ended as on the courts. Do NOT duplicate central pip to force rotational symmetry.
STYLE: meticulous softly shaded printed botanical illustration, crisp fine warm/gold contour and rich pigments, matching Morris/Safavid ornament around the existing Mucha court cards. No photorealism, no flat vector placeholder, no skulls, death symbolism, distress or vintage paper aging. An elegant spacious ace belonging to exactly the same deck.
```

## Spades — final revision

Reference: initial ornate Spades image.

```text
Use case: precise-object-edit. Edit this Ace of Spades playing card. Preserve the existing full card, corner A/spade indices, ivory edge, botanical rectangular border, ivory lobed inner cartouche, fine gold and olive acanthus style and palette.
CHANGE ONLY THE SIZE OF THE CENTRAL ORNATE SPADE. Enlarge the beautifully decorated black spade so it fills MOST of the available ivory middle area. At 750x1050 target raster the spade should extend roughly x=160..590 and y=220..825: noticeably taller and larger than the input, remaining fully inside the ivory field with a small elegant ivory breathing gap separating its outline from surrounding scrolls. Keep its recognizable spade shape, sharp top, rounded shoulders and flared stem. Retain the same intricate gold curling acanthus, red-tipped ivory blossoms and berries inside its black field, gold double outline, and central ivory flower with small turquoise jewel. Put the CENTER OF THAT TURQUOISE JEWEL precisely at 50% width and 50% height of full canvas. Expand the ornament above and below it to make the emblem taller, not just lower on the page.
No text changes, no extra symbols, no logo. Same single upright central spade, two opposite corner indices. Output ONE flat full-card image 5:7 portrait, requested 750x1050. Preserve original print illustration style and detail. The enlarged emblem is the focal point and uses most of the central blank space.
```

## Hearts — final revision

Reference: enlarged Spades master (`sources/generated/poker/aces/spades.png`).

```text
Use case: precise-object-edit. Create a matching ornate ACE by editing this enlarged ornate Ace of Spades.
Preserve the full card's ivory edge, rounded corners, dark floral perimeter frame, two ivory index cartouches, lobed ivory central field and its gold/olive scrollwork. Same pigment palette, fine illustrative botanical print style and painstaking detail.
REPLACE ONLY the central spade and the two corner index contents with the specified suit. The new central suit emblem must be LARGE and LAVISHLY ORNAMENTED like the supplied spade: gold double-outline around an unmistakable conventional suit silhouette; rich curling antique-gold and olive acanthus, red-tipped ivory flowers, palmettes and red berries INSIDE the silhouette; one central ivory rosette with turquoise jewel centered precisely at (375,525) in target 750x1050 canvas. Fill most of the available middle ivory area with the emblem while keeping a modest ivory gap separating it from the surrounding scrollwork. Keep the ornament balanced about its vertical centerline, and keep a substantial amount of suit-colored ground visible between botanical elements so the suit reads clearly.
Indices are serif A above a small SOLID conventional suit pip at top-left, identical pair rotated180degrees bottom-right. Exactly two A letters. One single upright large central emblem, no second inverted emblem. No people, other letters, words, logo or signature.
ONE flat full-card PNG, 5:7 portrait, request750x1050. Retain source border positions and colors.
SPECIFIC SUIT: HEARTS. Replace black spade with a deep MADDER-RED HEART silhouette, with two broad rounded lobes, distinct central top notch, and pointed bottom. Red field with intricate gold/ivory botanical ornament throughout, matching the lushness of the reference. Central heart about 440 pixels wide and 430pixels tall on750x1050, x155..595,y310..740, with turquoise jewel atcanvascenter. Both A letters and both small corner hearts deep madder red. No spade shape or stem anywhere; the main heart ends in one graceful point.
```

## Diamonds — final revision

Reference: enlarged Spades master (`sources/generated/poker/aces/spades.png`).

```text
Use case: precise-object-edit. Create a matching ornate ACE by editing this enlarged ornate Ace of Spades.
Preserve the full card's ivory edge, rounded corners, dark floral perimeter frame, two ivory index cartouches, lobed ivory central field and its gold/olive scrollwork. Same pigment palette, fine illustrative botanical print style and painstaking detail.
REPLACE ONLY the central spade and the two corner index contents with the specified suit. The new central suit emblem must be LARGE and LAVISHLY ORNAMENTED like the supplied spade: gold double-outline around an unmistakable conventional suit silhouette; rich curling antique-gold and olive acanthus, red-tipped ivory flowers, palmettes and red berries INSIDE the silhouette; one central ivory rosette with turquoise jewel centered precisely at (375,525) in target 750x1050 canvas. Fill most of the available middle ivory area with the emblem while keeping a modest ivory gap separating it from the surrounding scrollwork. Keep the ornament balanced about its vertical centerline, and keep a substantial amount of suit-colored ground visible between botanical elements so the suit reads clearly.
Indices are serif A above a small SOLID conventional suit pip at top-left, identical pair rotated180degrees bottom-right. Exactly two A letters. One single upright large central emblem, no second inverted emblem. No people, other letters, words, logo or signature.
ONE flat full-card PNG, 5:7 portrait, request750x1050. Retain source border positions and colors.
SPECIFIC SUIT: DIAMONDS. Replace black spade with a deep MADDER-RED elongated DIAMOND, a rhombus with four straight sides and crisp top/right/bottom/left points. Large red field containing the intricate gold/ivory floral ornament from the spade, equally lush throughout. Central diamond about430pixels wide and610pixels tall at750x1050, x160..590,y220..830, turquoise jewel centered at375,525. Clear sharp geometric diamond outline, no heart lobes or spade stem. Both A letters and both small corner diamond pips deep madder red.
```

## Clubs — final revision

Reference: enlarged Spades master (`sources/generated/poker/aces/spades.png`).

```text
Use case: precise-object-edit. Create a matching ornate ACE by editing this enlarged ornate Ace of Spades.
Preserve the full card's ivory edge, rounded corners, dark floral perimeter frame, two ivory index cartouches, lobed ivory central field and its gold/olive scrollwork. Same pigment palette, fine illustrative botanical print style and painstaking detail.
REPLACE ONLY the central spade and the two corner index contents with the specified suit. The new central suit emblem must be LARGE and LAVISHLY ORNAMENTED like the supplied spade: gold double-outline around an unmistakable conventional suit silhouette; rich curling antique-gold and olive acanthus, red-tipped ivory flowers, palmettes and red berries INSIDE the silhouette; one central ivory rosette with turquoise jewel centered precisely at (375,525) in target 750x1050 canvas. Fill most of the available middle ivory area with the emblem while keeping a modest ivory gap separating it from the surrounding scrollwork. Keep the ornament balanced about its vertical centerline, and keep a substantial amount of suit-colored ground visible between botanical elements so the suit reads clearly.
Indices are serif A above a small SOLID conventional suit pip at top-left, identical pair rotated180degrees bottom-right. Exactly two A letters. One single upright large central emblem, no second inverted emblem. No people, other letters, words, logo or signature.
ONE flat full-card PNG, 5:7 portrait, request750x1050. Retain source border positions and colors.
SPECIFIC SUIT: CLUBS. Replace black spade with a LAMP-BLACK CLUB silhouette: three distinct generous round lobes, one on top and one each side, plus a short flared stem. Overall large club about460pixels wide and540pixels tall at750x1050, x145..605,y255..795. Rich black field with gold acanthus and ivory flowers throughout ALL THREE LOBES and stem, same abundant treatment as the reference spade. Center ivory flower and turquoise jewel at375,525. Round top lobe, never a sharp spade point. Both A letters and both small corner CLUB pips black. One large club, no spades left.
```

