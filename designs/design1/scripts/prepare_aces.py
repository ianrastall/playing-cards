"""Export/center the four ornate aces and share their existing Spades frame.

Run without arguments to stage; inspect work/ace-preparation/preview-final.png,
then use --apply to install new ace files. Existing active assets are not replaced.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
from PIL import Image, PngImagePlugin
from align_courts import border_mask

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work/ace-preparation'
SUITS = ('spades', 'hearts', 'diamonds', 'clubs')
TARGET = np.array([375, 525])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def center(a):
    roi = a[490:555, 345:405, :3].astype(float)
    r, g, b = roi.transpose(2, 0, 1)
    m = (g-r > 18) & (b-r > 18) & (g > 65)
    if not 200 <= m.sum() <= 700:
        raise ValueError('Unexpected turquoise jewel segmentation')
    w = np.minimum(g-r, b-r) * m
    yy, xx = np.indices(m.shape)
    c = np.array([(xx*w).sum()/w.sum()+345, (yy*w).sum()/w.sum()+490])
    return np.floor(c+.5).astype(int), c


def shift_interior(a, shift):
    # Exact integer translation on the central emblem, fading to zero before
    # the fixed frame. Only surrounding ornament in the transition is resampled.
    yy, xx = np.indices(a.shape[:2], dtype=float)
    fx = np.minimum(np.clip((xx-75)/35, 0, 1), np.clip((675-xx)/35, 0, 1))
    fy = np.minimum(np.clip((yy-75)/110, 0, 1), np.clip((955-yy)/90, 0, 1))
    # Keep the entire corner cartouches fixed, including their outlines.
    tl = np.clip(np.maximum((xx-145)/40, (yy-300)/60), 0, 1)
    br = np.clip(np.maximum((605-xx)/40, (750-yy)/60), 0, 1)
    weight = fx * fy * tl * br
    sx = xx - int(shift[0])*weight
    sy = yy - int(shift[1])*weight
    x0 = np.floor(sx).astype(int); y0 = np.floor(sy).astype(int)
    x1 = np.minimum(x0+1, 749); y1 = np.minimum(y0+1, 1049)
    wx = (sx-x0)[..., None]; wy = (sy-y0)[..., None]
    values = (a[y0,x0]*(1-wx)*(1-wy) + a[y0,x1]*wx*(1-wy)
              + a[y1,x0]*(1-wx)*wy + a[y1,x1]*wx*wy)
    out = np.clip(np.rint(values), 0, 255).astype(np.uint8)
    rigid = weight == 1
    translated = np.roll(a, (int(shift[1]), int(shift[0])), axis=(0,1))
    assert np.array_equal(out[rigid], translated[rigid])
    return out


def stage():
    for suit in SUITS:
        export = WORK / f'exports/{suit}.png'
        if not export.exists():
            subprocess.run([sys.executable, str(ROOT/'scripts/export_face.py'),
                            str(ROOT/f'sources/generated/poker/aces/{suit}.png'),
                            str(export)], check=True)
    template_path = WORK / 'exports/spades.png'
    template = np.asarray(Image.open(template_path).convert('RGB'))
    mask = border_mask()
    entries = []
    sheet = Image.new('RGB', (1500, 2100), 'white')
    for i, suit in enumerate(SUITS):
        source = ROOT / f'sources/generated/poker/aces/{suit}.png'
        export = WORK / f'exports/{suit}.png'
        with Image.open(export) as im:
            a = np.asarray(im.convert('RGB'))
            assert im.size == (750,1050)
            anchor, centroid = center(a)
            shift = TARGET-anchor
            assert abs(shift).max() <= 10
            out = shift_interior(a, shift)
            out[mask] = template[mask]
            after_anchor, after_centroid = center(out)
            assert np.array_equal(after_anchor, TARGET)
            assert np.array_equal(out[mask], template[mask])
            meta = PngImagePlugin.PngInfo()
            for key, value in im.text.items():
                meta.add_text(key, str(value))
            meta.add_text('Preparation', 'scripts/prepare_aces.py; rigid emblem shift, tapered surround, common ace frame')
            meta.add_text('JewelAnchorXY', '375,525')
            meta.add_text('EmblemShiftXY', ','.join(map(str,shift)))
            candidate = WORK / f'final/{suit}.png'
            candidate.parent.mkdir(parents=True, exist_ok=True)
            options = {'icc_profile': im.info['icc_profile']} if im.info.get('icc_profile') else {}
            Image.fromarray(out).save(candidate, dpi=(300,300), pnginfo=meta, **options)
        with Image.open(candidate) as saved:
            assert np.array_equal(np.asarray(saved),out)
            assert all(abs(d-300)<.001 for d in saved.info['dpi'])
        entries.append(dict(suit=suit, path=f'cards/faces/french-suited/poker/{suit}/ace.png',
                            source=source.relative_to(ROOT).as_posix(), source_sha256=digest(source),
                            export_sha256=digest(export), candidate=candidate.relative_to(ROOT).as_posix(),
                            sha256=digest(candidate), before_centroid=centroid.tolist(),
                            shift_xy=shift.tolist(), after_centroid=after_centroid.tolist(),
                            anchor_xy=after_anchor.tolist(), shared_ace_border_exact=True))
        sheet.paste(Image.fromarray(out),((i%2)*750,(i//2)*1050))
        print(f'{suit}: {anchor.tolist()} -> {after_anchor.tolist()}')
    sheet.resize((1050,1470), Image.Resampling.LANCZOS).save(WORK/'preview-final.png')
    report = dict(canvas=[750,1050], nominal_dpi=300, target_anchor=[375,525],
                  coordinate_basis='Zero-based rounded chroma-weighted turquoise jewel centroid',
                  method='Lanczos export, exact whole-pixel central-emblem translation; bilinear tapered displacement of surrounding ornament to keep frame and corner cartouches fixed; common ace frame copied from Spades export',
                  frame_note='Aces share their own frame. The court frame was not used because its different inner geometry created visible joins.',
                  template_source='sources/generated/poker/aces/spades.png',
                  border_mask='scripts.align_courts.border_mask', cards=entries)
    (WORK/'final-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


def apply():
    report = json.loads((WORK/'final-report.json').read_text(encoding='utf-8'))
    for e in report['cards']:
        assert not (ROOT/e['path']).exists(), 'Refusing to overwrite an active ace'
        assert digest(ROOT/e['candidate']) == e['sha256']
        assert digest(ROOT/e['source']) == e['source_sha256']
    for e in report['cards']:
        with (ROOT/e['path']).open('xb') as f:
            f.write((ROOT/e['candidate']).read_bytes())
    (ROOT/'docs/design/ace-preparation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Installed four new aces; masters retained.')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply',action='store_true')
    args=p.parse_args()
    apply() if args.apply else stage()
