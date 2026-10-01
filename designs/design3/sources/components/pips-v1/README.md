# Large Celtic suit pip masters

Four reusable transparent PNG masters for the Design 3 aces and numeral cards:

| Suit | Master | Exact ImageGen prompt |
| --- | --- | --- |
| Spades | [PNG](spades-master.png) | [Prompt](spades-prompt.json) |
| Hearts | [PNG](hearts-master.png) | [Prompt](hearts-prompt.json) |
| Diamonds | [PNG](diamonds-master.png) | [Prompt](diamonds-prompt.json) |
| Clubs | [PNG](clubs-master.png) | [Prompt](clubs-prompt.json) |

Built-in ImageGen generated each master in one pass. The Celtic Spades Queen
supplied the initial style reference; the Design 2 Spade supplied only the
silhouette and isolated-component construction. The new Celtic Spade then
supplied the style reference for the other three suits.

Dark woad-blue/charcoal Spades and Clubs contrast with deep red Hearts and
Diamonds. Bronze/gold interlace traces the suit outlines; paired oak leaves,
acorns, spirals, red glass bosses and a two-coil central medallion tie them to
the courts. These are fictional Celtic artistic designs, not replicas of
historical objects. No card frames, rank indices or background are included.

All four originals are preserved unchanged, including their generated alpha.
[manifest.json](manifest.json) records dimensions, SHA-256 hashes, measured
silhouette bounds at alpha ≥128, alpha centroids, transparent/near-opaque
fractions and faint edge residue. The generated interiors are near-opaque,
and faint exterior alpha remains in the source. Production copies should
normalize this alpha and clean the faint residue during card layout, as in the
earlier design workflow. Canvas midpoints and alpha centroids must not be
assumed to be the medallion anchors.

Preserve aspect ratio and alpha when sizing. These are reusable artwork masters
for review, separate from the finished-card catalog. Their future placement,
optical size and ornament anchors will be registered when composing the cards.

[Pip viewer](../../../pips.html) ·
[Large and 100-pixel proof](../../../docs/design/pips-v1-proof.png)

From the repository root:

```text
python designs/design3/scripts/inspect_pips.py --check
```
