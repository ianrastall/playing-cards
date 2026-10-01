# First Celtic Poker court studies

Historical first pass. The active viewer now shows the
[four official rugged Kings](../../../docs/design/kings-registration-v1.md);
these original files remain preserved.

Three unmodified built-in ImageGen outputs, each 1060 × 1484 pixels (5:7).

| Rank | Master |
| --- | --- |
| King of Spades | [king-spades-v1.png](king-spades-v1.png) |
| Queen of Spades | [queen-spades-v1.png](queen-spades-v1.png) |
| Jack of Spades | [jack-spades-v1.png](jack-spades-v1.png) |

[prompts.json](prompts.json) contains every exact prompt, reference path and
transparency setting. The King used Design 1's King of Spades as a composition
reference; the Queen and Jack used the Celtic King as their style reference.
The generated files were copied byte for byte. No raster alterations were made.

[manifest.json](manifest.json) records dimensions, SHA-256 hashes and comparisons
with each image's 180-degree rotation. All three fail exact half-turn equality.
Center roundels retain three-spiral motifs despite a two-spiral request in the
Queen/Jack prompts. The center needs redesign during production.

Visual inspection checked rank/suit indices, portrait direction, visible eyes,
headwear, held attributes, object clearance, full canvas, palette and coordinated
geometric borders. The cloak fasteners are decorative brooch interpretations;
this pass does not reproduce the mechanics of a specific penannular brooch.
Naturalistic faces, royal circlets, tailored sleeves and generous gold tones are
illustration choices, not evidence of one historical costume or pigment recipe.

These remain initial studies, without user approval or production registration.
The [design brief](../../../docs/design/celtic-courts-v1.md) records their limits
and the court plan.
