# Design 1 v1.2

All six sizes are rebuilt from the current Design 1 catalog. Tarot contains the
97-card Minchiate deck; the other five sizes retain their 54 French-suited faces.
Every size includes five alternative backs.

The release files are local, under `designs/design1/build/releases/`:

- `design1-v1.2-poker.zip`
- `design1-v1.2-bridge.zip`
- `design1-v1.2-european-standard.zip`
- `design1-v1.2-travel.zip`
- `design1-v1.2-jumbo.zip`
- `design1-v1.2-tarot.zip`

Each archive contains native PNGs, 600 ppi bleed files, separate cut-guide
proofs, a manifest, SHA-256 checksums, a README and the MIT license. The five
French-suited archives contain 177 PNGs apiece; Tarot contains 306 PNGs.
Native files are copied byte for byte from the active cards.

`design1-v1.2.json` records archive sizes and hashes;
`design1-v1.2-SHA256SUMS.txt` lists all six archive checksums. Each ZIP also has
its own `.zip.sha256` file. The output folder is ignored by Git; attach these
files to the release separately from the website changes.

Rebuild from the repository root:

```text
python designs/design1/scripts/package_decks.py --build --all
```

The build verifies each archive against the active sources, including native
bytes, print geometry, pixel preservation, color profiles and ZIP checksums.
To verify existing output without rebuilding the PNGs:

```text
python designs/design1/scripts/package_decks.py --check --all
```

Building prepares local release assets. Publishing is a separate step: upload
the six ZIPs, six `.zip.sha256` files, release index and combined checksum file
to a GitHub release. A Git commit or website push alone does not upload ZIPs.

All six v1.2 archives were checked against the current cards on 2026-09-30.
The previous public v1.1 Tarot package predates the complete 97-card Minchiate
deck; use [Design 1 v1.2](https://github.com/ianrastall/playing-cards/releases/tag/1.2.0)
for the current full design.
