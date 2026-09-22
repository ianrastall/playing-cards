"""Compose the 36 Poker numeral faces from existing frames and pip artwork.

Default: prepare components, stage PNGs and contact sheets, write a manifest.
--apply: independently audit the stage, then install only absent/identical cards.
No image generation calls; original artwork is never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sources/components/pips-v1'
FRAMES = ROOT / 'sources/components/design2-face-frames-v1/poker'
COMP = ROOT / 'sources/components/number-cards-v1'
WORK = ROOT / 'work/number-cards-v1'
DOC = ROOT / 'docs/design'
MANIFEST = DOC / 'number-cards-v1.json'
SIZE = (750, 1050)
CENTER = (374.5, 524.5)
SAFE = (120, 110, 630, 940)
SUITS = ('spades', 'hearts', 'diamonds', 'clubs')
FONT = Path('C:/Windows/Fonts/timesbd.ttf')
COLORS = {'black': (33, 33, 31), 'red': (167, 52, 67)}
LANCZOS = Image.Resampling.LANCZOS


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def save(im, path, **metadata):
    path.parent.mkdir(parents=True, exist_ok=True)
    info = PngImagePlugin.PngInfo()
    info.add_text('Renderer', 'design2-number-cards-v1')
    for key, value in metadata.items():
        info.add_text(key, json.dumps(value, sort_keys=True))
    im.save(path, dpi=(300, 300), pnginfo=info)


def relative(path):
    return path.relative_to(ROOT).as_posix()


def record(path):
    return {'path': relative(path), 'sha256': sha(path)}


def halfturn(im):
    return im.transpose(Image.Transpose.ROTATE_180)


def jewel(im):
    a = np.array(im.convert('RGBA')).astype(np.int16)
    r, g, b, alpha = a.transpose(2, 0, 1)
    mask = (g-r > 18) & (b-r > 18) & (g > 65) & (alpha > 128)
    h, w = mask.shape
    candidates = mask.copy()
    candidates[:h//4] = False
    candidates[3*h//4:] = False
    candidates[:, :w//4] = False
    candidates[:, 3*w//4:] = False
    strength = np.minimum(g-r, b-r) * candidates
    assert strength.max() > 0, 'Missing turquoise jewel'
    sy, sx = np.unravel_index(strength.argmax(), mask.shape)
    connected = Image.fromarray(np.uint8(mask)*255).copy()
    ImageDraw.floodfill(connected, (int(sx), int(sy)), 128)
    weight = np.minimum(g-r, b-r) * (np.array(connected) == 128)
    yy, xx = np.indices(mask.shape)
    return float((weight*xx).sum()/weight.sum()), float((weight*yy).sum()/weight.sum())


def clean_source(suit):
    source = Image.open(SOURCE / f'{suit}-master.png').convert('RGBA')
    cx, cy = jewel(source)
    a = np.array(source)
    connected = Image.fromarray(np.uint8(a[:, :, 3] > 8)*255).copy()
    ImageDraw.floodfill(connected, (round(cx), round(cy)), 128)
    keep = np.array(connected) == 128
    a[~keep] = 0
    source = Image.fromarray(a)
    return source.crop(source.getbbox())


def layout():
    def point(x, y, rotation=0):
        return {'center': [x, y], 'rotation': rotation}

    def paired(points):
        return [p for x, y in points for p in
                (point(x, y), point(749-x, 1049-y, 180))]

    mx, my = CENTER
    four = [(224.5, 254.5), (524.5, 254.5)]
    six = [(224.5, 254.5), (524.5, 254.5), (224.5, my)]
    eight = [(224.5, 224.5), (524.5, 224.5),
             (224.5, 424.5), (524.5, 424.5)]
    grid = [(224.5, 254.5), (mx, 254.5), (524.5, 254.5), (224.5, my)]
    specs = {
        2: (paired([(mx, 274.5)]), (250, 280)),
        3: (paired([(mx, 254.5)]) + [point(mx, my)], (205, 225)),
        4: (paired(four), (195, 220)),
        5: (paired(four) + [point(mx, my)], (180, 205)),
        6: (paired(six), (175, 195)),
        7: (paired(six) + [point(mx, my)], (135, 160)),
        8: (paired(eight), (165, 180)),
        9: (paired(grid) + [point(mx, my)], (135, 155)),
        10: (paired(eight + [(mx, 324.5)]), (140, 160)),
    }
    return {str(rank): {'pips': points, 'component_bounds': list(bounds),
                       'reversibility': 'exact-half-turn' if rank % 2 == 0 else 'upright-center-only'}
            for rank, (points, bounds) in specs.items()}


def prepare_pip(suit, rank, bounds):
    source = clean_source(suit)
    cx, cy = jewel(source)
    # Fit the whole silhouette around its jewel, not the generated canvas center.
    ex, ey = max(cx+.5, source.width-cx-.5), max(cy+.5, source.height-cy-.5)
    scale = min((bounds[0]-8)/(2*ex), (bounds[1]-8)/(2*ey))
    scaled = source.resize((round(source.width*scale), round(source.height*scale)), LANCZOS)
    cx, cy = jewel(scaled)
    dims = tuple(2*math.ceil(n/2) for n in bounds)
    anchor = tuple((n-1)/2 for n in dims)
    sprite = scaled.transform(dims, Image.Transform.AFFINE,
                              (1, 0, cx-anchor[0], 0, 1, cy-anchor[1]),
                              resample=Image.Resampling.BICUBIC)
    a = np.array(sprite)
    a[a[:, :, 3] < 2] = 0
    sprite = Image.fromarray(a)
    measured = jewel(sprite)
    assert max(abs(v-c) for v, c in zip(measured, anchor)) < .5
    path = COMP / f'pips/{suit}/{rank}.png'
    save(sprite, path, SourceSHA256=sha(SOURCE/f'{suit}-master.png'), Anchor=anchor)
    return {**record(path), 'pixels': list(dims), 'anchor': list(anchor),
            'measured_jewel': list(measured), 'alpha_bounds': list(sprite.getbbox())}


def glyph_sprite(text, color, bounds):
    scale = 4
    font = ImageFont.truetype(str(FONT), 320)
    box = font.getbbox(text)
    mask = Image.new('L', (box[2]-box[0]+8, box[3]-box[1]+8))
    ImageDraw.Draw(mask).text((4-box[0], 4-box[1]), text, font=font, fill=255)
    mask = mask.crop(mask.getbbox())
    factor = min(bounds[0]*scale/mask.width, bounds[1]*scale/mask.height)
    mask = mask.resize((round(mask.width*factor), round(mask.height*factor)), LANCZOS)
    sprite = Image.new('RGBA', mask.size, color+(255,))
    sprite.putalpha(mask)
    return sprite


def prepare_index(suit, rank):
    color = COLORS['red' if suit in ('hearts', 'diamonds') else 'black']
    glyphs = {'spades': '\u2660', 'hearts': '\u2665', 'diamonds': '\u2666', 'clubs': '\u2663'}
    image = Image.new('RGBA', (46*4, 116*4))
    number = glyph_sprite(rank, color, (46, 45 if rank == '10' else 54))
    symbol = glyph_sprite(glyphs[suit], color, (40, 40))
    image.alpha_composite(number, ((image.width-number.width)//2, 4*4))
    image.alpha_composite(symbol, ((image.width-symbol.width)//2, 71*4))
    image = image.resize((46, 116), LANCZOS)
    path = COMP / f'indices/{suit}/{rank}.png'
    save(image, path, Typeface='Times New Roman Bold', Suit=suit, Rank=rank)
    return {**record(path), 'top_left': [48, 87], 'pixels': [46, 116]}


def render(suit, rank, spec):
    color = 'madder-lake' if suit in ('hearts', 'diamonds') else 'lamp-black'
    frame = Image.open(FRAMES/f'{color}.png').convert('RGBA')
    base = Image.open(ROOT/spec['components'][suit]['path']).convert('RGBA')
    positions = []
    for p in spec['pips']:
        sprite = halfturn(base) if p['rotation'] else base
        xy = tuple(round(c-(n-1)/2) for c, n in zip(p['center'], sprite.size))
        frame.alpha_composite(sprite, xy)
        positions.append({'top_left': list(xy), 'rotation': p['rotation']})
    index = Image.open(ROOT/spec['indices'][suit]['path']).convert('RGBA')
    indices = Image.new('RGBA', SIZE)
    indices.alpha_composite(index, (48, 87))
    indices.alpha_composite(halfturn(indices))
    frame.alpha_composite(indices)
    destination = WORK / f'cards/{suit}/{rank}.png'
    save(frame, destination, Suit=suit, Rank=rank, PipCount=len(positions),
         Reversibility=spec['reversibility'], PipSourceSHA256=sha(SOURCE/f'{suit}-master.png'))
    return {'suit': suit, 'rank': rank, 'path': f'cards/faces/french-suited/poker/{suit}/{rank}.png',
            'staged_path': relative(destination), 'sha256': sha(destination),
            'pixels': list(SIZE), 'reversibility': spec['reversibility'], 'placements': positions}


def contact_sheets():
    for suit in SUITS:
        sheet = Image.new('RGB', (960, 1416), '#e9dfcf')
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype(str(FONT), 22)
        for i, rank in enumerate(range(2, 11)):
            x, y = (i % 3)*320, (i//3)*472
            im = Image.open(WORK/f'cards/{suit}/{rank}.png').convert('RGBA')
            im = im.resize((300, 420), LANCZOS)
            sheet.paste(im, (x+10, y+10), im)
            draw.text((x+14, y+439), f'{rank} of {suit.title()}', font=font, fill='#35281c')
        path = DOC / f'number-cards-v1-{suit}.jpg'
        sheet.save(path, quality=93, subsampling=0)


def stage():
    ranks = layout()
    for rank, spec in ranks.items():
        spec['components'] = {s: prepare_pip(s, rank, spec['component_bounds']) for s in SUITS}
        spec['indices'] = {s: prepare_index(s, rank) for s in SUITS}
    manifest = {
        'revision': 'design2-number-cards-v1', 'status': 'rendered-review',
        'format': 'poker', 'pixels': list(SIZE), 'dpi': 300,
        'coordinate_basis': 'zero-based pixel centers', 'center': list(CENTER),
        'safe_pip_box': list(SAFE), 'ranks': ranks,
        'sources': {s: record(SOURCE/f'{s}-master.png') for s in SUITS},
        'frames': {c: record(FRAMES/f'{c}.png') for c in ('lamp-black', 'madder-lake')},
        'font': {'name': 'Times New Roman Bold', 'sha256': sha(FONT)},
        'seven_policy': 'Centered seventh pip; six surrounding pips form exact rotated pairs.',
        'odd_rank_policy': 'Only the single central upright pip is exempt from half-turn symmetry.',
        'preparation': 'Retain connected pip silhouette above alpha 8, crop, uniform Lanczos scale, subpixel jewel registration. Original masters unchanged.',
        'cards': [render(s, r, ranks[r]) for s in SUITS for r in ranks],
    }
    write_json(MANIFEST, manifest)
    contact_sheets()
    print('Staged 36 Poker number cards, 72 components and four review sheets.')


def apply():
    from audit_number_cards import audit
    audit(active=False)
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    # Validate all destinations before installing any card.
    for card in manifest['cards']:
        destination = ROOT/card['path']
        if destination.exists() and sha(destination) != card['sha256']:
            raise FileExistsError(f'Refusing to overwrite different artwork: {destination}')
    for card in manifest['cards']:
        destination = ROOT/card['path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copyfile(ROOT/card['staged_path'], destination)
    audit(active=True)
    print('Installed all 36 checked Poker number cards.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    apply() if args.apply else stage()
