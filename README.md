# Playing Cards

Two independent designs, with **444 finished PNGs available directly in the repository**.
Open the [collection gallery](index.html) to browse both designs on one dark
studio-style page. All 474 selected images have direct original-PNG links in
the HTML for download managers: the 444 production cards below, 18 Design 2
court/ace/Joker masters, and 12 blank face frames.

| Design | Finished artwork | Files | Gallery |
| --- | --- | --- | --- |
| [Design 1](designs/design1/README.md) — Morris, Mucha and Safavid-inspired botanical ornament | 348 faces, including the complete 78-card Tarot; 30 backs | [Cards](designs/design1/cards/) | [Browse](designs/design1/index.html) |
| [Design 2](designs/design2/README.md) — Ming and Tang-inspired silk florals | 36 Poker number faces; 30 approved backs in six sizes | [Cards](designs/design2/cards/) | [Browse](designs/design2/index.html) |

Design 2's [number-card gallery](designs/design2/number-cards.html) includes a
180-degree turn control. Its approved court, Joker and ace artworks are retained
as source masters. Tarot-sized backs are included.
The colors are Lamp Black, Madder Lake, Manganese Violet, Prussian Blue and Verdigris.

## Folder layout

```text
collection.json              Design registry
catalog.json                 All finished assets; repository-relative paths
index.html                   Collection gallery
designs/
  design1/
    cards/                   Finished faces and backs
    deck.json                This design's formats and inventory
    catalog.json             This design's assets; design-relative paths
    index.html               Design gallery
    sources/                 Components, generated masters and original inputs
    scripts/                 Design-specific rendering and packaging
    docs/                    Design notes and historical records
    build/ and work/         Local output and staging; ignored by Git
  design2/                   Same organization; backs and Poker number faces
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

Open `http://localhost:8000/`. All galleries also work as local HTML files.
Every image is present without JavaScript, pagination, or filtering. Click an
artwork to inspect it, turn it 180 degrees, or download it. The design-specific
galleries use the same shared theme and show the entire selected design.

Gallery pages are generated from the production catalog and the selected
Design 2 artwork manifests. After inventory changes, rebuild and check them:

```text
python scripts/build_gallery.py --write
python scripts/build_gallery.py --check
```

The shared appearance and viewer are in `assets/gallery.css` and
`assets/gallery.js`; edit page structure in `scripts/build_gallery.py`.
The checked-in HTML can be served directly by GitHub Pages with no build step.

```text
python scripts/catalog.py --check
python scripts/check_layout.py
python -m unittest discover -s scripts -p "test_*.py"
python -m unittest discover -s designs/design1/scripts -p "test_*.py"
python designs/design2/scripts/audit_design2_registration.py
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
`docs/asset-revisions.json`; Design 2 now uses the gold-panel release.

Licensed under the [MIT License](LICENSE).
