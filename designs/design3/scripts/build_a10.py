"""Compose and audit forty Celtic Poker A–10 faces from existing artwork."""
import argparse
import json
import math
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, PngImagePlugin
import register_kings as common

ROOT, REPO = common.ROOT, common.REPO
SIZE, CENTER = common.SIZE, common.CENTER
PIPS = ROOT/'sources/components/pips-v1'
COMP = ROOT/'sources/components/a10-v1'
WORK = ROOT/'work/a10-v1'
DOC = ROOT/'docs/design/a10-v1.json'
SUITS = ('spades', 'hearts', 'diamonds', 'clubs')
RANKS = ('ace', *map(str, range(2, 11)))
SAFE = (120, 110, 630, 940)
GUESSES = {'spades': (626, 640, 140), 'hearts': (628, 602, 133),
           'diamonds': (626, 627, 111), 'clubs': (626, 618, 134)}


def record(path):
    return dict(path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix(), sha256=common.sha(path))


def save(image, path, **metadata):
    path.parent.mkdir(parents=True, exist_ok=True)
    info = PngImagePlugin.PngInfo()
    info.add_text('Renderer', 'design3-a10-v1')
    for key, value in metadata.items():
        info.add_text(key, json.dumps(value))
    image.save(path, dpi=(300, 300), pnginfo=info)


def baseline():
    path = WORK/'input-hashes.json'
    if not path.exists():
        catalog = json.loads((REPO/'catalog.json').read_text(encoding='utf-8'))
        paths = {REPO/c['path'] for c in catalog['assets']}
        paths.update(p for p in ROOT.rglob('*.png') if '/work/' not in p.as_posix()
                     and '/a10-v1/' not in p.as_posix())
        common.write_json(path, {p.relative_to(REPO).as_posix(): common.sha(p) for p in sorted(paths)})


def measure(image, guess):
    """Least-squares circle fit to the existing central medallion's gold rim."""
    cx, cy, radius = guess
    a = np.array(image.convert('RGB')).astype(float)
    angles = np.linspace(0, 2*np.pi, 240, endpoint=False)
    radii = np.linspace(radius+5, radius+20, 160)
    x = cx+np.cos(angles)[:, None]*radii
    y = cy+np.sin(angles)[:, None]*radii
    v = a[np.rint(y).astype(int), np.rint(x).astype(int)]
    strength = np.minimum(v[:, :, 0]-v[:, :, 2], v[:, :, 1]-v[:, :, 2])
    ix = strength.argmax(axis=1)
    xx, yy = x[np.arange(len(angles)), ix], y[np.arange(len(angles)), ix]
    fit = np.linalg.lstsq(np.stack([2*xx, 2*yy, np.ones_like(xx)], axis=1),
                          xx*xx+yy*yy, rcond=None)[0]
    radius = float(np.sqrt(fit[2]+sum(fit[:2]**2)))
    residual = np.sqrt((xx-fit[0])**2+(yy-fit[1])**2)-radius
    assert np.std(residual) < 5, 'Uncertain medallion fit'
    return fit[:2].tolist(), radius, float(np.std(residual))


def prepared_source(suit):
    source = PIPS/f'{suit}-master.png'
    with Image.open(source) as im:
        anchor, radius, residual = measure(im, GUESSES[suit])
        a = np.array(im.convert('RGBA'))
    connected = Image.fromarray(np.uint8(a[:, :, 3] > 8)*255).copy()
    ImageDraw.floodfill(connected, tuple(round(c) for c in anchor), 128)
    keep = np.array(connected) == 128
    a[~keep] = 0
    # Normalize the generated near-opaque body on a separate production copy.
    alpha = a[:, :, 3].astype(float)
    a[:, :, 3] = np.rint(np.minimum(alpha*255/253, 255)).astype(np.uint8)
    a[:, :, 3][alpha >= 250] = 255
    image = Image.fromarray(a)
    box = image.getbbox()
    image = image.crop(box)
    adjusted = [anchor[0]-box[0], anchor[1]-box[1]]
    target = COMP/f'cleaned/{suit}.png'
    save(image, target, SourceSHA256=common.sha(source))
    data = dict(**record(source), source_anchor=anchor, rim_radius=radius,
                rim_fit_residual_px=residual, crop=list(box),
                cleaned=record(target), anchor=adjusted)
    return image, data


