# Design 2

[All designs](../../README.md) · [Gallery](index.html) · [Number cards](number-cards.html) · [Finished backs](cards/backs/)

The approved [balanced toranj release](docs/design/toranj-v1.md) contains **30
finished backs: five colors in six formats**. One central medallion, pendant
finials, corner quarter-medallions and connected islimi vines establish a clear
hierarchy. Matching double gold frames enclose the floral border. Four nested
values of each ground color move from a dark outer frame through a quiet field
to a rich central surround. Palette-specific foliage and medallion treatments
preserve contrast in Prussian Blue, Verdigris, Madder Lake, Manganese Violet and
Lamp Black.

Finished back PNGs live in `cards/backs/<format>/<color>.png`. The 36 Poker
number faces are in `cards/faces/french-suited/poker/<suit>/<rank>.png`.
Discarded dark-field studies are out of the active
source tree; local recovery copies are in the ignored work folder.

[Blank face frames](docs/design/face-frames-v1.md) are now available in Lamp
Black and Madder Lake for all six formats. They adapt Design 1's reusable
central-field and corner-index structure to Design 2's gold lotus vines.
The twelve templates and their masks live in
`sources/components/design2-face-frames-v1/`; browse them in the gallery's
[face frames section](all.html#face-frames).

The [four King artworks](sources/generated/courts-v1/README.md) now share the
finished King of Spades design approved by the user: Ming-inspired yellow
dragon robes, dense lotus fields and the conventional suit-specific poses.
Selected full-resolution masters and exact prompts are saved together.
All four Kings have been accepted as finished. The matching
[four Queens](docs/design/queens-v1.md) are now generated, with phoenix crowns,
red silk robes and their suit-specific scepter or flowers.
The [four Jacks](docs/design/jacks-v1.md) are also generated, with blue lotus
robes, youthful faces, and the same poses and attributes used in Design 1.
The [two Jokers and four aces](docs/design/jokers-and-aces-v1.md) are now
generated as well. All preceding court, Joker and ace artworks have been
accepted as finished. The [number-card layout](docs/design/number-card-layout-v1.md)
uses the open blank frames, with ornament confined to the outer band to leave
more space for pip patterns. All [36 number cards](docs/design/number-cards-v1.md)
are now composed at 750 × 1050. Even ranks are exactly reversible; odd ranks
have one upright center pip with all surrounding pips paired by rotation.
[Browse the cards and turn them over](number-cards.html).

## Formats and construction

| Format | Pixels | Trim inches | Construction |
| --- | --- | --- | --- |
| Poker | 750 × 1050 | 2.5 × 3.5 | Approved Poker composition, registered and framed |
| Bridge | 675 × 1050 | 2.25 × 3.5 | Independently reconfigured narrow composition |
| Travel | 525 × 750 | 1.75 × 2.5 | Independently reconfigured with simpler filler |
| Jumbo | 1050 × 1500 | 3.5 × 5 | Independently reconfigured with fuller ornament |
| Tarot | 825 × 1425 | 2.75 × 4.75 | Independently reconfigured tall composition |
| European Standard | 696 × 1074 | 2.32 × 3.58 | Direct resize of the finished Bridge back |

Bridge, Travel, Jumbo and Tarot were generated as separate native compositions
with built-in ImageGen, using the approved Poker artwork as the reference.
Their medallions, vines and spacing were composed for the different boxes.
The exporter maps measured frame landmarks to common production geometry and
places every central flower at the exact canvas center. European Standard alone
is made by resizing the finished Bridge back.

All formats have a **50 px (4.233 mm) border**, a 23 px (1.947 mm) outside paper
margin at 300 ppi. The five native formats use the collection's 3.5 mm rounded
corners; European Standard inherits Bridge's complete silhouette through its
direct resize. All saved PNGs have exact half-turn symmetry, with their central flower
at `((width-1)/2, (height-1)/2)`. One continuous top half is rotated to build the
bottom, and the central lotus and side-border flowers meet cleanly on that line.

The five palettes are native painted colorways rather than flat recolors.
Prussian Blue uses greener teal medallions; Verdigris uses indigo medallions and
warmer foliage; Manganese Violet is softened like mineral pigment; Lamp Black
separates its nested regions through graphite-to-ink values.

## Browse and reproduce

Open `index.html` directly or through the repository's HTTP server. Choose a
size before browsing its cards. Poker includes 36 number faces, five backs,
and two blank frames; the other sizes include five backs and two blank frames.
The [18 court/ace/Joker masters](masters.html) are shown separately at their
original dimensions. The [full gallery](all.html) includes all 96 selected
images, with every original PNG linked in the initial HTML for bulk download
tools. Search by name, suit, or color; click an image to open the viewer, use
the arrow keys to compare images, turn a card 180 degrees, or download it.
The root [bulk gallery](../../all.html) includes both designs together.

Run from `designs/design2/`:

```text
python scripts/render_toranj_backs.py
python scripts/audit_design2_registration.py --build
python scripts/render_toranj_backs.py --apply
```

The first command builds a review set in `build/design2-toranj-v1/`.
`--apply` rebuilds, independently audits, promotes the checked PNGs and refreshes
the catalogs and artwork-revision ledger. Exports exclude timestamp metadata
so the same masters and toolchain reproduce stable file hashes.
Python dependencies are in the root `requirements.txt`. To verify the permanent set:

```text
python scripts/audit_design2_registration.py
python ../../scripts/catalog.py --check
```

`manifest.json` records all source hashes, measured geometry and finished PNG
hashes. `registration-audit.json` checks the saved files independently,
including the Bridge-derived European artwork, exact alpha, center alignment and
common frame geometry.

Approved masters and exact built-in ImageGen prompts are in
`sources/generated/design2-toranj-v1/`. Older source directories document
historical releases; their scripts do not produce this approved release.

Choose one back color for a physical deck. Files are trim-size artwork without
bleed, cutting guides or imposed sheets. Preserve alpha and aspect ratio; place
by the catalog's `trim_inches`. Licensed under [MIT](../../LICENSE).
