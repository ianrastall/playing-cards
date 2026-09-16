# Court-card alignment

All twelve current poker court cards share the same center-dot **anchor pixel (375, 525)** in their 750 × 1050 canvases. Coordinates are zero-based column, row. The chosen pixel is the usual integer width/2, height/2 anchor; the geometric midpoint between pixels is (374.5, 524.5).

## Method

No image generation, redrawing, scaling or interpolation was used. The central turquoise jewel was isolated from surrounding ivory petals and gold outlines in a small center region. Its color-weighted centroid was rounded to its nearest pixel to define a repeatable registration anchor. The original painted dots have slightly different shapes and highlights, so their floating-point centroids are not claimed to be identical. Forcing subpixel equality would require resampling the artwork or changing the dots.

Whole-pixel vertical translations align the anchor. Four cards required no move; eight required a one-pixel move. There were no horizontal moves.

| Card | Vertical shift |
| --- | --- |
| Clubs / Jack | +1 pixel |
| Clubs / King | -1 pixel |
| Clubs / Queen | 0 |
| Diamonds / Jack | +1 pixel |
| Diamonds / King | -1 pixel |
| Diamonds / Queen | 0 |
| Hearts / Jack | +1 pixel |
| Hearts / King | -1 pixel |
| Hearts / Queen | 0 |
| Spades / Jack | 0 |
| Spades / King | -1 pixel |
| Spades / Queen | -1 pixel |

Positive y moves down. The full unrounded measurements, input/output hashes, backup locations and checks are in [court-alignment.json](court-alignment.json).

## Uniform border

The original Spades king supplies one existing border template. The same pixels are copied onto all twelve cards for the outer ivory edge, gold beading and perimeter ornament. Each card's own index panels remain protected, so its rank and suit are retained.

The border mask is outside the rectangle x=[75,675), y=[72,967), with two protected index-panel rectangles subtracted: [28,44,132,290) and [618,760,722,1008). These bounds are explicit in the report. This preserves the central court illustration and index-panel pixels exactly after translation. The interior floral ornament is not replaced with a common plate. The shared border retains the existing template's margins rather than inventing a new frame.

The border pixels under that mask are now byte-identical across all twelve cards. There is no claim that card-specific index panels or all interior flower details are identical.

## Preservation and validation

- Original 750 × 1050 courts are preserved byte-for-byte at `sources/before-court-alignment/poker/<suit>/<rank>.png`.
- All pixels outside the shared-border mask are checked against exact integer-index translations of those originals.
- All masked border pixels are checked against the common reference.
- All dot anchors are checked at (375,525).
- Dimensions remain 750 × 1050 at nominal 300 DPI.
- All 30 back images are unchanged.
- The catalog was rebuilt and checked.

This alignment does not impose exact half-turn symmetry on the portraits, and no existing generation master is modified.

## Reproduction and review

`scripts/align_courts.py` contains the measurements, protected regions, staging and application checks. It refuses to apply a second alignment over the saved report, preventing cumulative shifts.

The staged full-card overview and magnified dot comparison are under the Git-ignored `work/court-alignment/` directory as `preview-after.png` and `centers-after.png`. The report and original backups are tracked repository material.
