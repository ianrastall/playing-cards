# Design 2: first King costume study

**Current status:** The user accepted all four Kings as finished and requested
the [four Queens](queens-v1.md), which are now generated and saved. The initial
reference is
[the revised King of Spades](../../sources/generated/courts-v1/king-spades-floral-jian-v3.png)
as accepted before the companion Kings. The complete generated
[four-King set](../../sources/generated/courts-v1/README.md) is now saved.
The study notes below preserve the development history; they do not revoke
that artwork approval.

[King of Spades — Ming attire study](../../sources/generated/courts-v1/king-spades-ming-study.png)
was generated with built-in ImageGen. It is a costume and composition proposal,
not a finished or registered card. The original output is preserved, with its
[exact prompt](../../sources/generated/courts-v1/king-spades-ming-prompt.json).

## Historical foundation

The [National Palace Museum's seated portrait of the Ming emperor Xuanzong](https://digitalarchive.npm.gov.tw/Collection/Detail/1875?dep=P)
describes a black gauze cap with upward-folded wings, a yellow cloud-and-dragon
robe, and a belt inlaid with precious materials. These supply the costume
foundation: yishanguan headwear, yellow silk, dragon roundels, voluminous
sleeves and a plaque belt. The card uses a fictional sovereign in Ming-inspired
imperial attire for the Western playing-card King role. It is not a portrait
of Xuanzong or a claim that all Chinese monarchs wore the same costume.

The lotus cuffs, palette, central jewel, sword pose and opposing busts adapt
the historical reference to this deck. The sword is a jian-inspired design
choice. The generated cap proportions and embroidery are stylized and should
be reviewed before production. The museum source was consulted as text; the
two raster references supplied to ImageGen were this deck's frame and spade.

## Court identity to preserve

Use the existing Design 1 English-pattern pose conventions as the deck's
continuity reference (`designs/design1/docs/design/kings.md`):

| King | Pose and identifying attribute |
| --- | --- |
| Spades | Both eyes visible, slight turn toward viewer's right; upright sword |
| Hearts | Both eyes visible; sword behind head; no moustache |
| Diamonds | Strict profile toward viewer's left, only one eye visible; axe |
| Clubs | Three-quarter view toward viewer's left, both eyes visible; sword and orb |

[Bicycle's description of one-eyed cards](https://bicyclecards.com/how-to-play/basics-of-poker)
confirms Diamonds is the one-eyed King. The [World of Playing Cards history of
the Hearts pose](https://www.wopc.co.uk/playing-cards/suicide-king) documents
the sword-behind-head convention and its development from an earlier axe pose.
These conventions refer to the familiar English pattern, not every card tradition.
The precise Chinese treatment of the Clubs orb remains a design decision.

## Symmetry and next production step

The study has the intended double-ended composition, but generated opposing
figures, ornament, frame and indices are not pixel-exact rotated duplicates.
Do not treat it as a verified two-way playing card. To remove directional
differences, prepare one approved figure component, create its lower counterpart
by an exact 180-degree rotation, and design the center join around the exact
canvas center. Compose those figures into the saved Design 2 frame and masks;
use one index component and its rotated copy. Verify the entire final RGBA
image against its half-turn, including the center join, all ornament and alpha.

The study has not replaced any frame, pip or finished card, and is outside the
finished-card catalogs.

## Floral surround and sword revision

Current revised review image:
[King of Spades — dense lotus field and revised jian](../../sources/generated/courts-v1/king-spades-floral-jian-v3.png).
Both blade tips were visually checked to sit within the interior frame. A final
[local tip repair](../../sources/generated/courts-v1/king-spades-tip-repair-prompt.json)
corrected an intermediate generation that crossed the border. All artwork
passes used built-in ImageGen; the selected output is saved without raster edits.

The user supplied Design 1's finished Poker King of Spades as the composition
reference. The next revision reduces the head/torso scale, retains broad sleeves
across the interior, introduces a shaped ivory reserve, and fills the surrounding
black field with dense Design 2 lotus ornament. The 12–15% reduction in the
generation prompt is a visual target, not a measured output guarantee.

[Floral composition pass](../../sources/generated/courts-v1/king-spades-floral-study-v2.png)
and [exact revision prompts](../../sources/generated/courts-v1/king-spades-floral-prompts.json)
are preserved. These remain generated review images: the shared frame, indices,
center and opposing halves still require component registration before release.

### Sword evidence and limits

[Royal Armouries: Chinese arms and armour](https://shop.royalarmouries.org/blogs/news/chinese-arms-and-armour)
documents a fifteenth-century Ming jian with a straight, double-edged blade;
the museum captions its guard as embossed in the form of a monster mask.
This supports the sword category and an appropriate guard motif. The original
study's floral guard, gem arrangement and shortened proportions were generated
design choices, not verified details from an artifact. No evidence found here
establishes that original combination as a particular Ming short sword.

[Philip M. W. Tom, Metropolitan Museum Journal 36 (2001)](https://resources.metmuseum.org/resources/metpublications/pdf/Notable_Sabers_of_the_Qing_Dynasty_at_MMA_The_Metropolitan_Museum_Journal_v_36_2001.pdf)
distinguishes the straight double-edged jian from the single-edged dao and
discusses the jian's association with nobility and gentlemanly status. That
supports using a jian as the illustrated sovereign's attribute, without claiming
this is a documented imperial portrait pose or a replica of his personal weapon.

The focused sword edit requests a longer blade relative to the grip, a compact
gilt guard with restrained mask relief, a dark wrapped grip and modest pommel.
The requested ratio is an illustration target, not a museum measurement. The
Royal Armouries full object record was inaccessible during this check, so the
revision is historically informed rather than an exact reconstruction. The
surviving museum sword is referenced in text, not supplied as a raster input.
