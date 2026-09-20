# Tarot full-run assets — completed preparation

All assets in the full-run plan are present and prepared. The full 78-card
rendering pass remains paused as requested by the user.

## Inventory

| Group | Newly created | Reused |
| --- | ---: | --- |
| Suit masters | 3: Baton, Cup, Coin | Straight and curved Swords |
| Court illustrations | 15 | Queen of Cups |
| Trump illustrations | 21 | The Empress |
| Ace furniture | 0 | Crown and foliage |
| Index masks | 2: Baton and Coin | Sword, Cup and trump star |

There are 39 new generated illustrations and two code-drawn glyphs. Nine review
components are reused, for 50 recorded components. Existing Design 1 frame,
panel masks, corner mask, background tracery and typography remain the shared
inputs described in the review layout. Numbered cards will reuse the suit
masters with explicit positions, rotations and crossing masks during the run.

## Generation and selected corrections

Illustrations were created with the built-in image generation tool. Original
outputs are preserved under `sources/generated/tarot-full-assets-v1/`.
[Exact prompts and references](../../sources/generated/tarot-full-assets-v1/actual-prompts.json),
[generation results](../../sources/generated/tarot-full-assets-v1/generation-results.json)
and [selected revisions with exact edit prompts](../../sources/generated/tarot-full-assets-v1/asset-selections.json)
record their provenance. The earlier `prompts.json` is the initial plan;
`actual-prompts.json` records the prompts actually used, including suit references.

Four corrected versions are selected; originals remain available:

- Knight of Cups: removed a stray sheathed sword so the cup is its sole suit emblem.
- The Tower: brought the lightning's upper endpoint inside the canvas.
- Judgement: contained the complete trumpet and wings inside the canvas.
- The Star: corrected the cluster to one large star and seven small stars.

Prepared components have transparent RGBA backgrounds, recorded crop bounds,
pixel-center anchors and SHA-256 hashes. They are saved under
`sources/components/tarot/full-assets-v1/`. Masks use grayscale coverage.

## Validation

`python scripts/prepare_tarot_assets.py` completed successfully:

- 39 of 39 planned illustrations prepared; no missing assets.
- All 78 planned card primary artwork references resolved.
- Two new glyphs and all nine reused review components present.
- RGBA/transparency checks passed; no opaque source-edge warnings.
- Reused component hashes matched the review manifest.
- All four asset contact sheets visually inspected on ivory, including the revisions.

`python scripts/catalog.py --check` passed for all 300 active PNGs, IDs, hashes,
dimensions and inventory. No Tarot faces were promoted and no active artwork
was changed by this phase.

The [prepared inventory](tarot-full-assets-v1.json) contains component paths,
hashes, source crops, anchors, reference hashes and the selected revisions.
These checks establish asset readiness. Exact fit, countable pip arrangements,
side-panel clearance and title placement require the subsequent card compositor
and its staged review; they have not yet been validated across 78 faces.

## Inspect the artwork

- [Asset gallery](../../work/tarot-full-assets-v1/index.html)
- [Suit masters and furniture](../../work/tarot-full-assets-v1/suit-masters.jpg)
- [All 16 courts](../../work/tarot-full-assets-v1/courts.jpg)
- [Trumps 0–10](../../work/tarot-full-assets-v1/trumps-00-10.jpg)
- [Trumps 11–21](../../work/tarot-full-assets-v1/trumps-11-21.jpg)
- [New index glyphs](../../work/tarot-full-assets-v1/new-index-glyphs.png)

The gallery is asset-only; it contains no new complete card faces. `work/` is
ignored by Git and can be regenerated with the preparation command above.

## Pause boundary

The [full-run plan](tarot-full-run-plan-v1.md) and
[78-card inventory](tarot-full-production-v1.json) are ready for the next phase.
No full-deck staging, promotion, catalog update or release packaging was run.
Resume with deterministic placement and rendering only when the user requests it.
