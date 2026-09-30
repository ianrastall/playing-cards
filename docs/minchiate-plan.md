# Minchiate conversion

On 2026-09-25 the user selected historical Minchiate subjects and order for
both designs, retaining each design's art style. Complete Design 1 first,
then create Design 2 Tarot using the same inventory.

The previous Design 1 release was a complete **standard 78-card Tarot**.
Its replacement is **97-card Florentine Minchiate**: 40 pip cards,
16 courts, 40 trumps, and the separate, unnumbered Fool. No Jokers.
Neither tradition is an incomplete version of the other.

## Historical basis and design choices

- [Pagat: Minchiate](https://www.pagat.com/tarot/minchiate.html): inventory,
  suits, rank structure, Roman-numbered I–XXXV, five unnumbered Arie,
  separate Fool, maids in Cups/Coins and hybrid Cavaliers.
- [Minchiate trump table](https://en.wikipedia.org/wiki/Minchiate#Trumps):
  detailed order and historical variations in the Papi identities.
- [Etruria reference cards](https://www.wopc.co.uk/italy/minchiate/etruria-minchiate):
  visual evidence for hybrid courts and several distinctive allegories.
- [Earlier Florentine reference](https://www.wopc.co.uk/italy/minchiate/minchiate-fiorentine-17th-c):
  additional historical pattern reference.

This is an original illustrated interpretation of the historical structure,
not a facsimile of a specific surviving pack. Keep existing frame geometry,
gold tracery, print dimensions, and art direction. English titles are a modern
reading aid. Historical Papi II–IV have variable identifications; use Empress,
Emperor, and Eastern Emperor for this interpretation, recording their Papi
numbers as aliases rather than claiming universally fixed historical names.

Use Roman numerals I–XXXV in the existing paired side panels. Leave the Fool
and the five Arie unnumbered; retain their identifying titles. Store the Arie
ranking positions 36–40 separately from printed numbers. Fit longer Roman
indices to the panel without widening the panel or distorting the glyphs.

## Conversion requirements

- Retain the four Latin suits and A–10. Audit the long-suit arrangements
  against Minchiate's crossed straight swords and batons.
- Retain Kings and Queens where their subject attributes match. Swords and
  Batons retain male Jacks; Cups and Coins need female Maids. Replace the four
  mounted Knights with Cavaliers whose human and beast bodies form one
  creature. Their exact forms vary across historical packs.
- Add Hope, Prudence, Faith, Charity; Fire, Water, Earth, Air; and the twelve
  zodiac subjects in Minchiate order (not calendar order).
- Replace the High Priestess/Hierophant pairing with the selected Papi
  subjects. Do not count retired standard-Tarot subjects among the 97.
- Audit every existing trump illustration before reuse. In particular, Time
  needs an hourglass and crutches, the House of the Devil a burning house,
  and the Moon an astrologer. The Fool, Bagatella, Love, Wheel, Chariot,
  Hanged Man, Death, Star, Sun, World, and Trumpets also need iconographic
  review; simply retitling Rider–Waite imagery is insufficient.
- Preserve the current 78-card release until all replacement artwork has
  been prepared, rendered, visually inspected, and mechanically validated.
  Archive superseded faces with hashes during promotion.
- Update renderer, inventory validation, catalog, galleries, release packaging,
  and current documentation together when the 97-card set is ready. Do not
  advertise an unfinished set as 97 completed cards.

## Work status

Design 1 is complete: 97 faces rendered and inspected, with original artwork
and the previous 78-card release preserved. The user selected the existing
upside-down Tarot illustration for the Hanged Man on 2026-09-27; this is an
explicit iconographic exception. All other replacement subjects, the female
Maids, hybrid Cavaliers, and crossed straight long suits are implemented.
The catalog, galleries, and v1.2 Tarot-size packaging use the 97-card inventory.
See `designs/design1/docs/design/minchiate-v1-report.json` for validation.

Design 2 now has all 97 Minchiate faces in Poker size, with original illustration
masters, exact prompts and balanced exports preserved. Its first four proofs
were rebalanced before completing the rest. See
`designs/design2/docs/design/minchiate-poker-v1.json` for source hashes,
placements, shared-border checks and center measurements. Review of the complete
Design 2 collection and artwork for the other formats remain later stages.
Older reports remain records of the earlier releases.

On 2026-09-29 the user refined Design 2's direction: preserve card names,
inventory, ranks and usefulness, but give Chinese visual traditions priority
over European iconography. Western zodiac identities stay. Christian Faith
may become Buddhist devotion; other allegories may be reinterpreted where
recognition remains clear. This supersedes the earlier requirement to retain
every historical pictorial attribute for Design 2. Design 1 remains as selected.
See `designs/design2/docs/design/chinese-visual-direction.md` for the brief and
`designs/design2/sources/generated/minchiate-poker-v1/chinese-v2-prompts.json`
for the first seven revisions and their references.
