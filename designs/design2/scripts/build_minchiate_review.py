"""Build/check the balanced Poker Minchiate set from recorded components."""
from __future__ import annotations

import argparse
import shutil
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import build_number_cards as numbers

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
RAW = ROOT / 'sources/generated/minchiate-poker-v1'
OUT = ROOT / 'sources/components/minchiate-poker-v1'
FRAMES = ROOT / 'sources/components/design2-face-frames-v1/poker'
INVENTORY = REPO / 'docs/minchiate-97.json'
FONT = Path('C:/Windows/Fonts/timesbd.ttf')
CORRECTIONS = RAW/'corrections.json'
REPAIRS = {j['id']:j for j in json.loads(CORRECTIONS.read_text(encoding='utf-8'))['jobs'] if j['status']=='selected'} if CORRECTIONS.exists() else {}
SIZE = (750, 1050)
CENTER = (374.5, 524.5)
SELECTED = ('the-empress', 'queen-of-cups', 'ace-of-swords', '10-of-swords')
PIPS = {'swords':'sword-straight','batons':'baton-straight','cups':'cup','coins':'coin'}
GLYPHS = {
    'trumps': 'review-v1/trumps-index-mask.png',
    'cups': 'review-v1/cups-index-mask.png',
    'swords': 'review-v1/swords-index-mask.png',
    'batons': 'full-assets-v1/batons-index-mask.png',
    'coins': 'full-assets-v1/coins-index-mask.png',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=path.relative_to(REPO).as_posix(), sha256=sha(path))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def master_path(name):
    return RAW/(REPAIRS[name]['output']['path'] if name in REPAIRS else f'{name}.png')


def component(name):
    with Image.open(master_path(name)) as original:
        assert original.mode == 'RGBA', name
        alpha = np.array(original.getchannel('A'))
        assert np.count_nonzero(alpha == 0) > 100, f'{name}: missing transparency'
        # Ignore subvisible export noise when measuring placement; do not repaint.
        bounds = Image.fromarray(np.uint8(alpha > 8) * 255).getbbox()
        assert bounds, name
        bounds = (max(0, bounds[0]-4), max(0, bounds[1]-4),
                  min(original.width, bounds[2]+4), min(original.height, bounds[3]+4))
        return original.crop(bounds), bounds


def visual_center(image):
    a = np.asarray(image.convert('RGBA'), dtype=float)
    alpha = a[:, :, 3] / 255
    contrast = np.sqrt(np.mean((a[:, :, :3] - [250, 235, 215])**2, axis=2)) / 255
    weight = alpha * np.maximum(contrast, .08) * (alpha > 8/255)
    assert weight.sum() > 0
    yy, xx = np.indices(weight.shape)
    return np.array([(xx*weight).sum()/weight.sum(), (yy*weight).sum()/weight.sum()])


def place(layer, source, box, center=CENTER, angle=0):
    artwork = ImageOps.contain(source, box, Image.Resampling.LANCZOS)
    if angle:
        artwork = artwork.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    anchor = visual_center(artwork)
    x, y = np.array(center)-anchor
    visible=Image.fromarray(np.uint8(np.array(artwork.getchannel('A'))>8)*255).getbbox()
    assert visible[0]+x >= 0 and visible[1]+y >= 0 and visible[2]+x <= SIZE[0] and visible[3]+y <= SIZE[1], 'Source clipped before registration'
    fitted = artwork.transform(SIZE, Image.Transform.AFFINE, (1, 0, -x, 0, 1, -y),
                                Image.Resampling.BICUBIC)
    layer.alpha_composite(fitted)
    return dict(box=list(box), center=list(center), rotation=angle,
                source_anchor=anchor.tolist(), translation=[float(x),float(y)])


