"""Compose Design 1 faces at native format sizes; European derives from Bridge.

--stage builds Jumbo, Travel, Bridge, then European Standard, with review sheets.
--check [--active] verifies pixels, geometry, inventory and component provenance.
--apply promotes a validated stage without overwriting unrelated artwork.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
from functools import lru_cache

import numpy as np
from PIL import Image, ImageFilter

import rebuild_deck as base
import complete_poker as complete
from frame_palette import color_frame, face_color

ROOT = base.ROOT
WORK = ROOT / 'work/face-formats-v1'
MANIFEST = ROOT / 'docs/design/face-formats-v1.json'
REPORT = ROOT / 'docs/design/face-formats-v1-report.json'
FORMATS = ('poker', 'jumbo', 'travel', 'bridge', 'european-standard')
BACKUP = ROOT / 'sources/before-face-formats-v1'
COURTS = ('jack', 'queen', 'king')
TRACERY = ROOT / 'sources/components/front-tracery-v3'
RANKS = (*base.load_manifest()['ranks'], *COURTS)


def size_for(fmt):
    config = json.loads((ROOT / 'deck.json').read_text(encoding='utf-8'))
    return tuple(config['formats'][fmt]['back_pixels'])


def native_point(point, size):
    """Quantize offsets symmetrically around the true pixel-center anchor."""
    return tuple((n-1)/2 + round((p-c)*n/old)
                 for p, c, n, old in zip(point, base.CENTER, size, base.SIZE))


def sprite_size(dimensions, scale, size):
    return tuple(max(3, round(d*scale/2)*2 + n%2) for d, n in zip(dimensions, size))


@lru_cache(maxsize=128)
def pip_component(suit, rank, size):
    """Resize the generated master, register its jewel, preserve suit proportions."""
    spec = base.load_manifest()['ranks'][rank]
    if size == base.SIZE:
        return Image.open(ROOT/spec['components'][suit]['path']).convert('RGBA')
    scale = min(n/o for n, o in zip(size, base.SIZE))
    source = Image.open(base.GENERATED/f'{suit}-master.png').convert('RGBA')
    bounds = Image.fromarray(np.uint8(np.array(source)[:, :, 3] > 128)*255).getbbox()
    source = source.crop(bounds)
    factor = min(spec['component_bounds'][0]*scale/source.width,
                 spec['component_bounds'][1]*scale/source.height)
    source = source.resize(tuple(round(n*factor) for n in source.size), base.LANCZOS)
    (cx, cy), _ = base.turquoise(source)
    dims = (2*math.ceil(max(cx, source.width-1-cx)+8)+size[0]%2,
            2*math.ceil(max(cy, source.height-1-cy)+8)+size[1]%2)
    anchor = tuple((n-1)/2 for n in dims)
    sprite = source.transform(dims, Image.Transform.AFFINE,
                              (1, 0, cx-anchor[0], 0, 1, cy-anchor[1]),
                              resample=Image.Resampling.BICUBIC)
    _, box = base.turquoise(sprite)
    distance = max(abs(box[0]-anchor[0]), abs(box[2]-1-anchor[0]),
                   abs(box[1]-anchor[1]), abs(box[3]-1-anchor[1]))
    diameter = max(8, math.ceil(math.sqrt(2)*distance+3)*2)
    badge = Image.open(base.COMP/'jewel-master.png').convert('RGBA')
    badge = base.reciprocal(badge.resize((diameter+size[0]%2, diameter+size[1]%2), base.LANCZOS))
    a = np.array(badge)
    a[:, :, 3][a[:, :, 3] > 240] = 255
    base.put_at(sprite, Image.fromarray(a), anchor)
    center, _ = base.turquoise(sprite)
    assert np.max(np.abs(np.array(center)-anchor)) < 1e-6
    return sprite


@lru_cache(maxsize=4)
def filigree(size):
    """Approved gold acanthus texture, scaled and registered for two-way cards."""
    spec = json.loads((TRACERY/'template.json').read_text(encoding='utf-8'))
    w, h = size
    assert 0 < spec['scale'] <= 1 and 0 < spec['opacity'] <= 1
    assert 0 < spec['half_turn_blend_height'] <= 1
    master = Image.open(TRACERY/spec['master']).convert('RGBA')
    scaled = tuple(round(n*spec['scale']) for n in size)
    master = master.resize(scaled, base.LANCZOS)
    dx, dy = w-scaled[0], h-scaled[1]
    # Continue only the outer margins, retaining the approved source colors.
    pixels = np.pad(np.array(master), ((dy//2,dy-dy//2),(dx//2,dx-dx//2),(0,0)),
                    mode='symmetric').astype(np.float32)
    # Blend a narrow center band in premultiplied alpha so the two halves
    # meet without a hard seam or an increase in the gold's ink coverage.
    y = (np.arange(h, dtype=np.float32)+.5)/h
    weight = np.clip(.5+(.5-y)/spec['half_turn_blend_height'],0,1)
    weight = (weight*weight*(3-2*weight))[:,None,None]
    alpha = pixels[:,:,3:4]/255
    ink = pixels[:,:,:3]*alpha
    mixed_alpha = alpha*weight+alpha[::-1,::-1]*(1-weight)
    mixed_ink = ink*weight+ink[::-1,::-1]*(1-weight)
    rgb = np.divide(mixed_ink,mixed_alpha,out=np.zeros_like(ink),where=mixed_alpha>0)
    result = np.concatenate((rgb,mixed_alpha*255*spec['opacity']),axis=2)
    return base.reciprocal(Image.fromarray(np.rint(result).clip(0,255).astype(np.uint8)))


@lru_cache(maxsize=16)
def frame(size, color):
    perimeter,field,panels=base.frame_for(size)
    return color_frame(perimeter,color),field,panels


def background(size, occupied):
    layer = Image.new('RGBA', size, base.GROUND+(255,))
    lines = filigree(size).copy()
    # Leave a clear ivory halo around every pip or portrait.
    spread = max(3, round(min(size)/100)*2+1)
    halo = occupied.filter(ImageFilter.MaxFilter(spread)).filter(ImageFilter.GaussianBlur(2))
    alpha = np.array(lines)[:, :, 3].astype(float)*(1-np.array(halo)/255)
    lines.putalpha(Image.fromarray(np.rint(alpha).astype(np.uint8)))
    layer.alpha_composite(lines)
    return layer


def index_layer(size, suit, rank):
    source = (complete.COMP/f'joker-{rank}-index.png' if suit == 'jokers'
              else base.COMP/f'indices/{suit}/{rank}.png')
    sprite = Image.open(source).convert('RGBA')
    sx, sy = size[0]/750, size[1]/1050
    sprite = sprite.resize((round(64*sx), round(140*sy)), base.LANCZOS)
    result = Image.new('RGBA', size)
    result.alpha_composite(sprite, (round(39*sx), round(90*sy)))
    result.alpha_composite(base.halfturn(result))
    return result


@lru_cache(maxsize=40)
def court_interior(suit, rank, size, register=True):
    # Use preserved painted artwork, not a flattened active Poker export.
    original = Image.open(base.BACKUP/f'cards/faces/french-suited/poker/{suit}/{rank}.png').convert('RGBA')
    source = np.array(original)
    y = np.arange(1050, dtype=float)
    sy = np.where(y <= base.CENTER[1],
                  base.CENTER[1]+(y-base.CENTER[1])*(base.CENTER[1]-78)/(base.CENTER[1]-77),
                  base.CENTER[1]+(y-base.CENTER[1])*(952-base.CENTER[1])/(972-base.CENTER[1]))
    sy = np.clip(sy, 0, 1049)
    y0 = np.floor(sy).astype(int)
    weight = (sy-y0)[:, None, None]
    art = Image.fromarray(np.rint(source[y0]*(1-weight)+source[np.minimum(y0+1,1049)]*weight).astype(np.uint8))
    art = art.resize(size, base.LANCZOS)
    if rank == 'king' and register:
        # Register the entire painted layer before adding the replacement jewel.
        # The old renderer centered only the overlay, hiding drift in its source.
        target=np.array([(n-1)/2 for n in size])
        source_art=art
        offset=np.array(painted_center(art))-target
        # Evaluate small patches, always resampling the unchanged original.
        # Tiny painted jewels have thresholded edges, so centroid error is not
        # perfectly linear in translation. Search avoids iterative blur/drift.
        x,y=target
        box=(int(x)-24,int(y)-24,int(x)+26,int(y)+26)
        patch=source_art.crop(box)
        patch_target=target-np.array(box[:2])
        best_score=float('inf')
        best_offset=offset
        for radius,step in ((.8,.08),(.08,.01)):
            origin=best_offset.copy()
            for dx in np.arange(-radius,radius+step/2,step):
                for dy in np.arange(-radius,radius+step/2,step):
                    shift=origin+np.array([dx,dy])
                    candidate=patch.transform(patch.size,Image.Transform.AFFINE,
                                              (1,0,float(shift[0]),0,1,float(shift[1])),
                                              resample=Image.Resampling.BICUBIC)
                    center,_=base.turquoise(candidate)
                    score=np.max(np.abs(np.array(center)-patch_target))
                    if score<best_score:
                        best_score=score
                        best_offset=shift
            if best_score<.01: break
        art=source_art.transform(size,Image.Transform.AFFINE,
                                 (1,0,float(best_offset[0]),0,1,float(best_offset[1])),
                                 resample=Image.Resampling.BICUBIC)
        assert np.max(np.abs(np.array(painted_center(art))-target))<.1,(suit,size,best_score)
    return art


def painted_center(art):
    x,y=((n-1)/2 for n in art.size)
    radius=max(15,round(min(art.size)/30))
    box=(int(x)-radius,int(y)-radius,int(x)+radius+2,int(y)+radius+2)
    center,_=base.turquoise(art.crop(box))
    return tuple(float(c+b) for c,b in zip(center,box[:2]))


def court_art(suit, rank, size):
    art=court_interior(suit,rank,size).copy()
    badge = Image.open(base.COMP/'jewel-master.png').convert('RGBA')
    dims = sprite_size((14, 14), min(n/o for n,o in zip(size,base.SIZE)), size)
    badge = base.reciprocal(badge.resize(dims, base.LANCZOS))
    base.put_at(art, badge, tuple((n-1)/2 for n in size))
    return art


def render(fmt, suit, rank):
    if fmt == 'european-standard':
        raise ValueError('European must be resized from the staged Bridge export')
    size = size_for(fmt)
    perimeter, field, _ = frame(size,face_color(suit,rank))
    if rank in COURTS:
        art = court_art(suit, rank, size)
    else:
        sprites = Image.new('RGBA', size)
        if suit == 'jokers':
            upright = Image.open(complete.COMP/f'joker-{rank}-upright.png').convert('RGBA')
            scale = min(n/o for n,o in zip(size,base.SIZE))
            if size != base.SIZE:
                upright = upright.resize(sprite_size(upright.size, scale, size), base.LANCZOS)
            base.put_at(sprites, upright, native_point((374.5,302.5),size))
            sprites.alpha_composite(base.halfturn(sprites))
            rosette = Image.open(complete.COMP/'joker-center-rosette.png').convert('RGBA')
            rosette = base.reciprocal(rosette.resize(sprite_size(rosette.size,scale,size),base.LANCZOS))
            base.put_at(sprites,rosette,tuple((n-1)/2 for n in size))
        else:
            spec = base.load_manifest()['ranks'][rank]
            pip = pip_component(suit,rank,size)
            for item in spec['pips']:
                base.put_at(sprites,base.halfturn(pip) if item['rotation'] else pip,
                            native_point(item['center'],size))
        art = background(size,sprites.getchannel('A'))
        art.alpha_composite(sprites)
    result = base.composite_field(perimeter,art,field)
    result.alpha_composite(index_layer(size,suit,rank))
    result.putalpha(base.silhouette(size))
    return result


def inventory():
    return [(suit,rank) for suit in base.SUITS for rank in RANKS]+[('jokers',v) for v in complete.JOKERS]


def relative(fmt,suit,rank):
    return f'faces/french-suited/{fmt}/{suit}/{rank}.png'


def european(bridge):
    result = bridge.resize(size_for('european-standard'),base.LANCZOS)
    # Match the established physical corner radius of the European backs.
    result.putalpha(base.silhouette(size_for('european-standard')))
    return result


def provenance():
    paths = [base.MANIFEST, ROOT/'scripts/expand_faces.py',ROOT/'scripts/rebuild_deck.py',
             ROOT/'scripts/complete_poker.py', ROOT/'scripts/frame_palette.py', ROOT/'scripts/recolor_card_backs.py']
    paths += [TRACERY/'template.json', TRACERY/'ornament-master.png']
    paths += list(base.COMP.rglob('*.png'))+list(complete.COMP.rglob('*.png'))
    paths += [base.GENERATED/f'{suit}-master.png' for suit in base.SUITS]
    paths += [base.BACKUP/f'cards/faces/french-suited/poker/{suit}/{rank}.png'
              for suit in base.SUITS for rank in COURTS]
    paths += list((base.BACKUP/'cards/backs').rglob('prussian-blue.png'))
    return {p.relative_to(ROOT).as_posix():base.digest(p) for p in sorted(set(paths))}


def preserve():
    inventory_path=BACKUP/'sha256.json'
    if inventory_path.exists():
        saved=json.loads(inventory_path.read_text(encoding='utf-8'))
        for rel,sha in saved.items():
            assert base.digest(BACKUP/rel)==sha,f'Backup changed: {rel}'
        return saved
    paths=list((ROOT/'cards').rglob('*.png'))+[ROOT/'deck.json',ROOT/'catalog.json']
    saved={p.relative_to(ROOT).as_posix():base.digest(p) for p in paths}
    for p in paths:
        target=BACKUP/p.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,target)
    base.write_json(inventory_path,saved)
    return saved


def render_back(fmt,color):
    size=size_for(fmt)
    # Keep the existing interior and substitute only the palette-aware frame.
    art=complete.render_back(fmt,color,size)
    perimeter,field=complete.back_frame(size)
    result=base.composite_field(color_frame(perimeter,color),art,field)
    result.putalpha(base.silhouette(size))
    return result


def back_inventory():
    config=json.loads((ROOT/'deck.json').read_text(encoding='utf-8'))
    return [(fmt,color) for fmt in config['formats'] for color in config['back_colors']]


def stage():
    preserve()
    manifest = dict(version=1,order=list(FORMATS),sources=provenance(),formats={},
                    stage_inputs={p.relative_to(ROOT/'cards').as_posix():base.digest(p)
                                  for p in (ROOT/'cards').rglob('*.png')},
                    palette_policy='suit-aware faces; palette-aware backs',
                    backup='sources/before-face-formats-v1/sha256.json')
    for fmt in FORMATS:
        size = size_for(fmt)
        layouts = {rank:[dict(center=native_point(p['center'],size),rotation=p['rotation'])
                         for p in spec['pips']] for rank,spec in base.load_manifest()['ranks'].items()}
        manifest['formats'][fmt] = dict(pixels=list(size),method='bridge-resize' if fmt=='european-standard' else 'native-components',
                                       center=[(n-1)/2 for n in size],ranks=layouts if fmt!='european-standard' else None)
        for suit,rank in inventory():
            rel = relative(fmt,suit,rank)
            if fmt == 'european-standard':
                source = WORK/'cards'/relative('bridge',suit,rank)
                im = european(Image.open(source).convert('RGBA'))
                metadata = dict(bridge_sha256=base.digest(source))
            else:
                im = render(fmt,suit,rank)
                metadata = dict(method='native-components',frame_color=face_color(suit,rank))
            base.save(im,WORK/'cards'/rel,format=fmt,**metadata)
        paths = [WORK/'cards'/relative(fmt,suit,rank) for suit,rank in inventory()]
        base.contact_sheet(paths,WORK/f'{fmt}-all.jpg',cols=9,thumb=(150,round(150*size[1]/size[0])))
        print(f'Staged {fmt}: 54 faces at {size}',flush=True)
    for fmt,color in back_inventory():
        base.save(render_back(fmt,color),WORK/f'cards/backs/{fmt}/{color}.png',frame_color=color)
    base.write_json(MANIFEST,manifest)


def check(destination):
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    assert manifest['sources']==provenance(),'Source components or renderer changed; restage'
    preserve()
    records=[]
    for fmt in FORMATS:
        size=size_for(fmt)
        for suit,rank in inventory():
            path=destination/relative(fmt,suit,rank)
            im=Image.open(path)
            assert im.mode=='RGBA' and im.size==size,path
            assert all(abs(v-300)<.01 for v in im.info['dpi']),path
            a=np.array(im)
            assert np.array_equal(a[:,:,3],np.array(base.silhouette(size))),path
            if fmt=='european-standard':
                expected=european(Image.open(destination/relative('bridge',suit,rank)).convert('RGBA'))
            else:
                expected=render(fmt,suit,rank)
                if rank=='king':
                    measured=painted_center(court_interior(suit,rank,size))
                    assert np.max(np.abs(np.array(measured)-(np.array(size)-1)/2))<.1,(path,measured)
                _,field,panels=frame(size,face_color(suit,rank))
                ink=np.array(index_layer(size,suit,rank))[:,:,3]>128
                assert not np.any(ink&(np.array(panels)<128)),f'Index outside panel: {path}'
                if rank not in COURTS and suit!='jokers':
                    spec=base.load_manifest()['ranks'][rank]
                    assert len(spec['pips'])==(1 if rank=='ace' else int(rank))
                    occupied=np.zeros((size[1],size[0]),dtype=bool)
                    for item in spec['pips']:
                        point=native_point(item['center'],size)
                        sprite=pip_component(suit,rank,size)
                        layer=Image.new('RGBA',size)
                        base.put_at(layer,base.halfturn(sprite) if item['rotation'] else sprite,point)
                        footprint=np.array(layer)[:,:,3]>128
                        assert not np.any(footprint&occupied),f'Pip collision: {path}'
                        assert not np.any(footprint&(np.array(field)<250)),f'Pip clipped: {path}'
                        occupied|=footprint
                        x,y=point
                        box=(int(x)-24,int(y)-24,int(x)+26,int(y)+26)
                        measured,_=base.turquoise(im.crop(box))
                        assert np.max(np.abs(np.array(measured)+box[:2]-point))<1e-6,(path,point,measured)
            assert np.array_equal(a,np.array(expected)),f'Render mismatch: {path}'
            if fmt!='european-standard' and (suit=='jokers' or rank in ('2','4','6','8','10')):
                assert np.array_equal(a,a[::-1,::-1]),f'Half-turn mismatch: {path}'
            records.append(dict(path=relative(fmt,suit,rank),sha256=base.digest(path)))
        actual={p.relative_to(destination).as_posix() for p in (destination/f'faces/french-suited/{fmt}').rglob('*.png')}
        assert actual=={relative(fmt,s,r) for s,r in inventory()},f'Inventory mismatch: {fmt}'
        print(f'PASS {fmt}: 54 faces, render and geometry checks',flush=True)
    for fmt,color in back_inventory():
        path=destination/f'backs/{fmt}/{color}.png'
        im=Image.open(path)
        a=np.array(im)
        assert im.mode=='RGBA' and im.size==size_for(fmt),path
        assert np.array_equal(a,np.array(render_back(fmt,color))),path
        assert np.array_equal(a,a[::-1,::-1]),path
        records.append(dict(path=f'backs/{fmt}/{color}.png',sha256=base.digest(path)))
    check_inventory(destination, records)
    report=dict(version=1,count=len(records),checks_passed=True,cards=records)
    base.write_json(REPORT,report)
    return report


def check_inventory(destination, records):
    """The active collection also contains separately rendered Tarot faces."""
    expected = {record['path'] for record in records}
    if destination.resolve() == (ROOT/'cards').resolve():
        config = json.loads((ROOT/'deck.json').read_text(encoding='utf-8'))
        tarot = config['face_systems'].get('tarot')
        if tarot:
            for fmt in tarot['formats']:
                expected.update(f'faces/tarot/{fmt}/{suit}/{rank}.png'
                                for suit in tarot['suits'] for rank in tarot['ranks'])
                expected.update(f"faces/tarot/{fmt}/trumps/{trump['number']:02d}-{trump['slug']}.png"
                                for trump in tarot['trumps'])
    actual = {path.relative_to(destination).as_posix() for path in destination.rglob('*.png')}
    assert actual == expected, f'Inventory mismatch: {actual ^ expected}'


def apply():
    report=check(WORK/'cards')
    originals=preserve()
    inputs=json.loads(MANIFEST.read_text(encoding='utf-8')).get('stage_inputs',{})
    for record in report['cards']:
        active=ROOT/'cards'/record['path']
        if active.exists() and base.digest(active) not in (record['sha256'],originals.get('cards/'+record['path']),inputs.get(record['path'])):
            raise ValueError(f'Refusing to replace changed artwork: {active}')
    for record in report['cards']:
        active=ROOT/'cards'/record['path']
        active.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(WORK/'cards'/record['path'],active)
    config=json.loads((ROOT/'deck.json').read_text(encoding='utf-8'))
    config['face_systems']['french-suited']['formats']=list(FORMATS)
    config['renderer']='face-formats-v1'
    config['frame_palette']='suit-aware faces; palette-aware backs'
    base.write_json(ROOT/'deck.json',config)
    from catalog import build_catalog
    base.write_json(ROOT/'catalog.json',build_catalog())
    print('Promoted 270 checked faces and 30 palette-aware backs; refreshed catalog')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    for flag in ('stage','check','apply'):
        group.add_argument('--'+flag,action='store_true')
    parser.add_argument('--active',action='store_true')
    args=parser.parse_args()
    if args.stage: stage()
    elif args.check: check(ROOT/'cards' if args.active else WORK/'cards')
    else: apply()
