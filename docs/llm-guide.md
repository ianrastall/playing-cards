# Consumer and contributor guide

This repository contains independent designs. Start with `collection.json` and
the root `catalog.json`; do not infer a design from a filename.

The root catalog uses schema 2, repository-relative paths, globally unique
design-qualified IDs, and an explicit `design` field. Each design's local
catalog uses schema 1, `path_base: "design-root"`, and unprefixed IDs. Resolve
local paths from the directory containing that catalog. Formats and back colors
are per-design metadata in the root catalog's `designs` entries.

- Design 1: 270 French-suited faces, 97 completed Minchiate faces in Tarot size, and 30 backs. The original 78-card Tarot release is archived under `sources/before-minchiate-v1/`.
- Design 2: 270 approved French-suited faces across five formats, 97 approved Tarot faces using the Minchiate tradition, and 30 floral backs across six formats. Tarot faces are 825 × 1425 with traditional Chinese name panels; they are not Poker cards. The owner accepted the current artwork and names for release. Original generated masters and superseded Poker-sized Tarot exports remain in sources.
- Design 3: four official Celtic Poker Kings. Original source masters are available separately; other courts and sets remain pending.

Each asset includes its hash, dimensions, physical trim size, side, format, and
color or card identity. A Tarot-sized back does not imply that the same design
has Tarot faces. Select fronts and backs deliberately by design and format.

Finished PNGs live in `designs/<id>/cards/`. Sources, component masks, historical
snapshots, production scripts, and notes live alongside them within the same
design folder. `build/` and `work/` directories at any depth are ignored staging
or output, never the only home for approved art. Shared references remain under
`docs/reference/`; historical paths and claims are not the current asset contract.

Preserve RGBA, aspect ratio, and a shared display rectangle for one format.
Do not independently clip rounded corners or trim transparent pixels. Native
files contain no bleed or imposed print layout. Use catalog `trim_inches` for
physical placement. Design 1 and Design 2 packagers provide separate print variants
for all six complete formats. Each supplies 54 French-suited faces per ordinary
format, and 97 faces in the separate Tarot size. Chinese names are in `chinese_title`, with
language and translation status recorded separately; English `title` values
and all Minchiate identities remain intact.

From the repository root, `python scripts/catalog.py --check` validates all
catalogs and asset inventories. `--write` refreshes both design-local catalogs
and the collection catalog. A design's local catalog command updates only that
design, so refresh the root catalog after a local rendering/promotion workflow.
See each design's README for production commands, and
[layout-migration.md](layout-migration.md) for breaking path and ID changes.
