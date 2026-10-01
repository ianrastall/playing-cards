# Design 3: rugged Celtic Poker Kings

Four approved King paintings replace the initial Spades trio. The active viewer
opens their balanced official faces and offers the originals separately.
The previous King, Queen and Jack remain preserved in `courts-v1/`.
This revision follows the user's approval of an earthier, nature-oriented
direction and explicit request to create only the four Kings.

## Figure direction

The revised Kings wear substantial green wool mantles over oatmeal linen, with
madder-red lining and narrow woven trims. More weathered faces, loosely arranged
hair and simpler garment shapes reduce the polished courtier impression. Oak
leaves and acorns join the blue spiral field; brooches, torcs, modest circlets
and weapon fittings concentrate the metal ornament. These are artistic choices
for fictional Celtic rulers, not portraits of named kings or a single dated
costume reconstruction. The frame keeps the earlier design's interlace vocabulary.

The Spades master was generated from the earlier Celtic King, then became the
style reference for the other suits. Existing Design 1 cards supplied companion
pose references. Every exact prompt and image input is recorded in
[prompts.json](../../sources/generated/kings-v2/prompts.json).

## Court conventions

The user means the familiar **English/Anglo-American pattern** when referring
to the suicide King and the one-eyed axe King. The [IPCS account of Paris and
Rouen](https://www.i-p-c-s.org/faq/history_13.php) distinguishes the named Paris
courts from the Rouen lineage ancestral to Anglo-American courts. The [World of
Playing Cards account](https://www.wopc.co.uk/playing-cards/suicide-king) explains
the modern Hearts sword-behind-head pose. We preserve the collection's established
poses and do not print Paris-pattern historical names.

| King | Upper portrait | Required identifying attribute | Indices |
| --- | --- | --- | --- |
| Spades | Slight right turn, both eyes | Upright sword | Black K / spade |
| Hearts | Both eyes; completely bare upper lip, jaw/chin beard | Sword behind head | Red K / heart |
| Diamonds | Strict left profile, one visible eye | Axe | Red K / diamond |
| Clubs | Left three-quarter, both eyes | Sword and spherical orb | Black K / club |

The Clubs orb is retained as a clear sphere with an equatorial red-glass band;
a small spiral finial replaces the earlier cross. This adapts the attribute to
the requested Celtic direction rather than reproducing every conventional detail.

## Selection and checks

The Hearts initial pass had a moustache and a mismatched lower sword. Two built-in
ImageGen edits corrected both faces/weapon pose and then removed an extra lower
hand introduced in the first edit. The selected output has a bare upper lip in
both portraits and two hands per portrait. Intermediate outputs and prompts are
preserved but excluded from the gallery.

Visual review checked upper and inverted suit indices, both Hearts upper lips,
hands, Diamonds' single visible eye, the two-eye views for Spades/Clubs, held
objects and frame clearance. The [manifest](../../sources/generated/kings-v2/manifest.json)
records these checks, source hashes, actual dimensions and half-turn comparisons.

Spades is 1061 × 1483; Hearts, Diamonds and Clubs are 1060 × 1484. Masters are
saved byte for byte without raster alterations. The slight Spades aspect mismatch
is recorded rather than silently stretched or cropped.

All four source masters fail pixel-exact 180-degree equality. Their new center is a double
spiral, but its painted layout is not yet a verified twofold symmetric component.
The user subsequently approved these paintings and requested official balanced
cards. Production registration is complete in separate exports: shared frame/indices,
exact opposing halves, a centered half-turn-safe medallion and 750 × 1050 Poker
geometry with rounded alpha. The originals are preserved separately; the
[registration notes](kings-registration-v1.md) describe the four official faces.

## Next work

Extend the approved figure treatment to Queens and Jacks using the shared frame.
Other Design 3 sets and Norse Design 4 remain
deferred. The [first direction brief](celtic-courts-v1.md) retains the complete
court identity matrix and historical reference discussion.