def balance(art):
    # Keep the entire composition inside a common safe area, then register its
    # contrast-weighted painted mass. Borders, indices and titles are excluded.
    original = art
    anchor = visual_center(original)
    bounds = Image.fromarray(np.uint8(np.array(original.getchannel('A')) > 8)*255).getbbox()
    distances = [anchor[0]-bounds[0], bounds[2]-1-anchor[0],
                 anchor[1]-bounds[1], bounds[3]-1-anchor[1]]
    room = [CENTER[0]-126, 623-CENTER[0], CENTER[1]-116, 898-CENTER[1]]
    scale = min(1., *(r/max(1,d) for r,d in zip(room,distances)))
    offset = anchor-np.array(CENTER)/scale
    for _ in range(20):
        result = original.transform(SIZE, Image.Transform.AFFINE,
                                    (1/scale,0,float(offset[0]),0,1/scale,float(offset[1])),
                                    Image.Resampling.BICUBIC)
        measured = visual_center(result)
        error = measured-np.array(CENTER)
        if max(abs(error)) < .2:
            return result, dict(method='alpha times RMS contrast against #FAEBD7; 0.08 floor',
                                scale=scale, sampling_offset=offset.tolist(),
                                measured_center=measured.tolist(), max_error_pixels=float(max(abs(error))))
        offset += error/scale
    raise ValueError(f'Cannot register artwork: {error}')


def indices(card, ink):
    result = Image.new('RGBA', SIZE)
    draw = ImageDraw.Draw(result)
    font_size = 54
    rank = card['printed_index']
    while draw.textlength(rank, font=ImageFont.truetype(str(FONT), font_size)) > 47:
        font_size -= 1
    draw.text((71, 118), rank, font=ImageFont.truetype(str(FONT), font_size),
              fill=ink, anchor='mm')
    glyph = card.get('suit', 'trumps')
    mask = Image.open(REPO / 'designs/design1/sources/components/tarot' / GLYPHS[glyph]).convert('L')
    mask = ImageOps.contain(mask, (34, 40), Image.Resampling.LANCZOS)
    mark = Image.new('RGBA', mask.size, ink)
    mark.putalpha(mask)
    result.alpha_composite(mark, (round(71-mask.width/2), round(178-mask.height/2)))
    result.alpha_composite(result.transpose(Image.Transpose.ROTATE_180))
    return result


