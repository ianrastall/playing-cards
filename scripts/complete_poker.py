"""Prepare a panel-free back template and two component-rendered Jokers.

Run --prepare, then use rebuild_deck.py --stage / --check / --apply.
Artwork generation is separate; these commands only use saved source files.
"""
from __future__ import annotations

import argparse
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import rebuild_deck as base

COMP = base.ROOT / 'sources/components/poker/v2'
GENERATED = base.ROOT / 'sources/generated/poker-completion-v2'
JOKERS = ('black', 'red')


def prepare_back():
    source = base.GENERATED / 'plain-frame-master.png'
    a = np.array(Image.open(source).convert('RGB').resize(base.SIZE, base.LANCZOS))
    a[:,375:] = a[:,:375][:,::-1]
    a[525:] = a[:525][::-1]
    pale = (a[:,:,0]>225)&(a[:,:,1]>210)&(a[:,:,2]>180)
    field = base.flood_region(pale,(375,525))
    exterior = base.flood_region(pale,(375,4))
    a[field|exterior] = base.GROUND
    frame = Image.fromarray(a).convert('RGBA')
    frame.putalpha(base.silhouette(base.SIZE))
    base.save(frame,COMP/'back-frame.png',source_sha256=base.digest(source),version=2)
    base.save(Image.fromarray(np.uint8(field)*255),COMP/'back-field-mask.png',version=2)
    assert np.array_equal(np.array(frame),np.array(frame)[::-1,::-1])
    assert field[145,110] and field[905,639], 'Unexpected index-panel holes'


@lru_cache(maxsize=8)
def back_frame(size):
    frame=Image.open(COMP/'back-frame.png').convert('RGBA')
    field=Image.open(COMP/'back-field-mask.png').convert('L')
    if size != base.SIZE:
        ground=Image.new('RGBA',frame.size,base.GROUND+(255,))
        ground.alpha_composite(frame)
        frame=ground
        frame=base.reciprocal(frame.resize(size,base.LANCZOS))
        field=base.reciprocal(field.resize(size,base.LANCZOS))
    frame.putalpha(base.silhouette(size))
    return frame,field


def render_back(format_name,color,size):
    from recolor_card_backs import DOT_PATCH_CENTERS, recolor
    frame,field=back_frame(size)
    original=Image.open(base.BACKUP/f'cards/backs/{format_name}/prussian-blue.png').convert('RGBA')
    w,h=size
    target=((w-1)/2,(h-1)/2)
    cx,cy=DOT_PATCH_CENTERS[format_name]
    crop=np.array(original)[cy-5:cy+6,cx-5:cx+6,:3].astype(float)
    r,g,b=crop.transpose(2,0,1)
    weight=np.maximum(r-g-25,0)*((r-b)>45)
    yy,xx=np.indices(weight.shape)
    if weight.sum():
        cx=cx-5+(xx*weight).sum()/weight.sum()
        cy=cy-5+(yy*weight).sum()/weight.sum()
    zoom=1.025
    artwork=original.transform(size,Image.Transform.AFFINE,
                               (1/zoom,0,cx-target[0]/zoom,0,1/zoom,cy-target[1]/zoom),
                               Image.Resampling.BICUBIC)
    artwork=base.reciprocal(artwork)
    if color != 'prussian-blue':
        artwork=Image.fromarray(recolor(np.array(artwork),color)[0])
    result=base.composite_field(frame,artwork,field)
    result.putalpha(base.silhouette(size))
    return result


def joker_index(variant):
    scale=4
    im=Image.new('RGBA',(64*scale,140*scale))
    draw=ImageDraw.Draw(im)
    color=(151,13,21) if variant=='red' else (10,12,12)
    font=ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf',24*scale)
    for i,letter in enumerate('JOKER'):
        box=draw.textbbox((0,0),letter,font=font)
        x=(im.width-(box[2]-box[0]))/2-box[0]
        y=(5+i*23)*scale-box[1]
        draw.text((x,y),letter,font=font,fill=color)
    return im.resize((64,140),base.LANCZOS)


