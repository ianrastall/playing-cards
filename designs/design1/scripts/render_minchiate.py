"""Prepare and stage Design 1 Minchiate; incomplete artwork never enters cards/."""
from __future__ import annotations

import argparse
import copy
import html
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import render_tarot as tarot

ROOT = tarot.ROOT
SHARED = ROOT.parents[1] / 'docs/minchiate-97.json'
RAW = ROOT / 'sources/generated/minchiate-v1'
COMP = ROOT / 'sources/components/tarot/minchiate-v1'
WORK = ROOT / 'work/minchiate-v1'
MANIFEST = ROOT / 'docs/design/minchiate-layout-v1.json'

# Only explicitly audited illustrations can be carried over. Other subjects
# must resolve to a new generated file, never an automatic standard-Tarot fallback.
REUSE_TRUMPS = {'the-empress': 'empress', 'the-emperor': 'the-emperor',
                'justice': 'justice'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def inventory():
    spec = read(SHARED)
    cards = spec['cards']
    assert len(cards) == 97 and len({c['id'] for c in cards}) == 97
    assert {k: sum(c['kind'] == k for c in cards) for k in spec['counts']} == spec['counts']
    trumps = [c for c in cards if c['kind'] == 'trump']
    assert [c['rank_order'] for c in trumps] == list(range(1, 41))
    assert all(not c['printed_index'] for c in cards if c['kind'] == 'fool' or c.get('group') == 'arie')
    assert sum(c.get('group') == 'arie' for c in cards) == 5
    return spec


def prepare():
    source = inventory()
    old = read(tarot.MANIFEST)
    old_cards = {c['id']: c for c in old['cards']}
    components = copy.deepcopy(old['components'])
    cards, missing, generated = [], [], []
    COMP.mkdir(parents=True, exist_ok=True)
    for entry in source['cards']:
        card = copy.deepcopy(entry)
        card.update(index=card['printed_index'], glyph=card.get('suit', 'trumps'),
                    ink='madder-lake' if card.get('suit') in ('cups', 'coins') else 'lamp-black',
                    reversible=False, expected_emblems=0)
        card['title'] = None if card['kind'] == 'pip' else card['title'].upper()
        raw = RAW / (card['id'] + '.png')
        replace_court = card.get('rank') == 'knight' or (card.get('rank') == 'page' and card.get('suit') in ('cups', 'coins'))
        if raw.exists():
            im = Image.open(raw)
            assert im.mode == 'RGBA', raw
            a = np.array(im.getchannel('A'))
            assert np.count_nonzero(a == 0) > 100, f'No transparent space: {raw}'
            bounds = Image.fromarray(np.uint8(a > 128) * 255).getbbox()
            assert bounds, raw
            x0, y0, x1, y1 = bounds
            crop = [max(0, x0-12), max(0, y0-12), min(im.width, x1+12), min(im.height, y1+12)]
            prepared = im.crop(crop)
            dest = COMP / raw.name
            prepared.save(dest, dpi=(300, 300))
            component_id = 'minchiate-' + card['id']
            components[component_id] = dict(path=tarot.rel(dest), sha256=tarot.digest(dest),
                size=list(prepared.size), source=tarot.rel(raw), source_sha256=tarot.digest(raw), crop=crop)
            card['primary_asset'] = component_id
            card['instances'] = [tarot.figure_instance(card, components)]
            generated.append(card['id'])
        elif card['kind'] in ('pip', 'court') and not replace_court:
            previous = old_cards[card['id']]
            card.update(primary_asset=previous['primary_asset'], instances=copy.deepcopy(previous['instances']),
                        expected_emblems=previous['expected_emblems'])
            # Florentine long suits use straight blades. Preserve explicit
            # anchors/counts while removing the Marseille curved-sword variant.
            if card.get('suit') == 'swords' and card['kind'] == 'pip':
                for item in card['instances']:
                    if item['role'] == 'emblem':
                        item['component'] = 'sword-straight'
        elif card['id'] in REUSE_TRUMPS:
            card['primary_asset'] = REUSE_TRUMPS[card['id']]
            card['instances'] = [tarot.figure_instance(card, components)]
        else:
            missing.append(card['id'])
            continue
        cards.append(card)
    used = {item['component'] for c in cards for item in c['instances']} | {c['glyph']+'-index' for c in cards}
    spec = dict(version=1, status='incomplete' if missing else 'ready-to-stage',
        planned_count=97, available_count=len(cards), missing=missing, generated=generated,
        inventory_path='../../docs/minchiate-97.json', inventory_sha256=tarot.digest(SHARED),
        canvas=list(tarot.SIZE), dpi=300, corner_radius_mm=3.5,
        components={k: v for k, v in components.items() if k in used}, cards=cards,
        font=old['font'], indices=dict(old['indices'], max_rank_width=48),
        title=dict(old['title'], max_width=455),
        shared_inputs={p: h for p, h in old['shared_inputs'].items() if not p.endswith('.json') or 'template' in p})
    tarot.write_json(MANIFEST, spec)
    print(f"Prepared {len(cards)}/97 cards; {len(generated)} new illustrations; missing: {', '.join(missing)}")
    return spec


def stage(spec, partial=False):
    if spec['missing'] and not partial:
        raise ValueError('Artwork incomplete; --partial is for inspection only')
    assert tarot.digest(SHARED) == spec['inventory_sha256']
    for c in spec['components'].values():
        assert tarot.digest(ROOT/c['path']) == c['sha256']
    for p, h in spec['shared_inputs'].items():
        assert tarot.digest(ROOT/p) == h
    assert tarot.digest(spec['font']['path']) == spec['font']['sha256']
    out = WORK / 'faces'
    out.mkdir(parents=True, exist_ok=True)
    reports, errors, previews = [], [], []
    for card in spec['cards']:
        im, report = tarot.render(spec, card)
        for key in ('artwork_pixels_outside_field', 'index_pixels_outside_panels', 'artwork_pixels_in_title_band'):
            if report[key]:
                errors.append(f"{card['id']}: {key}={report[key]}")
        assert report['emblem_count'] == card['expected_emblems']
        path = out / (card['id']+'.png')
        tarot.base.save(im, path)
        report.update(path=tarot.rel(path), sha256=tarot.digest(path))
        reports.append(report)
        if card['id'] in spec['generated']:
            im.thumbnail((206, 356), Image.Resampling.LANCZOS)
            previews.append((card, im))
    sheet_paths = []
    for offset in range(0, len(previews), 8):
        group = previews[offset:offset+8]
        sheet = Image.new('RGB', (960, ((len(group)+3)//4)*410+55), (239,228,207))
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype(str(tarot.FONT), 19)
        draw.text((20,16), 'Design 1 / Minchiate / new artwork proofs', font=font, fill=(45,38,29))
        for n, (card, im) in enumerate(group):
            x, y = n%4*240+17, n//4*410+55
            sheet.paste(im, (x,y), im)
            draw.text((x+103,y+368), card['id'].replace('-', ' ').title(), font=font, fill=(45,38,29), anchor='mt')
        path = WORK/f'proofs-{offset//8+1:02d}.jpg'
        sheet.save(path, quality=95)
        sheet_paths.append(tarot.rel(path))
    tarot.write_json(WORK/'report.json', dict(status='failed' if errors else 'partial-inspection' if spec['missing'] else 'staged',
        rendered_count=len(reports), planned_count=97, missing=spec['missing'], errors=errors,
        layout_sha256=tarot.digest(MANIFEST), cards=reports, sheets=sheet_paths))
    figures = ''.join(f'<figure><a href="faces/{c["id"]}.png"><img loading="lazy" src="faces/{c["id"]}.png"></a><figcaption>{html.escape(c["title"] or c["id"])}</figcaption></figure>' for c in spec['cards'])
    (WORK/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Minchiate proofs</title><style>body{background:#efe4cf;color:#30261a;font:18px Georgia;margin:30px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:24px}figure{margin:0}img{width:100%}figcaption{text-align:center}</style><h1>Design 1 Minchiate proofs</h1><p>'+f'{len(reports)}/97 cards rendered. This is a staging set.'+'</p><main>'+figures+'</main>', encoding='utf-8')
    if errors:
        raise ValueError('\n'.join(errors))
    print(f'PASS: {len(reports)} staged RGBA cards; component hashes, emblem counts, field/index/title containment')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--stage', action='store_true')
    parser.add_argument('--partial', action='store_true')
    args = parser.parse_args()
    spec = prepare() if args.prepare else read(MANIFEST)
    if args.stage:
        stage(spec, args.partial)
