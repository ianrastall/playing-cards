"""Read-only, independent checks of the saved face templates and masks."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from audit_design2_registration import silhouette

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / 'sources/components/design2-face-frames-v1'


def audit():
    manifest = json.loads((COMP / 'manifest.json').read_text())
    config = json.loads((ROOT / 'deck.json').read_text())
    assert set(manifest['formats']) == set(config['formats'])
    source = manifest['source']
    assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256']
    count = 0
    for fmt, spec in manifest['formats'].items():
        w, h = spec['pixels']
        assert [w, h] == config['formats'][fmt]['back_pixels']
        masks = {}
        for name, record in spec['components'].items():
            p = ROOT / record['path']
            assert hashlib.sha256(p.read_bytes()).hexdigest() == record['sha256'], p
            with Image.open(p) as im:
                assert im.mode == 'L' and im.size == (w, h), p
                a = np.array(im)
            assert np.array_equal(a, a[::-1, ::-1]), p
            masks[name] = a
        assert np.array_equal(masks['outline'], np.array(silhouette((w, h))))
        assert not np.any((masks['field'] > 0) & (masks['panels'] > 0))
        assert np.mean(masks['field'] == 255) > .50, 'Insufficient clear artwork space'
        assert masks['field'][h//2, w//2] == 255
        # The recorded safe rectangle must actually fit in the cartouche.
        l, t, r, b = spec['index_safe_box']
        assert r > l and b > t
        assert np.all(masks['panels'][t:b, l:r] == 255), fmt
        assert np.all(masks['panels'][h-b:h-t, w-r:w-l] == 255), fmt
        frames = []
        for color, record in spec['frames'].items():
            p = ROOT / record['path']
            assert hashlib.sha256(p.read_bytes()).hexdigest() == record['sha256'], p
            with Image.open(p) as im:
                assert im.mode == 'RGBA' and im.size == (w, h), p
                assert all(abs(v-300) < .001 for v in im.info['dpi']), p
                a = np.array(im)
            assert np.array_equal(a, a[::-1, ::-1]), p
            assert np.array_equal(a[:, :, 3], masks['outline']), p
            blank = (masks['field'] == 255) | (masks['panels'] == 255)
            assert np.all(a[:, :, :3][blank] == manifest['ground_rgb']), p
            assert np.all(a[:, :, :3][masks['palette'] == 255] == manifest['palettes'][color]), p
            frames.append(a)
            count += 1
        assert len(frames) == 2
        assert np.array_equal(frames[0][masks['palette'] == 0], frames[1][masks['palette'] == 0]), fmt
        print(f'PASS {fmt}: dimensions, hashes, alpha, symmetry, blank fields, index containment, palette isolation')
    assert count == 12
    print('PASS 12 frames and 24 masks; finished-card inventory is unchanged')


if __name__ == '__main__':
    audit()