def prepare_jokers():
    for variant in JOKERS:
        path=GENERATED/f'joker-{variant}-master.png'
        source=Image.open(path).convert('RGBA')
        if source.getchannel('A').getextrema() != (0,255):
            raise ValueError(f'Joker {variant} requires a transparent master')
        alpha=np.array(source)[:,:,3]
        bounds=Image.fromarray(np.uint8(alpha>128)*255).getbbox()
        sprite=source.crop(bounds)
        factor=min(450/sprite.width,420/sprite.height)
        sprite=sprite.resize((round(sprite.width*factor),round(sprite.height*factor)),base.LANCZOS)
        # Even dimensions allow an exact half-pixel anchor with integer placement.
        canvas=Image.new('RGBA',(sprite.width+(sprite.width%2),sprite.height+(sprite.height%2)))
        canvas.alpha_composite(sprite,(0,0))
        base.save(canvas,COMP/f'joker-{variant}-upright.png',source_sha256=base.digest(path),version=2)
        base.save(joker_index(variant),COMP/f'joker-{variant}-index.png',version=2)
    # A floral center component bridges the paired waist flourishes.
    sprite=Image.open(base.COMP/'pips/spades/ace.png').convert('RGBA')
    x,y=(sprite.width-1)/2,(sprite.height-1)/2
    rosette=sprite.crop((round(x-38.5),round(y-38.5),round(x+39.5),round(y+39.5)))
    rosette=rosette.resize((60,60),base.LANCZOS)
    yy,xx=np.indices((60,60))
    rosette.putalpha(Image.fromarray(np.rint(np.clip(29.5-np.hypot(xx-29.5,yy-29.5),0,1)*255).astype(np.uint8)))
    rosette=base.reciprocal(rosette)
    base.centered_badge(rosette,(29.5,29.5),14)
    base.save(rosette,COMP/'joker-center-rosette.png',version=2)


def render_joker(variant):
    frame,field,_=base.frame_for(base.SIZE)
    art=Image.new('RGBA',base.SIZE,base.GROUND+(255,))
    upper=Image.new('RGBA',base.SIZE)
    sprite=Image.open(COMP/f'joker-{variant}-upright.png').convert('RGBA')
    base.put_at(upper,sprite,(374.5,302.5))
    art.alpha_composite(upper)
    art.alpha_composite(base.halfturn(upper))
    base.put_at(art,Image.open(COMP/'joker-center-rosette.png').convert('RGBA'),base.CENTER)
    result=base.composite_field(frame,art,field)
    indices=Image.new('RGBA',base.SIZE)
    indices.alpha_composite(Image.open(COMP/f'joker-{variant}-index.png').convert('RGBA'),(39,90))
    result.alpha_composite(indices)
    result.alpha_composite(base.halfturn(indices))
    result.putalpha(base.silhouette(base.SIZE))
    return result


def validate_joker(path,variant):
    im=Image.open(path)
    assert im.size==base.SIZE and im.mode=='RGBA',path
    actual=np.array(im)
    assert np.array_equal(actual,np.array(render_joker(variant))),path
    assert np.array_equal(actual,actual[::-1,::-1]),f'Joker is not reversible: {path}'
    assert np.array_equal(actual[:,:,3],np.array(base.silhouette(base.SIZE))),path
    frame,field,panels=base.frame_for(base.SIZE)
    glyph=Image.new('RGBA',base.SIZE)
    glyph.alpha_composite(Image.open(COMP/f'joker-{variant}-index.png').convert('RGBA'),(39,90))
    ink=np.array(glyph)[:,:,3]>0
    ink|=ink[::-1,::-1]
    assert not np.any(ink&(np.array(panels)==0)),path
    invariant=(np.array(field)==0)&~ink
    assert np.array_equal(actual[invariant],np.array(frame)[invariant]),path
    center,_=base.turquoise(im.crop((355,505,395,545)))
    assert np.max(np.abs(np.array(center)+[355,505]-base.CENTER))<1e-6,(path,center)
    sprite=Image.open(COMP/f'joker-{variant}-upright.png').convert('RGBA')
    layer=Image.new('RGBA',base.SIZE)
    base.put_at(layer,sprite,(374.5,302.5))
    footprint=np.array(layer)[:,:,3]>128
    assert not np.any(footprint&(np.array(field)<255)),f'Clipped Joker: {path}'
    assert not np.any(footprint&footprint[::-1,::-1]),f'Overlapping Joker portraits: {path}'
    return dict(path=path.as_posix(),sha256=base.digest(path),center=list(base.CENTER),
                half_turn_exact=True,frame_exact=True,outline_exact=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true',required=True)
    args=parser.parse_args()
    if args.prepare:
        COMP.mkdir(parents=True,exist_ok=True)
        prepare_back()
        prepare_jokers()
        files={p.relative_to(base.ROOT).as_posix():base.digest(p) for p in COMP.glob('*.png')}
        base.write_json(base.ROOT/'docs/design/poker-completion-v2-components.json',
                        dict(version=2,center=list(base.CENTER),files=files,
                             joker_upper_center=[374.5,302.5],joker_lower_center=[374.5,746.5]))
        print('Prepared dedicated panel-free back template and two Joker components')


if __name__=='__main__':
    main()
