"""Prepare and stage four Tarot review cards; never modifies the active catalog.

python scripts/tarot_review.py --prepare --stage --check
Subsequent --stage --check runs consume the saved layout and component hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

import rebuild_deck as base
import expand_faces as faces

ROOT = base.ROOT
RAW = ROOT / 'sources/generated/tarot-review-v1'
COMP = ROOT / 'sources/components/tarot/review-v1'
WORK = ROOT / 'work/tarot-review-v1'
MANIFEST = ROOT / 'docs/design/tarot-review-layout-v1.json'
SIZE = (825, 1425)
FONT = Path('C:/Windows/Fonts/timesbd.ttf')
INKS = {'lamp-black': (5, 5, 5), 'madder-lake': (78, 9, 23)}


def relative(p):
    return str(p.relative_to(ROOT)).replace('\\', '/')


def write_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def glyph(kind):
    # Small index shapes are code-native, consistent-weight ink silhouettes.
    im = Image.new('L', (160, 160))
    d = ImageDraw.Draw(im)
    if kind == 'swords':
        d.polygon([(80, 8), (94, 36), (87, 101), (108, 102), (108, 114),
                   (88, 114), (88, 141), (96, 144), (96, 152), (64, 152),
                   (64, 144), (72, 141), (72, 114), (52, 114), (52, 102),
                   (73, 101), (66, 36)], fill=255)
    elif kind == 'cups':
        d.ellipse((70, 10, 90, 28), fill=255)
        d.polygon([(80, 21), (121, 54), (39, 54)], fill=255)
        d.rounded_rectangle((36, 61, 124, 78), radius=5, fill=255)
        d.pieslice((38, 44, 122, 116), 0, 180, fill=255)
        d.rectangle((73, 100, 87, 133), fill=255)
        d.polygon([(73, 128), (87, 128), (109, 145), (51, 145)], fill=255)
    else:
        pts = [(80 + (68 if i % 2 == 0 else 29)*math.sin(i*math.pi/5),
                80 - (68 if i % 2 == 0 else 29)*math.cos(i*math.pi/5))
               for i in range(10)]
        d.line(pts+[pts[0]], fill=255, width=12, joint='curve')
    return im


def instance(i, component, center, height, rotation=0, mirror=False, role='emblem'):
    return dict(id=i, component=component, center=center, height=height,
                rotation=rotation, mirror=mirror, role=role)


def prepare():
    if MANIFEST.exists():
        raise SystemExit('Layout already exists; use --stage --check or edit the saved layout.')
    COMP.mkdir(parents=True, exist_ok=True)
    components = {}
    for name in ['sword-straight', 'sword-curved', 'ace-crown', 'foliage', 'empress', 'queen-cups']:
        source = RAW / (name+'.png')
        im = Image.open(source).convert('RGBA')
        visible = Image.fromarray(np.uint8(np.array(im.getchannel('A')) > 128)*255).getbbox()
        x0, y0, x1, y1 = visible
        box = (max(0,x0-8), max(0,y0-8), min(im.width,x1+8), min(im.height,y1+8))
        im = im.crop(box)
        path = COMP / (name+'.png')
        base.save(im, path)
        components[name] = dict(path=relative(path), sha256=base.digest(path),
            source=relative(source), source_sha256=base.digest(source), crop=list(box),
            size=list(im.size), anchor=[(im.width-1)/2, (im.height-1)/2])
    for kind in ['swords', 'cups', 'trumps']:
        p = COMP / (kind+'-index-mask.png')
        glyph(kind).save(p)
        components[kind+'-index'] = dict(path=relative(p), sha256=base.digest(p),
            size=[160,160], anchor=[79.5,79.5], source='code-native glyph in scripts/tarot_review.py')
    ten = []
    for j,y in enumerate([330,520,710,900,1090]):
        component='sword-straight' if j==2 else 'sword-curved'
        ten.extend([instance(f'sword-{j*2+1}',component,[364,y],440,-38),
                    instance(f'sword-{j*2+2}',component,[460,y],440,38,True)])
    cards = [
        dict(id='the-empress', title='THE EMPRESS', index='3', glyph='trumps', ink='lamp-black',
             expected_emblems=0, reversible=False,
             instances=[instance('figure','empress',[412,687],910,role='figure')]),
        dict(id='queen-of-cups', title='QUEEN OF CUPS', index='Q', glyph='cups', ink='madder-lake',
             expected_emblems=0, reversible=False,
             instances=[instance('figure','queen-cups',[412,687],930,role='figure')]),
        dict(id='ace-of-swords', title=None, index='A', glyph='swords', ink='lamp-black',
             expected_emblems=1, reversible=False,
             instances=[instance('sword-1','sword-straight',[412,763],970),
                        instance('sprig-left','foliage',[290,458],430,12,role='furniture'),
                        instance('sprig-right','foliage',[534,458],430,-12,True,role='furniture'),
                        instance('crown','ace-crown',[412,340],145,role='furniture')]),
        dict(id='ten-of-swords', title=None, index='10', glyph='swords', ink='lamp-black',
             expected_emblems=10, reversible=False, instances=ten,
             crossing_policy='Five open crossed pairs; alternating over/under with saved local masks.',
             crossings=[dict(over=f'sword-{2*j+1 if j%2==0 else 2*j+2}',
                             under=f'sword-{2*j+2 if j%2==0 else 2*j+1}') for j in range(5)])]
    inputs = [base.COMP/'frame.png',base.COMP/'field-mask.png',base.COMP/'panel-mask.png',
              faces.TRACERY/'ornament-master.png', faces.TRACERY/'template.json',
              RAW/'prompts.json']
    spec = dict(version=1, status='review-only', canvas=list(SIZE), center=[412,712],
        coordinate_basis='zero-based pixel centers', dpi=300, corner_radius_mm=3.5,
        components=components, cards=cards, shared_inputs={relative(p):base.digest(p) for p in inputs},
        font=dict(path=str(FONT),sha256=base.digest(FONT)),
        transform_policy='uniform scale from height, rounded dimensions; rotation bicubic expanded; nearest integral top-left from center',
        indices=dict(center_x=78,rank_center_y=166,rank_size=76,wide_rank_size=60,
                     glyph_center=[78,252],glyph_size=[43,49],paired_rotation=180),
        title=dict(center=[412,1254],font_size=35,rule_y=1215,rule_x=[225,599]))
    write_json(MANIFEST, spec)


def place(spec, item):
    c = spec['components'][item['component']]
    im = Image.open(ROOT/c['path']).convert('RGBA')
    if item['mirror']:
        im = ImageOps.mirror(im)
    scale = item['height']/im.height
    im = im.resize((round(im.width*scale), item['height']), base.LANCZOS)
    if item['rotation'] % 360:
        if item['rotation'] % 360 == 180:
            im = base.halfturn(im)
        else:
            im = im.rotate(item['rotation'], Image.Resampling.BICUBIC, expand=True)
    xy = [round(p-(s-1)/2) for p,s in zip(item['center'], im.size)]
    layer = Image.new('RGBA', SIZE)
    layer.alpha_composite(im, xy)
    return layer, dict(scale=scale,top_left=xy,transformed_size=list(im.size))


def indices(spec, card):
    s=spec['indices']; ink=INKS[card['ink']]
    layer=Image.new('RGBA',SIZE);d=ImageDraw.Draw(layer)
    font=ImageFont.truetype(spec['font']['path'], s['wide_rank_size'] if len(card['index'])>1 else s['rank_size'])
    d.text((s['center_x'],s['rank_center_y']),card['index'],fill=ink, font=font, anchor='mm')
    c=spec['components'][card['glyph']+'-index']
    mask=Image.open(ROOT/c['path']).resize(tuple(s['glyph_size']),base.LANCZOS)
    icon=Image.new('RGBA',mask.size,ink);icon.putalpha(mask)
    xy=[round(v-(n-1)/2) for v,n in zip(s['glyph_center'],mask.size)]
    layer.alpha_composite(icon,xy)
    layer.alpha_composite(base.halfturn(layer))
    return layer


def render(spec, card, save_masks=False):
    frame,field,panels=faces.frame(SIZE,card['ink'])
    art=Image.new('RGBA',SIZE);layers={};transforms={};crossings=[]
    for item in card['instances']:
        layer,transform=place(spec,item)
        art.alpha_composite(layer);layers[item['id']]=layer;transforms[item['id']]=transform
    if card.get('crossings'):
        # Restore the declared over-blade only at the recorded pair's intersection.
        for crossing in card['crossings']:
            over=crossing['over'];under=crossing['under']
            mask=ImageChops.multiply(layers[over].getchannel('A'),layers[under].getchannel('A'))
            mask=mask.point(lambda v:255 if v>80 else 0)
            if not mask.getbbox():
                continue
            patch=layers[over].copy()
            patch.putalpha(ImageChops.multiply(patch.getchannel('A'),mask))
            art.alpha_composite(patch)
            path=WORK/'crossings'/f'{over}-over-{under}.png'
            if save_masks:
                path.parent.mkdir(parents=True,exist_ok=True);mask.save(path)
            crossings.append(dict(over=over,under=under,mask=relative(path),bounds=list(mask.getbbox()),
                                  mask_pixel_sha256=hashlib.sha256(mask.tobytes()).hexdigest()))
    background=faces.background(SIZE, art.getchannel('A'))
    title_layer=Image.new('RGBA',SIZE)
    if card['title']:
        t=spec['title'];d=ImageDraw.Draw(title_layer)
        d.rectangle((180,1190,645,1295), fill=base.GROUND+(255,))
        d.line((t['rule_x'][0],t['rule_y'],t['rule_x'][1],t['rule_y']), fill=(198,161,91),width=2)
        d.text(tuple(t['center']),card['title'],fill=INKS[card['ink']],
               font=ImageFont.truetype(spec['font']['path'],t['font_size']),anchor='mm')
    background.alpha_composite(art)
    background.alpha_composite(title_layer)
    result=base.composite_field(frame,background,field)
    index=indices(spec,card);result.alpha_composite(index)
    result.putalpha(base.silhouette(SIZE))
    occupied=np.array(art.getchannel('A'))>128
    clipped=int((occupied & (np.array(field)<128)).sum())
    escaped=int(((np.array(index.getchannel('A'))>128)&(np.array(panels)<128)).sum())
    title_collision=0
    if card['title']:
        title_collision=int(occupied[1190:1296,180:646].sum())
    report=dict(id=card['id'],emblem_count=sum(i['role']=='emblem' for i in card['instances']),
                artwork_pixels_outside_field=clipped,index_pixels_outside_panels=escaped,
                artwork_pixels_in_title_band=title_collision,transforms=transforms,crossings=crossings)
    return result,report,layers


def verify_inputs(spec):
    for c in spec['components'].values():
        assert base.digest(ROOT/c['path'])==c['sha256'],c['path']
        if 'source_sha256' in c:
            assert base.digest(ROOT/c['source'])==c['source_sha256'],c['source']
    for p,h in spec['shared_inputs'].items():
        assert base.digest(ROOT/p)==h,p
    assert base.digest(spec['font']['path'])==spec['font']['sha256'],'Font changed'


def stage(spec):
    verify_inputs(spec);WORK.mkdir(parents=True,exist_ok=True)
    reports=[];thumbs=[]
    for card in spec['cards']:
        im,report,layers=render(spec,card,True)
        path=WORK/(card['id']+'.png');base.save(im,path)
        report['path']=relative(path);report['sha256']=base.digest(path)
        reports.append(report)
        thumb=im.copy();thumb.thumbnail((412,712));thumbs.append((card,thumb))
        if card['id']=='ten-of-swords':
            annotated=im.copy();ann=ImageDraw.Draw(annotated)
            label_font=ImageFont.truetype(spec['font']['path'],22)
            for j,item in enumerate(card['instances']):
                x=190 if j%2==0 else 635;y=item['center'][1]
                ann.line((x,y,item['center'][0],y),fill=(78,9,23),width=2)
                ann.ellipse((x-18,y-18,x+18,y+18),fill=base.GROUND,outline=(78,9,23),width=2)
                ann.text((x,y),str(j+1),font=label_font,fill=(78,9,23),anchor='mm')
            base.save(annotated,WORK/'ten-annotated.png')
            sheet=Image.new('RGB',(1500,660),(250,235,215));d=ImageDraw.Draw(sheet)
            font=ImageFont.truetype(spec['font']['path'],24)
            for j,(name,layer) in enumerate(layers.items()):
                isolated=layer.crop(layer.getbbox());isolated.thumbnail((130,270))
                x=(j%5)*300;y=(j//5)*330
                sheet.paste(isolated,(x+(300-isolated.width)//2,y+38),isolated)
                d.text((x+150,y+10),name,fill=(5,5,5),font=font,anchor='mt')
            sheet.save(WORK/'ten-instance-audit.jpg',quality=95)
    sheet=Image.new('RGB',(1776,840),(239,228,207));d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(spec['font']['path'],24)
    for j,(card,thumb) in enumerate(thumbs):
        x=24+j*438;sheet.paste(thumb,(x,60),thumb)
        d.text((x+206,24),card['id'].replace('-',' ').title(),font=font,fill=(45,38,29),anchor='mm')
    d.text((24,797),'DESIGN 1 / TAROT — component and layout proofs / v1',font=font,fill=(75,65,48))
    sheet.save(WORK/'review-sheet.jpg',quality=96)
    write_json(WORK/'report.json',dict(status='review-only',cards=reports))
    specimens=[]
    for rank,kind in [('10','swords'),('N','cups'),('21','trumps')]:
        c=dict(index=rank,glyph=kind,ink='lamp-black')
        fr,_,_=faces.frame(SIZE,'lamp-black');fr=fr.copy();fr.alpha_composite(indices(spec,c))
        specimens.append(fr.crop((25,65,139,330)))
    sample=Image.new('RGB',(432,305),base.GROUND)
    for j,im in enumerate(specimens):sample.paste(im,(15+j*140,15),im)
    sample.save(WORK/'index-specimens.png')
    cards_html=''.join(f'<figure><a href="{c["id"]}.png"><img src="{c["id"]}.png"></a><figcaption>{c["id"].replace("-"," ").title()}</figcaption></figure>' for c in spec['cards'])
    (WORK/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Tarot review v1</title><style>body{background:#eee3cf;color:#30291e;font:18px Georgia;margin:36px}main{display:flex;gap:24px;flex-wrap:wrap}figure{margin:0;max-width:340px}img{width:100%;height:auto}figcaption{padding:15px 0}a{color:inherit}</style><h1>Design 1 · Tarot review</h1><p>Four staged composites. Click a card for its native 825 × 1425 image.</p><main>'+cards_html+'</main><p><a href="ten-instance-audit.jpg">Ten sword instances</a> · <a href="index-specimens.png">Index specimens</a> · <a href="report.json">Render report</a></p>',encoding='utf-8')
    print(json.dumps(reports,indent=2))


def check(spec):
    verify_inputs(spec)
    for card in spec['cards']:
        expected,report,_=render(spec,card)
        actual=Image.open(WORK/(card['id']+'.png'))
        assert actual.mode=='RGBA' and actual.size==SIZE
        assert np.array_equal(np.array(actual),np.array(expected)),card['id']
        assert report['emblem_count']==card['expected_emblems'],card['id']
        assert report['artwork_pixels_outside_field']==0,report
        assert report['index_pixels_outside_panels']==0,report
        assert report['artwork_pixels_in_title_band']==0,report
        if card['reversible']:
            assert np.array_equal(np.array(actual),np.array(base.halfturn(actual)))
    print('PASS: four native RGBA proofs; source hashes, exact rerender, counts, artwork and index containment.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for option in ['prepare','stage','check']:parser.add_argument('--'+option,action='store_true')
    args=parser.parse_args()
    if args.prepare:prepare()
    spec=json.loads(MANIFEST.read_text(encoding='utf-8'))
    if args.stage:stage(spec)
    if args.check:check(spec)
