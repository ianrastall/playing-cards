# Source artwork

`king-spades-provisional.png` is a byte-for-byte copy of the provisional reference from the former Jukebox Solitaire workspace. It is retained for design provenance, not included in the current asset catalog.

Current Prussian Blue backs are themselves the original recoloring sources. They live in `cards/backs/<format>/prussian-blue.png`, avoiding a duplicate master copy.

`generated/poker/jacks/<suit>.png` preserves the four untouched 1060 × 1484 imagegen masters. Current 750 × 1050 exports were produced with the user's explicit approval using `scripts/export_face.py`. The source masters are not counted as additional playable cards in the catalog.

`before-court-alignment/poker/<suit>/<rank>.png` preserves the twelve 750 × 1050 courts immediately before their common-dot/border alignment. They are byte-for-byte originals with hashes in `docs/design/court-alignment.json`; current aligned cards remain under `cards/faces/`.

`generated/poker/aces/<suit>.png` preserves the four untouched 1060 × 1484 ornate ace masters. Current 750 × 1050 exports include deterministic jewel alignment and a shared ace border, documented in `docs/design/aces.md` and reproducible with `scripts/prepare_aces.py`. The ace frame is distinct from the existing shared court frame.
