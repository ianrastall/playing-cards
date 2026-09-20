# Tarot full run — asset preparation and render plan

## Scope and stopping point

The user requested a full-run plan, generation of the missing assets, then a
pause before the run. This phase creates illustrations, prepared components,
index glyphs, provenance records and asset contact sheets only. It does not
assemble 78 faces, promote cards, update the active catalog, or package releases.

The four review proofs establish the working art direction. Continuing the
asset preparation does not record individual approval of every symbol, label,
or composition. These remain editable before the full rendering pass.

## Inventory and missing assets

Asset preparation is complete: all 39 planned illustrations and both new index
glyphs are saved. The prepared inventory resolves artwork for all 78 cards with
no missing assets or mechanical warnings. See [asset results](tarot-full-assets-v1-results.md)
for checks, corrections, provenance and inspection sheets. The user subsequently
resumed the run; all 78 faces are now staged and validated. See the
[full-pack results](tarot-full-v1-results.md). Catalog promotion remains after
visual review.

[The production inventory](tarot-full-production-v1.json) enumerates every card:
40 aces/numbers, 16 courts, and 22 trumps including the Fool. No French Jokers.

| Asset group | Reuse | New generation |
| --- | --- | --- |
| Suits | Straight and curved Swords | One Baton, one lidded Cup, one Coin master |
| Ace furniture | Crown and foliage sprig | None initially |
| Courts | Queen of Cups | 15 original court illustrations |
| Trumps | The Empress | 21 original trump illustrations |
| Frame/background | Botanical frame, field/panel masks, gold tracery, corner mask | None |
| Indices | Sword, Cup, trump star; serif typography | Baton and Coin glyphs drawn in code |

**39 new generated illustrations**, plus two code-native index glyphs. Keep
illustrations separate from labels and frames. A material problem found in
layout may justify a later named variant; do not speculatively generate extra
blade shapes or a separate painting for each numbered card.

New courts: Page/Knight/Queen/King of Swords, Batons and Coins; Page/Knight/King
of Cups. Distinct adult figures and poses; mounted Knights; suit emblems must
remain clear. Match the review artwork's style and use the relevant emblem
master as an additional reference once it exists.

Working trump sequence: 0 The Fool; 1 The Magician; 2 The High Priestess;
3 The Empress (reuse); 4 The Emperor; 5 The Hierophant; 6 The Lovers;
7 The Chariot; 8 Strength; 9 The Hermit; 10 Wheel of Fortune; 11 Justice;
12 The Hanged Man; 13 Death; 14 Temperance; 15 The Devil; 16 The Tower;
17 The Star; 18 The Moon; 19 The Sun; 20 Judgement; 21 The World.
This is the deck's working sequence, not a claim of universal Tarot numbering.
Full titles and Arabic side indices are composited later.

## Generation and preparation

1. Generate the three missing suit masters against existing sword/Queen style
   references. Check full silhouettes, symmetry where appropriate, readable
   emblems and clean transparency.
2. Generate each remaining court separately using the established figure style
   and the relevant suit master. Keep crown, hands, emblem, horse and feet
   inside the image; full figures and transparent surrounding space.
3. Generate the 21 remaining trump compositions separately. Each prompt records
   essential iconographic attributes; retain transparent gaps and contained
   foreground elements. No baked border, index, lettering or title.
4. Save exact prompts, reference paths, raw output and hashes. Prepare alpha
   components with explicit crop bounds, pixel-center anchors and provenance.
   Inspect on ivory; a black-looking preview does not establish failed alpha.
5. Draw the two small missing index masks using the existing glyph vocabulary.
   Reuse serif index/title typography; no image generation for letters.
6. Build asset-only contact sheets and an inventory report. Inspect anatomy,
   attributes, alpha, margins and consistency. Correct failures before calling
   the asset phase complete. Record any remaining review concerns explicitly.
7. **Pause here.** Do not invoke full-deck staging or promotion.

## Full run

1. **Complete.** Extend the review compositor to consume all 78 inventory entries. Retain
   825 × 1425 native RGBA, 300 ppi, 3.5 mm corner alpha, existing botanical frame,
   paired upper-left/lower-right panels, and masked front-tracery-v3.
2. **Complete.** Create deterministic per-suit layouts for A–10. Cups/Coins use countable rows
   or symmetric groups; Batons use deliberate crossed arrangements; Swords use
   the two existing blade shapes. Reuse the reviewed open Ten concept where
   suitable, with explicit crossing masks. Decorative furniture never increments
   suit-emblem count. Do not infer count from image content alone.
3. **Complete.** Place each figure with recorded scale, anchor, target center and keep-out
   clearance. Apply full court/trump titles in the lower interior band. Use
   A/2–10/P/N/Q/K plus suit glyph; 0–21 plus star for trumps.
4. **Complete.** Working artwork policy is upright, including the current Ten. Side indices
   remain paired by half-turn. Declare and test any reversible pip layouts
   individually; never infer reversibility from index pairing.
5. **Complete.** Stage all 78 outside active paths. Validate inventory, exact emblem counts,
   visible counting, title spelling, alpha, anatomy, source hashes, repeatable
   output, font provenance and frame/panel/title containment. Inspect native
   images, contact sheets and print-scale samples.
6. **Awaiting user visual review.** Review the complete staging set before catalog promotion. Then implement
   Tarot-aware IDs/metadata/gallery support and print packaging as a separate
   promotion step. Preserve existing French faces and all current backs.

## Files

- `sources/generated/tarot-full-assets-v1/`: raw images, exact prompts/results.
- `sources/components/tarot/full-assets-v1/`: prepared RGBA and new index masks.
- `docs/design/tarot-full-production-v1.json`: complete card inventory and reuse.
- `docs/design/tarot-full-assets-v1.json`: generated/prepared component inventory.
- `work/tarot-full-assets-v1/`: asset inspection sheets and alpha checks only.

The full-production inventory is not yet a placement manifest. Numeric card
positions and crossing masks belong to the later run after this explicit pause.
