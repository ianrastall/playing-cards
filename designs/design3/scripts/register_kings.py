"""Build and audit the four approved Celtic Poker Kings without changing masters.

Default stages a proof; --apply installs the audited stage; --check checks release.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SIZE = (750, 1050)
CENTER = (374.5, 524.5)
COMP = ROOT / 'sources/components/kings-registration-v1'
WORK = ROOT / 'work/kings-registration-v1'
DOC = ROOT / 'docs/design/kings-registration-v1.json'
SOURCE = ROOT / 'sources/generated/kings-v2/manifest.json'
FONT = Path('C:/Windows/Fonts/timesbd.ttf')
LANCZOS = Image.Resampling.LANCZOS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def save(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    info = PngImagePlugin.PngInfo()
    info.add_text('Renderer', 'design3-kings-registration-v1')
    info.add_text('Center', json.dumps(CENTER))
    im.save(path, dpi=(300, 300), pnginfo=info)


def symmetric(im):
    a = np.array(im)
    a[525:] = a[:525][::-1, ::-1]
    return Image.fromarray(a)


def records():
    for c in json.loads(SOURCE.read_text(encoding='utf-8'))['cards']:
        path = SOURCE.parent / c['path']
        assert sha(path) == c['sha256'], path
        yield c, path


def rim_center(im):
    """Fit only the gold outer rim near the approved masters' center ornament."""
    a = np.array(im.convert('RGB')).astype(float)
    angles = np.linspace(0, 2*np.pi, 180, endpoint=False)
    radius = np.linspace(62, 73, 90)
    x = 531 + np.cos(angles)[:, None]*radius
    y = 735 + np.sin(angles)[:, None]*radius
    v = a[np.rint(y).astype(int), np.rint(x).astype(int)]
    strength = np.minimum(v[:, :, 0]-v[:, :, 2], v[:, :, 1]-v[:, :, 2])
    ix = strength.argmax(axis=1)
    xx, yy = x[np.arange(len(angles)), ix], y[np.arange(len(angles)), ix]
    fit = np.linalg.lstsq(np.stack([2*xx, 2*yy, np.ones_like(xx)], axis=1),
                          xx*xx+yy*yy, rcond=None)[0]
    return fit[:2].tolist()


def mapped(im, anchor):
    # Register the ornament while holding the inner frame edges fixed. Pixel
    # coordinates refer to pixel centers; this accommodates the odd Spades width.
    a = np.array(im.convert('RGB')).astype(float)
    h, w = a.shape[:2]
    x = np.interp(np.arange(750), [0, CENTER[0], 749], [0, anchor[0], w-1])
    y = np.interp(np.arange(1050), [0, 66, CENTER[1], 983, 1049],
                  [0, 66*(h-1)/1049, anchor[1], 983*(h-1)/1049, h-1])
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    x1, y1 = np.minimum(x0+1, w-1), np.minimum(y0+1, h-1)
    fx, fy = (x-x0)[None, :, None], (y-y0)[:, None, None]
    top = a[y0[:, None], x0[None, :]]*(1-fx) + a[y0[:, None], x1[None, :]]*fx
    bot = a[y1[:, None], x0[None, :]]*(1-fx) + a[y1[:, None], x1[None, :]]*fx
    return Image.fromarray(np.rint(top*(1-fy)+bot*fy).astype(np.uint8))


def joined(im):
    # Blend the robe in a narrow waist band before copying the upper portrait.
    # The complementary weights preserve the half-turn without a cut across wool.
    a = np.array(im).astype(float)
    weight = np.clip((549-np.arange(1050))/49, 0, 1)[:, None, None]
    blend = np.rint(a*weight + a[::-1, ::-1]*(1-weight)).astype(np.uint8)
    return symmetric(Image.fromarray(blend))


def glyph(text, bounds, color):
    font = ImageFont.truetype(str(FONT), 300)
    box = font.getbbox(text)
    mask = Image.new('L', (box[2]-box[0]+8, box[3]-box[1]+8))
    ImageDraw.Draw(mask).text((4-box[0], 4-box[1]), text, font=font, fill=255)
    mask = mask.crop(mask.getbbox())
    scale = min(bounds[0]*4/mask.width, bounds[1]*4/mask.height)
    mask = mask.resize((round(mask.width*scale), round(mask.height*scale)), LANCZOS)
    mask = mask.resize((round(mask.width/4), round(mask.height/4)), LANCZOS)
    layer = Image.new('RGBA', mask.size, color)
    layer.putalpha(mask)
    return layer


