# Design 2 — complete French-suited formats

The owner requested the remaining sets before releasing Design 2, with European
Standard derived from Bridge. Four sets of 54 faces add 216 official PNGs.
Poker and the separate 97-card Tarot deck remain byte-for-byte unchanged.

| Format | Pixels | Center in pixel coordinates | Construction |
| --- | --- | --- | --- |
| Bridge | 675 × 1050 | (337, 524.5) | Source art and pip components, narrow shared frame |
| Travel | 525 × 750 | (262, 374.5) | Source art and smaller uniformly scaled pips |
| Jumbo | 1050 × 1500 | (524.5, 749.5) | Source art and larger uniformly scaled pips |
| European Standard | 696 × 1074 | (347.5, 536.5) | Finished Bridge field resized; shared frame/indices reapplied |

All faces are RGBA at 300 ppi and retain each existing shared frame's rounded
alpha. Court, ace and Joker images are sampled from immutable generated masters,
with the central turquoise stone registered to the new canvas center before
mask composition. Pips come from their original transparent silhouettes, with
uniform scaling and subpixel registration; each rank's positions are recomposed
for the target canvas. Existing format masks protect borders and index panels.

Even ranks, courts and Jokers are exactly reversible. Odd ranks retain one
upright center pip, with exact rotated pairs around it. Aces retain their upright
suit shape. All indices have exact opposing partners.

The [manifest](french-formats-v1.json) records source/component/output hashes,
pip placements and centers. The [independent audit](french-formats-v1-audit.json)
checks final visible pip counts, pip center positions, allowed central exceptions,
exact half-turns, common borders and index panels, alpha and density.

```text
python designs/design2/scripts/expand_french_faces.py
python designs/design2/scripts/expand_french_faces.py --apply
python designs/design2/scripts/expand_french_faces.py --check
```

The first command stages and audits; apply installs absent or identical artwork.
European Standard derives from the staged Bridge cards, whose hashes must equal
the active Bridge inputs at release. Originals are preserved in `sources/`.
