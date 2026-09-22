# Design 2 number-card layout

The user accepted the preceding artwork as finished and requested a larger
pip area with less ornament around the inside edges for number cards.

Use the existing [blank face frames](face-frames-v1.md) as the number-card
base. Keep the gold lotus-vine outer band, beaded inner rule and opposing
index cartouches. Use a plain antique-white central field; omit the courts'
and aces' dense inner floral fields, scalloped reserve and interior tracery.
This selects existing reusable components without changing approved artwork.

- [Black Poker frame](../../sources/components/design2-face-frames-v1/poker/lamp-black.png): Spades and Clubs.
- [Red Poker frame](../../sources/components/design2-face-frames-v1/poker/madder-lake.png): Hearts and Diamonds.

At 750 × 1050 Poker size, the field mask has bounding box
`[94, 77, 656, 973)` (exclusive right and bottom). An inset layout rectangle
`[120, 110, 630, 940)` provides 510 × 830 pixels entirely inside that mask.
This rectangle is a guide for complete pip silhouettes, not just their centers.
Other formats use their own frame masks and must be fitted independently.

Use the existing [four pip components](../../sources/components/pips-v1/README.md)
with uniform scaling. Choose pip size and spacing against the denser 8, 9 and
10 arrangements before extending to ranks 2 through 7. Keep the center clear
of any extra rosette, jewel or decorative motif that could be mistaken for a pip.

This pass records the frame choice and verifies the clear Poker layout area.
The [36 numbered faces](number-cards-v1.md) are now composed using this layout.
