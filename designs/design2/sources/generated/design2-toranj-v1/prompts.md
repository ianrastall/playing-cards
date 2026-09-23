# Toranj master prompts

All calls used built-in ImageGen. The selected Madder Lake Poker study was the
input image for each native-format composition. Each native Madder Lake result
then became the exact edit target for the four color edits in its format.

## Native-format composition template

The following text was specialized with the format name, trim size and the
format-specific adaptation below:

```text
Use case: precise-object-edit
Asset type: native {FORMAT}-size playing-card back master, {TRIM} inches
Input image: Image 1 is the Poker structural and style reference.
Primary request: Recompose this exact Madder Lake toranj design for the {FORMAT_DESCRIPTION}. Preserve the single central medallion, top and bottom pendant finials, four corner quarter-medallions, connected islimi vines, red blossoms, double gold frames, outer lotus-vine band, four nested Madder shades, and uniform ivory margin. {FORMAT_ADAPTATION}
Balance: place the center of the central lotus at the exact geometric center. Design the card as an exact-looking 180-degree rotational composition. At the horizontal centerline, the central lotus and the left/right border blossoms must cross cleanly and continuously so a top-half rotational construction can be made without a seam.
Constraints: full card visible; a {TRIM} colored card panel centered in the portrait canvas; no stretching appearance, cut-off frame, extra ornaments, seams, dark halos, stray lines, text, symbols, watermark, mockup, hands, or table.
```

| Format | Trim | Description and adaptation |
| --- | --- | --- |
| Bridge | 2.25 × 3.5 | Narrower Bridge proportion. Make the central medallion modestly narrower and let the upper and lower vines extend naturally in the taller narrow field. Keep the same visual hierarchy and motif scale at physical size. |
| Travel | 1.75 × 2.5 | Compact Travel proportion. Simplify the scrolling vines slightly and use fewer, broader leaves so the ornament stays clear at the smaller physical size. Keep the central medallion bold and the border legible. |
| Jumbo | 3.5 × 5 | Larger Jumbo proportion. Allow slightly fuller leaf modeling and a little more breathing room around the medallion while retaining the same motif hierarchy and restrained density. |
| Tarot | 2.75 × 4.75 | Distinctly taller, narrower Tarot proportion. Extend the upper and lower vine passages vertically, keep the center medallion proportionate rather than stretched, and give the pendant finials more vertical breathing room. |

## Color-edit template

Each color used a separate built-in edit call:

```text
Use case: precise-object-edit
Asset type: native {FORMAT}-size playing-card back master
Input image: Image 1 is the exact edit target.
Primary request: Change only the palette to {COLOR}. Preserve the exact {FORMAT} composition, central point, motif placement, proportions, double gold frames, ivory margin, painted texture, {FORMAT_DETAIL}, and clean horizontal-center crossings. {PALETTE}
Constraints: preserve every motif and every edge; no structural redraw, no new or removed motifs, no crop, seams, halos, stray lines, text, symbols, watermark, mockup, hands, or table.
```

Format detail was `simplified broad motifs` for Travel, `fuller modeling` for
Jumbo, `extended vertical vine passages` for Tarot, and omitted for Bridge.

Palette text:

- **Prussian Blue:** four nested blue grounds: darkest muted ink-blue outer floral border, slightly brighter clear Prussian inner border, quiet middle-lightness slate-Prussian broad field, and richest deepest saturated Prussian central toranj surround. Keep warm olive foliage and cream/red blossoms. Make central and corner medallion interiors distinctly greener deep teal.
- **Verdigris:** four nested verdigris grounds: darkest muted pine-verdigris outer floral border, slightly brighter clear verdigris inner border, quiet middle-lightness mineral-verdigris broad field, and richest deepest saturated verdigris central toranj surround. Warm the foliage toward yellow-olive. Make central and corner medallion interiors deep muted indigo with small teal accents.
- **Manganese Violet:** four nested violet grounds: darkest muted aubergine outer floral border, slightly brighter clear manganese inner border, quiet middle-lightness dusty pigment-violet broad field, and richest deepest saturated violet central toranj surround. Keep warm olive foliage, cream/red blossoms and deep green-teal medallion interiors.
- **Lamp Black:** four nested warm black values: near-black matte outer floral border, slightly lighter clear charcoal inner border, quiet middle-lightness warm graphite broad field, and richest deepest ink-black central toranj surround. Keep warm olive foliage, cream/red blossoms and deep green-teal medallion interiors.
