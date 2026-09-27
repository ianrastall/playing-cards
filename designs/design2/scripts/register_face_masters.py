"""Register approved court/ace/Joker art into the shared Poker face frame.

Generated originals are immutable. This deterministic compositor registers each
central turquoise jewel to the canvas center and reuses the numeral border.
"""
from __future__ import annotations
import argparse
import json
import shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import build_number_cards as numbers

ROOT = numbers.ROOT
WORK = ROOT/'work/registered-faces-v1'
MANIFEST = ROOT/'docs/design/registered-faces-v1.json'
SIZE = numbers.SIZE
CENTER = numbers.CENTER
FRAMES = numbers.FRAMES


def sources():
    for name, rank in [('courts-v1/kings-manifest.json', 'king'),
                       ('courts-v1/queens-manifest.json', 'queen'),
                       ('courts-v1/jacks-manifest.json', 'jack'),
                       ('aces-v1/manifest.json', 'ace'), ('jokers-v1/manifest.json', 'joker')]:
        manifest = ROOT/'sources/generated'/name
        for c in json.loads(manifest.read_text(encoding='utf-8'))['cards']:
            path = manifest.parent/(c.get('path') or c['file'])
            assert numbers.sha(path) == c['sha256']
            suit = c.get('suit') or path.stem.split('-')[-1]
            yield dict(rank=rank, suit=suit, source=numbers.relative(path), source_sha256=c['sha256'])


def jewel(image):
    """Localize only the turquoise center stone, excluding robe and foliage."""
    a = np.array(image.convert('RGB')).astype(float)
    h, w = a.shape[:2]
    yy, xx = np.indices((h, w))
    r, g, b = a.transpose(2, 0, 1)
    mask = (abs(xx-(w-1)/2) < w*.06) & (abs(yy-(h-1)/2) < h*.06)
    weight = np.maximum(np.minimum(g-r, b-r)-18, 0)*mask
    assert weight.sum() > 100, 'No central turquoise stone'
    return [float((weight*xx).sum()/weight.sum()), float((weight*yy).sum()/weight.sum())]


def sample(image, anchor):
    # Map the interior just inside the original dotted frame to the reusable
    # frame's field. Three anchors per axis preserve its shared center exactly.
    a = np.array(image.convert('RGB')).astype(float)
    h, w = a.shape[:2]
    x = np.interp(np.arange(750), [94, CENTER[0], 655], [132, anchor[0], w-132])
    y = np.interp(np.arange(1050), [77, CENTER[1], 972], [102, anchor[1], h-126])
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = (x-x0)[None, :, None], (y-y0)[:, None, None]
    top = a[y0[:, None], x0[None, :]]*(1-fx) + a[y0[:, None], (x0+1)[None, :]]*fx
    bottom = a[(y0+1)[:, None], x0[None, :]]*(1-fx) + a[(y0+1)[:, None], (x0+1)[None, :]]*fx
    return Image.fromarray(np.rint(top*(1-fy)+bottom*fy).astype(np.uint8))


def index_layer(record):
    suit, rank = record['suit'], record['rank']
    layer = Image.new('RGBA', SIZE)
    if rank == 'joker':
        ink = numbers.COLORS['red' if suit == 'red' else 'black']
        draw = ImageDraw.Draw(layer)
        font = ImageFont.truetype(str(numbers.FONT), 20)
        for i, letter in enumerate('JOKER'):
            draw.text((71, 100+i*21), letter, font=font, fill=ink, anchor='mm')
    else:
        index = numbers.prepare_index(suit, {'ace':'A','king':'K','queen':'Q','jack':'J'}[rank])
        layer.alpha_composite(Image.open(ROOT/index['path']), (48, 87))
    layer.alpha_composite(numbers.halfturn(layer))
    return layer


def render(record):
    original = Image.open(ROOT/record['source'])
    anchor = jewel(original)
    # Correct subpixel resampling bias by measuring the output stone too.
    mapped = sample(original, anchor)
    for _ in range(3):
        measured = jewel(mapped)
        delta = np.array(measured)-CENTER
        if max(abs(delta)) < .03:
            break
        anchor = list(np.array(anchor) + delta*np.array([1.43, 1.4]))
        mapped = sample(original, anchor)
    if record['rank'] != 'ace':
        a = np.array(mapped)
        a[525:] = a[:525][::-1, ::-1]
        mapped = Image.fromarray(a)
    color = 'madder-lake' if record['suit'] in ('hearts', 'diamonds', 'red') else 'lamp-black'
    frame = Image.open(FRAMES/f'{color}.png').convert('RGBA')
    field = Image.open(FRAMES/'field-mask.png')
    result = Image.composite(mapped.convert('RGBA'), frame, field)
    result.alpha_composite(index_layer(record))
    result.putalpha(Image.open(FRAMES/'outline-mask.png'))
    return result, dict(frame_color=color, source_center=jewel(original), sampling_anchor=anchor,
                       measured_center=jewel(result), center=list(CENTER))


