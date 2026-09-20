# Design 2: porcelain and silk back proofs

Two visual prototypes generated with the built-in image-generation tool from
the user's Ming/Tang silk-and-porcelain brief and supplied Gemini notes.
All images and exact prompts are saved in `sources/generated/design2-v2/`.

- `porcelain-cobalt.png`: cobalt lotus ornament, small central floral roundel,
  four satellite roundels, ruyi-like inner edging and fine circle tracery.
- `silk-cinnabar-jade.png`: cinnabar flowers, jade foliage and ochre details,
  with a circular composite-flower center and four smaller roundels.
- The two `*-study.png` files preserve the initial generations before the
  oversized central cartouches were replaced.
- `prompts.json` records all four generation/edit prompts and input references.

Design 1's poker back served only as a geometry reference. Its narrow margin,
floral border band width, and rounded inner and outer corners were requested;
the floral vocabulary was replaced. The existing `sources/d2-01.png` supplied
color and floral-detail inspiration for the silk proof and was not modified.
The target ground is the deck's antique white, `#FAEBD7`.

Historical anchors checked for this exploration:

- [The Met: Tang textile with floral medallion](https://www.metmuseum.org/art/collection/search/39595)
- [The Met: Ming foliated dish with floral scrolls](https://www.metmuseum.org/art/collection/search/40766)

These are contemporary interpretations, not reconstructions of period objects.
The Gemini terminology and palette suggestions are inspiration, not verified
historical specifications. Museum images were not used as generation inputs.

Visual review confirmed complete card compositions, distinct floral frames,
circular centers, and no lettering. All four generated files are 1060 x 1484 RGB.
Geometry, ground color and symmetry are generated approximations: the ground
is not normalized to exact RGB, corners do not yet use the deck's alpha mask,
and half-turn symmetry is not pixel-exact. The artwork remains outside the
active catalog. Production preparation must register the border against the
existing component geometry, normalize the ground, enforce a true half-turn,
and apply the 750 x 1050 poker dimensions and 3.5 mm corner mask before claiming
compatibility with the production deck.
