"""Independently check saved numeral PNGs: counts, clearance and half-turns."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'docs/design/number-cards-v1.json'
FRAMES = ROOT/'sources/components/design2-face-frames-v1/poker'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def regions(mask):
    """Count connected visible shapes from final pixels, not layout metadata."""
    remaining = mask.copy()
    boxes = []
    while remaining.any():
        y, x = np.argwhere(remaining)[0]
        flood = Image.fromarray(np.uint8(remaining)*255).copy()
        ImageDraw.floodfill(flood, (int(x), int(y)), 128)
        component = np.array(flood) == 128
        assert component.any()
        remaining[component] = False
        if component.sum() >= 50:
            ys, xs = np.nonzero(component)
            boxes.append([int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)])
    return boxes


def audit(active=False):
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    cards = manifest['cards']
    expected = {(s, str(r)) for s in ('spades', 'hearts', 'diamonds', 'clubs') for r in range(2, 11)}
    assert len(cards) == 36 and {(c['suit'], c['rank']) for c in cards} == expected
    for source in (*manifest['sources'].values(), *manifest['frames'].values()):
        assert digest(ROOT/source['path']) == source['sha256']
    field = np.array(Image.open(FRAMES/'field-mask.png')) == 255
    panels = np.array(Image.open(FRAMES/'panel-mask.png')) == 255
    outline = np.array(Image.open(FRAMES/'outline-mask.png'))
    safe = np.zeros(field.shape, dtype=bool)
    x0, y0, x1, y1 = manifest['safe_pip_box']
    safe[y0:y1, x0:x1] = True
    assert field[safe].all()
    results = []
    for card in cards:
        suit, rank = card['suit'], card['rank']
        path = ROOT/card['path' if active else 'staged_path']
        assert digest(path) == card['sha256'], path
        with Image.open(path) as im:
            im.load()
            assert im.size == (750, 1050) and im.mode == 'RGBA', path
            assert all(abs(v-300) < .01 for v in im.info['dpi'])
            a = np.array(im)
        assert np.array_equal(a[:, :, 3], outline), path
        color = 'madder-lake' if suit in ('hearts', 'diamonds') else 'lamp-black'
        frame = np.array(Image.open(FRAMES/f'{color}.png').convert('RGBA'))
        changed = np.any(a != frame, axis=2)
        assert not changed[~(field | panels)].any(), f'Frame altered: {path}'
        assert not changed[field & ~safe].any(), f'Pip outside clear area: {path}'
        difference = np.max(np.abs(a[:, :, :3].astype(int)-frame[:, :, :3].astype(int)), axis=2)
        boxes = regions((difference > 12) & field)
        assert len(boxes) == int(rank), f'Visible pip count {len(boxes)} != {rank}: {path}'
        spec = manifest['ranks'][rank]
        pips = spec['pips']
        assert len(pips) == int(rank)
        centers = [tuple(p['center']) for p in pips]
        assert len(set(centers)) == len(centers)
        assert np.allclose(np.mean(centers, axis=0), (374.5, 524.5), atol=0), path
        for p in pips:
            cx, cy = p['center']
            assert sum(l <= cx < r and t <= cy < b for l, t, r, b in boxes) == 1
            if (cx, cy) != (374.5, 524.5):
                opposite = {'center': [749-cx, 1049-cy], 'rotation': (p['rotation']+180) % 360}
                assert opposite in pips, f'Missing rotated counterpart: {path}'
        comp = spec['components'][suit]
        assert digest(ROOT/comp['path']) == comp['sha256']
        sprite = Image.open(ROOT/comp['path']).convert('RGBA')
        occupied = np.zeros(field.shape, dtype=bool)
        for placement in card['placements']:
            rotated = sprite.transpose(Image.Transpose.ROTATE_180) if placement['rotation'] else sprite
            x, y = placement['top_left']
            alpha = np.array(rotated)[:, :, 3] > 0
            h, w = alpha.shape
            assert safe[y:y+h, x:x+w][alpha].all()
            assert not occupied[y:y+h, x:x+w][alpha].any(), f'Pip overlap: {path}'
            occupied[y:y+h, x:x+w] |= alpha
        index = spec['indices'][suit]
        assert digest(ROOT/index['path']) == index['sha256']
        idx = Image.open(ROOT/index['path']).convert('RGBA')
        index_layer = Image.new('RGBA', (750, 1050))
        index_layer.alpha_composite(idx, tuple(index['top_left']))
        index_layer.alpha_composite(index_layer.transpose(Image.Transpose.ROTATE_180))
        assert not (np.array(index_layer)[:, :, 3] > 0)[~panels].any()
        expected_indices = Image.fromarray(frame).copy()
        expected_indices.alpha_composite(index_layer)
        assert np.array_equal(a[panels], np.array(expected_indices)[panels])
        mismatch = np.any(a != a[::-1, ::-1], axis=2)
        if int(rank) % 2 == 0:
            assert not mismatch.any(), f'Even rank not exactly reversible: {path}'
        else:
            allowed = np.zeros(field.shape, dtype=bool)
            w, h = sprite.size
            x, y = (750-w)//2, (1050-h)//2
            allowed[y:y+h, x:x+w] = True
            assert not mismatch[~allowed].any(), f'Odd rank differs outside center pip: {path}'
        results.append({'suit': suit, 'rank': rank, 'visible_pips': len(boxes),
                        'pip_boxes': boxes, 'half_turn_mismatch_pixels': int(mismatch.sum()),
                        'symmetry_exception': None if int(rank) % 2 == 0 else 'single upright center pip',
                        'sha256': card['sha256']})
    baseline = ROOT/'work/number-cards-v1/input-hashes.json'
    preserved = None
    if baseline.exists():
        original = json.loads(baseline.read_text(encoding='utf-8'))
        repo = ROOT.parents[1]
        for name, checksum in original.items():
            assert digest(repo/name) == checksum, f'Existing image changed: {name}'
        preserved = len(original)
    report = {'status': 'passed', 'target': 'active' if active else 'staged',
              'cards_checked': len(results), 'exact_half_turn_cards': 20,
              'upright_center_only_cards': 16, 'preserved_original_images': preserved,
              'checks': ['visible connected pip counts', 'nonoverlap and clear field containment',
                         'index containment and exact opposing indices', 'frame and silhouette preservation',
                         '750x1050 RGBA and 300 DPI', 'full pixel half-turn comparisons',
                         'source and output hashes'], 'cards': results}
    (ROOT/'docs/design/number-cards-v1-audit.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS {len(results)} {report["target"]} cards: visible counts, spacing, indices, dimensions, alpha, hashes; 20 exact half-turns, 16 center-only exceptions.')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--active', action='store_true')
    args = parser.parse_args()
    audit(active=args.active)
