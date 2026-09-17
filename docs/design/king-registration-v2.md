# King artwork registration and all-format print packages

The previous compositor added an exactly centered jewel over preserved court
artwork, but did not register the underlying painted layer to that location.
This could conceal a small offset in the flower, medallion, and figure.

The revised renderer measures the original painted central jewel before any
overlay, then translates the entire King interior at its native format size.
It searches around the measured correction using small patches from the
unchanged source, then applies one final bicubic translation to that source.
Repeated rendering does not progressively resample the painting. Native
painted centers are verified within 0.1 pixel of the geometric canvas center;
the shared center jewel is placed afterward. European Standard remains a
direct resize of corrected Bridge.

All 20 King exports are corrected. The other 280 active PNGs, including all
number cards, Jacks, Queens, Jokers, and backs, are byte-identical to the prior
approved expansion. The shared frame, indices, filigree and corner geometry
are retained. The independently painted opposing portraits are not claimed
to have exact half-turn symmetry.

The prior Kings and relevant catalog/manifest/report are preserved under
`sources/before-king-registration-v2/` with SHA-256 hashes. Measurements of the
painted layer before and after registration are in `king-registration-v2.json`.

## Number-card audit

`scripts/audit_alignment.py` checks the actual exported jewel centers for
every ace and number pip: 1,100 measurements across the five formats.
Native-format errors are zero at the recorded precision. European Standard
uses the pixel-center-aware mapping from Bridge; its largest measured error
is approximately 0.095 pixel after interpolation. There is no whole-pixel
number-card drift to correct. Full results are in `pip-alignment-audit-v2.json`.

## Release packages

```text
python scripts/package_decks.py --build --all
python scripts/package_decks.py --check --all
```

The five ZIPs are `design1-poker.zip`, `design1-jumbo.zip`,
`design1-travel.zip`, `design1-bridge.zip`, and `design1-european-standard.zip`,
under `build/releases/`. Each has 54 faces and five backs, copied byte-for-byte
at native size, plus clean bleed and separate blue-guide PNGs (177 PNGs total),
its own dimension-specific README, license, manifest, and hash list.

Print exports use exact 2x pixel replication at 600 ppi. Each has 75 pixels of
antique-white bleed per edge (1/8 inch), and guide proofs have another 75
pixels of white slug per edge. The cut radius remains 3.5 mm. Dimensions,
guide locations, and crop marks are computed independently for each format.
Print files have embedded sRGB profiles. Native alpha and print trim pixels
are checked, along with complete ZIP membership, CRCs, and SHA-256 hashes.

Tarot is excluded from packaging. Building creates local release artifacts;
it does not commit, push, or publish a GitHub release.
