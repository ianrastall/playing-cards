# Design 3 — Celtic

[All designs](../../README.md) · [Card viewer](index.html) · [Poker faces](poker.html) · [A–10](a-10.html) · [Queens](queens.html) · [Jacks](jacks.html) · [Jokers](jokers.html) · [Large pips](pips.html)

The **four approved Poker Kings** establish the rugged Celtic direction.
The artwork was generated with built-in ImageGen and saved unchanged in
[sources/generated/kings-v2/](sources/generated/kings-v2/README.md).
The viewer opens the official 750 × 1050 faces; **Original artwork masters**
shows the four unchanged generated originals separately.

La Tène spirals, red-glass accents and bronze-inspired adornment combine with
Insular interlace, oak branches and creamy reserves. Weathered faces, substantial
green wool and plain linen establish the earthier character. These are fictional courts and a
deliberate synthesis of periods, rather than archaeological reconstructions.
The [King revision notes](docs/design/kings-v2.md) record the current direction.
The [first brief and court matrix](docs/design/celtic-courts-v1.md) retain the
reference discussion and complete court plan.

| Court | Official face |
| --- | --- |
| King of Spades | Upright sword; two eyes, slight rightward turn |
| King of Hearts | Sword behind head; two eyes and no moustache |
| King of Diamonds | Axe; strict left profile, one visible eye |
| King of Clubs | Sword and bronze orb; left three-quarter view, two eyes |

Official faces live in [cards/faces/french-suited/poker/](cards/faces/french-suited/poker/)
as 750 × 1050 RGBA PNGs at 300 ppi, for 2.5 × 3.5 inch trim with 3.5 mm rounded alpha corners.
All four use one Spades-derived Celtic border, consistent K/suit indices and
one painted medallion at the exact canvas center **(374.5, 524.5)**. Each card is
pixel-identical after a 180-degree turn. A narrow robe blend softens the waist
join, and the side roundels share its horizontal axis.

The originals remain 1060 × 1484, except Spades at 1061 × 1483, and retain their
recorded hashes. The [registration notes](docs/design/kings-registration-v1.md),
[release manifest](docs/design/kings-registration-v1.json) and
[audit](docs/design/kings-registration-v1-audit.json) document the deterministic
production normalization. The catalog contains these four approved Kings and
forty A–10 faces with review status.

The **four Poker Queens are now ready for review** in [their viewer](queens.html).
They share the Kings' border and center, with exact opposing halves and consistent
Q/suit indices. Spades carries a spiral scepter; Hearts a red rose; Diamonds a
pointed ivory flower; Clubs a white blossom and closed bud. The portraits retain
the established suit-specific turns, with both eyes visible on every Queen.
[Queen notes](docs/design/queens-v1.md), [proof](docs/design/queens-v1-proof.png)
and [prompts](sources/generated/queens-v1/prompts.json) document the new work.
The Queens are listed separately as review artwork.

The [initial Spades trio](sources/generated/courts-v1/README.md) remains preserved
as earlier work.

**Four Jacks and two Jokers are also ready for review.** The Jacks preserve
the spear, leaf, straight sword and feathered shaft attributes and established
portrait directions. The Black Joker is a storyteller with a carved fool's
staff; the Red Joker is a woman bard with a small wooden harp. All six share
the court border, center, rounded corners and exact opposing halves.
[Design notes](docs/design/jacks-jokers-v1.md) document the generated masters,
prompts and balancing audit. Dedicated [Jack](jacks.html) and [Joker](jokers.html)
pages keep each group easy to review alongside the Queens.

**Four large suit pips are ready for review** in the [pip viewer](pips.html).
They combine bronze interlace, oak leaves, acorns and double spirals with clear
dark Spades/Clubs and red Hearts/Diamonds. The transparent originals are reusable
artwork for the ace and numeral layouts; they are separate from finished cards.
[Master files and exact prompts](sources/components/pips-v1/README.md) and a
[large/small proof](docs/design/pips-v1-proof.png) record the new work.

**All forty Poker A–10 faces are assembled for review** in the [A–10 viewer](a-10.html).
They use the established border and pip masters, with consistent indices and
central registration. Even ranks are exactly reversible; A, 3, 5, 7 and 9 keep
one upright center pip while pairing every other pip with its rotated partner.
[Assembly notes and suit proofs](docs/design/a10-v1.md) explain the layouts;
the [audit](docs/design/a10-v1-audit.json) verifies all forty cards. Together with
the courts and Jokers, all 54 Poker faces are now available to view, with the
Queens, Jacks and Jokers still in their separate review sets.

The Poker viewer's **All faces** contains all 54 faces, including the review
courts and Jokers. Suit views contain all thirteen ranks, and the Jokers view
contains both colors. The dedicated review views remain available alongside
the complete deck.

Backs and other formats remain to be developed. Design 4's Norse exploration is deferred.

From the repository root:

```text
python scripts/catalog.py --check
python scripts/build_gallery.py --check
python designs/design3/scripts/register_kings.py --check
python designs/design3/scripts/register_queens.py --check
python designs/design3/scripts/register_jacks_jokers.py --check
python designs/design3/scripts/inspect_pips.py --check
python designs/design3/scripts/build_a10.py --check
python -m unittest discover -s scripts -p "test_*.py"
node scripts/test_gallery_filters.js
```
