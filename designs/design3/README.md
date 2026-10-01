# Design 3 — Celtic

[All designs](../../README.md) · [Card viewer](index.html) · [Official Poker Kings](poker.html)

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
production normalization. The catalog now contains these four approved Kings.

The [initial Spades trio](sources/generated/courts-v1/README.md) remains preserved
as earlier work. No new Queens or Jacks were created in this revision.

Next: extend the approved direction to Queens and Jacks using the established
frame and center join. Backs,
aces, numbers, Jokers and other formats follow after the court direction is
settled. Design 4's Norse exploration is deferred.

From the repository root:

```text
python scripts/catalog.py --check
python scripts/build_gallery.py --check
python designs/design3/scripts/register_kings.py --check
python -m unittest discover -s scripts -p "test_*.py"
```
