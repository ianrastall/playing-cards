"""Build and verify design1-poker.zip from the active catalog, without generation.

Root: native backs/ and faces/. Print: clean bleed and separate blue-guide files.
All print dimensions are exact at 600 ppi; artwork retains its native 300 ppi detail.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/releases'
PACKAGE=OUT/'design1-poker'
ZIP=OUT/'design1-poker.zip'
GROUND=(250,235,215)
TRIM=(750,1050)
PRINT_DPI=600
PRINT_TRIM=(1500,2100)
BLEED=75
GUTTER=75
BLEED_SIZE=(1650,2250)
GUIDE_SIZE=(1800,2400)
BLUE=(160,193,222)
SRGB=(ROOT/'sources/components/print/srgb.icc').read_bytes()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def opaque_native(im):
    im=im.convert('RGBA')
    ground=Image.new('RGBA',im.size,GROUND+(255,))
    return Image.alpha_composite(ground,im).convert('RGB')


def print_images(native):
    # An exact 2x pixel replication changes the density container, not the art.
    # Original trim pixels can be recovered byte-for-byte after compositing alpha.
    art=opaque_native(native).resize(PRINT_TRIM,Image.Resampling.NEAREST)
    clean=Image.new('RGB',BLEED_SIZE,GROUND)
    clean.paste(art,(BLEED,BLEED))
    guide=Image.new('RGB',GUIDE_SIZE,'white')
    guide.paste(clean,(GUTTER,GUTTER))
    draw=ImageDraw.Draw(guide)
    left=top=BLEED+GUTTER
    right=left+PRINT_TRIM[0]
    bottom=top+PRINT_TRIM[1]
    # One-pixel faint blue rounded die line, and short crop marks only in slug.
    radius=3.5/25.4*PRINT_DPI
    draw.rounded_rectangle((left,top,right-1,bottom-1),radius=radius,outline=BLUE,width=1)
    for x in (left,right):
        draw.line((x,20,x,60),fill=BLUE,width=2)
        draw.line((x,GUIDE_SIZE[1]-60,x,GUIDE_SIZE[1]-20),fill=BLUE,width=2)
    for y in (top,bottom):
        draw.line((20,y,60,y),fill=BLUE,width=2)
        draw.line((GUIDE_SIZE[0]-60,y,GUIDE_SIZE[0]-20,y),fill=BLUE,width=2)
    return clean,guide


def release_name(asset):
    if asset['side']=='back':
        return f"backs/{asset['color']}.png"
    if asset['rank']=='joker':
        return f"faces/joker-{asset['color_variant']}.png"
    return f"faces/{asset['suit']}-{asset['rank']}.png"


def readme():
    return '''# Design 1 - complete poker deck

This release contains **54 faces** (52 suited cards and two Jokers) and **five
alternative backs**. Choose one back color for all 54 cards in a physical deck.
The five backs are alternatives, not five additional faces. The package contains
59 unique card images, each supplied in three versions: 177 PNG files in total.

## Directory guide

```text
README.md
LICENSE
manifest.json
SHA256SUMS.txt
backs/                         5 native trim-size PNGs
faces/                        54 native trim-size PNGs, no suit subfolders
print/bleed/backs/              5 clean opaque PNGs with bleed
print/bleed/faces/             54 clean opaque PNGs with bleed
print/guides/backs/             5 padded proofs with faint blue cut guides
print/guides/faces/            54 padded proofs with faint blue cut guides
```

Native face filenames include the suit and rank, such as `spades-ace.png` and
`hearts-10.png`. The unsuited cards are `joker-black.png` and `joker-red.png`.
Back colors are Lamp Black, Madder Lake, Manganese Violet, Prussian Blue, and
Verdigris. These are pigment-inspired digital color names, not ink formulas.
Use `manifest.json` for exact inventory, ordering, source hashes, and dimensions.

## Trim, centers, and corner shape

The finished card is **2.5 x 3.5 inches (63.5 x 88.9 mm)**, portrait, 5:7 ratio.
Native files are **750 x 1050 pixels at nominal 300 ppi**, with RGBA transparency.
The outer rounded-corner radius is **3.5 mm**, approximately 41.3386 native pixels.
One antialiased silhouette mask is shared by every poker card.

The exact center is (374.5, 524.5) in zero-based pixel-center coordinates, or
(375, 525) measured from the outer canvas edges. The central jewel is registered
there when present. A rank without a central pip has the same virtual anchor;
it does not gain an extra pip. Seven intentionally has an offset pip and thus
a pip average above center. This does not shift its frame or canvas anchor.

For software, preserve the original alpha channel and aspect ratio. Use the
same display bounds for every card. Do not add an independent corner-radius
clip, automatically crop transparent margins, or scale cards individually.

## Clean files for print preparation: print/bleed

These files are **1650 x 2250 pixels at 600 ppi**, corresponding to an exact
**2.75 x 3.75 inch** canvas. The trim rectangle is **1500 x 2100 pixels**, inset
**75 pixels (0.125 inch / 3.175 mm)** from every edge. Using half-open pixel-edge
coordinates, its bounds are **[75, 75, 1575, 2175]**. The trim center is at
(825, 1125) in that edge-coordinate system.

This 600-ppi container uses exact 2x pixel replication of the native 300-ppi
artwork. It does not add image detail. It allows an exact 1/8-inch bleed without
introducing a 37.5-pixel placement offset into a 300-ppi image. Native trim
pixels are preserved exactly after alpha is composited over antique white.

Print PNGs are opaque RGB with an embedded sRGB profile. The background and
bleed are antique white **#FAEBD7 / RGB (250, 235, 215)**. Rounded transparent
corner areas are also filled with that ground. A printer cuts/rounds the stock;
the production file is a full rectangular image, with background extending
beyond the intended cut. Bleed is added outside trim, without shrinking the
card illustration. No new image generation is involved in print preparation.

There are **no blue guides, crop marks, registration targets, or page gutters**
in the clean bleed files. Submit this clean set when your printer accepts this
trim and bleed specification, or adapt it to the printer's actual template.
The artwork's own gold/beaded frame and dark outlines remain part of the art.

## Faint blue cut-guide proofs: print/guides

These files are **1800 x 2400 pixels at 600 ppi**, or **3 x 4 inches**. Each
contains the clean bleed image plus a **75-pixel white slug/gutter** outside
every bleed edge. Therefore the trim starts **150 pixels (0.25 inch)** from
the image edge. Trim bounds are **[150, 150, 1650, 2250]** in pixel-edge
coordinates; the bleed bounds are **[75, 75, 1725, 2325]**.

A faint blue rounded outline indicates the nominal trim and 3.5 mm corner
radius. It is 1 pixel wide at 600 ppi (0.12 point), RGB (160, 193, 222).
Short blue crop marks in the outer white slug align to the straight trim edges;
they are 2 pixels wide (0.24 point). Raster outlines are visual cutting aids,
not certified die tooling: use the numerical trim dimensions above as authority.

These are **proof/manual-cutting files**. Their blue pixels will print. Do not
upload this guide set as ordinary final production artwork. The separate clean
set makes it unnecessary to erase guide lines from an illustration.

## Safe area, gutters, and printer adaptation

Use an initial critical-content safe area of **1/8 inch inside trim**: 75 pixels
at 600 ppi. In clean bleed coordinates this is **[150, 150, 1500, 2100]**, or
2.25 x 3.25 inches. This is a planning inset, not a guarantee of a particular
printer's tolerances. Decorative borders intentionally extend outside it.
The narrow ornamental frame makes cutting/registration variation visible;
digital pixel alignment cannot eliminate physical print drift.

**Bleed** is printed background beyond a cut. **Gutter** is spacing between
cards on a sheet. **Slug** is extra area outside bleed for marks. This release
contains individual card images, not imposed sheets. For a sheet with separate
1/8-inch bleeds, use at least **1/4 inch between adjacent trim edges** so the
two bleeds fit without overlap; add space if the printer's marks or equipment
require it. The guide files include a further 1/8-inch slug outside each bleed.

Printer upload dimensions, corner dies, tolerances, and color workflows vary.
For example, MPC's published poker image guide uses 822 x 1122 pixels with
36-pixel bleed margins at 300 dpi, which differs from this package's exact
1/8-inch profile. Do not force-fit one specification into another. Render a
different surrounding canvas from the native trim images if a selected printer
requires different margins. Avoid scaling the card's trim artwork to compensate.

These PNGs are not PDF/X files or a CMYK press package. Use the selected printer's
ICC/output profile if conversion is requested. No particular stock thickness,
coating, duplex-feed direction, sheet size, or factory cutting tolerance is
assumed here. Print at actual physical size (100%), not 'fit to page'. A measured
proof is useful before manufacturing because every physical workflow differs.

Printer references checked September 17, 2026:

- [The Game Crafter templates](https://help.thegamecrafter.com/article/39-templates)
  describes RGB uploads, trim/safe areas, drift, and removing cut-guide layers.
- [The Game Crafter bleed](https://help.thegamecrafter.com/article/391-bleed)
  explains background extension past the cut.
- [MPC image-upload tips](https://www.makeplayingcards.com/pops/faq-photo.html)
  gives its own poker dimensions and bleed/safe-area pixel margins.

## Front/back pairing and artwork

For one complete deck, print each of the 54 faces once and the chosen back
54 times. Do not print all five back designs as if they belonged to one
uniform-backed deck. Keep front and back trim centers coincident, with no
individual-card rescaling. These files contain no imposed duplex ordering;
the printer determines sheet order and feed/flip behavior.

The dedicated back template has uninterrupted ornament and no designation
cartouches. Both Jokers are two-way illustrated jesters with opposing JOKER
indices. All backs, both Jokers, and numeral ranks 2, 4, 6, 8, and 10 have
pixel-exact half-turn symmetry. Odd numeral ranks intentionally have one-way
pips. Courts retain independently painted opposing poses with common geometry.

## Verification and reproduction

`SHA256SUMS.txt` covers every other file in this archive. `manifest.json` maps
the 59 unique assets to all three variants and records trim/bleed geometry.
The ZIP is deterministic for the same source files and packaging script.
No code needs to run to use the images.

In the source repository, reproduce the archive with:

```text
python scripts/rebuild_deck.py --check --active
python scripts/catalog.py --check
python scripts/package_poker.py --build
python scripts/package_poker.py --check
```

Original artwork and intermediate rebuild inputs are preserved in the source
repository. The release excludes those working files and non-poker formats.
Repository: [ianrastall/playing-cards](https://github.com/ianrastall/playing-cards).
See the included MIT `LICENSE`. This archive is prepared for a GitHub release;
building it does not publish a release or upload files anywhere.
'''


def build():
    from catalog import build_catalog
    current=build_catalog()
    saved=json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
    assert current==saved,'Catalog is stale'
    assets=[a for a in saved['assets'] if a['format']=='poker']
    assert len(assets)==59 and sum(a['side']=='face' for a in assets)==54
    names={release_name(a) for a in assets}
    assert len(names)==59
    PACKAGE.mkdir(parents=True,exist_ok=True)
    records=[]
    for order,asset in enumerate(assets,1):
        name=release_name(asset)
        src=ROOT/asset['path']
        target=PACKAGE/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,target)
        with Image.open(src) as im:
            assert im.size==TRIM and im.mode=='RGBA'
            clean,guide=print_images(im)
        variants={"native":name,"bleed":'print/bleed/'+name,"guides":'print/guides/'+name}
        for label,im in (('bleed',clean),('guides',guide)):
            p=PACKAGE/variants[label]
            p.parent.mkdir(parents=True,exist_ok=True)
            im.save(p,dpi=(600,600),icc_profile=SRGB)
        records.append(dict(order=order,id=asset['id'],source_path=asset['path'],
                            source_sha256=asset['sha256'],files=variants))
    (PACKAGE/'README.md').write_text(readme(),encoding='utf-8',newline='\n')
    shutil.copy2(ROOT/'LICENSE',PACKAGE/'LICENSE')
    manifest=dict(version=1,name='design1-poker',unique_assets=59,faces=54,backs=5,
                  png_count=177,trim_inches=[2.5,3.5],trim_mm=[63.5,88.9],corner_radius_mm=3.5,
                  native=dict(pixels=list(TRIM),ppi=300,mode='RGBA'),
                  bleed=dict(pixels=list(BLEED_SIZE),ppi=600,mode='RGB',margin_pixels=75,
                             trim_pixel_edges=[75,75,1575,2175],bleed_inches=.125),
                  guides=dict(pixels=list(GUIDE_SIZE),ppi=600,mode='RGB',slug_pixels=75,
                              trim_pixel_edges=[150,150,1650,2250],proof_only=True),
                  files=records)
    (PACKAGE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    expected={f for r in records for f in r['files'].values()}|{'README.md','LICENSE','manifest.json','SHA256SUMS.txt'}
    actual={p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob('*') if p.is_file()}
    assert not (actual-expected),f'Unexpected release files: {actual-expected}'
    hashes=''.join(f'{sha(PACKAGE/name)}  {name}\n' for name in sorted(expected-{'SHA256SUMS.txt'}))
    (PACKAGE/'SHA256SUMS.txt').write_text(hashes,encoding='utf-8')
    with zipfile.ZipFile(ZIP,'w') as archive:
        for name in sorted(expected):
            info=zipfile.ZipInfo(name,date_time=(2026,9,17,0,0,0))
            info.compress_type=zipfile.ZIP_STORED if name.endswith('.png') else zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            archive.writestr(info,(PACKAGE/name).read_bytes())
    (OUT/'design1-poker.zip.sha256').write_text(f'{sha(ZIP)}  {ZIP.name}\n',encoding='ascii')
    check()
    print(f'Created {ZIP} ({ZIP.stat().st_size/1024/1024:.1f} MiB)')


def check():
    manifest=json.loads((PACKAGE/'manifest.json').read_text())
    assert manifest['png_count']==177 and len(manifest['files'])==59
    hash_lines=(PACKAGE/'SHA256SUMS.txt').read_text().splitlines()
    hashes={line.split('  ',1)[1]:line.split('  ',1)[0] for line in hash_lines}
    with zipfile.ZipFile(ZIP) as archive:
        assert archive.testzip() is None,'ZIP CRC failure'
        assert len(archive.namelist())==len(set(archive.namelist()))==181
        assert set(archive.namelist())==set(hashes)|{'SHA256SUMS.txt'}
        for name,expected in hashes.items():
            assert sha(PACKAGE/name)==expected,(name,'Disk hash mismatch')
            assert hashlib.sha256(archive.read(name)).hexdigest()==expected,(name,'ZIP hash mismatch')
    for record in manifest['files']:
        native_path=PACKAGE/record['files']['native']
        assert sha(native_path)==record['source_sha256']
        assert sha(ROOT/record['source_path'])==record['source_sha256'],'Active source changed'
        with Image.open(native_path) as native:
            assert native.size==TRIM and native.mode=='RGBA'
            expected=opaque_native(native).resize(PRINT_TRIM,Image.Resampling.NEAREST)
        with Image.open(PACKAGE/record['files']['bleed']) as clean:
            assert clean.size==BLEED_SIZE and clean.mode=='RGB'
            assert max(abs(d-600) for d in clean.info['dpi'])<.01
            assert clean.info.get('icc_profile'),'Missing sRGB profile'
            assert np.array_equal(np.array(clean.crop((75,75,1575,2175))),np.array(expected)),record['id']
            a=np.array(clean)
            assert np.all(a[:75]==GROUND) and np.all(a[-75:]==GROUND)
            assert np.all(a[:,:75]==GROUND) and np.all(a[:,-75:]==GROUND)
        with Image.open(PACKAGE/record['files']['guides']) as guide:
            assert guide.size==GUIDE_SIZE and guide.mode=='RGB'
            assert guide.getpixel((900,150))==BLUE,'Missing trim guide'
            assert guide.getpixel((150,30))==BLUE,'Missing crop mark'
    expected_zip_hash=(OUT/'design1-poker.zip.sha256').read_text().split()[0]
    assert sha(ZIP)==expected_zip_hash
    print('PASS package: 59 unique cards, 177 PNGs; pixels, margins, guides, DPI, profiles, and ZIP hashes verified')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--build',action='store_true')
    group.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.build: build()
    else: check()


if __name__=='__main__':
    main()