def layouts():
    def point(x, y, rotation=0):
        return dict(center=[x, y], rotation=rotation)
    def pairs(points):
        return [p for x, y in points for p in (point(x, y), point(749-x, 1049-y, 180))]
    mx, my = CENTER
    four = [(224.5, 254.5), (524.5, 254.5)]
    six = four+[(224.5, my)]
    eight = [(224.5, 224.5), (524.5, 224.5), (224.5, 424.5), (524.5, 424.5)]
    grid = [(224.5, 254.5), (mx, 254.5), (524.5, 254.5), (224.5, my)]
    raw = {'ace': ([point(mx, my)], (490, 710)),
           '2': (pairs([(mx, 274.5)]), (250, 280)),
           '3': (pairs([(mx, 254.5)])+[point(mx, my)], (205, 225)),
           '4': (pairs(four), (195, 220)),
           '5': (pairs(four)+[point(mx, my)], (180, 205)),
           '6': (pairs(six), (175, 195)),
           '7': (pairs(six)+[point(mx, my)], (135, 160)),
           '8': (pairs(eight), (165, 180)),
           '9': (pairs(grid)+[point(mx, my)], (135, 155)),
           '10': (pairs(eight+[(mx, 324.5)]), (140, 160))}
    return {rank: dict(pips=points, bounds=list(bounds),
                       symmetry='exact-half-turn' if len(points)%2 == 0 else 'upright-center-only')
            for rank, (points, bounds) in raw.items()}


def prepare_frame():
    frame = Image.open(common.COMP/'shared-frame.png').convert('RGBA')
    field = np.array(Image.open(common.COMP/'field-mask.png')) > 0
    a = np.array(frame)
    original_field = field.copy()
    # Follow the painted panel's rounded rim and pointed lower leaf. The court
    # field's rectangular exclusion also retained navy/woodland artwork here.
    ys = [67,70,75,80,90,100,190,200,208,215,220,223,226,230,235,240,245,250]
    xs = [103,107,111,114,116,117,117,115,112,108,99,88,83,79,77,76,76,76]
    edges = []
    for y in range(67,251):
        edge = round(np.interp(y,ys,xs))
        if y <= 223:
            positions = np.arange(max(77,edge-9),edge+3)
            colors = a[y,positions,:3].astype(float)
            navy = (colors[:,2]>colors[:,1]+5)&(colors[:,2]>colors[:,0]+15)&(colors[:,2]>30)
            if navy.any():
                edge = int(positions[np.flatnonzero(navy)[0]])-1
        edges.append(edge)
    for i,y in enumerate(range(67,251)):
        edge = round(float(np.median(edges[max(0,i-2):i+3])))
        field[y,77:122] = np.arange(77,122) > edge
    field[525:] = field[:525][::-1,::-1]
    repair = field ^ original_field
    # Close narrow remnants of the original index ink inside the cream panel.
    rgb = a[:,:,:3].astype(int)
    cream = (rgb[:,:,0]>190)&(rgb[:,:,1]>185)&(rgb[:,:,2]>140)&((rgb[:,:,0]-rgb[:,:,2])<75)
    connected = Image.fromarray(np.uint8(cream)*255).copy()
    ImageDraw.floodfill(connected,(70,160),128)
    interior = Image.fromarray(np.uint8(np.array(connected)==128)*255)
    closed = np.array(interior.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.MinFilter(13)))>0
    cleanup = closed
    reserve = np.zeros(field.shape,dtype=bool)
    reserve[84:205,35:100] = True
    cleanup &= reserve
    cleanup[525:] = cleanup[:525][::-1,::-1]
    repair |= cleanup
    a[cleanup,:3] = (255,246,221)
    a[field, :3] = (255, 246, 221)
    frame = Image.fromarray(a)
    assert np.array_equal(a, a[::-1, ::-1])
    save(frame, COMP/'frame.png')
    save(Image.fromarray(np.uint8(field)*255), COMP/'field-mask.png')
    save(Image.fromarray(np.uint8(repair)*255), COMP/'panel-repair-mask.png')


