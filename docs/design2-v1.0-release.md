# Design 2 v1.0 — complete release

[GitHub release](https://github.com/ianrastall/playing-cards/releases/tag/design2-v1.0.0)

Six size-specific ZIPs cover 367 faces and 30 backs. Poker, Bridge, European
Standard, Travel and Jumbo each include 54 French-suited faces and five alternative
backs. Tarot is the separate 97-card Minchiate deck with five backs.

Each ZIP includes native trim-size RGBA PNGs, clean 600 ppi files with 1/8-inch
bleed, separate blue cut-guide proofs, a manifest, SHA-256 checksums, a usage
guide, MIT license and the LXGW WenKai TC font license notice. The font binary
is not redistributed in the packages. Each French-suited package has 177 PNGs;
Tarot has 306. Choose one back color for a physical deck.

Native images match the catalog byte for byte. Print trim pixels use exact 2×
replication after compositing alpha onto antique white, with no invented detail.
Clean files and marked cutting proofs are separate. Sheet imposition remains
outside the packages.

The owner accepted the existing Poker and Tarot artwork for release. Their pixels,
the 30 existing backs, and all other previously active cards remain unchanged.
The additional 216 French-suited faces derive from saved art and pip components;
European Standard derives from Bridge.

## Build, check, publish

```text
python designs/design2/scripts/audit_release.py --verify-renderers
python designs/design2/scripts/package_decks.py --build --all
python designs/design2/scripts/package_decks.py --check --all
```

Packages live under the ignored `designs/design2/build/releases/`:
`design2-v1.0-<format>.zip`, each with a `.zip.sha256` companion.
`design2-v1.0.json` and `design2-v1.0-SHA256SUMS.txt` summarize all six packages.

The [release gate](../designs/design2/docs/design/release-v1-audit.json) binds
all 397 active PNGs to validated renderer records and the current catalog.
The package checker independently verifies inventory, native hashes, exact print
pixels, bleed/guide geometry, embedded sRGB profiles, density and ZIP integrity.

Building creates local files. A repository push publishes the artwork and viewer;
the six ZIPs, six companion checksums, index and combined checksums must also
be uploaded as GitHub Release assets. A release is published after all 14 assets
have completed upload and their remote hashes match the local files.