def index(suit):
    layer = Image.new('RGBA', SIZE)
    color = (173, 21, 30, 255) if suit in ('hearts', 'diamonds') else (17, 18, 16, 255)
    for text, bounds, center in [('K', (49, 48), (69.5, 119.5)),
            ({'spades':'♠', 'hearts':'♥', 'diamonds':'♦', 'clubs':'♣'}[suit],
             (44, 47), (69.5, 181.5))]:
        sprite = glyph(text, bounds, color)
        xy = tuple(round(c-(n-1)/2) for c, n in zip(center, sprite.size))
        layer.alpha_composite(sprite, xy)
    return symmetric(layer)


def prepare(reference, anchor):
    COMP.mkdir(parents=True, exist_ok=True)
    frame = reference.resize(SIZE, LANCZOS).convert('RGBA')
    # Replace the index ink with cream sampled inside the same source panel.
    patch = frame.crop((37, 78, 102, 88)).resize((65, 125), LANCZOS)
    frame.paste(patch, (37, 85))
    frame = symmetric(frame)
    field = Image.new('L', SIZE)
    d = ImageDraw.Draw(field)
    d.rectangle((77, 67, 672, 524), fill=255)
    d.rectangle((0, 0, 115, 244), fill=0)
    d.ellipse((343, 7, 406, 77), fill=0)
    # A short inward feather keeps the source's painted gold edges continuous.
    field = field.filter(ImageFilter.GaussianBlur(1))
    a = np.array(field)
    a[:67] = 0
    a[:, :77] = 0
    a[:, 673:] = 0
    a[:245, :116] = 0
    field = symmetric(Image.fromarray(a))
    # Retain the painted spiral and rim, using the left half and its rotated
    # partner to give the two coils opposite orientations around the same center.
    cx, cy = anchor
    medallion = reference.transform((140, 140), Image.Transform.AFFINE,
        (1, 0, cx-69.5, 0, 1, cy-69.5), resample=Image.Resampling.BICUBIC)
    medallion = medallion.resize((104, 104), LANCZOS).convert('RGBA')
    a = np.array(medallion)
    a[:, 52:] = a[::-1, :52][:, ::-1]
    medallion = Image.fromarray(a)
    circle = Image.new('L', (400, 400))
    ImageDraw.Draw(circle).ellipse((2, 2, 397, 397), fill=255)
    circle = circle.resize((104, 104), LANCZOS)
    medallion.putalpha(circle)
    side = reference.transform((88, 88), Image.Transform.AFFINE,
        (1, 0, 194.58439202-43.5, 0, 1, 740.12042028-43.5),
        resample=Image.Resampling.BICUBIC).resize((62, 62), LANCZOS).convert('RGBA')
    side.putalpha(circle.resize((62, 62), LANCZOS))
    ornaments = Image.new('RGBA', SIZE)
    ornaments.alpha_composite(side, (107, 494))
    ornaments.alpha_composite(ornaments.transpose(Image.Transpose.ROTATE_180))
    # Reuse the collection's established physical 3.5 mm corner mask, not its art.
    outline = Image.open(REPO / 'designs/design2/sources/components/design2-face-frames-v1/poker/outline-mask.png')
    frame.putalpha(outline)
    for name, im in [('shared-frame.png', frame), ('field-mask.png', field),
                     ('center-medallion.png', medallion), ('paired-side-medallions.png', ornaments),
                     ('outline-mask.png', outline)]:
        save(im, COMP / name)
    for suit in ('spades', 'hearts', 'diamonds', 'clubs'):
        save(index(suit), COMP / f'index-{suit}.png')


def compose(im, anchor, suit):
    frame = Image.open(COMP / 'shared-frame.png').convert('RGBA')
    field = Image.open(COMP / 'field-mask.png').convert('L')
    result = Image.composite(joined(mapped(im, anchor)).convert('RGBA'), frame, field)
    result.alpha_composite(Image.open(COMP / f'index-{suit}.png'))
    result.alpha_composite(Image.open(COMP / 'paired-side-medallions.png'))
    result.alpha_composite(Image.open(COMP / 'center-medallion.png'), (323, 473))
    result.putalpha(Image.open(COMP / 'outline-mask.png'))
    return result


