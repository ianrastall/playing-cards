# Balanced toranj masters

This source set contains 25 native built-in ImageGen masters: five colors for
Poker, Bridge, Travel, Jumbo and Tarot. Poker uses the accepted structural
colorway studies. The other formats were independently recomposed from the
Madder Lake Poker reference and then edited into the other four colorways.

Every native format has its own physical composition:

- Bridge is narrower, with extended vertical vine passages.
- Travel uses fewer, broader motifs for its smaller printed size.
- Jumbo allows fuller modeling and more breathing room.
- Tarot is distinctly taller, with elongated upper and lower vine passages.

The exporter registers measured outer and inner frame landmarks to a common
23 px ivory margin and 50 px ornamental border. It places the central flower at
the geometric center, retains one continuous top half, and rotates that half to
construct the bottom exactly. This makes every saved PNG pixel-exact under a
half turn without averaging or a visible midpoint join.

European Standard has no native master. It is produced only by resizing the
finished Bridge back.

The exact format and color-edit prompts are in `prompts.md`. These source images
are not themselves production cards; run `python scripts/render_toranj_backs.py`
from the Design 2 root to register and export them.
