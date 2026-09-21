# Design 2

[All designs](../../README.md) · [Gallery](index.html) · [Finished backs](cards/backs/)

The approved gold-panel release contains **30 finished backs: five colors in six
formats**. The antique-white ornamental middle has a prominent beaded gold band.
Each surrounding field is a darker shade of its own border color; floral artwork
and teal medallions are shared across the five colors within each format.

Finished RGBA PNGs live in `cards/backs/<format>/<color>.png`. There are no
finished Design 2 faces. Discarded dark-field studies are out of the active
source tree; local recovery copies are in the ignored work folder.

[Blank face frames](docs/design/face-frames-v1.md) are now available in Lamp
Black and Madder Lake for all six formats. They adapt Design 1's reusable
central-field and corner-index structure to Design 2's gold lotus vines.
The twelve templates and their masks live in
`sources/components/design2-face-frames-v1/`; browse them in the gallery's
[face frames section](index.html#face-frames).

## Formats and construction

| Format | Pixels | Trim inches | Construction |
| --- | --- | --- | --- |
| Poker | 750 × 1050 | 2.5 × 3.5 | Approved Poker composition, registered and framed |
| Bridge | 675 × 1050 | 2.25 × 3.5 | Independently reconfigured narrow composition |
| Travel | 525 × 750 | 1.75 × 2.5 | Independently reconfigured with simpler filler |
| Jumbo | 1050 × 1500 | 3.5 × 5 | Independently reconfigured with fuller ornament |
| Tarot | 825 × 1425 | 2.75 × 4.75 | Independently reconfigured tall composition |
| European Standard | 696 × 1074 | 2.32 × 3.58 | Bridge enlargement, then common framing |

Bridge, Travel, Jumbo and Tarot were generated as separate native compositions
with built-in ImageGen, using the approved Poker artwork as the reference.
Their flowers, panel shapes and filler were composed for the different boxes.
The exporter samples each format's own master uniformly and translates its
measured floral center to the exact canvas center; it does not stretch Poker
into those formats. European Standard alone enlarges Bridge's artwork and field
mask with Lanczos sampling, then receives the same physical border geometry.

All formats have a **50 px (4.233 mm) border**, a 23 px (1.947 mm) outside paper
margin, a 40 px inner-frame corner radius and a 6 px outer-frame corner radius
at 300 ppi. The card silhouette uses the collection's 3.5 mm rounded corners.
The interior is fitted uniformly; small residual space is filled with the
matching dark ground. The border is reconstructed from the master's lotus-vine
ornament with consistent gold outlines. All saved PNGs have exact half-turn
symmetry, with their central flower at `((width-1)/2, (height-1)/2)`.

The five palettes are Prussian Blue, Verdigris, Madder Lake, Manganese Violet and
Lamp Black. Each field palette is 64% of its border RGB values, rounded to the
nearest integer. Separate masks control border and surrounding-field color,
leaving the common flowers, antique-white panel and medallions fixed.

## Browse and reproduce

Open `index.html` directly or through the repository's HTTP server. Select a
format, then use the color buttons, arrow keys or mouse wheel to compare colors
in a fixed position. Center guides and all 30 downloads are included.

Run from `designs/design2/`:

```text
node scripts/register_gold_panel.mjs
python scripts/audit_design2_registration.py --build
node scripts/register_gold_panel.mjs --apply
```

The first command builds a review set in `build/design2-gold-panel-v1/`.
`--apply` rebuilds, independently audits, promotes the checked PNGs and refreshes
the catalogs and artwork-revision ledger. Exports exclude timestamp metadata
so the same masters and toolchain reproduce stable file hashes.
Node.js and ImageMagick must be on PATH; Python dependencies are in the root
`requirements.txt`. To verify the permanent set:

```text
python scripts/audit_design2_registration.py
python ../../scripts/catalog.py --check
```

`manifest.json` records sources, palette targets, source-center measurements,
geometry, component hashes and finished PNG hashes. `registration-audit.json`
checks the saved files independently, including the Bridge-derived European
artwork, exact alpha, palette invariance, center alignment and frame geometry.

Approved masters and exact ImageGen prompts are in
`sources/generated/design2-gold-panel-v1/`. Reusable artwork plates and the two
palette masks are in `sources/components/design2-gold-panel-v1/`. Older source
directories document historical releases; their scripts do not produce this
approved release.

Choose one back color for a physical deck. Files are trim-size artwork without
bleed, cutting guides or imposed sheets. Preserve alpha and aspect ratio; place
by the catalog's `trim_inches`. Licensed under [MIT](../../LICENSE).
