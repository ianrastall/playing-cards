# Design 2 Minchiate: balanced Poker cards

All 97 Minchiate cards are drawn and balanced at 750 × 1050 pixels, RGBA,
300 ppi. [Open the card viewer](../../poker.html#design=design2&size=poker&set=minchiate)
or the [single-card proof review](../../minchiate-review.html).
The PNGs are in `cards/faces/tarot/poker/`. The
[machine-readable record](minchiate-poker-v1.json) lists all 97 proofs,
source hashes, placements and measured centers.

The subsequent [Chinese visual-direction review](chinese-visual-direction.md)
records the intended Chinese audience and the initial cultural-reference issues.
Layout completion does not mark that artwork review as complete.

## Balance and construction

The original four proofs—The Empress, Queen of Cups, Ace of Swords and Ten
of Swords—have been balanced. Their previous exports are preserved in
`sources/components/minchiate-poker-v1/before-balance/`.

Each painted composition is registered to `(374.5, 524.5)`. The anchor is
its alpha-weighted RMS color contrast against the cream field (#FAEBD7),
with a 0.08 contrast floor. Borders, indices and titles are excluded from
this measurement. The saved composition must measure within 0.2 pixels of
the common center. This balances painted visual mass; it does not force a
particular jewel or a figure's anatomical midpoint to that point.

The entire visible composition fits a common safe area, leaving the title
band and paired index panels clear. Source placement is checked for clipping
before registration. The existing Poker frame, silhouette and border pixels
are preserved. Swords, Batons and trumps use Lamp Black; Cups and Coins use
Madder Lake. Index glyph masks come from Design 1; titles and ranks are typeset
separately. No generated lettering is used.

Four individually generated suit components supply all 40 pip cards. Their
counts are explicit in the manifest. Swords and Batons form crossed pairs,
with an extra upright component for odd ranks. Cups and Coins use paired
layouts; their separate pips are checked for overlap and a minimum gap.
The 16 courts and 41 trump/Fool subjects each have their own new illustration.
Cups and Coins retain female Maids; the Cavaliers are centaurs. The Hanged
Man retains the deliberately inverted subject selected for Design 1.
The Fool and the five Arie are unnumbered; the other trumps use I–XXXV.

## Artwork sources

Original RGBA masters are preserved in `sources/generated/minchiate-poker-v1/`.
The [first prompts](../../sources/generated/minchiate-poker-v1/prompts.json)
and [continuation prompts](../../sources/generated/minchiate-poker-v1/completion-prompts.json)
record the exact built-in ImageGen requests, references and output hashes.
The first Empress and Queen of Cups established the painted style from Design
2's Queen of Hearts: silk robes, lotus ornament, red, dark teal, warm gold,
pearls and turquoise. These are contemporary stylized illustrations.

Full-resolution review confirms Cancer's eight walking legs in addition to
its two claw-bearing arms. The original was retained without an edit; this
review is recorded in
[corrections.json](../../sources/generated/minchiate-poker-v1/corrections.json).

## Rebuild and check

Run from the repository root:

```text
python designs/design2/scripts/build_minchiate_review.py
python designs/design2/scripts/build_minchiate_review.py --check --active
```

The default requires all 97 cards and selected corrections. `--apply` checks the complete
staged set before copying it into `cards/faces/tarot/poker/` and recording
the inventory in `deck.json`. `--check --active` also compares active exports.

The checker rerenders every proof and compares pixels, native dimensions,
RGBA mode, 300 ppi metadata, recorded source hashes, inventory and review HTML.
It verifies frame preservation, field/index/title containment, source clipping,
pip counts and measured centers. Windows Times Bold is used for lettering;
its file hash is recorded. Proof sheets are saved eight cards at a time for
visual inspection; the public viewer continues to show one card at a time.
