# Wide-panel poker numerals — 3 through 9

Generated September 16, 2026 with the built-in image-generation tool. These cards extend the approved enlarged-pip twos while retaining their broad rounded ivory panel, pale champagne-gold filigree, narrow botanical frame, ivory cartouches, gold linework, and ornate ace-derived center pips.

The generated 1060 × 1484 masters are retained under `sources/generated/poker/numerals/wide-panel/`. Each playable face was exported with `scripts/export_face.py` to 750 × 1050 PNG at nominal 300 DPI, without cropping or stretching.

Pip layouts use conventional balanced arrangements: a centered column for threes; two-column arrangements for four, six, and eight; a centered extra pip for five and seven; and a three-by-three grid for nines. Black suits use black pips and indices; hearts and diamonds use deep madder red. Corner suit marks remain solid while central pips use the floral treatment.

## Gallery

| Rank | Spades | Hearts | Diamonds | Clubs |
| --- | --- | --- | --- | --- |
| 3 | ![3S](../../cards/faces/french-suited/poker/spades/3.png) | ![3H](../../cards/faces/french-suited/poker/hearts/3.png) | ![3D](../../cards/faces/french-suited/poker/diamonds/3.png) | ![3C](../../cards/faces/french-suited/poker/clubs/3.png) |
| 4 | ![4S](../../cards/faces/french-suited/poker/spades/4.png) | ![4H](../../cards/faces/french-suited/poker/hearts/4.png) | ![4D](../../cards/faces/french-suited/poker/diamonds/4.png) | ![4C](../../cards/faces/french-suited/poker/clubs/4.png) |
| 5 | ![5S](../../cards/faces/french-suited/poker/spades/5.png) | ![5H](../../cards/faces/french-suited/poker/hearts/5.png) | ![5D](../../cards/faces/french-suited/poker/diamonds/5.png) | ![5C](../../cards/faces/french-suited/poker/clubs/5.png) |
| 6 | ![6S](../../cards/faces/french-suited/poker/spades/6.png) | ![6H](../../cards/faces/french-suited/poker/hearts/6.png) | ![6D](../../cards/faces/french-suited/poker/diamonds/6.png) | ![6C](../../cards/faces/french-suited/poker/clubs/6.png) |
| 7 | ![7S](../../cards/faces/french-suited/poker/spades/7.png) | ![7H](../../cards/faces/french-suited/poker/hearts/7.png) | ![7D](../../cards/faces/french-suited/poker/diamonds/7.png) | ![7C](../../cards/faces/french-suited/poker/clubs/7.png) |
| 8 | ![8S](../../cards/faces/french-suited/poker/spades/8.png) | ![8H](../../cards/faces/french-suited/poker/hearts/8.png) | ![8D](../../cards/faces/french-suited/poker/diamonds/8.png) | ![8C](../../cards/faces/french-suited/poker/clubs/8.png) |
| 9 | ![9S](../../cards/faces/french-suited/poker/spades/9.png) | ![9H](../../cards/faces/french-suited/poker/hearts/9.png) | ![9D](../../cards/faces/french-suited/poker/diamonds/9.png) | ![9C](../../cards/faces/french-suited/poker/clubs/9.png) |

Generation prompts consistently required exact rank counts, standard pip positions, suit-specific silhouettes, paired inverted lower pips, preserved broad-panel framing, and exactly two matching rank indices. As with the twos, the botanical interiors are generatively matched rather than pixel-identical.

## Reversibility correction

Visual QA identified upright lower pips in the initial sixes, sevens, eights, and the spade, heart, and diamond nines. Those 15 playable faces were regenerated with the affected lower pips specified as complete 180-degree rotations, including their botanical interiors. The corrected masters replace the original masters at their canonical paths; `*-before-reversibility.png` retains the prior generated master and `*-reversible.png` retains the corrected-generation source. The Club Nine was already correct and was not regenerated.
