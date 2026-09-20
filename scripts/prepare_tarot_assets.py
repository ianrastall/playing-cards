"""Prepare Tarot assets and inspection sheets only; does not render any cards."""
from __future__ import annotations

import hashlib
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'sources/generated/tarot-full-assets-v1'
COMP = ROOT / 'sources/components/tarot/full-assets-v1'
WORK = ROOT / 'work/tarot-full-assets-v1'
INVENTORY = ROOT / 'docs/design/tarot-full-assets-v1.json'
GROUND = (250, 235, 215)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')


def new_glyph(kind):
    im = Image.new('L', (160,160));d=ImageDraw.Draw(im)
    if kind == 'batons':
        d.rounded_rectangle((71,15,89,149),radius=6,fill=255)
        d.ellipse((64,7,96,29),fill=255)
        d.ellipse((38,38,73,57),fill=255)
        d.line((52,48,80,73),fill=255,width=7)
        d.ellipse((87,61,121,81),fill=255)
        d.line((108,74,80,99),fill=255,width=7)
    else:
        d.ellipse((15,15,145,145),fill=255)
        d.ellipse((29,29,131,131),fill=0)
        d.ellipse((42,42,118,118),fill=255)
    return im


def contact(name, ids, components, title):
    ids=[asset_id for asset_id in ids if asset_id in components]
    if not ids:
        return None
    columns=4;cw,ch=360,560
    rows=(len(ids)+columns-1)//columns
    sheet=Image.new('RGB',(columns*cw,rows*ch+90),GROUND)
    d=ImageDraw.Draw(sheet)
    heading=ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf',32)
    label=ImageFont.truetype('C:/Windows/Fonts/times.ttf',23)
    d.text((25,22),title,font=heading,fill=(45,36,25))
    for n,asset_id in enumerate(ids):
        x=(n%columns)*cw;y=(n//columns)*ch+85
        im=Image.open(ROOT/components[asset_id]['path']).convert('RGBA')
        im.thumbnail((320,495),Image.Resampling.LANCZOS)
        sheet.paste(im,(x+(cw-im.width)//2,y+(495-im.height)//2),im)
        text=asset_id.replace('-',' ').title()
        d.text((x+cw//2,y+510),text,font=label,fill=(45,36,25),anchor='mt')
    path=WORK/(name+'.jpg');sheet.save(path,quality=95)
    return rel(path)


def main(allow_partial=False):
    COMP.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    prompts=json.loads((RAW/'actual-prompts.json').read_text(encoding='utf-8-sig'))
    selection_path=RAW/'asset-selections.json'
    selections=json.loads(selection_path.read_text())['selections'] if selection_path.exists() else {}
    jobs=prompts['jobs'];components={};warnings=[];missing=[]
    assert len(jobs)==39 and len({j['id'] for j in jobs})==39
    for job in jobs:
        selection=selections.get(job['id'])
        source=RAW/(selection['source'] if selection else job['id']+'.png')
        if not source.exists():
            missing.append(job['id'])
            if not allow_partial:
                raise FileNotFoundError(f'{source}; use --allow-partial only for incomplete asset inspection')
            continue
        im=Image.open(source)
        assert im.mode=='RGBA',f'Missing RGBA: {source}'
        a=np.array(im.getchannel('A'))
        assert np.count_nonzero(a==0)>100,f'Missing transparent background: {source}'
        visible=Image.fromarray(np.uint8(a>128)*255).getbbox()
        assert visible is not None,source
        edge=int((a[0]>128).sum()+(a[-1]>128).sum()+(a[:,0]>128).sum()+(a[:,-1]>128).sum())
        if edge:warnings.append(dict(id=job['id'],issue='Opaque art touches source edge',pixels=edge))
        x0,y0,x1,y1=visible
        crop=[max(0,x0-12),max(0,y0-12),min(im.width,x1+12),min(im.height,y1+12)]
        prepared=im.crop(crop);dest=COMP/(job['id']+'.png')
        prepared.save(dest,dpi=(300,300))
        components[job['id']]=dict(kind=job['kind'],source=rel(source),source_sha256=digest(source),
            source_size=list(im.size),path=rel(dest),sha256=digest(dest),crop=crop,
            size=list(prepared.size),anchor=[(prepared.width-1)/2,(prepared.height-1)/2],
            alpha_extrema=list(prepared.getchannel('A').getextrema()),
            visible_source_bounds=list(visible),source_edge_pixels=edge,
            prompt_id=job['id'],references=[dict(path=p,sha256=digest(Path(p))) for p in job['refs']])
        if selection:
            components[job['id']]['revision']=selection
    for kind in ['batons','coins']:
        path=COMP/(kind+'-index-mask.png');new_glyph(kind).save(path)
        components[kind+'-index']=dict(kind='code-native-index',path=rel(path),sha256=digest(path),
            size=[160,160],anchor=[79.5,79.5],source='scripts/prepare_tarot_assets.py')
    reused=json.loads((ROOT/'docs/design/tarot-review-layout-v1.json').read_text())['components']
    for key,c in reused.items():
        assert digest(ROOT/c['path'])==c['sha256'],key
        components[key]=dict(c,reused=True)
    production=json.loads((ROOT/'docs/design/tarot-full-production-v1.json').read_text())
    assert len(production['cards'])==78
    unresolved=[card['id'] for card in production['cards'] if card['primary_asset'] not in components]
    if not allow_partial:
        assert not unresolved,unresolved
    # Full card rendering is deliberately absent. These sheets show isolated assets.
    court_ids=[]
    for suit in ['swords','batons','cups','coins']:
        for rank in ['page','knight','queen','king']:
            court_ids.append('queen-cups' if suit=='cups' and rank=='queen' else f'{rank}-of-{suit}')
    trump_cards=sorted((c for c in production['cards'] if c['kind']=='trump'),key=lambda c:c['number'])
    trump_ids=[c['primary_asset'] for c in trump_cards]
    sheets=[contact('suit-masters',['sword-straight','sword-curved','batons-master','cups-master','coins-master','ace-crown','foliage'],components,'Tarot / reusable suit assets and furniture'),
            contact('courts',court_ids,components,'Tarot / all 16 court illustrations'),
            contact('trumps-00-10',trump_ids[:11],components,'Tarot / trumps 0–10'),
            contact('trumps-11-21',trump_ids[11:],components,'Tarot / trumps 11–21')]
    sheets=[p for p in sheets if p]
    glyph_sheet=Image.new('RGB',(450,190),GROUND)
    for i,kind in enumerate(['batons','coins']):
        mask=Image.open(ROOT/components[kind+'-index']['path']);ink=Image.new('RGB',mask.size,(5,5,5))
        glyph_sheet.paste(ink,(35+i*215,15),mask)
    glyph_sheet.save(WORK/'new-index-glyphs.png')
    inventory=dict(version=1,status='incomplete-image-generation-usage-limit' if missing else 'assets-prepared; paused-before-full-render',
        new_generated_count=len(jobs)-len(missing),planned_generated_count=39,
        missing_asset_ids=missing,unresolved_card_ids=unresolved,
        new_code_glyph_count=2,reused_component_count=len(reused),
        planned_card_count=78,components=components,inspection_sheets=sheets,
        mechanical_warnings=warnings,prompt_file=rel(RAW/'actual-prompts.json'),
        prompt_sha256=digest(RAW/'actual-prompts.json'))
    if selection_path.exists():
        inventory['selection_file']=rel(selection_path)
        inventory['selection_sha256']=digest(selection_path)
    save_json(INVENTORY,inventory)
    gallery=''.join(f'<h2>{Path(p).stem}</h2><a href="{Path(p).name}"><img src="{Path(p).name}"></a>' for p in sheets)
    (WORK/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Tarot assets</title><style>body{background:#faebd7;color:#30251a;font:18px Georgia;margin:32px}img{max-width:100%;width:1440px}h2{margin-top:50px}</style><h1>Tarot asset review</h1>'+f'<p>{len(jobs)-len(missing)} of 39 new illustrations prepared, plus existing review assets and two new index glyphs. {len(missing)} illustrations remain. Full card rendering has not started.</p>'+gallery,encoding='utf-8')
    print(json.dumps(dict(prepared=len(jobs)-len(missing),missing=missing,glyphs=2,card_dependencies_resolved=78-len(unresolved),warnings=warnings),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-partial',action='store_true')
    args=parser.parse_args()
    main(args.allow_partial)
