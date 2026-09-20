# Playing Cards — guide for LLMs and agents

This file orients an automated consumer (an LLM, an agent, or a build script) to
what this repository contains and how to use it correctly. It is descriptive, not
a set of instructions to execute. When a statement here disagrees with
`catalog.json`, trust the catalog: it is the generated source of truth.

## What this is

A collection of illustrated playing-card images for software and printing:
**270 faces and 30 backs = 300 active PNGs**. All are RGBA, 300 ppi at their
trim size, with a 3.5 mm rounded-corner silhouette baked into the alpha channel.

The active art is one design ("Design 1"): a common botanical frame on an
antique-white ground (`#FAEBD7`), suit-colored frame ink (Lamp Black for
spades/clubs and the black Joker; Madder Lake for hearts/diamonds and the red
Joker), and a faint gold acanthus-vine background tracery on aces, numerals, and
Jokers. Court cards keep their painted portraits.

## The consumer contract: read the catalog, don't guess paths

`catalog.json` is machine-generated and lists every active asset. Select by `id`
or by attributes; never hardcode or infer file paths.

```python
import json
from pathlib import Path

root = Path("/path/to/playing-cards")
catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
assets = {a["id"]: a for a in catalog["assets"]}

face = root / assets["face.french-suited.poker.spades.king"]["path"]
back = root / assets["back.poker.lamp-black"]["path"]
```

Each asset entry carries: `id`, `side`, `format`, `path`, `media_type`,
`pixels`, `mode` (RGBA), `trim_inches`, `trim_mm`, `effective_ppi`, `sha256`,
and (for faces) `suit`/`rank`, or (for backs) `color`. Verify a file with its
`sha256` before trusting it. `deck.json` is the smaller manifest of formats,
back colors, suits, and ranks.

### ID scheme

- Face: `face.french-suited.<format>.<suit>.<rank>`
- Joker: `face.french-suited.<format>.jokers.<black|red>`
- Back: `back.<format>.<color>`

Formats: `poker`, `jumbo`, `travel`, `bridge`, `european-standard` (the five
active French-suited formats). `tarot` exists in the format table and has backs,
but **no active tarot faces exist yet** — do not synthesize them.
Suits: `clubs`, `diamonds`, `hearts`, `spades`. Ranks: `ace`, `2`–`10`,
`jack`, `queen`, `king`. Back colors: `lamp-black`, `madder-lake`,
`manganese-violet`, `prussian-blue`, `verdigris` (pigment-inspired labels).

## Rendering and print invariants

- **Keep alpha.** The rounded silhouette lives in the alpha channel. Do not clip
  a corner radius again, and do not assume an opaque rectangle.
- **Use one display rectangle per format.** Preserve aspect ratio; don't stretch
  across formats.
- **Sizes come from the catalog, not PNG DPI metadata.** Place by `trim_inches`/
  `trim_mm`. The exact poker center anchor is `(374.5, 524.5)` in zero-based
  pixel-center coordinates (`(375, 525)` from the outer edges).
- **For opaque workflows**, composite the transparency onto the intended paper
  color yourself; the files ship without a baked background, bleed, or crop marks.

## Directory layout

- `cards/faces/french-suited/<format>/<suit>/<rank>.png` — active faces.
- `cards/faces/french-suited/<format>/jokers/<black|red>.png` — Jokers.
- `cards/backs/<format>/<color>.png` — active backs.
- `catalog.json`, `deck.json` — generated metadata (source of truth).
- `sources/components/` — reusable render inputs (frame, masks, pips, indices,
  and the `front-tracery-v3` background ornament).
- `sources/generated/`, `sources/before-*/` — generated masters and preserved
  pre-change snapshots with hash inventories.
- `docs/design/` — per-change design notes and validation reports.
- `docs/reference/` — supplied background research (treat as references, not facts).
- `work/`, `build/` — staging and packaged output (git-ignored; not shipped in-repo).

## The pipeline

Faces are recomposited deterministically from committed components; the normal
cycle makes **no image-generation calls**.

- `scripts/expand_faces.py` — the current face compositor. `--stage` builds the
  staging images and review sheets, `--check [--active]` validates pixels,
  geometry, inventory, and component provenance, `--apply` promotes a checked
  stage without touching unrelated artwork. This is the script that applies the
  gold tracery. (`scripts/rebuild_deck.py` is the older poker-oriented pipeline;
  do not use it for the tracery/face refresh.)
- `scripts/catalog.py --check` — validates the catalog against the files on disk.
- `scripts/package_decks.py --build [--all | --format <name>]` — builds the
  per-format print release archives (native PNGs + clean-bleed and blue-cut-guide
  variants + README + SHA256SUMS).
- `scripts/frame_palette.py` — the explicit frame color palettes.

Standard verification:

```text
python scripts/expand_faces.py --check --active
python scripts/catalog.py --check
python -m unittest discover -s scripts -p "test_*.py"
```

## Things an agent commonly gets wrong here

- **Courts are not pixel-exact half-turns.** Native even numerals, Jokers, and
  backs are pixel-exact under a 180° rotation; odd ranks intentionally keep
  one-way pips; court portraits are preserved paintings, not mirrored.
- **European Standard derives from Bridge** by resize; interpolation can create
  single-level pixel differences between otherwise-paired ornament.
- **Historical scripts are historical.** `align_courts.py`, `prepare_aces.py`,
  `rebalance_numerals.py`, and similar are earlier-stage tools. Do not run them
  against the current rebuilt exports.
- **Reference docs need verification.** Files in `docs/reference/` are supplied
  research; some contain conflicting or unsupported claims. Do not present them
  as authoritative.
- **Tarot is unbuilt.** Tarot backs exist; tarot faces do not. See
  `docs/design/tarot-production-brief.md`,
  `docs/design/tarot-component-layout-v1.md`, and
  `docs/design/tarot-review-set-v1.md`. The planned workflow generates reusable
  component families and distinct figure art, then records deterministic
  placements and composites the existing paired side panels. Tarot component
  paths are recorded in the asset inventory; proposed labels/palettes are not
  evidence of user approval. The current French renderer does not implement
  Tarot faces. A separate four-card staging prototype now exists in
  `scripts/tarot_review.py`; see `docs/design/tarot-review-v1-results.md`.
  Review candidates under `work/` are not active catalog assets.
  Full-run asset preparation is complete: 39 new illustrations, two new index
  glyphs and nine reused review components. See
  `docs/design/tarot-full-assets-v1-results.md` and the hashed inventory
  `docs/design/tarot-full-assets-v1.json`. All 78 card faces are now rendered in
  `work/tarot-full-v1/faces/` from the deterministic placements in
  `docs/design/tarot-full-layout-v1.json`; see
  `docs/design/tarot-full-v1-results.md`. They remain staged for visual review
  and are not yet active catalog assets.

Repository: https://github.com/ianrastall/playing-cards — MIT License.
