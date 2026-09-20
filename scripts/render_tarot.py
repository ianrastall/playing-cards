"""Build and validate the complete 78-card Design 1 Tarot staging set.

This consumes prepared, hashed components and never calls image generation.
It writes only to docs/design/tarot-full-layout-v1.json and work/tarot-full-v1/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

import rebuild_deck as base
import expand_faces as faces

ROOT = base.ROOT
PRODUCTION = ROOT / 'docs/design/tarot-full-production-v1.json'
ASSETS = ROOT / 'docs/design/tarot-full-assets-v1.json'
REVIEW = ROOT / 'docs/design/tarot-review-layout-v1.json'
MANIFEST = ROOT / 'docs/design/tarot-full-layout-v1.json'
VALIDATION = ROOT / 'docs/design/tarot-full-v1-report.json'
WORK = ROOT / 'work/tarot-full-v1'
OUT = WORK / 'faces'
ACTIVE = ROOT / 'cards/faces/tarot/tarot'
SIZE = (825, 1425)
FONT = Path('C:/Windows/Fonts/timesbd.ttf')
INKS = {'lamp-black': (5, 5, 5), 'madder-lake': (78, 9, 23)}


def rel(path):
    return path.relative_to(ROOT).as_posix()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def active_path(card):
    if card['kind'] == 'trump':
        return ACTIVE / 'trumps' / f"{card['number']:02d}-{card['id']}.png"
    return ACTIVE / card['suit'] / f"{card['rank']}.png"


def instance(name, component, center, height, rotation=0, mirror=False, role='emblem'):
    return dict(id=name, component=component, center=list(center), height=height,
                rotation=rotation, mirror=mirror, role=role)


def rank_points(rank):
    layouts = {
        2: [(412, 420), (412, 980)],
        3: [(412, 360), (412, 700), (412, 1040)],
        4: [(300, 420), (524, 420), (300, 980), (524, 980)],
        5: [(300, 390), (524, 390), (412, 700), (300, 1010), (524, 1010)],
        6: [(300, 350), (524, 350), (300, 700), (524, 700), (300, 1050), (524, 1050)],
        7: [(300, 330), (524, 330), (412, 515), (300, 700), (524, 700), (300, 1060), (524, 1060)],
        8: [(300, 300), (524, 300), (300, 565), (524, 565),
            (300, 835), (524, 835), (300, 1100), (524, 1100)],
        9: [(270, 370), (412, 370), (554, 370), (270, 700), (412, 700),
            (554, 700), (270, 1030), (412, 1030), (554, 1030)],
        10: [(310, 275), (514, 275), (310, 490), (514, 490), (310, 705),
             (514, 705), (310, 920), (514, 920), (310, 1135), (514, 1135)],
    }
    return layouts[rank]


def pip_instances(card):
    suit = card['suit']
    rank = 1 if card['rank'] == 'ace' else int(card['rank'])
    primary = card['primary_asset']
    if rank == 1:
        heights = {'swords': 970, 'batons': 970, 'cups': 650, 'coins': 455}
        center_y = {'swords': 765, 'batons': 765, 'cups': 755, 'coins': 750}[suit]
        items = [instance(f'{suit}-1', primary, (412, center_y), heights[suit])]
        items += [instance('sprig-left', 'foliage', (290, 458), 430, 12, False, 'furniture'),
                  instance('sprig-right', 'foliage', (534, 458), 430, -12, True, 'furniture'),
                  instance('crown', 'ace-crown', (412, 340), 145, 0, False, 'furniture')]
        return items

    points = rank_points(rank)
    if suit in ('swords', 'batons'):
        height = 420 if rank <= 5 else 300 if rank <= 8 else 245
    elif suit == 'cups':
        height = 265 if rank <= 5 else 205 if rank <= 8 else 165
    else:
        height = 190 if rank <= 5 else 150 if rank <= 8 else 125
    items = []
    for i, point in enumerate(points):
        component = primary
        rotation = 0
        mirror = False
        if suit == 'swords':
            component = 'sword-curved' if rank >= 5 and i % 3 else 'sword-straight'
            rotation = (-24 if i % 2 == 0 else 24) if rank >= 4 else 0
            mirror = bool(i % 2)
        elif suit == 'batons' and rank >= 4:
            rotation = -20 if i % 2 == 0 else 20
            mirror = bool(i % 2)
        items.append(instance(f'{suit}-{i+1}', component, point, height, rotation, mirror))
    return items


def figure_instance(card, components):
    component = components[card['primary_asset']]
    width, height = component['size']
    target_height = min(920, round(520 * height / width))
    return instance('figure', card['primary_asset'], (412, 685), target_height, role='figure')


def prepare():
    production = json.loads(PRODUCTION.read_text(encoding='utf-8'))
    assets = json.loads(ASSETS.read_text(encoding='utf-8'))
    review = json.loads(REVIEW.read_text(encoding='utf-8'))
    assert len(production['cards']) == 78
    components = assets['components']
    cards = []
    for source in production['cards']:
        card = dict(source)
        card['glyph'] = source.get('glyph', source.get('suit'))
        card['ink'] = source['frame_ink']
        card['reversible'] = False
        if source['kind'] == 'pip':
            card['instances'] = pip_instances(source)
            card['expected_emblems'] = 1 if source['rank'] == 'ace' else int(source['rank'])
        else:
            card['instances'] = [figure_instance(source, components)]
            card['expected_emblems'] = 0
        cards.append(card)
    inputs = [base.COMP/'frame.png', base.COMP/'field-mask.png', base.COMP/'panel-mask.png',
              faces.TRACERY/'ornament-master.png', faces.TRACERY/'template.json',
              PRODUCTION, ASSETS]
    spec = dict(version=1, status='staging-layout', canvas=list(SIZE), center=[412, 712],
        coordinate_basis='zero-based pixel centers', dpi=300, corner_radius_mm=3.5,
        components=components, cards=cards,
        shared_inputs={rel(p): digest(p) for p in inputs},
        font=dict(path=str(FONT), sha256=digest(FONT)),
        transform_policy='uniform scale from height; optional mirror; bicubic expanded rotation; integral center placement',
        pip_policy='one reusable master per instance; sword curved variant is declared per instance; furniture excluded from count',
        indices=review['indices'], title=review['title'])
    write_json(MANIFEST, spec)
    print('Prepared deterministic placements for 78 Tarot faces')


def verify_inputs(spec):
    assert len(spec['cards']) == 78 and len({c['id'] for c in spec['cards']}) == 78
    for component in spec['components'].values():
        assert digest(ROOT/component['path']) == component['sha256'], component['path']
    for path, expected in spec['shared_inputs'].items():
        assert digest(ROOT/path) == expected, path
    assert digest(spec['font']['path']) == spec['font']['sha256'], 'Font changed'


def place(spec, item):
    source = Image.open(ROOT/spec['components'][item['component']]['path']).convert('RGBA')
    if item['mirror']:
        source = ImageOps.mirror(source)
    scale = item['height'] / source.height
    source = source.resize((round(source.width * scale), item['height']), base.LANCZOS)
    if item['rotation'] % 360:
        source = source.rotate(item['rotation'], Image.Resampling.BICUBIC, expand=True)
    top_left = [round(p - (length - 1) / 2) for p, length in zip(item['center'], source.size)]
    layer = Image.new('RGBA', SIZE)
    layer.alpha_composite(source, top_left)
    return layer, dict(scale=scale, top_left=top_left, transformed_size=list(source.size))


def index_layer(spec, card):
    settings = spec['indices']
    ink = INKS[card['ink']]
    layer = Image.new('RGBA', SIZE)
    draw = ImageDraw.Draw(layer)
    font_size = settings['wide_rank_size'] if len(card['index']) > 1 else settings['rank_size']
    font = ImageFont.truetype(spec['font']['path'], font_size)
    draw.text((settings['center_x'], settings['rank_center_y']), card['index'],
              fill=ink, font=font, anchor='mm')
    mask_info = spec['components'][card['glyph'] + '-index']
    mask = Image.open(ROOT/mask_info['path']).convert('L').resize(tuple(settings['glyph_size']), base.LANCZOS)
    icon = Image.new('RGBA', mask.size, ink)
    icon.putalpha(mask)
    xy = [round(v - (n - 1) / 2) for v, n in zip(settings['glyph_center'], mask.size)]
    layer.alpha_composite(icon, xy)
    layer.alpha_composite(base.halfturn(layer))
    return layer


def title_layer(spec, card):
    layer = Image.new('RGBA', SIZE)
    if not card.get('title'):
        return layer
    settings = spec['title']
    draw = ImageDraw.Draw(layer)
    draw.rectangle((175, 1184, 650, 1300), fill=base.GROUND + (255,))
    draw.line((settings['rule_x'][0], settings['rule_y'], settings['rule_x'][1], settings['rule_y']),
              fill=(198, 161, 91), width=2)
    font = ImageFont.truetype(spec['font']['path'], settings['font_size'])
    draw.text(tuple(settings['center']), card['title'], fill=INKS[card['ink']], font=font, anchor='mm')
    return layer


def render(spec, card):
    frame, field, panels = faces.frame(SIZE, card['ink'])
    art = Image.new('RGBA', SIZE)
    transforms = {}
    for item in card['instances']:
        layer, transform = place(spec, item)
        art.alpha_composite(layer)
        transforms[item['id']] = transform
    background = faces.background(SIZE, art.getchannel('A'))
    background.alpha_composite(art)
    background.alpha_composite(title_layer(spec, card))
    result = base.composite_field(frame, background, field)
    indices = index_layer(spec, card)
    result.alpha_composite(indices)
    result.putalpha(base.silhouette(SIZE))
    occupied = np.array(art.getchannel('A')) > 128
    report = dict(
        id=card['id'], kind=card['kind'],
        emblem_count=sum(i['role'] == 'emblem' for i in card['instances']),
        artwork_pixels_outside_field=int((occupied & (np.array(field) < 128)).sum()),
        index_pixels_outside_panels=int(((np.array(indices.getchannel('A')) > 128) & (np.array(panels) < 128)).sum()),
        artwork_pixels_in_title_band=int(occupied[1184:1301, 175:651].sum()) if card.get('title') else 0,
        transforms=transforms)
    return result, report


def contact_sheets(spec, rendered):
    sheets = []
    groups = [
        ('minor-swords', [c for c in spec['cards'] if c.get('suit') == 'swords']),
        ('minor-batons', [c for c in spec['cards'] if c.get('suit') == 'batons']),
        ('minor-cups', [c for c in spec['cards'] if c.get('suit') == 'cups']),
        ('minor-coins', [c for c in spec['cards'] if c.get('suit') == 'coins']),
        ('trumps-00-10', [c for c in spec['cards'] if c['kind'] == 'trump' and c['number'] <= 10]),
        ('trumps-11-21', [c for c in spec['cards'] if c['kind'] == 'trump' and c['number'] >= 11]),
    ]
    heading = ImageFont.truetype(spec['font']['path'], 30)
    label = ImageFont.truetype(spec['font']['path'], 18)
    for name, cards in groups:
        cols = 7 if len(cards) == 14 else 6
        cell_w, cell_h = 245, 455
        rows = math.ceil(len(cards) / cols)
        sheet = Image.new('RGB', (cols * cell_w, rows * cell_h + 72), (239, 228, 207))
        draw = ImageDraw.Draw(sheet)
        draw.text((22, 20), name.replace('-', ' ').upper(), fill=(45, 38, 29), font=heading)
        for i, card in enumerate(cards):
            thumb = rendered[card['id']].copy()
            thumb.thumbnail((215, 372), base.LANCZOS)
            x = (i % cols) * cell_w + (cell_w - thumb.width) // 2
            y = (i // cols) * cell_h + 66
            sheet.paste(thumb, (x, y), thumb)
            draw.text(((i % cols) * cell_w + cell_w // 2, y + 383),
                      card['id'].replace('-', ' ').title(), fill=(45, 38, 29), font=label, anchor='mt')
        path = WORK / 'sheets' / f'{name}.jpg'
        path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(path, quality=95)
        sheets.append(rel(path))
    return sheets


def stage(spec):
    verify_inputs(spec)
    OUT.mkdir(parents=True, exist_ok=True)
    reports = []
    rendered = {}
    for card in spec['cards']:
        image, report = render(spec, card)
        path = OUT / f"{card['id']}.png"
        base.save(image, path)
        report.update(path=rel(path), sha256=digest(path))
        reports.append(report)
        rendered[card['id']] = image
    sheets = contact_sheets(spec, rendered)
    write_json(WORK/'report.json', dict(status='staged', card_count=78, cards=reports,
                                        inspection_sheets=sheets))
    figures = ''.join(f'<figure><a href="faces/{c["id"]}.png"><img src="faces/{c["id"]}.png"></a><figcaption>{c["id"].replace("-", " ").title()}</figcaption></figure>' for c in spec['cards'])
    links = ' &middot; '.join(
        f'<a href="{(ROOT/Path(p)).relative_to(WORK).as_posix()}">{Path(p).stem}</a>'
        for p in sheets)
    html = '<!doctype html><meta charset="utf-8"><title>Design 1 Tarot full staging</title><style>body{background:#eee3cf;color:#30291e;font:17px Georgia;margin:30px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:22px}figure{margin:0}img{width:100%;height:auto}figcaption{text-align:center;padding:8px}a{color:inherit}</style><h1>Design 1 · Tarot · 78-card staging set</h1><p>Click a face for its native 825 × 1425 RGBA image.</p><p>'+links+'</p><main>'+figures+'</main>'
    (WORK/'index.html').write_text(html, encoding='utf-8')
    print(f'Staged {len(reports)} Tarot faces and {len(sheets)} inspection sheets')


def check(spec, active=False):
    verify_inputs(spec)
    report = json.loads((WORK/'report.json').read_text(encoding='utf-8'))
    by_id = {r['id']: r for r in report['cards']}
    assert len(by_id) == 78
    errors = []
    for card in spec['cards']:
        expected, current = render(spec, card)
        path = active_path(card) if active else OUT/f"{card['id']}.png"
        actual = Image.open(path).convert('RGBA')
        if actual.size != SIZE or not np.array_equal(np.array(actual), np.array(expected)):
            errors.append(f"{card['id']}: native dimensions or exact rerender failed")
        if current['emblem_count'] != card['expected_emblems']:
            errors.append(f"{card['id']}: expected {card['expected_emblems']} emblems, got {current['emblem_count']}")
        for field in ['artwork_pixels_outside_field', 'index_pixels_outside_panels', 'artwork_pixels_in_title_band']:
            if current[field]:
                errors.append(f"{card['id']}: {field}={current[field]}")
        if digest(path) != by_id[card['id']]['sha256']:
            errors.append(f"{card['id']}: staged hash changed")
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f"PASS: 78 {'active' if active else 'staged'} native RGBA faces; hashes, exact rerender, emblem counts, field/index/title containment.")


def apply(spec):
    check(spec)
    records = []
    for card in spec['cards']:
        source = OUT / f"{card['id']}.png"
        destination = active_path(card)
        if destination.exists() and digest(destination) != digest(source):
            raise ValueError(f'Refusing to replace different active Tarot artwork: {destination}')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        records.append(dict(id=card['id'], kind=card['kind'], suit=card.get('suit'),
                            rank=card.get('rank'), number=card.get('number'),
                            title=card.get('title'), path=rel(destination),
                            sha256=digest(destination)))
    expected = {active_path(card) for card in spec['cards']}
    actual = set(ACTIVE.rglob('*.png'))
    assert actual == expected, f'Active Tarot inventory mismatch: {actual ^ expected}'
    write_json(VALIDATION, dict(version=1, status='promoted-and-validated',
        card_count=78, layout_manifest=rel(MANIFEST), layout_sha256=digest(MANIFEST),
        background_component='sources/components/front-tracery-v3/ornament-master.png',
        background_sha256=digest(ROOT/'sources/components/front-tracery-v3/ornament-master.png'),
        cards=records))
    check(spec, active=True)
    print('Promoted 78 checked Tarot faces and wrote the active validation report')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ['prepare', 'stage', 'check', 'apply']:
        parser.add_argument('--' + option, action='store_true')
    parser.add_argument('--active', action='store_true')
    args = parser.parse_args()
    if args.prepare:
        prepare()
    spec = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if args.stage:
        stage(spec)
    if args.check:
        check(spec, args.active)
    if args.apply:
        apply(spec)
