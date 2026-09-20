# Tarot representative artwork — review v1

Four staged 825 × 1425 RGBA proofs are available in
`work/tarot-review-v1/index.html` and as individual PNGs in that directory.
The tracked overview is [the review sheet](tarot-review-v1-preview.jpg).
These are visual review candidates, not active catalog assets or approval to
expand to the entire deck.

## What was produced

Built-in image generation produced six separate sources: a straight sword,
curved sword, crown, foliage sprig, Empress, and Queen of Cups. Exact prompts,
reference inputs, and generation output locations are saved in
`sources/generated/tarot-review-v1/prompts.json`; all six original PNGs are
copied into that directory. Prepared transparent components are under
`sources/components/tarot/review-v1/`, with hashes and crop/anchor records in
[the layout manifest](tarot-review-layout-v1.json).

`scripts/tarot_review.py` composes those assets with the existing botanical
frame, paired side panels, and front-tracery-v3. It typesets indices/titles and
draws three small index glyphs separately. The font is local Times New Roman
Bold, identified by path and SHA-256 in the manifest, rather than a redistributed
font file. Reproduction on another machine requires that recorded font.

The Ace uses one straight sword, a separate crown, and two foliage instances.
The Ten uses eight instances of the curved sword and two of the straight sword.
Its first nested layout read as a bundle; the review version opens it into five
crossed pairs with alternating local over/under patches. No new sword generation
was needed for that layout change. Mirroring is explicitly recorded. It is an
upright number-card proposal, not a pixel-exact reversible card or a reproduction
of a particular historical Tarot pack.

The Empress and Queen were reduced slightly from the first placements to clear
the botanical frame. Their art is single-ended while their indices are paired
by a half-turn. Full titles sit in the lower interior band. The reviewed labels
are `3`/star, `Q`/cup, `A`/sword, and `10`/sword; additional `N` and `21` panel
specimens are saved for legibility review.

## Validation and review focus

Run `python scripts/tarot_review.py --stage --check` to reproduce the proofs
without image-generation calls. `--prepare` is only for initial component/layout
creation and refuses to overwrite an existing layout manifest.

Checks passed for source/component/font hashes, native dimensions, RGBA output,
exact rerender, semantic emblem counts (1 and 10), index containment, artwork
containment, and title-band clearance. The existing catalog validation also
passes; the 300 active assets remain unchanged.

The work directory includes the render report, saved crossing masks,
`ten-annotated.png`, `ten-instance-audit.jpg`, and `index-specimens.png`.
The nested study is preserved there for comparison. The final proof sheet and
report also have tracked copies in `docs/design/`.

Visual review should judge the figures against the brighter existing frame,
the sword family's fine detail at print size, whether the open Ten arrangement
has the desired ornamental density, and the compact suit/star index treatment.
The art direction, proposed index convention, and full-deck trump ordering still
need review before a production expansion. Only the two needed suit glyphs and
the trump glyph are implemented; this is a four-card prototype renderer.
