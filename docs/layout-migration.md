# Migration to multiple designs

The collection now uses `designs/<design-id>/` as the boundary for artwork,
configuration, sources, history and production scripts. This is an intentional
breaking path change. Existing release ZIPs retain their internal paths and bytes.

| Previous repository location | New location |
| --- | --- |
| `cards/**` | `designs/design1/cards/**` |
| `deck.json` | `designs/design1/deck.json` |
| `scripts/<Design 1 script>` | `designs/design1/scripts/<script>` |
| `sources/<Design 1 source>` | `designs/design1/sources/<source>` |
| `docs/design/<Design 1 note>` | `designs/design1/docs/design/<note>` |
| `docs/history/**` | `designs/design1/docs/history/**` |
| `sources/generated/design2-*` | `designs/design2/sources/generated/design2-*` |
| `sources/components/design2-registered-v1` | `designs/design2/sources/components/design2-registered-v1` |
| `sources/d2-01.png` | `designs/design2/sources/d2-01.png` |
| `docs/design/design2-*` | `designs/design2/docs/design/design2-*` |
| `scripts/*design2*` | `designs/design2/scripts/*design2*` |
| `build/design2-registered-v1/backs/**` (approved export) | `designs/design2/cards/backs/**` (permanent assets) |
| `build/design2*` (local packages/studies) | `designs/design2/build/design2*` |
| Other existing `build/` and `work/` | `designs/design1/build/` and `designs/design1/work/` |
| `index.html` (Design 1 gallery) | `designs/design1/index.html`; root is now the collection gallery |

`scripts/catalog.py` remains the collection entry point. It now checks or writes
all catalogs. The old Design 1 catalog is retained at `designs/design1/catalog.json`.
Root `catalog.json` is schema 2: `back.poker.verdigris` becomes
`design1.back.poker.verdigris`, and every asset has `design` and `local_id` fields.
Root paths remain relative to the repository; local catalog paths are relative
to their design folder, declared as `path_base: "design-root"`.

For an existing consumer, either switch to qualified IDs in the root catalog,
or load the Design 1 local catalog and resolve its paths against
`designs/design1/`. Do not resolve local catalog paths against the repository root.

Shared research stays in `docs/reference/`. Historical source snapshots,
prompts, and hash reports retain the paths they recorded at the time. These
are provenance, not current collection paths. Historical Design 1 commands
can generally be run from `designs/design1/`; current commands are in its README.
Design 2 uses the same convention inside its own folder.

[layout-migration.json](layout-migration.json) maps every one of the 408 finished
images from its old location to its permanent location, with pre-migration
hashes taken from the existing Design 1 catalog and approved Design 2 manifest.
`python scripts/check_layout.py` verifies that this migration preserved the bytes.
This is a historical migration check; a later intentional artwork revision will
require review against this baseline rather than rewriting the history.

For a future design, add `designs/<id>/deck.json`, put final PNGs under its
`cards/` hierarchy, add an entry to `collection.json`, then rebuild the catalogs.
An empty `face_systems` object supports backs-only designs.
