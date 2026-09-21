# Design 2 suit pip prototypes

All four suit masters are now available. Each is an unmodified transparent
ImageGen prototype intended for both the ace and uniformly resized numeral
pips. Hearts and diamonds use Madder Lake red; spades and clubs use Lamp Black.
The three companion suits were generated with the spade as their style reference.

- [Spades](spades-master.png) · [prompt](spades-prompt.json)
- [Hearts](hearts-master.png) · [prompt](hearts-prompt.json)
- [Diamonds](diamonds-master.png) · [prompt](diamonds-prompt.json)
- [Clubs](clubs-master.png) · [prompt](clubs-prompt.json)

All four PNGs have verified RGBA alpha transparency. Each needs its own measured
jewel anchor and production edge cleanup before final card layout; generated
canvas centers must not be assumed to match the jewel centers.

## Original spade measurements and reference

[spades-master.png](spades-master.png) is the unmodified built-in ImageGen
output: 1254 × 1254 RGBA, with actual exterior transparency. It is one upright
illustration intended for both the ace and uniformly downscaled numeral pips.
The black ground, beaded gold outline, red/ivory lotus and teal foliage follow
Design 2's approved backs and face frames.

[Exact generation prompt](spades-prompt.json). References were
`designs/design2/cards/backs/poker/lamp-black.png` and
`designs/design2/sources/components/design2-face-frames-v1/poker/lamp-black.png`.

This is a prototype component, not a finished ace. Preserve aspect ratio and
alpha when sampling. Future production preparation should clean stray faint
alpha outside the silhouette and register the jewel before producing sizes.
The approximate turquoise chroma centroid is (626.77, 653.55) in zero-based
pixel coordinates; it is not exactly the canvas center (626.5, 626.5).
Do not assume the canvas midpoint is the jewel anchor. A final anchor and pip
spacing will be recorded when this prototype is prepared for card composition.

No completed cards or existing components were replaced.
