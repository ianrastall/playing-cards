# Design 2 Aces

All four selected artworks have been accepted by the user as finished.

| Suit | Selected artwork | Exact prompt record |
| --- | --- | --- |
| Spades | [Ace of Spades](ace-spades.png) | [Prompt](ace-spades-prompt.json) |
| Hearts | [Ace of Hearts](ace-hearts.png) | [Prompt](ace-hearts-prompt.json) |
| Diamonds | [Ace of Diamonds](ace-diamonds.png) | [Prompt](ace-diamonds-prompt.json) |
| Clubs | [Ace of Clubs](ace-clubs.png) | [Prompt](ace-clubs-prompt.json) |

Each ace carries one large upright lotus suit emblem in a scalloped ivory
reserve, surrounded by dense black floral fields. The existing
[pip masters](../../components/pips-v1/README.md) supplied the emblem references.
These full-card generations adapt those designs; they are not pixel-identical
composites of the transparent components. The original pip assets remain intact
for the number-card workflow.

Spades and Clubs have black outer bands and indices; Hearts and Diamonds have
red bands and indices. The gold-beaded emblem outline, teal foliage, red/ivory
lotus rosette and turquoise jewel tie the aces to the courts and backs.
Single upright central symbols follow Design 1's ace convention; only the
opposing corner indices and framing are arranged double-ended.

All four selected masters are 1060 × 1484 RGB PNGs, generated with built-in
ImageGen and preserved as returned. Dimensions and SHA-256 hashes are saved in
[manifest.json](manifest.json). The first Spades render is retained as provenance;
the selected `ace-spades.png` corrects its canvas proportions to 5:7.

Visual review checked suit readability, indices, emblem clearance and design
consistency. The jewel positions and borders are visually aligned rather than
deterministically registered. Catalog exports remain a separate workflow.
