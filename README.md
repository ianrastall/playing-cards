# Playing Cards

Two independent designs, with **578 card PNGs available directly in the repository**.
Open the [card viewer](index.html) to choose a design, size, set, and card.
One shared display area shows each complete PNG without cropping. Step through
cards with the buttons, arrow keys, or position slider; rotate the view or
download the selected PNG. Direct file links are available below the viewer,
including the 18 Design 2 French-suited source masters and 12 blank face frames.

| Design | Finished artwork | Files | Gallery |
| --- | --- | --- | --- |
| [Design 1](designs/design1/README.md) — Morris, Mucha and Safavid-inspired botanical ornament | 367 faces, including the complete 97-card Minchiate; 30 backs | [Cards](designs/design1/cards/) | [Browse](designs/design1/index.html) |
| [Design 2](designs/design2/README.md) — Ming and Tang-inspired silk florals | 54 Poker faces; 97 Tarot faces in layout review (Minchiate tradition); 30 approved backs in six sizes | [Cards](designs/design2/cards/) | [Browse](designs/design2/index.html) |

Design 2's [number-card gallery](designs/design2/number-cards.html) includes a
180-degree turn control. Its courts, Jokers and aces now share the numeral
borders and center point in the [complete Poker gallery](designs/design2/poker.html).
Original source masters are preserved separately. Tarot-sized backs are included.
Design 2's separate [Tarot deck](designs/design2/tarot.html) now uses its native
825 × 1425 canvas, with taller traditional Chinese name panels. The
[first costume proofs](designs/design2/tarot.html#design=design2&size=tarot&set=first-proofs)
begin the Ming-based clothing revisions; translations and remaining costumes
are under review. Minchiate describes this Tarot deck's 97-card tradition.
The colors are Lamp Black, Madder Lake, Manganese Violet, Prussian Blue and Verdigris.

## Folder layout

```text
collection.json              Design registry
catalog.json                 All finished assets; repository-relative paths
index.html                   Single-card viewer
all.html                     Viewer with expanded file directory
designs/
  design1/
    cards/                   Finished faces and backs
    deck.json                This design's formats and inventory
    catalog.json             This design's assets; design-relative paths
    index.html               Design card viewer
    <format>.html            Viewer opened to one size
    all.html                 Viewer with design file directory
    sources/                 Components, generated masters and original inputs
    scripts/                 Design-specific rendering and packaging
    docs/                    Design notes and historical records
    build/ and work/         Local output and staging; ignored by Git
  design2/                   Same organization; backs and Poker faces
scripts/                     Collection-wide catalog and migration checks
docs/                        Shared references and migration guidance
```

Finished artwork belongs under each design's `cards/`, not inside a ZIP or a
build directory. New designs get their own folder and entry in `collection.json`.
Earlier studies stay in that design's `sources/` and `docs/`.

## Use the cards

Select assets from the root catalog by design and attributes, or by a design-qualified ID:

```python
import json
from pathlib import Path

root = Path("/path/to/playing-cards")
catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
assets = {asset["id"]: asset for asset in catalog["assets"]}
face = root / assets["design1.face.french-suited.poker.spades.king"]["path"]
back = root / assets["design2.back.poker.prussian-blue"]["path"]
```

Root catalog schema 2 uses repository-relative paths and a `design` field.
Each design also has a local catalog with its original, unprefixed IDs and
paths relative to that design folder. See the [consumer guide](docs/llm-guide.md).

Preserve alpha and aspect ratio. Use the same display rectangle for all cards
of one format. Native cards are trim-size RGBA PNGs at nominal 300 ppi, with
3.5 mm rounded corners. Place printed artwork using `trim_inches`, not inferred
PNG density. Native files have no bleed or cut guides.

## Browse and verify

Run these commands from the repository root:

```text
python -m pip install -r requirements.txt
python -m http.server 8000
```

Open `http://localhost:8000/`. The viewer also works as local HTML files.
Design, size and set selectors share one centered card stage. Search applies to
the selected set. Rotation stays in place while comparing cards, and the URL
fragment records the selected card, filter and rotation for sharing or reloading.
Design 2 sizes without finished faces show backs and blank frames. Source masters
are labeled separately and retain their original dimensions.

The size pages open the same viewer with a size selected. Without JavaScript,
the first card, its download link, size-page links and the direct file directory
remain usable. `all.html` expands the file directory for download tools without
loading every image.

Gallery pages are generated from the production catalog and the selected
Design 2 artwork manifests. Image URLs include a content hash so replacing a
PNG changes its browser cache key. After artwork or inventory changes, rebuild
and check the pages:

```text
python scripts/build_gallery.py --write
python scripts/build_gallery.py --check
```

The shared appearance and viewer are in `assets/gallery.css` and
`assets/gallery.js`; edit page structure in `scripts/build_gallery.py`.
The checked-in HTML can be served directly by GitHub Pages with no build step.
Publish the regenerated pages, shared assets, and updated card PNGs together;
local artwork changes do not appear on GitHub until they are committed and pushed.

```text
python scripts/catalog.py --check
python scripts/check_layout.py
python -m unittest discover -s scripts -p "test_*.py"
python -m unittest discover -s designs/design1/scripts -p "test_*.py"
python designs/design2/scripts/audit_design2_registration.py
python designs/design2/scripts/register_face_masters.py --check --active
python designs/design2/scripts/audit_number_cards.py --active
python designs/design2/scripts/render_tarot_faces.py --check --active
python designs/design1/scripts/render_minchiate.py --check --active
```

After changing approved artwork or inventory, run `python scripts/catalog.py --write`
to refresh both local catalogs and the collection catalog. Rendering and packaging
commands are in each design's README. Design 1's six release formats include Tarot.

## Migrating an existing clone

The former root `cards/`, `deck.json`, artwork scripts, and sources now belong to
`designs/design1/`. Design 2's approved backs have been promoted from build output
to `designs/design2/cards/backs/`. Old hard-coded paths must be updated; see the
[migration map](docs/layout-migration.md). The migration preserved all 408 native
images byte for byte. Subsequent approved changes are recorded in
`docs/asset-revisions.json`; Design 2 now uses the balanced toranj release.

Licensed under the [MIT License](LICENSE). The bundled LXGW WenKai TC font
uses its separate [SIL OFL license](designs/design2/sources/fonts/lxgw-wenkai-tc-v1.522/OFL.txt).

## Next work

The ordered [Design 2 roadmap](docs/design2-roadmap.md) covers Poker tarot cards,
whole-design alignment, and the remaining formats.
