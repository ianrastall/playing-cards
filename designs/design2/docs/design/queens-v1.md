# Design 2 Queens

Four generated Queens match the four Kings that the user explicitly accepted
as finished. Spades was generated from the approved King of Spades; Diamonds
and Clubs from the new Queen of Spades. The selected Hearts adapts Diamonds'
correctly opposed portrait layout with a rose, heart indices and crown details.

| Suit | Selected artwork | Pose and attribute |
| --- | --- | --- |
| Spades | [Queen of Spades](../../sources/generated/courts-v1/queen-spades.png) | Slight rightward turn, both eyes; jade-and-gold scepter |
| Hearts | [Queen of Hearts](../../sources/generated/courts-v1/queen-hearts.png) | Slight leftward turn, both eyes; ivory/red rose |
| Diamonds | [Queen of Diamonds](../../sources/generated/courts-v1/queen-diamonds.png) | Slight leftward turn, both eyes; pointed-petal lotus |
| Clubs | [Queen of Clubs](../../sources/generated/courts-v1/queen-clubs.png) | Slight leftward turn, both eyes; small blossom with bud |

The Queens share madder-red phoenix robes, teal/gold embroidered bands, ivory
collars, pearl ornaments, and compact gold/teal phoenix crowns. Spades/Clubs
have black outer bands and indices; Hearts/Diamonds have red. All retain the
Kings' dense black floral ground, shaped ivory reserve, broad sleeve span,
small figure scale and turquoise center jewel.

The [Palace Museum's Ming dragon-and-phoenix crown](https://www.dpm.org.cn/collection/embroider/231038.html)
provides the historical headwear vocabulary: gold ornament, blue/teal surfaces,
pearls, red stones and phoenix/dragon forms. It was consulted as text, not used
as a raster reference. These are simplified illustrated interpretations for
the deck, not exact copies of a named empress or a complete historical outfit.
The court directions and scepter-versus-flowers distinction follow Design 1's
saved Queen conventions; European hoods/veils were replaced with Chinese headwear.

All selected PNGs are preserved built-in ImageGen outputs. Exact prompts live
in `sources/generated/courts-v1/queen-<suit>-prompt.json`; file dimensions and
hashes are recorded in the [manifest](../../sources/generated/courts-v1/queens-manifest.json).
The first Hearts version retained the wrong gaze; a correction left inconsistent
portrait directions. The selected Hearts instead derives from Diamonds and
passes visual direction review. Use `queen-hearts.png`, not the initial variant.

Visual inspection checked suit symbols, Q indices, visible eyes, flowers or
scepter, crown/frame clearance and consistent design vocabulary. Opposing
portraits are visually two-way; no new claim of pixel-exact symmetry is made.
The approved Kings were not repainted or transformed.
