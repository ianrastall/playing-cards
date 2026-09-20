# Design 1 Tarot — full staging results

The complete 78-card Tarot face set is rendered and ready for visual review.
It remains staged outside the active catalog so review changes can be made
without disturbing the existing 300 published PNGs.

## Output

- 40 suit cards: A–10 across Swords, Batons, Cups and Coins.
- 16 courts: Page, Knight, Queen and King for each suit.
- 22 numbered trumps: the Fool at 0 through the World at 21.
- Native output: 825 × 1425 RGBA at 300 ppi with the existing 3.5 mm alpha corners.
- Paired upper-left/lower-right indices on every face.
- Full titles on courts and trumps; numbered suit cards remain untitled.

The faces are in `work/tarot-full-v1/faces/`. The browsable
[78-card gallery](../../work/tarot-full-v1/index.html) links each native PNG.
Six inspection sheets divide the set by suit and trump range under
`work/tarot-full-v1/sheets/`.

## Deterministic composition

`scripts/render_tarot.py` consumes the hashed component inventory and writes the
saved [placement manifest](tarot-full-layout-v1.json). Every emblem instance has
an explicit component, center, height, rotation, mirror flag and semantic role.
Ace foliage and crowns are marked as furniture and excluded from suit counts.
Figure scale is recorded per card. No image generation occurs during rendering.

The renderer preserves the shared Design 1 botanical frame, side panels,
tracery, title band, typography and corner silhouette. It can reproduce the
complete stage with:

```text
python scripts/render_tarot.py --stage --check
```

Use `--prepare` only when intentionally regenerating the layout manifest from
the production and component inventories.

## Validation

The exact rerender check passed for all 78 native faces. It also verified:

- 78 unique IDs and all component/input/font hashes.
- Exact suit-emblem instance counts for every Ace and number card.
- Zero artwork pixels outside the interior field.
- Zero index pixels outside the paired panels.
- Zero figure pixels inside the title band.
- Stable saved-file hashes and exact pixel equality on rerender.
- Visual inspection of all six sheets and native-size samples from each class.

`python scripts/catalog.py --check` still passes for the 300 active assets,
confirming that staging did not alter the published French faces or backs.

## Review boundary

Catalog support, promotion into `cards/faces/tarot/`, and a release package come
after the user reviews the complete gallery. This preserves a clean distinction
between generated candidates and accepted active artwork.
