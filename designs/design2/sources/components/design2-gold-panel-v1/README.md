# Gold-panel registration components

Each format has a registered RGB artwork plate, an artwork field-color mask,
an RGBA shared plate with normalized framing, and separate border/field palette
masks. `layout.json` records their hashes and geometry.

Rebuild with `node scripts/register_gold_panel.mjs` from the Design 2 root.
European artwork and field masks are Lanczos enlargements of Bridge, made
reciprocal before framing. Other artwork plates come from their own native
format masters with uniform sampling and translation.