def render(card):
    color = 'madder-lake' if card.get('suit') in ('cups','coins') else 'lamp-black'
    ink = (167, 52, 67, 255) if color == 'madder-lake' else (33, 33, 31, 255)
    frame = Image.open(FRAMES / f'{color}.png').convert('RGBA')
    art = Image.new('RGBA', SIZE)
    source_name = PIPS[card['suit']] if card['kind'] == 'pip' else card['id']
    source, crop = component(source_name)
    transforms = []
    if card['kind'] != 'pip':
        transforms.append(place(art, source, (494, 734)))
    elif card['rank'] == 'ace':
        box = (260,740) if card['suit'] in ('swords','batons') else (460,660) if card['suit']=='cups' else (490,490)
        transforms.append(place(art, source, box))
    elif card['suit'] in ('swords','batons'):
        rank = int(card['rank']); pairs = rank//2
        rows = {1:[524.5],2:[334.5,714.5],3:[254.5,524.5,794.5],
                4:[224.5,424.5,624.5,824.5],5:[224.5,374.5,524.5,674.5,824.5]}[pairs]
        height = {1:480,2:330,3:260,4:210,5:200}[pairs]
        if card['suit']=='batons' and pairs==5:
            height=170
        for y in rows:
            for angle in (-45,45):
                transforms.append(place(art, source, (180,height), (374.5,y), angle))
        if rank%2:
            transforms.append(place(art,source,(180,round(height*.85)),CENTER))
    else:
        rank = int(card['rank'])
        layout = numbers.layout()[str(rank)]
        box=tuple(layout['component_bounds'])
        if card['suit']=='cups' and rank in (8,10):
            box=(145,150) if rank==8 else (130,145)
        for point in layout['pips']:
            pip=Image.new('RGBA',SIZE)
            transforms.append(place(pip,source,box,tuple(point['center']),point['rotation']))
            occupied=art.getchannel('A').filter(ImageFilter.MaxFilter(7))
            assert not np.any((np.array(occupied)>8)&(np.array(pip.getchannel('A'))>8)), card['id']+': pips touch'
            art.alpha_composite(pip)
    if card['kind'] == 'pip':
        assert len(transforms) == (1 if card['rank'] == 'ace' else int(card['rank']))
    for n, transform in enumerate(transforms, 1):
        transform['instance_id'] = f'{source_name}-{n}'
    art, registration = balance(art)
    field = Image.open(FRAMES / 'field-mask.png').convert('L')
    occupied = np.array(art.getchannel('A')) > 8
    assert not np.any(occupied & (np.array(field) < 128)), 'Artwork leaves central field'
    assert not np.any(occupied[910:962]), 'Artwork enters title band'
    text = Image.new('RGBA', SIZE)
    if card['kind'] != 'pip':
        draw = ImageDraw.Draw(text)
        draw.line((220, 913, 529, 913), fill=(182, 145, 75, 255), width=1)
        font_size=24
        while draw.textlength(card['title'].upper(),font=ImageFont.truetype(str(FONT),font_size))>450:
            font_size-=1
        draw.text((375, 938), card['title'].upper(), fill=ink,
                  font=ImageFont.truetype(str(FONT), font_size), anchor='mm')
    index = indices(card, ink)
    panels = np.array(Image.open(FRAMES / 'panel-mask.png'))
    assert not np.any((np.array(index.getchannel('A')) > 8) & (panels < 128)), 'Indices leave panels'
    result = frame.copy()
    result.alpha_composite(art)
    result.alpha_composite(text)
    result.alpha_composite(index)
    result.putalpha(Image.open(FRAMES / 'outline-mask.png'))
    preserved = (np.array(field) == 0) & (panels == 0)
    assert np.array_equal(np.array(result)[preserved], np.array(frame)[preserved]), 'Frame changed'
    return result, dict(source=source_name, source_path=master_path(source_name).relative_to(REPO).as_posix(), crop=list(crop), frame=color,
                        instance_count=len(transforms), instances=transforms,
                        center=list(CENTER), registration=registration, artwork_outside_field=0,
                        index_outside_panels=0, artwork_in_title_band=0)


