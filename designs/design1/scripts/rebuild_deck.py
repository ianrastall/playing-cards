"""Deterministic deck rebuild from preserved artwork and generated components.

--prepare creates versioned components and the layout manifest.
--stage renders all 84 cards and review sheets without changing active cards.
--check validates the staged (or --active) deck against components and layout.
--apply promotes only a checked stage with unchanged preserved active inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / "sources/before-deck-rebuild-v1"
GENERATED = ROOT / "sources/generated/deck-rebuild-v1"
COMP = ROOT / "sources/components/poker/v1"
WORK = ROOT / "work/deck-rebuild-v1"
MANIFEST = ROOT / "docs/design/numeral-layout-v1.json"
REPORT = ROOT / "docs/design/poker-completion-v2-report.json"
SUITS = ("spades", "hearts", "diamonds", "clubs")
GROUND = (250, 235, 215)
SIZE = (750, 1050)
CENTER = (374.5, 524.5)
RADIUS = 3.5 / 25.4 * 300
LANCZOS = Image.Resampling.LANCZOS


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(im, path, **metadata):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = PngImagePlugin.PngInfo()
    meta.add_text("Rebuild", "deck-rebuild-v1")
    for key, value in metadata.items():
        meta.add_text(key, json.dumps(value, sort_keys=True))
    im.save(path, dpi=(300, 300), pnginfo=meta)


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def halfturn(im):
    return im.transpose(Image.Transpose.ROTATE_180)


def reciprocal(im):
    """Reuse upper pixels under a true half-turn, no interpolation."""
    a = np.array(im)
    h = a.shape[0]
    a[(h + 1)//2:] = a[:h//2][::-1, ::-1]
    if h % 2:
        row = a[h//2].astype(np.uint16)
        a[h//2] = ((row + row[::-1] + 1)//2).astype(np.uint8)
    return Image.fromarray(a)


@lru_cache(maxsize=8)
def silhouette(size):
    # Evaluate the physical circular corner in pixel-edge coordinates at 8x.
    w, h = size
    scale = 8
    yy, xx = np.ogrid[:h*scale, :w*scale]
    x, y = (xx+.5)/scale, (yy+.5)/scale
    dx = np.maximum(np.maximum(RADIUS-x, x-(w-RADIUS)), 0)
    dy = np.maximum(np.maximum(RADIUS-y, y-(h-RADIUS)), 0)
    inside = dx*dx + dy*dy <= RADIUS*RADIUS
    coverage = inside.reshape(h, scale, w, scale).mean(axis=(1, 3))
    return Image.fromarray(np.rint(coverage*255).astype(np.uint8))


def flood_region(binary, seed):
    im = Image.fromarray(np.where(binary, 255, 0).astype(np.uint8)).copy()
    if im.getpixel(seed) != 255:
        raise ValueError(f"Seed {seed} is not in the requested region")
    ImageDraw.floodfill(im, seed, 128)
    return np.array(im) == 128


def turquoise(im):
    a = np.array(im.convert("RGBA"))
    r, g, b, alpha = a.astype(np.int16).transpose(2, 0, 1)
    m = (g-r > 18) & (b-r > 18) & (g > 65) & (alpha > 128)
    if not m.any():
        raise ValueError("No jewel in component")
    # Transparent-generation edge specks are not the central jewel. Select its
    # connected component before calculating its bounds or chroma centroid.
    h,w=m.shape
    candidates=m.copy()
    candidates[:h//4]=False; candidates[3*h//4:]=False
    candidates[:,:w//4]=False; candidates[:,3*w//4:]=False
    if not candidates.any():
        raise ValueError("No jewel near component anchor")
    strength=np.minimum(g-r,b-r)*candidates
    sy,sx=np.unravel_index(np.argmax(strength),m.shape)
    m=flood_region(m,(int(sx),int(sy)))
    weight = np.minimum(g-r, b-r)*m
    y, x = np.indices(m.shape)
    center = ((weight*x).sum()/weight.sum(), (weight*y).sum()/weight.sum())
    ys, xs = np.nonzero(m)
    return center, (int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1))


def put_at(dest, sprite, point, anchor=None):
    anchor = anchor or ((sprite.width-1)/2, (sprite.height-1)/2)
    xy = (point[0]-anchor[0], point[1]-anchor[1])
    if any(abs(v-round(v)) > 1e-9 for v in xy):
        raise ValueError(f"Non-integral component placement: {xy}")
    dest.alpha_composite(sprite, tuple(round(v) for v in xy))


def layout_manifest():
    def p(x, y, angle=0):
        return dict(center=[x, y], rotation=angle)
    def rows(xs, ys):
        return [p(x, y, 0 if y < CENTER[1] else 180) for y in ys for x in xs]
    mid = CENTER[0]
    specs = {
        "ace": ([p(*CENTER)], [420, 570], "one-way"),
        "2": ([p(mid, 314.5), p(mid, 734.5, 180)], [230, 280], "two-way"),
        "3": ([p(mid, 284.5), p(*CENTER), p(mid, 764.5, 180)], [190, 220], "one-way-center"),
        "4": (rows([244.5, 504.5], [294.5, 754.5]), [190, 220], "two-way"),
        "5": (rows([244.5, 504.5], [294.5, 754.5])+[p(*CENTER)], [175, 205], "one-way-center"),
        "6": (rows([234.5, 514.5], [284.5, 764.5])+[p(234.5, 524.5), p(514.5, 524.5, 180)], [160, 190], "two-way"),
        "7": (rows([234.5, 514.5], [284.5, 764.5])+[p(234.5, 524.5), p(514.5, 524.5), p(mid, 404.5)], [135, 160], "one-way-offset"),
        "8": (rows([234.5, 514.5], [244.5, 424.5, 624.5, 804.5]), [145, 175], "two-way"),
        "9": (rows([224.5, mid, 524.5], [284.5, 764.5])+[p(224.5, 524.5), p(*CENTER), p(524.5, 524.5, 180)], [125, 175], "one-way-center"),
        "10": (rows([234.5, 514.5], [244.5, 424.5, 624.5, 804.5])+[p(mid, 334.5), p(mid, 714.5, 180)], [125, 155], "two-way"),
    }
    ranks = {}
    for rank, (points, bounds, policy) in specs.items():
        for i, point in enumerate(points):
            point["id"] = f"pip-{i+1}"
            point["z"] = i
        ranks[rank] = dict(pips=points, component_bounds=bounds, reversibility=policy,
                           expected_centroid=np.mean([v["center"] for v in points], axis=0).tolist())
    return dict(version=1, coordinate_basis="zero-based pixel centers", canvas=list(SIZE),
                center=list(CENTER), ground_rgb=list(GROUND), corner_radius_mm=3.5,
                dpi=300, ranks=ranks,
                seven_policy="Six side pips retain fixed rows. Offset seventh pip is intentional; its aggregate centroid is not the card anchor.",
                placement_tolerance_px=0, jewel_measurement_tolerance_px=0.000001)


def prepare_frame():
    plain = Image.open(GENERATED / "plain-frame-master.png").convert("RGB").resize(SIZE, LANCZOS)
    # A generated quarter supplies all perimeter ink. Reusing it by reflection
    # gives a centered aperture and continuous edges at the quadrant joins.
    a=np.array(plain)
    a[:,375:]=a[:,:375][:,::-1]
    a[525:]=a[:525][::-1]
    original=Image.fromarray(a)
    panel_source=Image.open(GENERATED / "frame-master.png").convert("RGB").resize(SIZE,LANCZOS)
    pa=np.array(panel_source)
    panel_pale=(pa[:,:,0]>225)&(pa[:,:,1]>210)&(pa[:,:,2]>180)
    panel=flood_region(panel_pale,(70,145))
    panel_alpha=Image.fromarray(np.uint8(panel)*255).filter(ImageFilter.MaxFilter(17))
    draw=ImageDraw.Draw(panel_alpha)
    draw.polygon([(54,215),(66,222),(72,212),(81,223),(91,218),
                  (94,233),(82,242),(76,260),(71,260),(65,244),(54,236)],fill=255)
    draw.polygon([(65,59),(73,48),(82,62),(82,70),(73,80),(63,70)],fill=255)
    panel_alpha=panel_alpha.filter(ImageFilter.GaussianBlur(.35))
    panel_sprite=panel_source.convert("RGBA")
    panel_sprite.putalpha(panel_alpha)
    original=original.convert("RGBA")
    original.alpha_composite(panel_sprite)
    original.alpha_composite(halfturn(panel_sprite))
    a=np.array(original.convert("RGB"))
    # Only connected flat-ground regions change. Botanical ink is retained.
    pale = (a[:,:,0] > 225) & (a[:,:,1] > 210) & (a[:,:,2] > 180)
    field = flood_region(pale, (375, 525))
    panels = flood_region(pale, (70, 145))
    panels |= panels[::-1,::-1]
    exterior = flood_region(pale, (375, 4))
    a[field | panels | exterior] = GROUND
    frame = Image.fromarray(a).convert("RGBA")
    frame.putalpha(silhouette(SIZE))
    # Matte edge stays within generated outline and cannot cover its gold rules.
    field_mask = Image.fromarray(np.uint8(field)*255)
    save(frame, COMP / "frame.png", source_sha256=digest(GENERATED / "plain-frame-master.png"),
         panel_source_sha256=digest(GENERATED / "frame-master.png"))
    save(field_mask, COMP / "field-mask.png")
    save(Image.fromarray(np.uint8(panels)*255), COMP / "panel-mask.png")
    save(silhouette(SIZE), COMP / "outline-mask.png")


def canonical_jewel():
    im = Image.open(GENERATED / "spades-master.png").convert("RGBA")
    _, box = turquoise(im)
    x0, y0, x1, y1 = box
    # Preserve the generated gold rim around the jewel, then remove directional
    # illumination by averaging it with its exact opposite. Centroid is exact.
    pad = max(3, round((x1-x0)*.15))
    crop = im.crop((x0-pad, y0-pad, x1+pad, y1+pad)).resize((64,64), LANCZOS)
    a = np.array(crop).astype(np.uint16)
    a = ((a+a[::-1,::-1]+1)//2).astype(np.uint8)
    yy, xx = np.indices((64,64))
    a[:,:,3] = np.rint(np.clip(32-np.hypot(xx-31.5,yy-31.5),0,1)*255).astype(np.uint8)
    jewel = Image.fromarray(a)
    save(jewel, COMP / "jewel-master.png")
    return jewel


def prepare_pip(suit, rank, spec, jewel):
    source = Image.open(GENERATED / f"{suit}-master.png").convert("RGBA")
    if source.getchannel("A").getextrema() != (0,255):
        raise ValueError(f"{suit}: generation must have genuine transparent alpha")
    # Ignore almost-transparent generation specks when determining the scale.
    alpha = np.array(source.getchannel("A"))
    bounds = Image.fromarray(np.uint8(alpha > 128)*255).getbbox()
    source = source.crop(bounds)
    maxw, maxh = spec["component_bounds"]
    factor = min(maxw/source.width, maxh/source.height)
    source = source.resize((round(source.width*factor), round(source.height*factor)), LANCZOS)
    (cx,cy), box = turquoise(source)
    # Component is registered once. Subsequent cards only use integer placement.
    extent_x = math.ceil(max(cx, source.width-1-cx)+8)
    extent_y = math.ceil(max(cy, source.height-1-cy)+8)
    outsize = (extent_x*2, extent_y*2)
    local = ((outsize[0]-1)/2, (outsize[1]-1)/2)
    registered = source.transform(outsize, Image.Transform.AFFINE,
                                  (1,0,cx-local[0],0,1,cy-local[1]),
                                  resample=Image.Resampling.BICUBIC)
    _, registered_box = turquoise(registered)
    # Cover the original cyan completely with one centered, reciprocal jewel.
    distance = max(abs(registered_box[0]-local[0]),abs(registered_box[2]-1-local[0]),
                   abs(registered_box[1]-local[1]),abs(registered_box[3]-1-local[1]))
    diameter = max(8, math.ceil(math.sqrt(2)*distance+3)*2)
    if diameter > min(maxw,maxh)*.25:
        raise ValueError(f"Implausible jewel diameter {suit}/{rank}: {diameter}")
    badge = jewel.resize((diameter, diameter), LANCZOS)
    # Resampling may break byte equality by one value; restore exact pairing.
    a = np.array(badge).astype(np.uint16)
    a = ((a+a[::-1,::-1]+1)//2).astype(np.uint8)
    a[:,:,3][a[:,:,3] > 240] = 255
    badge = Image.fromarray(a)
    put_at(registered, badge, local)
    center, _ = turquoise(registered)
    if np.max(np.abs(np.array(center)-local)) > 1e-6:
        save(registered, WORK / "debug-pip.png")
        save(badge, WORK / "debug-badge.png")
        raise ValueError(f"{suit}/{rank} jewel not exact: {center} vs {local}")
    path = COMP / f"pips/{suit}/{rank}.png"
    save(registered, path, anchor=local, master_sha256=digest(GENERATED/f"{suit}-master.png"))
    return dict(path=path.relative_to(ROOT).as_posix(), anchor=list(local),
                size=list(outsize), sha256=digest(path))


def make_indices():
    # Rasterize once, keep font dependence out of rendering and future exports.
    font_path = Path("C:/Windows/Fonts/timesbd.ttf")
    glyphs = {"spades":"♠", "hearts":"♥", "diamonds":"♦", "clubs":"♣"}
    for suit in SUITS:
        color = (151, 13, 21) if suit in ("hearts", "diamonds") else (10, 12, 12)
        for rank in ("ace", *map(str,range(2,11)), "jack", "queen", "king"):
            label = {"ace":"A","jack":"J","queen":"Q","king":"K"}.get(rank,rank)
            im = Image.new("RGBA", (64*4,140*4))
            draw = ImageDraw.Draw(im)
            font = ImageFont.truetype(str(font_path), (57 if rank=="10" else 65)*4)
            bbox = draw.textbbox((0,0),label,font=font)
            draw.text(((im.width-(bbox[2]-bbox[0]))/2-bbox[0],8*4-bbox[1]), label, font=font, fill=color)
            font = ImageFont.truetype(str(font_path),62*4)
            bbox = draw.textbbox((0,0),glyphs[suit],font=font)
            draw.text(((im.width-(bbox[2]-bbox[0]))/2-bbox[0],78*4-bbox[1]),glyphs[suit],font=font,fill=color)
            save(im.resize((64,140), LANCZOS), COMP/f"indices/{suit}/{rank}.png")


def prepare():
    COMP.mkdir(parents=True, exist_ok=True)
    prepare_frame()
    jewel = canonical_jewel()
    manifest = layout_manifest()
    for rank, spec in manifest["ranks"].items():
        spec["components"] = {suit:prepare_pip(suit,rank,spec,jewel) for suit in SUITS}
    make_indices()
    write_json(MANIFEST, manifest)
    print("Prepared shared frame, exact outline, indices, and 40 registered pip components")


def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def frame_for(size):
    frame = Image.open(COMP/"frame.png").convert("RGBA")
    field = Image.open(COMP/"field-mask.png").convert("L")
    panels = Image.open(COMP/"panel-mask.png").convert("L")
    if size != SIZE:
        ground = Image.new('RGBA', frame.size, GROUND+(255,))
        ground.alpha_composite(frame)
        frame = ground
        frame = frame.resize(size,LANCZOS)
        field = field.resize(size,LANCZOS)
        panels = panels.resize(size,LANCZOS)
        frame=reciprocal(frame)
        field=reciprocal(field)
        panels=reciprocal(panels)
    frame.putalpha(silhouette(size))
    return frame, field, panels


def composite_field(frame, artwork, field):
    return Image.composite(artwork,frame,field)


def numeral(suit,rank,manifest):
    frame, field, _ = frame_for(SIZE)
    layer = Image.new("RGBA",SIZE,GROUND+(255,))
    for pip in manifest["ranks"][rank]["pips"]:
        component = manifest["ranks"][rank]["components"][suit]
        sprite = Image.open(ROOT/component["path"]).convert("RGBA")
        if pip["rotation"] == 180:
            sprite = halfturn(sprite)
        put_at(layer,sprite,pip["center"])
    result = composite_field(frame,layer,field)
    return add_indices(result,suit,rank)


def add_indices(im,suit,rank):
    index = Image.open(COMP/f"indices/{suit}/{rank}.png").convert("RGBA")
    # Whole index group is an exact rotated counterpart, including spacing.
    layer = Image.new("RGBA",SIZE)
    layer.alpha_composite(index,(39,90))
    im.alpha_composite(layer)
    im.alpha_composite(halfturn(layer))
    return im


def centered_badge(im, point, diameter):
    jewel = Image.open(COMP/"jewel-master.png").resize((diameter,diameter), LANCZOS)
    jewel = reciprocal(jewel)
    a=np.array(jewel)
    a[:,:,3][a[:,:,3]>240]=255
    jewel=Image.fromarray(a)
    put_at(im,jewel,point)


def court(suit,rank):
    frame, field, _ = frame_for(SIZE)
    original = Image.open(BACKUP/f"cards/faces/french-suited/poker/{suit}/{rank}.png").convert("RGBA")
    # The legacy lower inner rule sat at y~959, inside the new symmetric field.
    # Fit only the illustrated field vertically around the fixed center so that
    # legacy rules stay outside the new aperture. The original portraits remain
    # source artwork; their old frame is never allowed to become a second rule.
    source=np.array(original)
    destination_y=np.arange(1050,dtype=float)
    source_y=np.where(destination_y<=CENTER[1],
                      CENTER[1]+(destination_y-CENTER[1])*(CENTER[1]-78)/(CENTER[1]-77),
                      CENTER[1]+(destination_y-CENTER[1])*(952-CENTER[1])/(972-CENTER[1]))
    source_y=np.clip(source_y,0,1049)
    y0=np.floor(source_y).astype(int); y1=np.minimum(y0+1,1049)
    weight=(source_y-y0)[:,None,None]
    original=Image.fromarray(np.rint(source[y0]*(1-weight)+source[y1]*weight).astype(np.uint8))
    # Preserve the existing portrait and its decorative field as a component.
    # The reusable central jewel covers the old dot, whose centroid only rounded
    # to the old target. Borders and indices come exclusively from shared assets.
    centered_badge(original,CENTER,14)
    result = composite_field(frame,original,field)
    return add_indices(result,suit,rank)


def back(format_name,color,size):
    from complete_poker import render_back
    return render_back(format_name,color,size)


def render_all(destination):
    from complete_poker import JOKERS, render_joker
    manifest=load_manifest()
    config=json.loads((ROOT/"deck.json").read_text(encoding="utf-8"))
    for suit in SUITS:
        for rank in (*manifest["ranks"],"jack","queen","king"):
            im = court(suit,rank) if rank in ("jack","queen","king") else numeral(suit,rank,manifest)
            im.putalpha(silhouette(SIZE))
            save(im,destination/f"faces/french-suited/poker/{suit}/{rank}.png",
                 manifest_sha256=digest(MANIFEST), frame_sha256=digest(COMP/"frame.png"),
                 center=CENTER, suit=suit,rank=rank)
    for format_name, spec in config["formats"].items():
        size=tuple(spec["back_pixels"])
        for color in config["back_colors"]:
            save(back(format_name,color,size),destination/f"backs/{format_name}/{color}.png",
                 center=[(size[0]-1)/2,(size[1]-1)/2],color=color)
    for variant in JOKERS:
        save(render_joker(variant),destination/f"faces/french-suited/poker/jokers/{variant}.png",
             center=CENTER,rank="joker",variant=variant,version=2)


def contact_sheet(paths,path,cols=4,thumb=(225,315)):
    rows=math.ceil(len(paths)/cols)
    sheet=Image.new("RGB",(cols*(thumb[0]+16)+16,rows*(thumb[1]+40)+16),(34,35,37))
    draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(paths):
        im=Image.open(p).convert("RGBA")
        im.thumbnail(thumb,LANCZOS)
        x=16+(i%cols)*(thumb[0]+16); y=16+(i//cols)*(thumb[1]+40)
        sheet.paste(im,(x+(thumb[0]-im.width)//2,y),im)
        draw.text((x,y+thumb[1]+6),f"{p.parent.name} / {p.stem}",fill=(245,236,221))
    save(sheet,path)


def previews(destination):
    contact_sheet([destination/f"faces/french-suited/poker/jokers/{variant}.png" for variant in ("black","red")],
                  WORK/"previews/jokers.png",2,(375,525))
    for rank in (*map(str,range(2,11)),"ace","jack","queen","king"):
        paths=[destination/f"faces/french-suited/poker/{suit}/{rank}.png" for suit in SUITS]
        contact_sheet(paths,WORK/f"previews/rank-{rank}.png")
    contact_sheet(sorted((destination/"backs").glob("*/*.png")),WORK/"previews/backs.png",5,(150,230))
    paths=[destination/f"faces/french-suited/poker/{suit}/{rank}.png"
           for rank in ("ace",*map(str,range(2,11)),"jack","queen","king") for suit in SUITS]
    contact_sheet(paths,WORK/"previews/all-faces.png",4,(150,210))
    for suit in SUITS:
        paths=[]
        for rank in ("3","10","king"):
            paths.extend([BACKUP/f"cards/faces/french-suited/poker/{suit}/{rank}.png",
                          destination/f"faces/french-suited/poker/{suit}/{rank}.png"])
        contact_sheet(paths,WORK/f"previews/before-after-{suit}.png",2)


def check(destination):
    from complete_poker import back_frame, JOKERS, validate_joker
    manifest=load_manifest()
    config=json.loads((ROOT/"deck.json").read_text(encoding="utf-8"))
    records=[]
    frame,field,panels=frame_for(SIZE)
    # Everything outside the field and the glyph/medallion ink is invariant.
    frame_array=np.array(frame)
    assert np.array_equal(frame_array,frame_array[::-1,::-1]),"Shared frame is not reciprocal"
    for suit in SUITS:
        for rank in (*manifest["ranks"],"jack","queen","king"):
            path=destination/f"faces/french-suited/poker/{suit}/{rank}.png"
            with Image.open(path) as im:
                assert im.size==SIZE and im.mode=="RGBA",path
                assert max(abs(v-300) for v in im.info["dpi"])<.01,path
                actual=np.array(im)
            assert np.array_equal(actual[:,:,3],np.array(silhouette(SIZE))),path
            glyph=Image.new("RGBA",SIZE)
            glyph.alpha_composite(Image.open(COMP/f"indices/{suit}/{rank}.png").convert("RGBA"),(39,90))
            ink=np.array(glyph)[:,:,3]>0
            ink|=ink[::-1,::-1]
            assert not np.any(ink & (np.array(panels)==0)),f"Index outside cartouche: {path}"
            invariant=(np.array(field)==0)&~ink
            assert np.array_equal(actual[invariant],frame_array[invariant]),f"Frame drift: {path}"
            expected=court(suit,rank) if rank in ("jack","queen","king") else numeral(suit,rank,manifest)
            expected.putalpha(silhouette(SIZE))
            assert np.array_equal(actual,np.array(expected)),f"Render mismatch: {path}"
            positions=[]
            if rank in manifest["ranks"]:
                spec=manifest["ranks"][rank]
                assert len(spec["pips"])==(1 if rank=="ace" else int(rank))
                comp=spec["components"][suit]
                assert digest(ROOT/comp["path"])==comp["sha256"]
                occupied=np.zeros((1050,750),dtype=bool)
                for pip in spec["pips"]:
                    assert pip["rotation"] in (0,180),(path,pip)
                    x,y=pip["center"]
                    sprite=Image.open(ROOT/comp["path"]).convert("RGBA")
                    if pip["rotation"]==180: sprite=halfturn(sprite)
                    layer=Image.new("RGBA",SIZE)
                    put_at(layer,sprite,pip["center"])
                    footprint=np.array(layer)[:,:,3]>128
                    assert not np.any(footprint&occupied),f"Overlapping pips: {path}"
                    assert not np.any(footprint&(np.array(field)<255)),f"Clipped pip: {path}"
                    occupied|=footprint
                    crop=Image.fromarray(actual).crop((int(x)-20,int(y)-20,int(x)+22,int(y)+22))
                    c,_=turquoise(crop)
                    measured=[c[0]+int(x)-20,c[1]+int(y)-20]
                    assert np.max(np.abs(np.array(measured)-pip["center"]))<1e-6,(path,pip,measured)
                    positions.append(measured)
                # Independent component count over the full field.
                from rebalance_numerals import jewel_components
                found=jewel_components(actual)
                assert len(found)==len(spec["pips"]),(path,len(found))
                if spec["reversibility"]=="two-way":
                    assert np.array_equal(actual,actual[::-1,::-1]),f"Card half-turn mismatch: {path}"
                    point_set={(tuple(p["center"]),p["rotation"]) for p in spec["pips"]}
                    for pip in spec["pips"]:
                        x,y=pip["center"]
                        counterpart=((749-x,1049-y),(pip["rotation"]+180)%360)
                        assert counterpart in point_set,(path,pip,"missing opposite")
                        w,h=comp["size"]
                        left=round(x-(w-1)/2); top=round(y-(h-1)/2)
                        crop=actual[top:top+h,left:left+w]
                        other=actual[1050-top-h:1050-top,750-left-w:750-left]
                        assert np.array_equal(crop,other[::-1,::-1]),f"Pip half-turn mismatch: {path}"
            else:
                crop=Image.fromarray(actual).crop((360,510,390,540))
                c,_=turquoise(crop)
                assert np.max(np.abs(np.array(c)+[360,510]-CENTER))<1e-6,(path,c)
            records.append(dict(path=path.relative_to(destination).as_posix(),sha256=digest(path),
                                frame_exact=True,outline_exact=True,jewel_centers=positions))
    for format_name,spec in config["formats"].items():
        size=tuple(spec["back_pixels"])
        for color in config["back_colors"]:
            path=destination/f"backs/{format_name}/{color}.png"
            actual=np.array(Image.open(path))
            assert actual.shape==(size[1],size[0],4),path
            assert np.array_equal(actual[:,:,3],np.array(silhouette(size))),path
            assert np.array_equal(actual,actual[::-1,::-1]),f"Back half-turn mismatch: {path}"
            _,mask=back_frame(size)
            common=(np.array(mask)==255)&(np.array(mask)[::-1,::-1]==255)
            assert np.array_equal(actual[common],actual[::-1,::-1][common]),f"Back pattern reversal: {path}"
            assert np.array_equal(actual,np.array(back(format_name,color,size))),path
            base,mask=back_frame(size)
            inv=np.array(mask)==0
            assert np.array_equal(actual[inv],np.array(base)[inv]),f"Back frame drift: {path}"
            records.append(dict(path=path.relative_to(destination).as_posix(),sha256=digest(path),
                                half_turn_exact=True,outline_exact=True,frame_exact=True,
                                center=[(size[0]-1)/2,(size[1]-1)/2]))
    for variant in JOKERS:
        path=destination/f"faces/french-suited/poker/jokers/{variant}.png"
        record=validate_joker(path,variant)
        record["path"]=path.relative_to(destination).as_posix()
        records.append(record)
    expected={r["path"] for r in records}
    actual={p.relative_to(destination).as_posix() for p in destination.rglob("*.png")}
    assert actual==expected,(actual^expected)
    report=dict(version=2,manifest_sha256=digest(MANIFEST),cards=records,checks_passed=True,
                count=len(records),visual_review="See versioned review record")
    write_json(REPORT,report)
    print(f"PASS rebuild: {len(records)} cards; fixed frames, outlines, individual jewels, exact paired rotations")
    return report


def apply():
    report=check(WORK/"cards")
    originals=json.loads((ROOT/"sources/before-poker-completion-v2/sha256.json").read_text())
    for item in report["cards"]:
        rel="cards/"+item["path"]
        active=ROOT/rel
        if active.exists() and digest(active) not in (originals.get(rel),item["sha256"]):
            raise ValueError(f"Active input changed since backup: {rel}")
    for item in report["cards"]:
        active=ROOT/"cards"/item["path"]
        active.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(WORK/"cards"/item["path"],active)
    from catalog import build_catalog
    write_json(ROOT/"catalog.json",build_catalog())
    check(ROOT/"cards")
    print("Promoted all checked cards and refreshed catalog")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    for flag in ("prepare","stage","check","apply"):
        group.add_argument("--"+flag,action="store_true")
    parser.add_argument("--active",action="store_true")
    args=parser.parse_args()
    config=json.loads((ROOT/'deck.json').read_text(encoding='utf-8'))
    if config.get('renderer')=='face-formats-v1' and not args.prepare:
        import expand_faces
        if args.stage: expand_faces.stage()
        elif args.check: expand_faces.check(ROOT/'cards' if args.active else expand_faces.WORK/'cards')
        elif args.apply: expand_faces.apply()
        return
    if args.prepare: prepare()
    elif args.stage:
        render_all(WORK/"cards")
        previews(WORK/"cards")
        print("Staged 84 cards and review sheets")
    elif args.check: check(ROOT/"cards" if args.active else WORK/"cards")
    elif args.apply: apply()


if __name__=="__main__":
    main()