def indices(suit, rank):
    layer = Image.new('RGBA', SIZE)
    color = (173, 21, 30, 255) if suit in ('hearts', 'diamonds') else (17, 18, 16, 255)
    for text, bounds, center in [('A' if rank == 'ace' else rank, (49, 48), (69.5, 119.5)),
                                ({'spades':'♠', 'hearts':'♥', 'diamonds':'♦', 'clubs':'♣'}[suit],
                                 (44, 47), (69.5, 181.5))]:
        sprite = common.glyph(text, bounds, color)
        layer.alpha_composite(sprite, tuple(round(c-(n-1)/2) for c, n in zip(center, sprite.size)))
    return common.symmetric(layer)


def sprites(rank, spec, sources):
    w, h = [2*math.ceil(v/2) for v in spec['bounds']]
    # One optical medallion radius per rank, fitting all four suit silhouettes.
    candidates = []
    for image, data in sources.values():
        cx, cy = data['anchor']
        ex, ey = max(cx+.5, image.width-cx-.5), max(cy+.5, image.height-cy-.5)
        candidates.append(min((w-8)/(2*ex), (h-8)/(2*ey))*data['rim_radius'])
    target_radius = min(candidates)
    records = {}
    for suit, (image, data) in sources.items():
        scale = target_radius/data['rim_radius']
        anchor = [(w-1)/2, (h-1)/2]
        matrix = (1/scale, 0, data['anchor'][0]-anchor[0]/scale,
                  0, 1/scale, data['anchor'][1]-anchor[1]/scale)
        sprite = image.transform((w, h), Image.Transform.AFFINE, matrix,
                                 resample=Image.Resampling.BICUBIC)
        a = np.array(sprite)
        a[a[:, :, 3] < 2] = 0
        sprite = Image.fromarray(a)
        path = COMP/f'pips/{suit}/{rank}.png'
        save(sprite, path, Anchor=anchor, SourceSHA256=data['sha256'])
        records[suit] = dict(**record(path), pixels=[w,h], anchor=anchor,
                             target_rim_radius=target_radius, uniform_scale=scale,
                             transform=list(matrix), alpha_bounds=list(sprite.getbbox()))
    return records


def compose(suit, rank, spec):
    frame = Image.open(COMP/'frame.png').convert('RGBA')
    sprite = Image.open(ROOT/spec['components'][suit]['path']).convert('RGBA')
    for p in spec['pips']:
        part = sprite.transpose(Image.Transpose.ROTATE_180) if p['rotation'] else sprite
        xy = tuple(round(c-(n-1)/2) for c, n in zip(p['center'], part.size))
        frame.alpha_composite(part, xy)
    frame.alpha_composite(indices(suit, rank))
    return frame


def stage():
    previous = {(c['suit'],c['rank']): c for c in
                json.loads(DOC.read_text(encoding='utf-8'))['cards']} if DOC.exists() else {}
    baseline()
    prepare_frame()
    sources = {s: prepared_source(s) for s in SUITS}
    specs, cards = layouts(), []
    for rank, spec in specs.items():
        spec['components'] = sprites(rank, spec, sources)
    for suit in SUITS:
        for rank, spec in specs.items():
            target = WORK/f'cards/{suit}/{rank}.png'
            image = compose(suit, rank, spec)
            save(image, target, Suit=suit, Rank=rank, PipCount=len(spec['pips']), Symmetry=spec['symmetry'])
            installed = ROOT/f'cards/faces/french-suited/poker/{suit}/{rank}.png'
            prior_hash = common.sha(installed) if installed.exists() else None
            known = previous.get((suit,rank), {})
            assert prior_hash is None or prior_hash in (known.get('sha256'),known.get('prior_sha256')), installed
            cards.append(dict(suit=suit, rank=rank, status='review', pixels=list(SIZE),
                              prior_sha256=prior_hash,
                              path=f'cards/faces/french-suited/poker/{suit}/{rank}.png',
                              staged_path=target.relative_to(ROOT).as_posix(), sha256=common.sha(target)))
    common.write_json(DOC, dict(renderer='design3-a10-v1', status='review',
        pixels=list(SIZE), center=list(CENTER), safe_pip_box=list(SAFE), ranks=specs,
        sources={s: data for s, (_,data) in sources.items()}, frame=record(COMP/'frame.png'),
        frame_source=record(common.COMP/'shared-frame.png'),
        field=record(COMP/'field-mask.png'), panel_repair=record(COMP/'panel-repair-mask.png'), outline=record(common.COMP/'outline-mask.png'),
        font=record(common.FONT), cards=cards,
        preserved_inputs=json.loads((WORK/'input-hashes.json').read_text(encoding='utf-8')),
        symmetry_policy='Even ranks exact half-turn; A,3,5,7,9 differ only within one upright central pip.',
        preparation='Separate copies: retain connected alpha >8, normalize near-opaque interior, crop, uniformly scale and register fitted medallion center. Masters unchanged.'))
    proofs()
    audit(False)


