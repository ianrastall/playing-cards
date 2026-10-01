"""Compose Bridge, Travel and Jumbo from source components; derive Europe from Bridge.

Default stages and audits; --apply installs the checked stage; --check audits active.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
import build_number_cards as numbers
import register_face_masters as courts
from audit_number_cards import regions

ROOT = numbers.ROOT
WORK = ROOT/'work/french-formats-v1'
COMP = ROOT/'sources/components/french-formats-v1'
DOC = ROOT/'docs/design/french-formats-v1.json'
FORMATS = ('bridge', 'travel', 'jumbo', 'european-standard')
FRAME_SPEC = json.loads((numbers.FRAMES.parent/'manifest.json').read_text(encoding='utf-8'))
DECK = json.loads((ROOT/'deck.json').read_text(encoding='utf-8'))
LANCZOS = Image.Resampling.LANCZOS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def save(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    info = PngImagePlugin.PngInfo()
    info.add_text('Renderer', 'design2-french-formats-v1')
    im.save(path, dpi=(300, 300), pnginfo=info)


def center(size):
    return np.array([(n-1)/2 for n in size])


def paired(im):
    a = np.array(im)
    h = im.height//2
    a[h:] = a[:h][::-1, ::-1]
    return Image.fromarray(a)


def put(layer, sprite, anchor):
    xy = tuple(round(c-(n-1)/2) for c, n in zip(anchor, sprite.size))
    layer.alpha_composite(sprite, xy)
    return xy


def frame(fmt, suit):
    color = 'madder-lake' if suit in ('hearts', 'diamonds', 'red') else 'lamp-black'
    folder = numbers.FRAMES.parent/fmt
    return Image.open(folder/f'{color}.png').convert('RGBA'), color, folder


def index(fmt, suit, rank):
    size = tuple(DECK['formats'][fmt]['back_pixels'])
    safe = FRAME_SPEC['formats'][fmt]['index_safe_box']
    dims = (safe[2]-safe[0], safe[3]-safe[1])
    layer = Image.new('RGBA', size)
    if rank == 'joker':
        ink = numbers.COLORS['red' if suit == 'red' else 'black']
        font = ImageFont.truetype(str(numbers.FONT), max(10, round(20*min(size[0]/750, size[1]/1050))))
        draw = ImageDraw.Draw(layer)
        for i, letter in enumerate('JOKER'):
            draw.text(((safe[0]+safe[2]-1)/2, safe[1]+(i+.5)*dims[1]/5),
                      letter, font=font, fill=ink, anchor='mm')
    else:
        source = numbers.COMP/f'indices/{suit}/{rank}.png'
        sprite = Image.open(source).convert('RGBA').resize(dims, LANCZOS)
        layer.alpha_composite(sprite, tuple(safe[:2]))
    return paired(layer)


def pip(fmt, suit, rank, bounds):
    size = tuple(DECK['formats'][fmt]['back_pixels'])
    scale = min(size[0]/750, size[1]/1050)
    dims = tuple(2*math.ceil(n*scale/2)+(size[i]%2) for i,n in enumerate(bounds))
    source = numbers.clean_source(suit)
    anchor = np.array(numbers.jewel(source))
    extent = np.maximum(anchor+.5, np.array(source.size)-anchor-.5)
    factor = min((np.array(dims)-6)/(2*extent))
    scaled = source.resize(tuple(round(n*factor) for n in source.size), LANCZOS)
    stone = np.array(numbers.jewel(scaled))
    offset = stone-center(dims)
    for _ in range(6):
        sprite = scaled.transform(dims, Image.Transform.AFFINE,
            (1,0,offset[0],0,1,offset[1]), resample=Image.Resampling.BICUBIC)
        error = np.array(numbers.jewel(sprite))-center(dims)
        if max(abs(error)) < .05:
            break
        offset += error
    assert max(abs(error)) < .2, (fmt,suit,rank,error)
    path = COMP/f'{fmt}/pips/{suit}/{rank}.png'
    save(sprite, path)
    return sprite, dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path),
        anchor=center(dims).tolist(), measured_stone=numbers.jewel(sprite))


def number(fmt, suit, rank, spec):
    result, color, folder = frame(fmt, suit)
    size = result.size
    sprite, component = pip(fmt, suit, rank, spec['component_bounds'])
    layout = Image.new('RGBA', size)
    positions = []
    half = len(spec['pips'])//2
    for p in spec['pips'][:half*2:2]:
        anchor = (np.array(p['center'])+.5)*np.array(size)/np.array(numbers.SIZE)-.5
        upper = Image.new('RGBA', size)
        xy = put(upper, sprite, anchor)
        layout.alpha_composite(upper)
        layout.alpha_composite(upper.transpose(Image.Transpose.ROTATE_180))
        positions.extend([xy, [size[0]-xy[0]-sprite.width, size[1]-xy[1]-sprite.height]])
    if int(rank)%2:
        positions.append(put(layout, sprite, center(size)))
    field = np.array(Image.open(folder/'field-mask.png'))
    assert not np.any((np.array(layout)[:,:,3]>0) & (field==0)), (fmt,suit,rank,'pip outside field')
    result.alpha_composite(layout)
    result.alpha_composite(index(fmt,suit,rank))
    result.putalpha(Image.open(folder/'outline-mask.png'))
    return result, dict(frame_color=color, pip_component=component, pip_positions=positions,
        pip_count=int(rank), half_turn_exact=int(rank)%2==0)


def sample(im, fmt, anchor):
    size = tuple(DECK['formats'][fmt]['back_pixels'])
    target = center(size)
    box = FRAME_SPEC['formats'][fmt]['field_bounds']
    a = np.array(im.convert('RGB')).astype(float)
    h,w = a.shape[:2]
    x = np.interp(np.arange(size[0]), [box[0],target[0],box[2]-1], [132,anchor[0],w-132])
    y = np.interp(np.arange(size[1]), [box[1],target[1],box[3]-1], [102,anchor[1],h-126])
    x0,y0 = np.floor(x).astype(int),np.floor(y).astype(int)
    fx,fy = (x-x0)[None,:,None],(y-y0)[:,None,None]
    top = a[y0[:,None],x0[None,:]]*(1-fx)+a[y0[:,None],(x0+1)[None,:]]*fx
    bottom = a[(y0+1)[:,None],x0[None,:]]*(1-fx)+a[(y0+1)[:,None],(x0+1)[None,:]]*fx
    return Image.fromarray(np.rint(top*(1-fy)+bottom*fy).astype(np.uint8))


def artwork(fmt, record):
    original = Image.open(ROOT/record['source'])
    result, color, folder = frame(fmt,record['suit'])
    target = center(result.size)
    anchor = np.array(courts.jewel(original))
    box = FRAME_SPEC['formats'][fmt]['field_bounds']
    scale = np.array([(original.width-264)/(box[2]-box[0]-1),
                      (original.height-228)/(box[3]-box[1]-1)])
    for _ in range(8):
        mapped = sample(original,fmt,anchor)
        error = np.array(courts.jewel(mapped))-target
        if max(abs(error)) < .025:
            break
        anchor += error*scale
    if record['rank'] != 'ace':
        mapped = paired(mapped)
    result = Image.composite(mapped.convert('RGBA'),result,Image.open(folder/'field-mask.png'))
    result.alpha_composite(index(fmt,record['suit'],{'ace':'A','king':'K','queen':'Q','jack':'J','joker':'joker'}[record['rank']]))
    result.putalpha(Image.open(folder/'outline-mask.png'))
    measured = courts.jewel(result)
    assert max(abs(np.array(measured)-target)) < .2, (fmt,record,measured)
    return result,dict(frame_color=color, source=record['source'],source_sha256=record['source_sha256'],
        sampling_anchor=anchor.tolist(), measured_center=measured, half_turn_exact=record['rank']!='ace')


def derived(record):
    source = WORK/'bridge'/record['relative']
    size = tuple(DECK['formats']['european-standard']['back_pixels'])
    result, color, folder = frame('european-standard',record['suit'])
    resized = Image.open(source).convert('RGBA').resize(size,LANCZOS)
    result = Image.composite(resized,result,Image.open(folder/'field-mask.png'))
    # Clear and rebuild both indices to maintain the same panels across all cards.
    result.alpha_composite(index('european-standard',record['suit'],
        {'ace':'A','king':'K','queen':'Q','jack':'J','joker':'joker'}.get(record['rank'],record['rank'])))
    if record['half_turn_exact']:
        result = paired(result)
    result.putalpha(Image.open(folder/'outline-mask.png'))
    return result,dict(frame_color=color, bridge_source=source.relative_to(ROOT).as_posix(),
        bridge_sha256=sha(source),half_turn_exact=record['half_turn_exact'],
        derivation='Finished Bridge field resized with Lanczos; common European frame and indices reapplied.')


def stage():
    art = list(courts.sources())
    records = []
    for fmt in FORMATS:
        for suit in numbers.SUITS:
            for rank in DECK['face_systems']['french-suited']['ranks']:
                if fmt == 'european-standard':
                    base = next(c for c in records if c['format']=='bridge' and c['suit']==suit and c['rank']==rank)
                    im,metrics = derived(base)
                elif rank.isdigit():
                    im,metrics = number(fmt,suit,rank,numbers.layout()[rank])
                else:
                    im,metrics = artwork(fmt,next(c for c in art if c['rank']==rank and c['suit']==suit))
                relative = f'{suit}/{rank}.png'
                path = WORK/fmt/relative
                save(im,path)
                records.append(dict(format=fmt,suit=suit,rank=rank,relative=relative,
                    path=f'cards/faces/french-suited/{fmt}/{relative}', staged_path=path.relative_to(ROOT).as_posix(),
                    pixels=list(im.size),center=center(im.size).tolist(),sha256=sha(path),**metrics))
        for suit in ('black','red'):
            if fmt == 'european-standard':
                base = next(c for c in records if c['format']=='bridge' and c['suit']==suit and c['rank']=='joker')
                im,metrics = derived(base)
            else:
                im,metrics = artwork(fmt,next(c for c in art if c['rank']=='joker' and c['suit']==suit))
            relative = f'jokers/{suit}.png'
            path = WORK/fmt/relative
            save(im,path)
            records.append(dict(format=fmt,suit=suit,rank='joker',relative=relative,
                path=f'cards/faces/french-suited/{fmt}/{relative}',staged_path=path.relative_to(ROOT).as_posix(),
                pixels=list(im.size),center=center(im.size).tolist(),sha256=sha(path),**metrics))
        proof(fmt,records)
        print(f'STAGED {fmt}: 54 faces',flush=True)
    components = [dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(COMP.rglob('*.png'))]
    write_json(DOC,dict(revision='french-formats-v1',formats=list(FORMATS),card_count=216,
        construction='Format-specific source art, pip sprites, positions, indices and existing shared frames; European Standard derives from finished Bridge.',
        components=components,cards=records))
    audit(False)


def proof(fmt,records):
    selected = [c for c in records if c['format']==fmt and ((c['rank']=='king') or
        (c['suit']=='spades' and c['rank'] in ('ace','7','10')) or c['rank']=='joker')]
    sheet = Image.new('RGB',(1280,math.ceil(len(selected)/4)*690),'#e9dfcf')
    draw = ImageDraw.Draw(sheet)
    for i,c in enumerate(selected):
        im = Image.open(ROOT/c['staged_path'])
        im.thumbnail((285,600),LANCZOS)
        x,y = (i%4)*320+15,(i//4)*690+25
        sheet.paste(im,(x,y),im)
        draw.text((x,y+620),f"{fmt}: {c['rank']} / {c['suit']}",fill='black')
    sheet.save(WORK/f'{fmt}-proof.jpg',quality=95)


def audit(active=True):
    spec = json.loads(DOC.read_text(encoding='utf-8'))
    expected = {(f,s,r) for f in FORMATS for s in numbers.SUITS for r in DECK['face_systems']['french-suited']['ranks']}
    expected |= {(f,s,'joker') for f in FORMATS for s in ('black','red')}
    assert len(spec['cards'])==216 and {(c['format'],c['suit'],c['rank']) for c in spec['cards']}==expected
    for c in spec['components']:
        assert sha(ROOT/c['path'])==c['sha256']
    reports = []
    cache = {}
    for c in spec['cards']:
        fmt = c['format']
        if fmt not in cache:
            folder = numbers.FRAMES.parent/fmt
            cache[fmt] = (np.array(Image.open(folder/'field-mask.png'))>0,
                np.array(Image.open(folder/'panel-mask.png'))>0,np.array(Image.open(folder/'outline-mask.png')),
                {col:np.array(Image.open(folder/f'{col}.png')) for col in ('lamp-black','madder-lake')})
        field,panels,outline,frames = cache[fmt]
        path = ROOT/c['path' if active else 'staged_path']
        assert sha(path)==c['sha256'],path
        with Image.open(path) as im:
            assert im.size==tuple(c['pixels']) and im.mode=='RGBA'
            assert all(abs(d-300)<.01 for d in im.info['dpi'])
            a = np.array(im)
            measured = courts.jewel(im) if not c['rank'].isdigit() else None
        assert np.array_equal(a[:,:,3],outline),path
        assert np.array_equal(a[~(field|panels)],frames[c['frame_color']][~(field|panels)]),path
        indices = index(fmt,c['suit'],{'ace':'A','king':'K','queen':'Q','jack':'J','joker':'joker'}.get(c['rank'],c['rank']))
        expected_panel = Image.fromarray(frames[c['frame_color']]); expected_panel.alpha_composite(indices)
        assert np.array_equal(a[panels],np.array(expected_panel)[panels]),(path,'indices')
        if c['half_turn_exact']:
            assert np.array_equal(a,a[::-1,::-1]),path
        if c.get('source'):
            assert sha(ROOT/c['source'])==c['source_sha256']
        if c.get('bridge_source'):
            # The active Bridge must be exactly the staged derivative input.
            bridge = ROOT/c['bridge_source'] if not active else ROOT/'cards/faces/french-suited/bridge'/c['relative']
            assert sha(bridge)==c['bridge_sha256']
        if measured:
            assert max(abs(np.array(measured)-c['center'])) < .3,(path,measured)
        pip_metrics = {}
        if c['rank'].isdigit():
            difference = np.max(np.abs(a[:,:,:3].astype(int)-frames[c['frame_color']][:,:,:3].astype(int)),axis=2)
            boxes = regions((difference>12)&field)
            assert len(boxes)==int(c['rank']),(path,'visible pip count',len(boxes))
            expected_pips = numbers.layout()[c['rank']]['pips']
            measured_pips = []
            for p in expected_pips:
                target = (np.array(p['center'])+.5)*np.array(c['pixels'])/np.array(numbers.SIZE)-.5
                hits = [b for b in boxes if b[0]<=target[0]<b[2] and b[1]<=target[1]<b[3]]
                assert len(hits)==1,(path,target,'missing or overlapping pip')
                b = hits[0]
                stone = np.array(numbers.jewel(Image.fromarray(a).crop(tuple(b))))+b[:2]
                assert max(abs(stone-target)) < 1,(path,stone,target)
                measured_pips.append(stone)
            mass_center = np.mean(measured_pips,axis=0)
            assert max(abs(mass_center-c['center'])) < .15,(path,'pip layout center',mass_center)
            if int(c['rank'])%2:
                b = next(b for b in boxes if b[0]<=c['center'][0]<b[2] and b[1]<=c['center'][1]<b[3])
                allowed = np.zeros(field.shape,dtype=bool)
                allowed[max(0,b[1]-6):b[3]+6,max(0,b[0]-6):b[2]+6]=True
                allowed |= allowed[::-1,::-1].copy()
                assert not np.any(np.any(a!=a[::-1,::-1],axis=2)&~allowed),(path,'odd rank differs beyond center pip')
            pip_metrics = dict(visible_pip_count=len(boxes),measured_pip_layout_center=mass_center.tolist())
        reports.append(dict(path=c['path'],sha256=c['sha256'],shared_border_exact=True,
            common_alpha=True,half_turn_exact=c['half_turn_exact'],measured_center=measured,**pip_metrics))
    write_json(ROOT/'docs/design/french-formats-v1-audit.json',dict(status='passed',target='active' if active else 'staged',cards=reports))
    print(f"PASS 216 {'active' if active else 'staged'} faces: inventory, hashes, shared borders/indices, alpha, symmetry and centers",flush=True)


def apply():
    audit(False)
    for c in json.loads(DOC.read_text(encoding='utf-8'))['cards']:
        dest = ROOT/c['path']
        assert not dest.exists() or sha(dest)==c['sha256'],dest
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/c['staged_path'],dest)
    config = json.loads((ROOT/'deck.json').read_text(encoding='utf-8'))
    config['face_systems']['french-suited']['formats'] = ['poker',*FORMATS]
    config['face_status'] = 'approved'
    config['face_systems']['tarot']['translation_status'] = 'accepted-for-release'
    if 'french-formats-v1' not in config['face_renderer']:
        config['face_renderer'] += ' + french-formats-v1'
    config['release_version'] = '1.0'
    write_json(ROOT/'deck.json',config)
    audit(True)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply',action='store_true'); mode.add_argument('--check',action='store_true')
    args = parser.parse_args()
    if args.apply: apply()
    elif args.check: audit()
    else: stage()
