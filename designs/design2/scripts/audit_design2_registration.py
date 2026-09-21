"""Independently inspect saved Design 2 exports; never modifies artwork."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
import argparse

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / 'sources/components/design2-registered-v1'


def silhouette(size):
    # Independent physical silhouette check, sampled at 8x resolution.
    w, h = size
    scale, radius = 8, 3.5/25.4*300
    yy, xx = np.ogrid[:h*scale, :w*scale]
    x, y = (xx+.5)/scale, (yy+.5)/scale
    dx = np.maximum(np.maximum(radius-x, x-(w-radius)), 0)
    dy = np.maximum(np.maximum(radius-y, y-(h-radius)), 0)
    inside = dx*dx + dy*dy <= radius*radius
    coverage = inside.reshape(h, scale, w, scale).mean(axis=(1, 3))
    return Image.fromarray(np.rint(coverage*255).astype(np.uint8))


def audit(out=ROOT):
    manifest = json.loads((out / 'manifest.json').read_text())
    if manifest.get('revision') == 'gold-panel-v1':
        from audit_gold_panel import audit as audit_gold_panel
        return audit_gold_panel(out)
    records = []
    for fmt in manifest['formats']:
        plate = np.array(Image.open(COMP / fmt / 'shared-plate.png').convert('RGBA'))
        mask = np.array(Image.open(COMP / fmt / 'border-color-mask.png').convert('L'))
        h, w = mask.shape
        geom = manifest['layout'][fmt]
        outer, inner = geom['outer_bounds'], geom['inner_bounds']
        widths = [inner[0]-outer[0], inner[1]-outer[1], outer[2]-inner[2], outer[3]-inner[3]]
        assert max(widths)-min(widths) < 1e-9
        reference_alpha = np.asarray(silhouette((w, h)))
        for card in [c for c in manifest['cards'] if c['format'] == fmt]:
            path = out / card['path']
            with Image.open(path) as im:
                assert im.mode == 'RGBA' and im.size == (w, h)
                assert all(abs(d-300) < .001 for d in im.info['dpi'])
                a = np.array(im)
            assert hashlib.sha256(path.read_bytes()).hexdigest() == card['sha256']
            assert np.array_equal(a, a[::-1, ::-1])
            assert np.array_equal(a[:, :, 3], reference_alpha)
            assert np.array_equal(a[mask == 0], plate[mask == 0])
            target = np.array(manifest['palettes'][card['color']])
            mix = mask[:, :, None].astype(float) / 255
            expected = np.floor(plate[:, :, :3]*(1-mix)+target*mix+.5).astype(np.uint8)
            assert np.array_equal(a[:, :, :3], expected)
            # Localize the painted gold/red central disk, not the border or canvas.
            cx, cy = (w-1)/2, (h-1)/2
            yy, xx = np.indices((h, w))
            region = (xx-cx)**2+(yy-cy)**2 <= (18*w/750)**2
            rgb = a[:, :, :3].astype(float)
            weight = np.maximum(rgb[:, :, 0]+rgb[:, :, 1]-2*rgb[:, :, 2]-40, 0)*region
            assert np.count_nonzero(weight) > 60
            measured = [float((xx*weight).sum()/weight.sum()), float((yy*weight).sum()/weight.sum())]
            error = max(abs(measured[0]-cx), abs(measured[1]-cy))
            assert error < 1e-9
            assert np.array_equal(a[0, w//2, :3], [250,235,215])
            records.append(dict(path=card['path'], center_expected=[cx,cy], center_measured=measured,
                                center_error_px=error, border_widths_px=widths,
                                rgba_half_turn_exact=True, shared_frame_geometry_exact=True,
                                unchanged_outside_color_mask=True, alpha_matches_existing_deck=True))
    assert len(records) == 30
    report = dict(status='passed', card_count=30,
                  max_measured_center_error_px=max(c['center_error_px'] for c in records),
                  method='Independent saved-PNG inspection with Pillow/NumPy; localized gold/red disk centroid and source-plate/mask comparisons.',
                  cards=records)
    (out / 'registration-audit.json').write_text(json.dumps(report, indent=2)+'\n')
    if out == ROOT:
        (ROOT / 'docs/design/design2-registration-audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"PASS 30 saved PNGs; maximum measured center error {report['max_measured_center_error_px']:.3g} px; shared frame and masks exact.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='Check staged output instead of approved cards')
    args = parser.parse_args()
    stage = ROOT/'build/design2-gold-panel-v1'
    if not stage.exists():
        stage = ROOT/'build/design2-registered-v1'
    audit(stage if args.build else ROOT)
