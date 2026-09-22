# Olive acanthus foliage

The September 22, 2026 olive-leaf update changes the existing green foliage
directly in the export pipeline. It does not use the generated visual study as
production artwork and does not regenerate or modify any source masters.

After the existing source sampling, green-dominant pixels receive a feathered
selection based on green minus blue (12-level ramp) and green minus red
(20-level ramp). The selection is quantized to 8 bits. Inside the selection,
the exporter adds `(green - red) × (1.3, 0.4, -0.2)` to RGB, weighted by selection
strength. This lifts and warms the foliage while retaining its painted tonal
variation. The center medallion and satellite medallions are excluded using the
same source-space protection regions already used by the field-color mask.

No coordinates, artwork bounds, source anchors, framing, alpha, or palette
values change. The field mask is computed from the original RGB before the
foliage adjustment. Every color variant uses the same recolored artwork.
European Standard retains its existing Bridge-derived construction and thus
inherits Bridge's olive foliage through the existing Lanczos enlargement.

Reproduce all 30 finished backs with
`node designs/design2/scripts/register_gold_panel.mjs --apply` from the repository
root. The manifest records the parameters under `foliage_adjustment`; component
folders retain `foliage-color-mask.png` for inspection. The gold-panel release
identifier is unchanged; the foliage adjustment is identified as `olive-leaves-v1`.

The one-time before/after pixel comparison is recorded in
`olive-leaves-v1-audit.json`. The normal registration audit also checks the
exported files, alpha, centers, half-turn symmetry, palette compositing and
Bridge-derived European Standard artwork.
