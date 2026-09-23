# Softer inner fields — second attempt

The September 22, 2026 revision brings the inner backgrounds closer to their
border colors and reduces their saturation. It affects all five colors in all
six formats. The gold-panel artwork and olive foliage remain unchanged.

For each border RGB color, compute its weighted sRGB gray using
`0.2126 R + 0.7152 G + 0.0722 B`. Blend 35% toward that gray, multiply by 0.88,
and round to the nearest integer. This replaces the previous 0.64 RGB multiplier.
The brightness figure describes weighted encoded RGB, not linear-light luminance.

The existing field masks apply the new palette, including their feathered edges.
Original source masters, registered plates, masks, borders, ivory panels, flowers,
olive leaves, medallions, geometry and alpha are preserved outside those masks.
The original plate padding stays fixed so recoloring is confined to compositing.

`manifest.json` records the formula and revision under `field_adjustment`.
`muted-fields-v2-audit.json` records the comparison against all 30 previous backs,
including unchanged component hashes and exact pixels outside the field masks.
The normal registration audit verifies the output geometry, half-turn symmetry,
alpha, compositing, darker and less saturated fields, and Bridge-derived
European Standard artwork.

Rebuild and promote with:

```text
node designs/design2/scripts/register_gold_panel.mjs --apply
```

The built-in ImageGen blue study is retained in
`sources/generated/design2-muted-fields-v2/`, with its exact prompt. Production
backs use the existing deterministic exporter to preserve the registered artwork.
