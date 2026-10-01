# Playing Cards

Three independent designs, with **838 card PNGs available directly in the repository**, including forty Celtic A–10 faces for review.
Open the [card viewer](index.html) to choose a design, size, set, and card.
One shared display area shows each complete PNG without cropping. Step through
cards with the buttons, arrow keys, or position slider; rotate the view or
download the selected PNG. Direct file links are available below the viewer,
including the 18 Design 2 and four Design 3 source masters, ten Celtic Queen,
Jack and Joker review faces, four large Celtic pip masters and 12 blank face frames.

| Design | Finished artwork | Files | Gallery |
| --- | --- | --- | --- |
| [Design 1](designs/design1/README.md) — Morris, Mucha and Safavid-inspired botanical ornament | 367 faces, including the complete 97-card Minchiate; 30 backs | [Cards](designs/design1/cards/) | [Browse](designs/design1/index.html) |
| [Design 2](designs/design2/README.md) — Ming and Tang-inspired silk florals | 367 approved faces, including 97 Minchiate Tarot cards; 30 backs in six sizes | [Cards](designs/design2/cards/) | [Browse](designs/design2/index.html) |
| [Design 3](designs/design3/README.md) — Celtic spirals, metalwork and woodland ornament | Four approved Poker Kings; forty A–10 faces, four Queens, four Jacks and two Jokers for review | [Cards](designs/design3/cards/faces/french-suited/poker/) | [Browse](designs/design3/index.html) · [A–10](designs/design3/a-10.html) · [Queens](designs/design3/queens.html) · [Jacks](designs/design3/jacks.html) · [Jokers](designs/design3/jokers.html) |

Design 2's [number-card gallery](designs/design2/number-cards.html) includes a
180-degree turn control. Its courts, Jokers and aces now share the numeral
borders and center point in the [complete Poker gallery](designs/design2/poker.html).
Original source masters are preserved separately. Tarot-sized backs are included.
Design 2's separate [Tarot deck](designs/design2/tarot.html) now uses its native
825 × 1425 canvas, with taller traditional Chinese name panels. The
[costume revision group](designs/design2/tarot.html#design=design2&size=tarot&set=first-proofs)
records the Ming-based clothing revisions. The owner accepted the current
Poker and Tarot artwork and names for release. Minchiate describes this Tarot deck's 97-card tradition.
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
Both full designs have faces and backs in all six sizes. Source masters
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

Design 1 and Design 2 release packages include all six sizes, with native files,
clean bleed variants, separate cut-guide proofs, manifests and checksums.
See the [Design 1 v1.2 release](https://github.com/ianrastall/playing-cards/releases/tag/1.2.0)
and [Design 2 v1.0 release](https://github.com/ianrastall/playing-cards/releases/tag/design2-v1.0.0).

Design 3's [four Poker Queens](designs/design3/queens.html) are ready for review,
following its [four official Celtic Kings](designs/design3/docs/design/kings-registration-v1.md).
The related Norse Design 4 remains deferred. The
[Design 2 roadmap](docs/design2-roadmap.md) records the completed release work.
