# Design 2 Tarot: Chinese name panels

User direction recorded 2026-09-29. The first implementation is now recorded
in [Tarot faces v1](tarot-faces-v1.md): all 97 native layouts have the taller
panels and traditional WenKai lettering. Translations and remaining costumes
are under review. The instructions below retain the construction direction.

## Deck and geometry

Tarot is its own 825 × 1425 deck, with its existing Tarot-size back. Minchiate
describes its 97-card inventory and tradition. The current 750 × 1050 Tarot
exports were recomposed from their source illustrations and archived; they
are not the active Tarot release.

Retain the upper-left and lower-right rank/symbol panels. Add Chinese name
panels in the opposite diagonal: upper right and lower left. The name panels
may be taller than the rank panels to accommodate longer translated names.
Match their cream ground, gold rules, palette and ornamental vocabulary to
the existing frame. Keep the opposite name panels related by a half-turn.

Set the upper-right name as one top-to-bottom column of upright characters.
Rotate that complete name panel 180 degrees for the lower-left counterpart,
so the name reads upright when the card turns. Reserve the extended panels
in the artwork mask before composing illustrations; do not cover finished
artwork with a browser-only overlay.

Choose a shared name-panel height using the longest actual translated title,
with consistent character size and spacing across the deck. Increase panel
height before reducing lettering size. Keep both pairs inside the silhouette
and leave sufficient room for the main illustration. The available height is
promising, but exact fit remains to be established with translated titles.

## Characters and lettering

First choice: traditional Chinese characters in readable calligraphic
lettering that fits the theme. Regular script (楷書, kaishu) can itself be
calligraphic; traditional characters do not require running or cursive script.
Retain recognizable character forms and sufficient stroke separation at
printed size. Treat the Chinese name as functional identification as well as
decoration.

The user permits simplified Chinese if traditional lettering cannot remain
readable after accommodating taller panels. Simplification often reduces
stroke complexity, but it does not inherently reduce the number of characters
or the square space allocated to each character. Simplified lettering can
also be calligraphic. Prefer a coherent character system across the deck to
switching individual cards solely to solve spacing.

Simplified characters are the usual choice for a mainland Chinese audience;
traditional characters remain standard in Taiwan and Hong Kong. Audience
and lettering style are separate choices. Mandarin is a language, not a
lettering style or a choice between traditional and simplified forms.

Preserve each Minchiate identity when translating, including unusual rulers,
virtues and allegories. Do not substitute the names of a different tarot
inventory. Store translations as editable text and typeset with a font that
covers the chosen characters; avoid generated pseudo-lettering.

## Proofing

Start with a short, medium and long translated name on the actual Tarot frame.
Inspect the upright and turned views, lettering at 2.75 × 4.75 in, margins,
stroke clarity, illustration clearance and the balance of all four panels.
Use those proofs to establish the shared panel height and font size before
applying the layout to all 97 cards.

## Reference

- [W3C Requirements for Chinese Text Layout](https://www.w3.org/TR/clreq/):
  character framing, vertical layout, and traditional/simplified usage.
- [National Palace Museum: Qian Feng, Calligraphy in Regular Script](https://digitalarchive.npm.gov.tw/Collection/Detail/31274?dep=P):
  an example of regular script as calligraphy, not a selected production font.