def proofs():
    font = ImageFont.truetype(str(common.FONT), 20)
    for suit in SUITS:
        sheet = Image.new('RGB', (1500, 916), '#e9dfcf')
        draw = ImageDraw.Draw(sheet)
        for i, rank in enumerate(RANKS):
            x, y = (i%5)*300, (i//5)*458
            image = Image.open(WORK/f'cards/{suit}/{rank}.png').resize((285,399), common.LANCZOS)
            sheet.paste(image, (x+7,y+10), image)
            draw.text((x+15,y+421), f"{'Ace' if rank=='ace' else rank} of {suit.title()}", fill='#302a20', font=font)
        sheet.save(ROOT/f'docs/design/a10-v1-{suit}.jpg', quality=94, subsampling=0)
    sheet = Image.new('RGB', (1560,595), '#e9dfcf')
    for i, suit in enumerate(SUITS):
        image = Image.open(WORK/f'cards/{suit}/ace.png').resize((375,525), common.LANCZOS)
        sheet.paste(image, (i*390+7,15), image)
        ImageDraw.Draw(sheet).text((i*390+20,556), f'Ace of {suit.title()}', fill='#302a20', font=font)
    sheet.save(ROOT/'docs/design/a10-v1-aces.png')


def regions(mask):
    boxes = []
    while mask.any():
        y,x = np.argwhere(mask)[0]
        flood = Image.fromarray(np.uint8(mask)*255).copy()
        ImageDraw.floodfill(flood, (int(x),int(y)), 128)
        component = np.array(flood)==128
        mask[component] = False
        if component.sum() >= 50:
            ys,xs = np.nonzero(component)
            boxes.append([int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)])
    return boxes