def review_page(cards):
    data = [dict(id=c['id'], title=c['title'], src=f'sources/components/minchiate-poker-v1/proofs/{c["id"]}.png') for c in cards]
    options = ''.join(f'<option value="{i}">{c["title"]}</option>' for i, c in enumerate(data))
    first=data[0]
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Design 2 · Minchiate proofs</title><link rel="stylesheet" href="../../assets/gallery.css">
<header class="site-header"><a class="wordmark" href="index.html">Design 2</a><span>Minchiate · Poker</span></header>
<main><aside class="browser-panel"><h1>Minchiate</h1><p class="intro">Balanced cards from the 97-card Minchiate inventory.</p>
<div class="selectors"><label for="proof">Card</label><select id="proof">''' + options + '''</select></div>
<p class="muted">750 × 1050 px · 2.5 × 3.5 in<br>Existing Poker frames; paired side indices.<br>Figures follow the Minchiate subjects.</p>
<a href="sources/generated/minchiate-poker-v1/prompts.json">Generation prompts</a><a href="docs/design/minchiate-poker-v1.md">Construction notes</a></aside>
<section class="card-view"><header class="card-heading"><h2 id="title">The Empress</h2><span id="position" role="status"></span></header>
<div class="viewer-stage"><img id="image" src="sources/components/minchiate-poker-v1/proofs/the-empress.png" width="750" height="1050" alt="The Empress"></div>
<div class="card-step"><button id="previous">← Previous</button><button id="next">Next →</button></div>
<div class="viewer-actions"><button id="turn" aria-pressed="false">Turn 180°</button><a id="viewer-download" href="sources/components/minchiate-poker-v1/proofs/the-empress.png" download>Download PNG ↓</a></div></section></main>
<script>
const cards = ''' + json.dumps(data) + ''';
const select=document.getElementById('proof'), image=document.getElementById('image');
let index=0;
function show(n){index=(n+cards.length)%cards.length;const card=cards[index];select.value=index;image.src=card.src;image.alt=card.title;document.getElementById('title').textContent=card.title;document.getElementById('position').textContent=`${index+1} / ${cards.length}`;const link=document.getElementById('viewer-download');link.href=card.src;link.download=card.id+'.png';}
select.addEventListener('change',()=>show(Number(select.value)));
document.getElementById('previous').addEventListener('click',()=>show(index-1));
document.getElementById('next').addEventListener('click',()=>show(index+1));
document.getElementById('turn').addEventListener('click',e=>{const turned=image.classList.toggle('turned');e.target.setAttribute('aria-pressed',String(turned));e.target.textContent=turned?'Return upright':'Turn 180°';});
document.addEventListener('keydown',e=>{if(e.target.tagName==='SELECT')return;if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();show(index+(e.key==='ArrowRight'?1:-1));}});show(0);
</script></html>'''
    return page.replace('>The Empress</h2>', '>'+first['title']+'</h2>').replace('proofs/the-empress.png', 'proofs/'+first['id']+'.png').replace('alt="The Empress"', 'alt="'+first['title']+'"')


def active_path(card):
    relative=(f'trumps/{card.get("rank_order") or 0:02d}-{card["id"]}.png' if card['kind'] in ('fool','trump')
              else f'{card["suit"]}/{card["rank"]}.png')
    return ROOT/'cards/faces/tarot/poker'/relative


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--active', action='store_true', help='Also compare active exports')
    parser.add_argument('--partial', action='store_true', help='Render currently available sources only')
    parser.add_argument('--apply', action='store_true', help='Promote a checked complete set')
    args = parser.parse_args()
    spec = json.loads(INVENTORY.read_text(encoding='utf-8'))
    assert len(spec['cards']) == len({c['id'] for c in spec['cards']}) == 97
    source_for=lambda c: PIPS[c['suit']] if c['kind']=='pip' else c['id']
    cards = [c for c in spec['cards'] if master_path(source_for(c)).exists()]
    pending = [c['id'] for c in spec['cards'] if c not in cards]
    if not args.partial and CORRECTIONS.exists():
        assert all(j['status']=='selected' for j in json.loads(CORRECTIONS.read_text(encoding='utf-8'))['jobs']), 'Artwork corrections still pending'
    if pending and not args.partial:
        raise ValueError(f'{len(pending)} cards still lack artwork; use --partial for staging')
    jobs=[j for name in ('prompts.json','completion-prompts.json') for j in json.loads((RAW/name).read_text(encoding='utf-8'))['jobs']]
    assert len(jobs)==len({j['id'] for j in jobs})==61
    for name in {source_for(c) for c in cards}:
        job=REPAIRS.get(name) or next(j for j in jobs if j['id']==name)
        assert job['output']['sha256']==sha(RAW/job['output']['path']), name+': generated master changed'
    records, images = [], []
    for card in cards:
        image, metrics = render(card)
        path = OUT / 'proofs' / (card['id'] + '.png')
        if args.check or args.apply:
            with Image.open(path) as actual:
                assert actual.mode == 'RGBA' and actual.size == SIZE
                assert all(abs(d-300) < .01 for d in actual.info['dpi'])
                assert np.array_equal(np.array(actual), np.array(image)), card['id']
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path, dpi=(300, 300))
        if args.active:
            assert sha(active_path(card))==sha(path), card['id']+': active export differs'
        records.append(dict(card, status='balanced-proof', **record(path), **metrics))
        images.append(image)
    shared = [INVENTORY, RAW/'prompts.json', RAW/'completion-prompts.json', *sorted(FRAMES.glob('*.png'))]
    if CORRECTIONS.exists():
        shared.append(CORRECTIONS)
    shared += [REPO/'designs/design1/sources/components/tarot'/p for p in GLYPHS.values()]
    manifest = dict(version=2, status='partial-balanced' if pending else 'complete-balanced',
                    format='poker', pixels=list(SIZE), planned_count=97, proof_count=len(cards), remaining_count=len(pending),
                    font=dict(path=str(FONT), sha256=sha(FONT)),
                    inputs=[record(p) for p in shared],
                    sources=[record(master_path(name)) for name in sorted({source_for(c) for c in cards})],
                    cards=records, pending=pending)
    target = ROOT/'docs/design/minchiate-poker-v1.json'
    html = review_page(cards)
    if args.check or args.apply:
        assert json.loads(target.read_text(encoding='utf-8')) == manifest
        assert (ROOT/'minchiate-review.html').read_text(encoding='utf-8') == html
    else:
        write_json(target, manifest)
        (ROOT/'minchiate-review.html').write_text(html, encoding='utf-8', newline='\n')
        for start in range(0,len(cards),8):
            subset=list(zip(cards,images))[start:start+8]
            sheet = Image.new('RGB', (1560, 1160 if len(subset)>4 else 610), '#e9dfcf')
            draw = ImageDraw.Draw(sheet)
            draw.text((20,16),f'Design 2 / Minchiate / Poker / {start+1}-{start+len(subset)} of {len(cards)}',
                      fill='#30261a',font=ImageFont.truetype(str(FONT),24))
            for i,(card,image) in enumerate(subset):
                thumb=image.resize((375,525),Image.Resampling.LANCZOS)
                x,y=i%4*390+7,i//4*550+55
                sheet.paste(thumb,(x,y),thumb)
                draw.text((x+187,y+535),card['title'],fill='#30261a',font=ImageFont.truetype(str(FONT),18),anchor='mm')
            sheet.save(OUT/f'review-{start//8+1:02d}.jpg',quality=95)
        # Preserve the first four comparison sheet as the entry-point preview.
        initial=[(c,im) for c,im in zip(cards,images) if c['id'] in SELECTED]
        initial.sort(key=lambda pair:SELECTED.index(pair[0]['id']))
        sheet=Image.new('RGB',(1560,610),'#e9dfcf');draw=ImageDraw.Draw(sheet)
        draw.text((20,16),'Design 2 / first four cards / balanced',fill='#30261a',font=ImageFont.truetype(str(FONT),24))
        for i,(card,im) in enumerate(initial):
            thumb=im.resize((375,525),Image.Resampling.LANCZOS);sheet.paste(thumb,(i*390+7,55),thumb)
            draw.text((i*390+194,590),card['title'],fill='#30261a',font=ImageFont.truetype(str(FONT),18),anchor='mm')
        sheet.save(OUT/'review.jpg',quality=95)
    if args.apply:
        assert not pending
        for c in cards:
            dest=active_path(c)
            assert not dest.exists() or sha(dest)==sha(OUT/'proofs'/(c['id']+'.png'))
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(OUT/'proofs'/(c['id']+'.png'),dest)
        deck=json.loads((ROOT/'deck.json').read_text(encoding='utf-8'))
        tarot=json.loads((REPO/'designs/design1/deck.json').read_text(encoding='utf-8'))['face_systems']['tarot']
        tarot['formats']=['poker'];deck['face_systems']['tarot']=tarot
        deck['face_renderer']='number-cards-v1 + registered-faces-v1 + minchiate-poker-v1'
        write_json(ROOT/'deck.json',deck)
    print(f'PASS: {len(cards)}/97 cards; pixel checks, shared borders, indices, containment, pip counts and center error <0.2 px')


if __name__ == '__main__':
    main()
