# Design 2 Minchiate: first Poker proofs

The first four draft proofs are The Empress (II), Queen of Cups, Ace of Swords,
and Ten of Swords. They exercise a trump, a court, a large suit emblem and a
counted pip composition before the rest of the 97-card inventory is drawn.

[Open the single-card review](../../minchiate-review.html) or the
[four-card proof sheet](../../sources/components/minchiate-poker-v1/review.jpg).

## Artwork and construction

Three new illustrations were generated with built-in ImageGen: an upright
Empress, an upright Queen of Cups, and one straight ornamental jian sword.
The selected Design 2 Queen of Hearts supplied the painted style: red phoenix
robes, dark teal lotus bands, warm gold, pearls and turquoise details. Design
1's Empress supplied subject attributes only. These are contemporary stylized
illustrations, not historical reconstructions.

Original RGBA masters and exact prompts are preserved in
`sources/generated/minchiate-poker-v1/`. The swords on both pip proofs come from
the same new master; the Ten has five crossed pairs with ten explicit instances.
No complete pip card was generated as a single painting.

The compositor uses the existing 750 × 1050 Poker frames and outline mask,
with Lamp Black for Swords/trumps and Madder Lake for Cups. Border pixels
outside the field and index panels are unchanged. Paired side indices are
rotated by 180 degrees. The small neutral sword, cup and trump-star index
masks are reused from Design 1 with their source paths and hashes recorded.
Titles are typeset separately; generated lettering is not used.

Placement uses the canvas center `(374.5, 524.5)` and records component crops,
scales, rotations and bounds. This establishes common layout geometry; it does
not claim that every painted jewel or perceived center has been balanced.
That full-set visual alignment pass remains a later roadmap stage. Courts
and trumps retain the upright Minchiate approach; these proofs are not two-way
French-suited courts.

## Status and next work

Four of 97 cards have draft proofs; 93 remain pending. No Minchiate face has
been promoted into `cards/`, and the active production catalog is unchanged.
The complete inventory, including the unnumbered Fool and five unnumbered Arie,
is inherited from `docs/minchiate-97.json` without renaming its subjects.

The next artwork work is the remaining suit components (Batons, Cups and
Coins), followed by the rest of the courts and trumps. Keep Maids for Cups and
Coins and the hybrid Cavalier figures from the selected Minchiate inventory.
Preserve the existing Hanged Man subject exception when its new illustration
is drawn. Expand pip layouts with explicit counts and anchors.

## Rebuild and check

Run from the repository root:

```text
python designs/design2/scripts/build_minchiate_review.py
python designs/design2/scripts/build_minchiate_review.py --check
```

The checker rerenders all four proofs and compares pixels, native dimensions,
RGBA mode, 300 ppi metadata, source hashes, the inventory and the generated
review page. It also checks unchanged frame pixels, field/index/title-band
containment and pip instance counts. The manifest is `minchiate-poker-v1.json`
beside this document. The renderer uses the existing Windows Times Bold font
and records its hash.
