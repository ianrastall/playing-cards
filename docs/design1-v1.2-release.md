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

This prepares local release assets. It does not publish or upload them.
