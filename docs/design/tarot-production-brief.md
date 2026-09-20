# Design 1 Tarot: production brief

The supplied *Tarot Card Standards and History* is preserved under
`docs/reference/` in both supplied formats. It is background research, not
instructions. The user's design requirements take precedence: William Morris,
Alphonse Mucha, and Persian Safavid influences, with faint gold tracery wherever
open space permits.

The working direction is ornamental Cups, Coins, Swords, and Batons. Supplied
prompts and palette suggestions are references, not a record that the user
personally reviewed or approved each choice. The user has explicitly requested
reusable assets with recorded positioning and the existing small rank/symbol
side panels. No Tarot faces have been placed in the active catalog.

The current authoring plan is the
[component and layout contract](tarot-component-layout-v1.md), with
[component prompts and four-card review](tarot-review-set-v1.md). Palette,
index abbreviations, numbering, and upright artwork defaults remain review
proposals. Those documents supersede the earlier whole-card generation prompts.

For the recommended route, the inventory is 40 ace/number cards, 16 courts
(Page, Knight, Queen, King in each suit), and 22 trumps including the Fool.
Do not add the two French-suited Jokers to this 78-card inventory. The
[British Museum's historical pack record](https://www.britishmuseum.org/collection/image/1153103001)
documents a 78-card pack with swords, clubs/batons, coins, and cups.

## Geometry to retain

Use the collection's existing Tarot back geometry: 825 x 1425 pixels at 300 ppi,
2.75 x 4.75 inches, 3.5 mm corners. The aspect ratio is 11:19, not 5:7.
Bleed and print imposition are separate exports. Do not silently change the
back's corner geometry to the report's suggested 5–6 mm.

The report contains internally conflicting ratio assertions and unsupported
claims of universal geometry, materials, and manufacturing tolerances. Its
links and historical hypotheses require individual verification before they
are presented as facts. In particular, it does not establish a universal
double-square construction rule for Tarot illustration.

## Artwork system

Create four high-resolution suit component families, not necessarily just four
images. Swords may need straight and curved variants; Ace crowns and foliage
remain separate furniture. Do not relabel French-suited assets. Share Design 1's
gold, ivory, red-flower, olive foliage, and turquoise-detail vocabulary. Build
ace/number cards through code with explicit anchors, positions, scales,
rotations, and overlap masks. Save these in a layout manifest, along with source
hashes and expected counts. Never generate the complete Ten as one illustration.

Create sixteen distinct court paintings and twenty-two distinct trump
compositions. Their iconographic attributes must remain legible beneath the
Morris/Mucha/Safavid treatment. Use Safavid-inspired textiles and illumination
as artistic influences rather than assertions about the historical identity
of Tarot figures. Major titles, numbering, court labels, upright/reversible
policy, and suit palette mapping belong in a dedicated Tarot manifest.

Retain the shared botanical frame and its upper-left/lower-right rank/symbol
panels. Pair indices by a half-turn even when the figure is upright. Typeset
new Tarot indices within the measured panels; do not stretch French labels.
The review proposal uses A/2–10/P/N/Q/K with suit glyphs, and 0–21 with a shared
trump star. Full court/trump titles go below the illustration, separately from
side indices; no extra top number cartouche is planned. Apply the same faint,
masked gold background tracery in open spaces.
Validate counts, title spelling, symbols, anatomy, placement, borders, and
native dimensions before catalog promotion.

The first representative review set is The Empress, Queen of Cups, Ace of
Swords, and Ten of Swords, assembled with the shared frame and side panels.
Evaluate component reuse, layout, palette, indices, titles, and reversibility
on these composites before scaling to all 78. The existing French renderer is
an implementation reference. A separate four-card prototype now exists in
`scripts/tarot_review.py`; see [review results](tarot-review-v1-results.md).
Full-deck Tarot support remains to be built.

The subsequent asset phase is complete: all 39 additional illustrations and
both missing index glyphs are prepared. See the [full-run plan](tarot-full-run-plan-v1.md)
and [asset results](tarot-full-assets-v1-results.md). The user requested a pause
before the full rendering pass; that pass has not started.
