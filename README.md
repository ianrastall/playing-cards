# Playing Cards

A standalone illustrated card collection for software and printing.

**Current collection:** 30 backs (five colors × six formats), plus four French-suited poker kings. Every face uses the same multicolor palette and can pair with any back in its format. The kings remain review artwork with the known symmetry limitations below.

## Layout

```text
playing-cards/
├── cards/
│   ├── backs/
│   │   └── <format>/<color>.png
│   └── faces/
│       └── french-suited/<format>/<suit>/<rank>.png
├── catalog.json              # Actual asset paths, IDs, hashes, pixels and print sizes
├── deck.json                 # Format definitions, active colors and card vocabulary
├── sources/                  # Earlier artwork retained as design reference
├── scripts/                  # Catalog verification and recoloring tools
├── docs/
│   ├── design/               # Current design notes and generation prompts
│   ├── reference/            # Supplied research and dimension reference
│   └── history/              # Original imported records and migration map
├── work/                     # Local candidates/previews; generated and Git-ignored
└── build/                    # Future digital/print deliveries; generated and Git-ignored
```

Concrete examples:

- `cards/backs/poker/lamp-black.png`
- `cards/backs/bridge/madder-lake.png`
- `cards/faces/french-suited/poker/spades/king.png`

**Taxonomy:** side → format → color for backs; side → card system → format → suit → rank for faces. Rank identifies a card; its gameplay value belongs to the consuming game's rules. Color applies to backs, so faces are not copied into color folders. A card system describes content; a format describes dimensions. Thus tarot-sized backs do not imply that French-suited faces are tarot cards.

Keep filenames lowercase with hyphens. A filename need not repeat its parent folders. Git records revisions; current assets use stable names without `v1` suffixes. Use descriptive versioned names under `work/` for simultaneous candidates. This repo currently contains one visual collection; add a collection namespace if a second independent deck style actually arrives.

Tarot faces will have their own `cards/faces/tarot/` branch and appropriate major/minor-arcana identities. No tarot fronts or additional face sizes exist yet. Their catalog definitions will be introduced with those assets.

## Software use

Load [catalog.json](catalog.json) and select an asset by ID or its attributes. Paths are relative to the repository root, use forward slashes, and can be resolved against a filesystem directory or an application's asset base URL.

```python
import json
from pathlib import Path

root = Path("/path/to/playing-cards")
catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
assets = {card["id"]: card for card in catalog["assets"]}
face = root / assets["face.french-suited.poker.spades.king"]["path"]
back = root / assets["back.poker.lamp-black"]["path"]
```

The front and back can have different pixel resolutions while sharing the same physical aspect ratio. Render them into the same logical card bounds. Generated atlases, thumbnails or format-normalized images belong under `build/digital/`; the originals remain in `cards/`. Jukebox Solitaire can consume a pinned checkout/release of this repository without owning the artwork. No application dependency or remote hosting is configured by this initial setup.

## Printing

These are individual **trim-size artworks**, suitable for placement at the specified physical dimensions. They are not imposed press sheets and contain no added bleed, cut marks or gutters. Place using `trim_inches` in the catalog, not the PNG's embedded DPI. Future printer-specific layouts belong under `build/print/`.

| Format | Trim inches | Back pixels | Effective back PPI |
| --- | --- | --- | --- |
| Bridge | 2.25 × 3.50 | 675 × 1050 | 300 |
| European standard | 2.32 × 3.58 | 696 × 1074 | 300 |
| Jumbo | 3.50 × 5.00 | 1050 × 1500 | 300 |
| Poker | 2.50 × 3.50 | 750 × 1050 | 300 |
| Tarot | 2.75 × 4.75 | 825 × 1425 | 300 |
| Travel | 1.75 × 2.50 | 525 × 750 | 300 |

Poker kings are 1060 × 1484 pixels: 424 PPI at 2.5 × 3.5 inches. Their 96-DPI metadata is unchanged. The dimension-reference inch column defines this collection; millimeter measurements in the catalog are exact conversions from those inches.

## Colors and design status

Active back colors: Lamp Black, Madder Lake, Manganese Violet, Prussian Blue and Verdigris. Their names are pigment-inspired digital color labels, not physical ink specifications. Prussian Blue is the original recoloring source for each format.

The four kings share a botanical frame and multicolor palette. Hearts has a clean upper lip and sword behind the head; Diamonds has a profile and axe; Spades has an upright broadsword; Clubs has a sword and orb. Their painted patterns and opposing halves are not pixel-exact repeats. See [design notes](docs/design/kings.md) and [generation prompts](docs/design/poker-kings-prompts.md).

## Tools and checks

Python with Pillow and NumPy:

```text
python -m pip install -r requirements.txt
python scripts/catalog.py --check
python scripts/recolor_card_backs.py --verify-archive
```

After an intentional asset/configuration update, rebuild the catalog, then check it:

```text
python scripts/catalog.py --write
python scripts/catalog.py --check
```

The catalog check verifies the complete file inventory against its saved records, unique identities, hashes, dimensions and trim ratios. Recolor verification compares all 30 current backs with their original pixels and palette recipes, including alpha, unchanged non-blue pixels and central-dot patches.

Recoloring writes candidates under `work/recolored-backs/`, never over the archive:

```text
python scripts/recolor_card_backs.py --colors lamp-black verdigris
python scripts/recolor_card_backs.py --preview
```

The default generates the four active recolors. Older optional color recipes remain in the script for provenance and explicit experimentation; they are not members of the current collection. Adding a color requires adopting its files and updating `deck.json`.

## Provenance

The initial import reorganized the 34 existing images without modifying their bytes. [Migration records](docs/history/migration.json) map every imported path to its destination and hash at import. Imported documentation, tree and the former 60-card validation report are preserved under `docs/history/`; they describe an earlier inventory and are not current manifests.

The supplied research documents are references, not project instructions. Source prompts record how the existing artwork was created. Earlier studies and unselected recolors still in the Jukebox Solitaire workspace were not promoted into this collection. A copy of the provisional Spades reference is retained under `sources/`.

No distribution license has been selected.