def stage():
    selected = list(records())
    reference = Image.open(selected[0][1]).convert('RGB')
    prepare(reference, rim_center(reference))
    cards = []
    for c, source in selected:
        im = Image.open(source).convert('RGB')
        anchor = rim_center(im)
        output = compose(im, anchor, c['suit'])
        path = WORK / f"{c['suit']}/king.png"
        save(output, path)
        cards.append(dict(suit=c['suit'], rank='king', source=source.relative_to(ROOT).as_posix(),
            source_sha256=c['sha256'], source_center=anchor, center=list(CENTER),
            medallion_bounds=[323, 473, 427, 577], half_turn_exact=True,
            path=f"cards/faces/french-suited/poker/{c['suit']}/king.png",
            staged_path=path.relative_to(ROOT).as_posix(), sha256=sha(path)))
    write_json(DOC, dict(renderer='design3-kings-registration-v1', center=list(CENTER),
        pixels=list(SIZE), trim_inches=[2.5, 3.5], corner_radius_mm=3.5,
        border_policy='One Spades-derived painted Celtic frame, pixel-identical outside field and index ink.',
        center_policy='One 104-pixel painted medallion, left half plus 180-degree partner; paired side roundels centered on the same waist axis.',
        components=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in sorted(COMP.glob('*.png'))],
        cards=cards))
    sheet = Image.new('RGB', (1560, 595), '#e9dfcf')
    draw = ImageDraw.Draw(sheet)
    for i, c in enumerate(cards):
        im = Image.open(ROOT/c['staged_path']).resize((375, 525), LANCZOS)
        sheet.paste(im, (i*390+7, 15), im)
        draw.text((i*390+20, 556), f"King of {c['suit'].title()}", fill='black')
    sheet.save(WORK/'proof.png')
    audit(False)


def audit(active=True):
    spec = json.loads(DOC.read_text(encoding='utf-8'))
    assert len(spec['cards']) == 4
    for c in spec['components']:
        assert sha(ROOT/c['path']) == c['sha256']
    field = np.array(Image.open(COMP/'field-mask.png'))
    frame = np.array(Image.open(COMP/'shared-frame.png'))
    outline = np.array(Image.open(COMP/'outline-mask.png'))
    medallion = Image.open(COMP/'center-medallion.png')
    assert np.array_equal(np.array(medallion), np.array(medallion)[::-1, ::-1])
    yy, xx = np.indices((104, 104))
    weight = np.array(medallion)[:, :, 3].astype(float)
    measured = [(weight*xx).sum()/weight.sum()+323, (weight*yy).sum()/weight.sum()+473]
    assert max(abs(np.array(measured)-CENTER)) < 1e-9
    reports = []
    for c in spec['cards']:
        source = ROOT/c['source']
        assert sha(source) == c['source_sha256']
        path = ROOT/c['path' if active else 'staged_path']
        assert sha(path) == c['sha256']
        with Image.open(path) as im:
            assert im.size == SIZE and im.mode == 'RGBA'
            assert all(abs(d-300)<.01 for d in im.info['dpi'])
            a = np.array(im)
        assert np.array_equal(a, a[::-1, ::-1]), path
        assert np.array_equal(a[:, :, 3], outline), path
        ink = np.array(Image.open(COMP/f"index-{c['suit']}.png"))[:, :, 3]
        shared = (field == 0) & (ink == 0)
        assert np.array_equal(a[shared], frame[shared]), path
        # Confirm release pixels come from the approved source, not only metadata.
        rebuilt = compose(Image.open(source), c['source_center'], c['suit'])
        assert np.array_equal(a, np.array(rebuilt)), path
        reports.append(dict(path=c['path'], measured_center=measured, center_error_px=0,
            shared_border_exact=True, half_turn_exact=True, source_hash_unchanged=True))
    write_json(ROOT/'docs/design/kings-registration-v1-audit.json',
        dict(status='passed', target='active' if active else 'staged', cards=reports))
    print(f"PASS four {'official' if active else 'staged'} Kings: shared frame, exact center and half-turn, alpha, 300 ppi and unchanged sources")


def apply():
    audit(False)
    for c in json.loads(DOC.read_text(encoding='utf-8'))['cards']:
        dest = ROOT/c['path']
        assert not dest.exists() or sha(dest) == c['sha256'], dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/c['staged_path'], dest)
    audit(True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.apply:
        apply()
    elif args.check:
        audit()
    else:
        stage()
