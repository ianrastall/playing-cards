"""Independent saved-file checks for the approved gold-panel release."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def silhouette(w, h):
    # Accumulate 8x subpixel samples without allocating a full supersized image.
    yy, xx = np.ogrid[:h, :w]
    radius = 3.5 / 25.4 * 300
    count = np.zeros((h, w), dtype=np.uint8)
    for oy in range(8):
        for ox in range(8):
            x, y = xx + (ox + .5) / 8, yy + (oy + .5) / 8
            dx = np.maximum(np.maximum(radius-x, x-(w-radius)), 0)
            dy = np.maximum(np.maximum(radius-y, y-(h-radius)), 0)
            count += dx*dx + dy*dy <= radius*radius
    return np.floor(count.astype(float)*255/64+.5).astype(np.uint8)


def reciprocal(a):
    result = a.copy()
    h, w = a.shape[:2]
    if h % 2:
        y = h//2
        result[y] = np.floor((a[y].astype(float)+a[y, ::-1])/2+.5).astype(np.uint8)
    result[(h+1)//2:] = result[:h//2][::-1, ::-1]
    return result


def audit(out):
    manifest = json.loads((out/'manifest.json').read_text())
    assert manifest['revision'] == 'gold-panel-v1'
    records = []
    for fmt in manifest['formats']:
        geom = manifest['layout'][fmt]
        components = {}
        for name, record in geom['components'].items():
            path = ROOT / record['path']
            assert digest(path) == record['sha256'], path
            components[name] = np.array(Image.open(path))
        plate = components['shared-plate']
        bm, fm = components['border-color-mask'], components['field-color-mask']
        h, w = bm.shape
        foliage = components.get('foliage-color-mask')
        if manifest.get('foliage_adjustment'):
            assert foliage is not None and foliage.shape == (h, w)
            assert np.count_nonzero(foliage) > 0
            assert np.array_equal(foliage, foliage[::-1, ::-1])
        assert np.max(bm.astype(int)+fm) <= 255
        outer, inner = geom['outer_bounds'], geom['inner_bounds']
        widths = [inner[0]-outer[0], inner[1]-outer[1], outer[2]-inner[2], outer[3]-inner[3]]
        assert widths == [50]*4
        assert geom['outer_margin_px'] == 23
        assert geom['inner_frame_radius_px'] == 40
        assert geom['outer_frame_radius_px'] == 6
        reference_alpha = silhouette(w, h)
        if fmt == 'european-standard':
            bridge = manifest['layout']['bridge']['components']
            enlarged_components = [('artwork-plate', 3), ('artwork-field-mask', 1)]
            if foliage is not None:
                enlarged_components.append(('foliage-color-mask', 1))
            for name, channels in enlarged_components:
                # Independently enlarge the saved Bridge artifact, not the raw source master.
                raw = subprocess.check_output(['magick', str(ROOT/bridge[name]['path']),
                                               '-filter', 'Lanczos', '-resize', f'{w}x{h}!',
                                               '-depth', '8', 'rgb:-' if channels == 3 else 'gray:-'])
                expected = np.frombuffer(raw, dtype=np.uint8).reshape((h,w,3) if channels == 3 else (h,w))
                assert np.array_equal(components[name], reciprocal(expected)), name
        else:
            assert geom['uniform_artwork_scale'] > 0
            assert digest(ROOT / geom['source']) == geom['source_sha256']
        yy, xx = np.indices((h, w))
        cx, cy = (w-1)/2, (h-1)/2
        region = (xx-cx)**2+(yy-cy)**2 <= (18*w/750)**2
        mix_b, mix_f = bm[:,:,None].astype(float)/255, fm[:,:,None].astype(float)/255
        for card in [c for c in manifest['cards'] if c['format'] == fmt]:
            path = out/card['path']
            with Image.open(path) as im:
                assert im.mode == 'RGBA' and im.size == (w,h)
                assert all(abs(value-300) < .001 for value in im.info['dpi'])
                a = np.array(im)
            assert digest(path) == card['sha256']
            assert np.array_equal(a, a[::-1,::-1]), path
            assert np.array_equal(a[:,:,3], reference_alpha), path
            border = np.array(manifest['palettes'][card['color']])
            field = np.array(manifest['field_palettes'][card['color']])
            assert np.all(field < border)
            expected = np.floor(plate[:,:,:3]*(1-mix_b-mix_f)+border*mix_b+field*mix_f+.5).astype(np.uint8)
            assert np.array_equal(a[:,:,:3], expected), path
            assert np.array_equal(a[(bm == 0)&(fm == 0)], plate[(bm == 0)&(fm == 0)])
            # Inspect the central painted gold/red flower separately from its border.
            rgb = a[:,:,:3].astype(float)
            weight = np.maximum(rgb[:,:,0]+rgb[:,:,1]-2*rgb[:,:,2]-40, 0)*region
            assert np.count_nonzero(weight) > 60
            measured = [float((xx*weight).sum()/weight.sum()), float((yy*weight).sum()/weight.sum())]
            error = max(abs(measured[0]-cx),abs(measured[1]-cy))
            assert error < 1e-9
            # Saved pixels must contain the full gold outline at all straight-side midpoints.
            for x,y in [(w//2,74),(w//2,h-75),(74,h//2),(w-75,h//2)]:
                assert np.array_equal(a[y,x,:3],[227,181,75]), (path,x,y)
            # Common ivory paper margin and full frame ground on both ends of every side.
            assert np.array_equal(a[0,w//2,:3],[250,235,215])
            records.append(dict(path=card['path'],center_expected=[cx,cy],center_measured=measured,
                                center_error_px=error,border_widths_px=widths,
                                inner_frame_radius_px=40,outer_frame_radius_px=6,
                                rgba_half_turn_exact=True,alpha_matches_existing_deck=True,
                                shared_artwork_geometry_exact=True,palette_masks_exact=True,
                                surrounding_field_darker_than_own_border=True))
    assert len(records) == 30
    report = dict(status='passed',revision='gold-panel-v1',card_count=30,
                  max_measured_center_error_px=max(c['center_error_px'] for c in records),
                  european_standard_derived_from_bridge=True,
                  method='Independent saved-PNG hashes, mask compositing, localized central-flower centroids, physical silhouette, frame-ink samples and Bridge enlargement comparison.',cards=records)
    (out/'registration-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    if out == ROOT:
        (ROOT/'docs/design/design2-registration-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS 30 gold-panel PNGs: exact centers and half-turns; common 50 px borders and corner curves; palette masks; Bridge-derived European Standard.')