def audit(active=True):
    doc = json.loads(DOC.read_text(encoding='utf-8'))
    assert len(doc['cards'])==40 and {(c['suit'],c['rank']) for c in doc['cards']} == {(s,r) for s in SUITS for r in RANKS}
    for item in [doc[k] for k in ('frame','frame_source','field','panel_repair','outline','font')]+list(doc['sources'].values()):
        assert common.sha(ROOT/item['path']) == item['sha256'], item['path']
    for source in doc['sources'].values():
        assert common.sha(ROOT/source['cleaned']['path']) == source['cleaned']['sha256']
    for spec in doc['ranks'].values():
        radii = [c['target_rim_radius'] for c in spec['components'].values()]
        assert max(radii)-min(radii) < 1e-8
        for suit, component in spec['components'].items():
            scale = component['uniform_scale']
            source = doc['sources'][suit]
            assert abs(scale*source['rim_radius']-component['target_rim_radius']) < 1e-8
            xx,_,offset_x,_,yy,offset_y = component['transform']
            assert abs(xx-yy) < 1e-8 and abs(xx-1/scale) < 1e-8
            fitted = [(source['anchor'][0]-offset_x)/xx, (source['anchor'][1]-offset_y)/yy]
            assert np.allclose(fitted,component['anchor'],atol=1e-8)
    for name, digest in doc['preserved_inputs'].items():
        assert common.sha(REPO/name)==digest, f'Existing artwork changed: {name}'
    frame = np.array(Image.open(COMP/'frame.png'))
    field = np.array(Image.open(COMP/'field-mask.png')) > 0
    original = np.array(Image.open(common.COMP/'shared-frame.png'))
    repair = np.array(Image.open(COMP/'panel-repair-mask.png')) > 0
    assert np.array_equal(frame[~(field|repair)],original[~(field|repair)])
    assert np.all(frame[225:245,90:125,:3] == (255,246,221)), 'Court remnants below index panel'
    assert np.all(frame[95:205,119:125,:3] == (255,246,221)), 'Court remnants beside index panel'
    outline = np.array(Image.open(common.COMP/'outline-mask.png'))
    safe = np.zeros((1050,750),dtype=bool)
    l,t,r,b = SAFE
    safe[t:b,l:r] = True
    results=[]
    for card in doc['cards']:
        suit,rank = card['suit'],card['rank']
        path = ROOT/card['path' if active else 'staged_path']
        assert common.sha(path)==card['sha256']
        with Image.open(path) as im:
            assert im.size==SIZE and im.mode=='RGBA'
            assert all(abs(d-300)<.01 for d in im.info['dpi'])
            a=np.array(im)
        assert np.array_equal(a[:,:,3],outline)
        spec=doc['ranks'][rank]
        count=1 if rank=='ace' else int(rank)
        difference=np.max(np.abs(a[:,:,:3].astype(int)-frame[:,:,:3].astype(int)),axis=2)
        boxes=regions((difference>12)&field)
        assert len(boxes)==count, (path, len(boxes), count)
        changed=np.any(a!=frame,axis=2)
        ink=np.array(indices(suit,rank))[:,:,3]>0
        assert not changed[~(field|ink)].any()
        assert not changed[field&~safe].any(), f'Pip outside safe field: {path}'
        component=spec['components'][suit]
        assert common.sha(ROOT/component['path'])==component['sha256']
        sprite=Image.open(ROOT/component['path']).convert('RGBA')
        occupied=np.zeros(field.shape,dtype=bool)
        centers=[p['center'] for p in spec['pips']]
        assert np.array_equal(np.mean(centers,axis=0),np.array(CENTER))
        for p in spec['pips']:
            cx,cy=p['center']
            assert sum(l<=cx<r and t<=cy<b for l,t,r,b in boxes)==1
            if p['center']!=list(CENTER):
                assert dict(center=[749-cx,1049-cy],rotation=(p['rotation']+180)%360) in spec['pips']
            part=sprite.transpose(Image.Transpose.ROTATE_180) if p['rotation'] else sprite
            x,y=tuple(round(c-(n-1)/2) for c,n in zip(p['center'],part.size))
            w,h=part.size
            alpha=np.array(part)[:,:,3]>0
            assert safe[y:y+h,x:x+w][alpha].all()
            assert not occupied[y:y+h,x:x+w][alpha].any(), f'Overlapping pips: {path}'
            occupied[y:y+h,x:x+w] |= alpha
        assert np.array_equal(a,np.array(compose(suit,rank,spec)))
        mismatch=np.any(a!=a[::-1,::-1],axis=2)
        if count%2==0:
            assert not mismatch.any(), path
        else:
            allowed=np.zeros(field.shape,dtype=bool)
            w,h=sprite.size
            x,y=(750-w)//2,(1050-h)//2
            allowed[y:y+h,x:x+w]=True
            assert not mismatch[~allowed].any(), path
        results.append(dict(suit=suit,rank=rank,visible_pips=len(boxes),
                            half_turn_mismatch_pixels=int(mismatch.sum()),symmetry=spec['symmetry']))
    common.write_json(ROOT/'docs/design/a10-v1-audit.json',dict(status='passed',target='active' if active else 'staged',
        cards_checked=40,panel_surrounds_clear=True,exact_half_turn_cards=20,upright_center_only_cards=20,cards=results))
    print('PASS 40 A–10 cards: clear panel surrounds, visible counts, spacing, orientations, preserved masters, 300 ppi and rounded alpha; 20 exact half-turns, 20 center-only exceptions')


def apply():
    audit(False)
    cards=json.loads(DOC.read_text(encoding='utf-8'))['cards']
    for card in cards:
        target=ROOT/card['path']
        assert not target.exists() or common.sha(target) in (card['sha256'],card.get('prior_sha256')), target
    for card in cards:
        target=ROOT/card['path']
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists() or common.sha(target)!=card['sha256']:
            shutil.copyfile(ROOT/card['staged_path'],target)
    audit(True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--apply',action='store_true')
    group.add_argument('--check',action='store_true')
    args=parser.parse_args()
    audit() if args.check else apply() if args.apply else stage()
