# Celtic Poker Queens — first review set

Four new Queens extend the approved rugged Kings: weathered individual faces,
green wool, oatmeal linen, restrained red lining, bronze circlets and torcs,
oak leaves and acorns. Built-in ImageGen created the artwork. These fictional
courts continue the Celtic artistic synthesis described in the existing brief.

| Suit | Upper portrait and attribute |
| --- | --- |
| Spades | Auburn hair; slight rightward three-quarter turn; both eyes; spiral scepter on viewer right |
| Hearts | Chestnut hair and broader face; leftward three-quarter turn; both eyes; red wild rose on viewer right |
| Diamonds | Dark hair and narrower face; leftward three-quarter turn; both eyes; pointed ivory blossom on viewer right |
| Clubs | Silver-streaked braid; leftward three-quarter turn; both eyes; white blossom and closed bud on viewer left |

The existing Design 1 Queens supplied pose references only. The approved Celtic
Spades King supplied the initial style reference; the new Spades Queen supplied
the other Queens' style reference. Targeted corrections fixed Hearts' gaze,
Diamonds' gaze and hand placement, and Clubs' hand placement. The first passes
are preserved but excluded from the viewer's selected review set.

Generated masters remain unchanged under
[queens-v1](../../sources/generated/queens-v1/README.md), with exact prompts,
selected file hashes and dimensions. The four balanced **review faces** live in
[queens-registration-v1](../../sources/components/queens-registration-v1/).
They are not yet approved production cards.

Registration reuses the approved Kings' frame, field mask, paired side roundels,
104-pixel central double-spiral medallion and rounded outline without modifying
those components. Q/suit indices share the Kings' index positions. Each review
face is 750 × 1050 RGBA at 300 ppi, with exact 180-degree symmetry and the same
center at (374.5, 524.5). The upper portrait supplies the lower rotated portrait;
a narrow wool blend softens the waist join. The audit checks shared border
pixels, exact central ornament, alpha, symmetry, source hashes and reconstruction.

[Review the Queens](../../queens.html) · [Four-card proof](queens-v1-proof.png)
· [Registration manifest](queens-registration-v1.json)
· [Audit](queens-registration-v1-audit.json)

```text
python designs/design3/scripts/register_queens.py --check
```
