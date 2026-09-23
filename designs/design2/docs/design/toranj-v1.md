# Balanced toranj backs

The toranj release replaces the assembled gold-panel backs with the calmer
bookbinding structure developed in the structural studies. All 30 backs use one
central toranj medallion, smaller pendant finials, corner quarter-medallions,
connected islimi vines, double inner and outer gold frames, and four nested
values of the colorway ground.

Poker, Bridge, Travel, Jumbo and Tarot have native masters in all five colors.
European Standard is a direct Lanczos resize of the complete finished Bridge
RGBA back and has no independent master.

The exporter maps measured source landmarks to the same production geometry in
every native format:

- 23 px ivory margin at 300 ppi;
- 50 px ornamental border;
- central flower at `((width-1)/2, (height-1)/2)`;
- 3.5 mm physical card-corner radius in the five native formats;
- exact RGBA equality under a 180-degree turn.

Exact half-turn symmetry is constructed from the continuous top half. Its center
line crosses the central lotus and the border's left and right blossoms, so the
rotated lower half joins without the old rule jump or dark vertical line. The
exporter does not average two generated halves.

The permanent audit checks all 30 PNG hashes, dimensions, alpha silhouettes,
central centroids, exact reciprocal pixels, common registered geometry and the
European-from-Bridge derivation. Source masters and prompts are in
`../../sources/generated/design2-toranj-v1/`.

The complete production set is shown in `toranj-v1-review.jpg`.
