# Design 2 Jacks

Four Jacks extend the Kings and Queens using the approved King of Spades as
the style reference. Spades was generated first; its image then served as
the reference for the three companions. All four use built-in ImageGen.

| Suit | Artwork | Upper portrait | Attribute |
| --- | --- | --- | --- |
| Spades | [Master](../../sources/generated/courts-v1/jack-spades.png) | Left profile, one eye, small moustache | Upright pike |
| Hearts | [Master](../../sources/generated/courts-v1/jack-hearts.png) | Right profile, one eye, clean-shaven | Raised olive leaf |
| Diamonds | [Master](../../sources/generated/courts-v1/jack-diamonds.png) | Slight left three-quarter, both eyes | Slender jian |
| Clubs | [Master](../../sources/generated/courts-v1/jack-clubs.png) | Slight right three-quarter, both eyes | Arrow-like shaft with cream fletching |

These identities follow [Design 1's Jacks](../../../design1/docs/design/jacks.md).
Young adult Chinese attendants wear blue round-collared robes embroidered with
lotuses and clouds, red inner collars, jade belts and stylized black court caps.
The clothing is Ming-inspired, not a reconstruction of a specific official's
rank or surviving outfit. The leaf and feathered shaft preserve the deck's
playing-card attributes rather than asserting historical Chinese court usage.

Black frames and indices distinguish Spades and Clubs; red frames and indices
distinguish Hearts and Diamonds. All four retain dense black floral fields,
shaped ivory reserves, gold ornament and diagonal joins with turquoise jewels.

The source PNGs are preserved as generated. Exact prompts are saved beside
each master in `jack-<suit>-prompt.json`, with dimensions and SHA-256 hashes in
[jacks-manifest.json](../../sources/generated/courts-v1/jacks-manifest.json).
Visual review checked the indices, facing directions, visible eyes, attributes,
frame clearance and design consistency. Compositions are visually double-ended;
pixel-exact rotational equality is not claimed. Catalog exports remain separate.

The user's requested sequence after these Jacks is: two Jokers, four aces,
then number cards. This pass generates only the four Jacks.
