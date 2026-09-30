"""Compose/check Design 2's separate 825x1425 Tarot deck from source layers.

Default writes review output; --check compares it; --apply archives the old
Poker-sized Tarot exports and promotes a complete checked 97-card inventory.
No flattened card is resized and no image generation occurs during builds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

import build_minchiate_review as prior

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
RAW = ROOT / 'sources/generated/tarot-faces-v1'
OUT = ROOT / 'sources/components/tarot-faces-v1'
FRAMES = OUT / 'frame'
SIZE = (825, 1425)
CENTER = (412, 712)
GROUND = (250, 235, 215)
INKS = {'lamp-black': (33, 33, 31, 255), 'madder-lake': (167, 52, 67, 255)}
NAMES_FILE = ROOT / 'docs/design/tarot-names-zh-Hant.json'
NAMES = json.loads(NAMES_FILE.read_text(encoding='utf-8'))
CHINESE_FONT = ROOT / 'sources/fonts/lxgw-wenkai-tc-v1.522/LXGWWenKaiTC-Regular.ttf'
LATIN_FONT = prior.FONT
MANIFEST = ROOT / 'docs/design/tarot-faces-v1.json'
PROOFS = ('the-empress', 'king-of-swords', 'page-of-cups', 'knight-of-swords', 'the-fool', 'the-world')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=path.relative_to(REPO).as_posix(), sha256=sha(path))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def reciprocal(array):
    result = array.copy()
    h, w = result.shape[:2]
    result[h//2+1:] = result[:h//2][::-1, ::-1]
    result[h//2, w//2+1:] = result[h//2, :w//2][::-1]
    return result


def flood(rgb, seed):
    pale = ((rgb[:, :, 0] > 225) & (rgb[:, :, 1] > 210) & (rgb[:, :, 2] > 185))
    mask = Image.fromarray(np.uint8(pale) * 255).copy()
    assert mask.getpixel(seed) == 255, ('Not inside cream region', seed)
    ImageDraw.floodfill(mask, seed, 128)
    return np.uint8(np.asarray(mask) == 128) * 255


def top_bounds(mask):
    top = mask.copy()
    top[SIZE[1]//2:] = 0
    return Image.fromarray(top).getbbox()


def frame_layers():
    source = Image.open(RAW / 'frame-master.png').convert('RGBA')
    # Register a reusable generated template at the native Tarot canvas.
    rgb = reciprocal(np.array(source.resize(SIZE, Image.Resampling.LANCZOS)))
    field = reciprocal(flood(rgb, CENTER))
    ranks = reciprocal(flood(rgb, (78, 180)))
    names = reciprocal(flood(rgb, (747, 290)))
    outside = reciprocal(flood(rgb, (412, 3)))
    assert not np.any((field > 0) & ((ranks > 0) | (names > 0)))
    assert not np.any((ranks > 0) & (names > 0))
    assert np.count_nonzero(field) > 600_000
    assert np.count_nonzero(names) > np.count_nonzero(ranks) * 1.5
    rgb[(field > 0) | (ranks > 0) | (names > 0) | (outside > 0), :3] = GROUND
    # Use the matching Tarot back's exact physical trim silhouette.
    alpha = np.array(Image.open(ROOT / 'cards/backs/tarot/lamp-black.png').getchannel('A'))
    rgb[:, :, 3] = alpha
    color = rgb[:, :, :3].astype(float)
    hi, lo = color.max(axis=2), color.min(axis=2)
    mix = np.clip((125-hi)/70, 0, 1) * np.clip((42-(hi-lo))/28, 0, 1)
    mix[(field > 0) | (ranks > 0) | (names > 0) | (outside > 0)] = 0
    frames = {}
    for name, ink in INKS.items():
        result = rgb.copy()
        result[:, :, :3] = np.rint(color * (1-mix[:, :, None]) + np.array(ink[:3]) * mix[:, :, None])
        frames[name] = Image.fromarray(result)
    masks = {'field': Image.fromarray(field), 'index': Image.fromarray(ranks),
             'name': Image.fromarray(names), 'outline': Image.fromarray(alpha)}
    geometry = dict(index_top_bounds=list(top_bounds(ranks)), name_top_bounds=list(top_bounds(names)),
                    center=list(CENTER), pixels=list(SIZE), chinese_font_pixels=52,
                    chinese_line_step_pixels=66)
    return frames, masks, geometry


def chinese_name(card):
    if card['kind'] in ('trump', 'fool'):
        return NAMES['trumps'][card['id']]
    rank = NAMES['maid'] if card['rank'] == 'page' and card['suit'] in ('cups', 'coins') else NAMES['ranks'][card['rank']]
    return NAMES['suits'][card['suit']] + rank


def source_path(card):
    name = prior.PIPS[card['suit']] if card['kind'] == 'pip' else card['id']
    revised = RAW / (name + '.png')
    return revised if revised.exists() else prior.master_path(name)


def source_component(path):
    with Image.open(path) as actual:
        assert actual.mode == 'RGBA', path
        alpha = np.array(actual.getchannel('A'))
        assert np.count_nonzero(alpha == 0) > 100, path
        bounds = Image.fromarray(np.uint8(alpha > 8) * 255).getbbox()
        assert bounds
        bounds = (max(0, bounds[0]-4), max(0, bounds[1]-4),
                  min(actual.width, bounds[2]+4), min(actual.height, bounds[3]+4))
        return actual.crop(bounds), list(bounds)


def place(layer, source, box, center=CENTER, angle=0):
    fitted = ImageOps.contain(source, box, Image.Resampling.LANCZOS)
    if angle:
        fitted = fitted.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    anchor = prior.visual_center(fitted)
    x, y = np.array(center) - anchor
    visible = Image.fromarray(np.uint8(np.array(fitted.getchannel('A')) > 8) * 255).getbbox()
    assert visible[0]+x >= 0 and visible[1]+y >= 0 and visible[2]+x <= SIZE[0] and visible[3]+y <= SIZE[1]
    transformed = fitted.transform(SIZE, Image.Transform.AFFINE, (1, 0, -x, 0, 1, -y), Image.Resampling.BICUBIC)
    layer.alpha_composite(transformed)
    return dict(box=list(box), center=list(center), rotation=angle,
                source_anchor=anchor.tolist(), translation=[float(x), float(y)])


def balance(art):
    anchor = prior.visual_center(art)
    bounds = Image.fromarray(np.uint8(np.array(art.getchannel('A')) > 8)*255).getbbox()
    # Shared safe rectangle clears both taller name cartouches and the title.
    safe = (144, 137, 681, 1269)
    distances = [anchor[0]-bounds[0], bounds[2]-1-anchor[0], anchor[1]-bounds[1], bounds[3]-1-anchor[1]]
    room = [CENTER[0]-safe[0], safe[2]-1-CENTER[0], CENTER[1]-safe[1], safe[3]-1-CENTER[1]]
    scale = min(1., *(r/max(1, d) for r, d in zip(room, distances)))
    offset = anchor - np.array(CENTER)/scale
    for _ in range(30):
        result = art.transform(SIZE, Image.Transform.AFFINE,
                               (1/scale, 0, float(offset[0]), 0, 1/scale, float(offset[1])), Image.Resampling.BICUBIC)
        measured = prior.visual_center(result)
        error = measured - np.array(CENTER)
        if max(abs(error)) < .2:
            return result, dict(scale=scale, sampling_offset=offset.tolist(), measured_center=measured.tolist(),
                                max_error_pixels=float(max(abs(error))), safe_box=list(safe))
        offset += error/scale
    raise ValueError(f'Cannot center illustration: {error}')


def indices(card, ink, masks, geometry):
    layer = Image.new('RGBA', SIZE)
    draw = ImageDraw.Draw(layer)
    l, t, r, b = geometry['index_top_bounds']
    cx = (l+r-1)/2
    rank = card['printed_index']
    size = 62
    while draw.textlength(rank, font=ImageFont.truetype(str(LATIN_FONT), size)) > r-l-22:
        size -= 1
    draw.text((cx, t+(b-t)*.33), rank, fill=ink, font=ImageFont.truetype(str(LATIN_FONT), size), anchor='mm')
    glyph = Image.open(REPO / 'designs/design1/sources/components/tarot' / prior.GLYPHS[card.get('suit', 'trumps')]).convert('L')
    glyph = ImageOps.contain(glyph, (36, 44), Image.Resampling.LANCZOS)
    mark = Image.new('RGBA', glyph.size, ink)
    mark.putalpha(glyph)
    layer.alpha_composite(mark, (round(cx-glyph.width/2), round(t+(b-t)*.72-glyph.height/2)))
    layer.alpha_composite(layer.transpose(Image.Transpose.ROTATE_180))
    assert not np.any((np.array(layer.getchannel('A')) > 8) & (np.array(masks['index']) < 128)), card['id']
    return layer


def name_layer(card, ink, masks, geometry):
    text = chinese_name(card)
    layer = Image.new('RGBA', SIZE)
    draw = ImageDraw.Draw(layer)
    font = ImageFont.truetype(str(CHINESE_FONT), 52)
    l, t, r, b = geometry['name_top_bounds']
    cx, cy = (l+r-1)/2, (t+b-1)/2
    assert len(text)*66 <= b-t-32, ('Name too tall', card['id'], text)
    missing = bytes(font.getmask('\U0010ffff'))
    for i, char in enumerate(text):
        assert bytes(font.getmask(char)) != missing, ('Missing glyph', char)
        y = cy + (i-(len(text)-1)/2)*66
        draw.text((cx, y), char, font=font, fill=ink, anchor='mm', stroke_width=0)
    layer.alpha_composite(layer.transpose(Image.Transpose.ROTATE_180))
    assert not np.any((np.array(layer.getchannel('A')) > 8) & (np.array(masks['name']) < 128)), card['id']
    return layer


def compose(card, frames, masks, geometry):
    color = 'madder-lake' if card.get('suit') in ('cups', 'coins') else 'lamp-black'
    source_file = source_path(card)
    source, crop = source_component(source_file)
    art = Image.new('RGBA', SIZE)
    instances = []
    if card['kind'] != 'pip':
        instances.append(place(art, source, (537, 1110)))
    elif card['rank'] == 'ace':
        box = (275, 1040) if card['suit'] in ('swords', 'batons') else (460, 920) if card['suit'] == 'cups' else (510, 510)
        instances.append(place(art, source, box))
    elif card['suit'] in ('swords', 'batons'):
        rank = int(card['rank'])
        pairs = rank//2
        rows = {1:[712], 2:[442, 982], 3:[352, 712, 1072],
                4:[292, 572, 852, 1132], 5:[262, 487, 712, 937, 1162]}[pairs]
        height = {1:600, 2:440, 3:350, 4:280, 5:240}[pairs]
        if card['suit'] == 'batons' and pairs == 5:
            height = 215
        for y in rows:
            for angle in (-45, 45):
                instances.append(place(art, source, (195, height), (412, y), angle))
        if rank % 2:
            instances.append(place(art, source, (195, round(height*.85)), CENTER))
    else:
        layout = prior.numbers.layout()[card['rank']]
        box = tuple(round(d*1.12) for d in layout['component_bounds'])
        if card['suit'] == 'cups' and int(card['rank']) in (8, 10):
            box = (150, 158) if card['rank'] == '8' else (142, 156)
        for point in layout['pips']:
            cx = 412 + (point['center'][0]-374.5)*1.09
            cy = 712 + (point['center'][1]-524.5)*1.4
            instances.append(place(art, source, box, (cx, cy), point['rotation']))
    assert len(instances) == (1 if card['kind'] != 'pip' or card['rank'] == 'ace' else int(card['rank']))
    art, registration = balance(art)
    occupied = np.array(art.getchannel('A')) > 8
    assert not np.any(occupied & (np.array(masks['field']) < 128)), ('Art leaves field', card['id'])
    assert not np.any(occupied[1280:1330]), ('Art enters title', card['id'])
    # Composite through the aperture, including subvisible alpha noise in
    # preserved generated sources, so no frame pixel can be contaminated.
    art.putalpha(ImageChops.multiply(art.getchannel('A'), masks['field']))
    labels = Image.new('RGBA', SIZE)
    if card['kind'] != 'pip':
        draw = ImageDraw.Draw(labels)
        draw.line((250, 1276, 574, 1276), fill=(182, 145, 75, 255), width=1)
        size = 25
        while draw.textlength(card['title'].upper(), font=ImageFont.truetype(str(LATIN_FONT), size)) > 490:
            size -= 1
        draw.text((412, 1298), card['title'].upper(), fill=INKS[color], font=ImageFont.truetype(str(LATIN_FONT), size), anchor='mm')
    result = frames[color].copy()
    for layer in (art, labels, indices(card, INKS[color], masks, geometry), name_layer(card, INKS[color], masks, geometry)):
        result.alpha_composite(layer)
    result.putalpha(masks['outline'])
    protected = (np.array(masks['field']) == 0) & (np.array(masks['index']) == 0) & (np.array(masks['name']) == 0)
    changed = protected & np.any(np.array(result) != np.array(frames[color]), axis=2)
    assert not np.any(changed), ('Frame changed', card['id'], Image.fromarray(np.uint8(changed)*255).getbbox())
    return result, dict(source=record(source_file), source_crop=crop, frame=color, chinese_title=chinese_name(card),
                        instances=instances, registration=registration, artwork_outside_field=0,
                        index_outside_panels=0, name_outside_panels=0, artwork_in_title_band=0,
                        costume_status='first-revised-proof' if source_file.parent == RAW else 'carried-forward-for-review')


def active_path(card):
    suffix = (f'trumps/{card.get("rank_order") or 0:02d}-{card["id"]}.png' if card['kind'] in ('fool', 'trump')
              else f'{card["suit"]}/{card["rank"]}.png')
    return ROOT / 'cards/faces/tarot/tarot' / suffix


def verify_png(path, expected):
    with Image.open(path) as actual:
        assert actual.mode == 'RGBA' and actual.size == SIZE, path
        assert all(abs(v-300) < .01 for v in actual.info['dpi']), path
        assert np.array_equal(np.asarray(actual), np.asarray(expected)), path


def save_or_check(path, image, check):
    if check:
        verify_png(path, image)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, dpi=(300, 300))


def promote(cards):
    old_root = (ROOT / 'cards/faces/tarot/poker').resolve()
    archive = (OUT / 'previous-poker-exports').resolve()
    if old_root.exists():
        assert old_root == (ROOT / 'cards/faces/tarot/poker').resolve() and old_root.is_relative_to(ROOT.resolve())
        assert archive.is_relative_to(OUT.resolve()) and not archive.exists()
        records = [dict(path=p.relative_to(old_root).as_posix(), sha256=sha(p)) for p in sorted(old_root.rglob('*.png'))]
        assert len(records) == 97
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_root), str(archive))
        shutil.copy2(ROOT / 'minchiate-review.html', archive / 'review.html')
        write_json(archive / 'manifest.json', dict(original_root='cards/faces/tarot/poker', status='superseded-wrong-size', cards=records))
        assert all(sha(archive/r['path']) == r['sha256'] for r in records)
    for card in cards:
        proof = OUT / 'proofs' / (card['id'] + '.png')
        dest = active_path(card)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(proof, dest)
        assert sha(dest) == sha(proof)
    config = json.loads((ROOT / 'deck.json').read_text(encoding='utf-8'))
    config['face_systems']['tarot']['formats'] = ['tarot']
    config['face_systems']['tarot']['chinese_titles'] = {
        (f'trump.{c.get("rank_order") or 0}.{c["id"]}' if c['kind'] in ('trump', 'fool') else f'{c["suit"]}.{c["rank"]}'): chinese_name(c)
        for c in cards}
    config['face_systems']['tarot']['chinese_language'] = 'zh-Hant'
    config['face_systems']['tarot']['translation_status'] = NAMES['status']
    config['face_systems']['tarot']['first_proofs'] = [
        (f'trump.{c.get("rank_order") or 0}.{c["id"]}' if c['kind'] in ('trump', 'fool') else f'{c["suit"]}.{c["rank"]}')
        for c in cards if c['id'] in PROOFS]
    config['face_renderer'] = 'number-cards-v1 + registered-faces-v1 + tarot-faces-v1'
    write_json(ROOT / 'deck.json', config)


def contact_sheet(images):
    selected = [(c, im) for c, im in images if c['id'] in PROOFS]
    selected.sort(key=lambda item: PROOFS.index(item[0]['id']))
    sheet = Image.new('RGB', (1296, 1550), '#e9dfcf')
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 18), 'Design 2 / Tarot / first costume and Chinese-name proofs', fill='#30261a', font=ImageFont.truetype(str(LATIN_FONT), 23))
    for i, (card, im) in enumerate(selected):
        thumb = im.resize((396, 684), Image.Resampling.LANCZOS)
        x, y = 24+i%3*424, 65+i//3*742
        sheet.paste(thumb, (x, y), thumb)
        draw.text((x+198, y+701), card['title'], fill='#30261a', font=ImageFont.truetype(str(LATIN_FONT), 19), anchor='mm')
    sheet.save(OUT / 'first-proofs.jpg', quality=95)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--active', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--cards', nargs='+', help='Partial staging only; cannot apply')
    args = parser.parse_args()
    prompts = json.loads((RAW / 'prompts.json').read_text(encoding='utf-8'))
    assert len(prompts['jobs']) == 6
    for job in prompts['jobs']:
        assert sha(RAW / job['output']['path']) == job['output']['sha256'], job['id']
        for path, checksum in job['reference_hashes'].items():
            assert sha(REPO / path) == checksum, path
    spec = json.loads(prior.INVENTORY.read_text(encoding='utf-8'))
    cards = spec['cards']
    assert len(cards) == 97 and len({c['id'] for c in cards}) == 97
    assert set(NAMES['trumps']) == {c['id'] for c in cards if c['kind'] in ('fool', 'trump')}
    assert max(len(chinese_name(c)) for c in cards) == 4
    if args.cards:
        assert not args.apply and not args.active
        assert set(args.cards) <= {c['id'] for c in cards}
        cards = [c for c in cards if c['id'] in args.cards]
    frames, masks, geometry = frame_layers()
    check = args.check or args.apply
    for color, frame in frames.items():
        save_or_check(FRAMES / (color+'.png'), frame, check)
    for key, mask in masks.items():
        path = FRAMES / (key+'-mask.png')
        if check:
            assert np.array_equal(np.array(Image.open(path)), np.array(mask)), path
        else:
            mask.save(path)
    records, images = [], []
    for card in cards:
        image, metrics = compose(card, frames, masks, geometry)
        path = OUT / 'proofs' / (card['id']+'.png')
        save_or_check(path, image, check)
        if args.active:
            assert sha(path) == sha(active_path(card)), card['id']
        records.append(dict(card, **record(path), **metrics))
        images.append((card, image))
        print('PASS', card['id'], flush=True)
    manifest = dict(revision='tarot-faces-v1', status='complete-layout-review' if len(cards) == 97 else 'partial-layout-review',
                    format='tarot', tradition='florentine-minchiate-97', pixels=list(SIZE), trim_inches=[2.75, 4.75],
                    card_count=len(cards), geometry=geometry, translations=record(NAMES_FILE),
                    chinese_font=record(CHINESE_FONT), latin_font=record(LATIN_FONT) if LATIN_FONT.is_relative_to(REPO) else dict(path=str(LATIN_FONT), sha256=sha(LATIN_FONT)),
                    frame_source=record(RAW / 'frame-master.png'), prompts=record(RAW / 'prompts.json'),
                    cards=records)
    if check:
        assert json.loads(MANIFEST.read_text(encoding='utf-8')) == manifest, 'Stale manifest'
    else:
        write_json(MANIFEST, manifest)
        contact_sheet(images)
    if args.apply:
        assert len(cards) == 97
        promote(cards)
    print(f'PASS {len(cards)}/97 Tarot compositions: 825x1425, silhouette, labels, borders and centers')


if __name__ == '__main__':
    main()