def stage():
    records = []
    WORK.mkdir(parents=True, exist_ok=True)
    for record in sources():
        im, metrics = render(record)
        suit, rank = record['suit'], record['rank']
        relative = f'jokers/{suit}.png' if rank == 'joker' else f'{suit}/{rank}.png'
        dest = WORK/relative
        numbers.save(im, dest, Renderer='registered-faces-v1', Center=list(CENTER))
        record.update(metrics, path=f'cards/faces/french-suited/poker/{relative}',
                      staged_path=numbers.relative(dest), sha256=numbers.sha(dest))
        records.append(record)
    numbers.write_json(MANIFEST, dict(revision='registered-faces-v1', center=list(CENTER),
        border_policy='Pixel-identical to the existing Poker numeral frames outside field and panels.',
        directional_cards='Aces retain their upright suit shape; courts and Jokers are exact half-turns.',
        frames={p.name:numbers.record(p) for p in FRAMES.glob('*.png')}, cards=records))
    for start in range(0, len(records), 6):
        sheet = Image.new('RGB', (1260, 650), '#e9dfcf')
        draw = ImageDraw.Draw(sheet)
        for i, c in enumerate(records[start:start+6]):
            im = Image.open(ROOT/c['staged_path']).resize((300, 420))
            # Six across at useful 200 x 280 proof scale.
            im.thumbnail((200, 280))
            x, y = (i%3)*420+110, (i//3)*325+5
            sheet.paste(im, (x,y), im)
            draw.text((x,y+287), f"{c['rank'].title()} / {c['suit']}", fill='black')
        sheet.save(WORK/f'proof-{start//6+1}.jpg', quality=95)
    audit()


def audit(active=False):
    spec = json.loads(MANIFEST.read_text(encoding='utf-8'))
    assert len(spec['cards']) == 18
    for r in spec['frames'].values():
        assert numbers.sha(ROOT/r['path']) == r['sha256']
    field = np.array(Image.open(FRAMES/'field-mask.png')) > 0
    panels = np.array(Image.open(FRAMES/'panel-mask.png')) > 0
    outline = np.array(Image.open(FRAMES/'outline-mask.png'))
    reports=[]
    for c in spec['cards']:
        assert numbers.sha(ROOT/c['source']) == c['source_sha256']
        path = ROOT/c['path' if active else 'staged_path']
        with Image.open(path) as im:
            assert im.mode == 'RGBA' and im.size == SIZE
            assert all(abs(d-300)<.01 for d in im.info['dpi'])
            a = np.array(im)
            measured = jewel(im)
        assert numbers.sha(path) == c['sha256']
        frame = np.array(Image.open(FRAMES/f"{c['frame_color']}.png"))
        assert np.array_equal(a[~(field|panels)], frame[~(field|panels)]), path
        assert np.array_equal(a[:,:,3], outline), path
        expected = Image.fromarray(frame)
        expected.alpha_composite(index_layer(c))
        assert np.array_equal(a[panels], np.array(expected)[panels]), path
        error = max(abs(np.array(measured)-CENTER))
        assert error < .15, (path, measured, error)
        if c['rank'] != 'ace':
            assert np.array_equal(a, a[::-1,::-1]), path
        reports.append(dict(path=c['path'], measured_center=measured, center_error_px=error,
                            shared_border_exact=True, half_turn_exact=c['rank']!='ace'))
    numbers.write_json(ROOT/'docs/design/registered-faces-v1-audit.json',
        dict(status='passed', target='active' if active else 'staged', cards=reports,
             maximum_center_error_px=max(c['center_error_px'] for c in reports)))
    print(f"PASS 18 {'active' if active else 'staged'} registered faces: centered jewels, shared borders, indices, alpha and hashes")


def apply():
    audit()
    for c in json.loads(MANIFEST.read_text(encoding='utf-8'))['cards']:
        dest = ROOT/c['path']
        assert not dest.exists() or numbers.sha(dest) == c['sha256'], dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/c['staged_path'], dest)
    config = json.loads((ROOT/'deck.json').read_text(encoding='utf-8'))
    config['face_systems']['french-suited'].update(ranks=['ace',*map(str,range(2,11)),'jack','queen','king'], jokers=['black','red'])
    config['face_renderer']='number-cards-v1 + registered-faces-v1'
    numbers.write_json(ROOT/'deck.json', config)
    audit(True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--active',action='store_true')
    args=parser.parse_args()
    if args.check: audit(args.active)
    elif args.apply: apply()
    else: stage()
