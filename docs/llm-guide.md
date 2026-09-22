# Consumer and contributor guide

This repository contains independent designs. Start with `collection.json` and
the root `catalog.json`; do not infer a design from a filename.

The root catalog uses schema 2, repository-relative paths, globally unique
design-qualified IDs, and an explicit `design` field. Each design's local
catalog uses schema 1, `path_base: "design-root"`, and unprefixed IDs. Resolve
local paths from the directory containing that catalog. Formats and back colors
are per-design metadata in the root catalog's `designs` entries.

- Design 1: 270 French-suited faces, 78 completed Tarot faces, and 30 backs.
- Design 2: 36 Poker number faces (2–10 in four suits), plus 30 approved floral backs across six formats. Approved court, Joker and ace masters remain in sources.

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
physical placement. Design 1's packager provides separate print variants;
Design 2 supplies native backs and 750 × 1050 Poker number faces.

From the repository root, `python scripts/catalog.py --check` validates all
catalogs and asset inventories. `--write` refreshes both design-local catalogs
and the collection catalog. A design's local catalog command updates only that
design, so refresh the root catalog after a local rendering/promotion workflow.
See each design's README for production commands, and
[layout-migration.md](layout-migration.md) for breaking path and ID changes.
