"""Build/verify all six Design 1 v1.1 release ZIPs, without publishing.

python scripts/package_decks.py --build --all
python scripts/package_decks.py --check --format jumbo
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile

import numpy as np
from PIL import Image

import package_poker as poker
from catalog import build_catalog

ROOT=poker.ROOT
OUT=poker.OUT
FORMATS=('poker','jumbo','travel','bridge','european-standard','tarot')
RELEASE_VERSION='1.1'


def geometry(fmt):
    if fmt not in FORMATS:
        raise ValueError(f'Unknown release format: {fmt}')
    spec=json.loads((ROOT/'deck.json').read_text(encoding='utf-8'))['formats'][fmt]
    native=spec['back_pixels']
    trim=[n*2 for n in native]
    return dict(native=native,trim=trim,inches=spec['trim_inches'],
                bleed=[n+150 for n in trim],guides=[n+300 for n in trim],
                bleed_trim=[75,75,75+trim[0],75+trim[1]],
                guide_trim=[150,150,150+trim[0],150+trim[1]])


def readme(fmt,g):
    w,h=g['inches'];nw,nh=g['native'];pw,ph=g['trim'];bw,bh=g['bleed'];gw,gh=g['guides']
    if fmt == 'tarot':
        face_summary = '''78 faces: 40 numbered suit cards, 16 courts, and 22 trumps; plus five
alternative backs. Choose one back color for a physical deck. There are 83
unique images, each supplied in native, clean-bleed, and cut-guide versions:
249 PNGs total.'''
        face_notes = '''The four suits are Swords, Batons, Cups, and Coins. Courts use Page,
Knight, Queen, and King. Trumps run from 0 The Fool through 21 The World.
Faces use paired side indices; court and trump art is upright. Swords, Batons,
and trumps use Lamp Black frames; Cups and Coins use Madder Lake.'''
    else:
        face_summary = '''54 faces (52 suited cards and two Jokers), plus five alternative backs.
Choose one back color and use it for every face in a physical deck.
59 unique cards, each supplied in three versions: 177 PNGs total.'''
        face_notes = '''Jokers are `joker-black.png` and `joker-red.png`; they are not a fifth suit.
Face frames use Lamp Black for spades/clubs and the black Joker, Madder Lake for
hearts/diamonds and the red Joker.'''
    cx,cy=(nw-1)/2,(nh-1)/2
    return f'''# Design 1 v{RELEASE_VERSION} — {fmt.replace('-', ' ').title()}

{face_summary}

## Files

- `faces/`: original native face PNGs with descriptive filenames.
- `backs/`: five native back PNGs.
- `print/bleed/faces/` and `print/bleed/backs/`: clean printing files.
- `print/guides/faces/` and `print/guides/backs/`: separate cutting proofs.
- `manifest.json`: source IDs, hashes, dimensions, and variant mapping.
- `SHA256SUMS.txt`: hashes of every other packaged file.
- `LICENSE`: repository MIT license.

{face_notes}
Backs are Lamp Black, Madder Lake, Manganese Violet, Prussian Blue and Verdigris.
Back frames follow those back palettes.
These names describe digital pigment-inspired colors, not physical ink formulas.

## Native geometry

Trim: **{w:g} x {h:g} inches**, or {w*25.4:g} x {h*25.4:g} mm.
Native images: **{nw} x {nh} pixels**, nominal 300 ppi, RGBA.
Native files are copied byte-for-byte from the checked collection.
Center: ({cx:g}, {cy:g}) in zero-based pixel-center coordinates;
({nw/2:g}, {nh/2:g}) measured from the outside canvas edges.
Corner radius: 3.5 mm. Preserve the supplied alpha for software; do not crop
transparent margins or apply a second independent corner-radius clip.

{'European Standard artwork is resized from the component-built Bridge cards. Interpolation may introduce single-level differences between rotated pairs.' if fmt=='european-standard' else 'Faces are assembled from shared source components at this format size, not resized from flattened cards.'}

## Clean bleed files

Canvas: **{bw} x {bh} pixels at 600 ppi** ({bw/600:g} x {bh/600:g} inches).
Trim pixels: {pw} x {ph}; exact trim bounds {g['bleed_trim']}.
Bounds are half-open pixel-edge coordinates: left, top, right, bottom.
Each edge has exactly 75 pixels = 1/8 inch = 3.175 mm of antique-white bleed.
Trim artwork is reproduced by exact 2x pixel replication, adding no new detail.
Alpha is composited onto #FAEBD7 before printing. Files are opaque RGB with
an embedded sRGB profile. Clean files contain no blue guides or crop marks.
Bleed extends the ground outside the card; it does not shrink the artwork.

## Blue cut-guide proofs

Canvas: **{gw} x {gh} pixels at 600 ppi** ({gw/600:g} x {gh/600:g} inches).
A further 75-pixel white slug surrounds the clean bleed image.
Trim bounds: {g['guide_trim']}. The trim starts 150 pixels from each outer edge.
Faint blue rounded cut outlines (3.5 mm radius) and crop marks are included.
Blue pixels will print: these are separate proof/manual-cutting files, not
ordinary final printer uploads. The outline is 1 pixel wide at 600 ppi;
crop marks are 2 pixels wide and stay in the outer slug.

## Printing and pairing

Place using physical trim dimensions, not inferred PNG density. Print at 100%
actual size. Align front/back trim centers and use identical scale for all
cards. The archive supplies individual artworks, not imposed duplex sheets.
Printer-specific feed direction and page ordering remain separate choices.

Bleed is background beyond trim; gutter is space between cards on a sheet;
slug is the outside area for marks. Adjacent trims need at least 1/4 inch
between them to accommodate separate 1/8-inch bleeds without overlap.
An initial critical-content planning inset is 1/8 inch inside trim (75 pixels
at 600 ppi); ornamental borders extend outside this inset. Fine borders make
physical cutting drift visible. Check the selected printer's actual template,
corner die, color profile, and safe area. These are general print-preparation
PNGs, not vendor-certified sheets, CMYK separations, or PDF/X files.

## Reproduction

```text
python scripts/package_decks.py --build --format {fmt}
python scripts/package_decks.py --check --format {fmt}
```

The package checker verifies native bytes against current source assets,
exact print trim pixels, bleed/slug geometry, guides, density, profiles,
complete inventory, and SHA-256 hashes on disk and inside the ZIP.
ZIP generation is deterministic for the same sources and script.
Building publishes nothing. Source and working files are excluded.

Repository: https://github.com/ianrastall/playing-cards
'''


def release_name(asset):
    if asset['side'] == 'face' and asset.get('system') == 'tarot':
        if asset['arcana'] == 'major':
            return f"faces/trumps/{asset['number']:02d}-{asset['slug']}.png"
        return f"faces/{asset['suit']}/{asset['rank']}.png"
    return poker.release_name(asset)


def release_paths(fmt):
    stem=f'design1-v{RELEASE_VERSION}-{fmt}'
    return OUT/stem,OUT/f'{stem}.zip',OUT/f'{stem}.zip.sha256'


def build(fmt):
    g=geometry(fmt)
    catalog=build_catalog()
    assert catalog==json.loads((ROOT/'catalog.json').read_text(encoding='utf-8')),'Catalog stale'
    # Tie packages to the last complete artwork validation, not just its catalog.
    reports=[json.loads((ROOT/'docs/design/face-formats-v1-report.json').read_text(encoding='utf-8')),
             json.loads((ROOT/'docs/design/tarot-full-v1-report.json').read_text(encoding='utf-8'))]
    validated={(a['path'] if a['path'].startswith('cards/') else 'cards/'+a['path']):a['sha256']
               for report in reports for a in report['cards']}
    assets=[a for a in catalog['assets'] if a['format']==fmt]
    face_count=78 if fmt=='tarot' else 54
    unique_count=face_count+5
    png_count=unique_count*3
    assert len(assets)==unique_count and sum(a['side']=='face' for a in assets)==face_count
    folder,archive_path,checksum_path=release_paths(fmt)
    folder.mkdir(parents=True,exist_ok=True)
    records=[]
    for asset in assets:
        assert validated[asset['path']]==asset['sha256'],'Unvalidated source'
        name=release_name(asset)
        source=ROOT/asset['path']
        destination=folder/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,destination)
        with Image.open(source) as native:
            assert list(native.size)==g['native'] and native.mode=='RGBA'
            clean,guide=poker.print_images(native)
        variants=dict(native=name,bleed='print/bleed/'+name,guides='print/guides/'+name)
        for key,im in (('bleed',clean),('guides',guide)):
            path=folder/variants[key]
            path.parent.mkdir(parents=True,exist_ok=True)
            im.save(path,dpi=(600,600),icc_profile=poker.SRGB)
        records.append(dict(id=asset['id'],source_path=asset['path'],source_sha256=asset['sha256'],files=variants))
    manifest=dict(version=3,design='Design 1',release_version=RELEASE_VERSION,
                  format=fmt,unique_assets=unique_count,faces=face_count,backs=5,png_count=png_count,
                  geometry=g,corner_radius_mm=3.5,native_ppi=300,print_ppi=600,
                  bleed_inches=.125,bleed_pixels=75,slug_pixels=75,files=records)
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (folder/'README.md').write_text(readme(fmt,g),encoding='utf-8')
    shutil.copy2(ROOT.parents[1]/'LICENSE',folder/'LICENSE')
    expected={p for r in records for p in r['files'].values()}|{'README.md','manifest.json','LICENSE','SHA256SUMS.txt'}
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    assert not actual-expected,(fmt,'Unexpected release files',actual-expected)
    hashes=''.join(f'{poker.sha(folder/name)}  {name}\n' for name in sorted(expected-{'SHA256SUMS.txt'}))
    (folder/'SHA256SUMS.txt').write_text(hashes,encoding='ascii')
    with zipfile.ZipFile(archive_path,'w') as archive:
        for name in sorted(expected):
            entry=zipfile.ZipInfo(name,date_time=(2026,9,19,0,0,0))
            entry.compress_type=zipfile.ZIP_STORED if name.endswith('.png') else zipfile.ZIP_DEFLATED
            entry.external_attr=0o100644<<16
            archive.writestr(entry,(folder/name).read_bytes())
    checksum_path.write_text(f'{poker.sha(archive_path)}  {archive_path.name}\n',encoding='ascii')
    check(fmt)
    print(f'Created {archive_path} ({archive_path.stat().st_size/1024**2:.1f} MiB)',flush=True)


def check(fmt):
    g=geometry(fmt)
    folder,archive_path,checksum_path=release_paths(fmt)
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    face_count=78 if fmt=='tarot' else 54
    unique_count=face_count+5
    png_count=unique_count*3
    assert manifest['format']==fmt and manifest['geometry']==g
    assert manifest['release_version']==RELEASE_VERSION
    assert manifest['png_count']==png_count and len(manifest['files'])==unique_count
    catalog=build_catalog()
    current={a['id']:a for a in catalog['assets'] if a['format']==fmt}
    assert {r['id'] for r in manifest['files']}==set(current)
    hashes={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (folder/'SHA256SUMS.txt').read_text().splitlines()}
    with zipfile.ZipFile(archive_path) as archive:
        assert len(archive.namelist())==len(set(archive.namelist()))==png_count+4
        assert set(archive.namelist())==set(hashes)|{'SHA256SUMS.txt'}
        assert archive.read('SHA256SUMS.txt')==(folder/'SHA256SUMS.txt').read_bytes()
        assert archive.testzip() is None
        for name,sha in hashes.items():
            assert poker.sha(folder/name)==hashlib.sha256(archive.read(name)).hexdigest()==sha,name
    for record in manifest['files']:
        assert record['source_sha256']==current[record['id']]['sha256']
        native_path=folder/record['files']['native']
        assert poker.sha(native_path)==record['source_sha256']
        with Image.open(native_path) as native:
            assert list(native.size)==g['native'] and native.mode=='RGBA'
            expected_clean,expected_guide=poker.print_images(native)
        for label,expected in (('bleed',expected_clean),('guides',expected_guide)):
            with Image.open(folder/record['files'][label]) as actual:
                assert actual.size==expected.size and actual.mode=='RGB'
                assert all(abs(d-600)<.01 for d in actual.info['dpi'])
                assert actual.info['icc_profile']==poker.SRGB
                assert np.array_equal(np.array(actual),np.array(expected)),record['id']
        # Independent geometry and pixel-preservation checks.
        assert expected_guide.getpixel((g['guides'][0]//2,150))==poker.BLUE
        assert expected_guide.getpixel((150,30))==poker.BLUE
        with Image.open(native_path) as native:
            trim=poker.opaque_native(native).resize(tuple(g['trim']),Image.Resampling.NEAREST)
        assert np.array_equal(np.array(expected_clean.crop(g['bleed_trim'])),np.array(trim))
    assert poker.sha(archive_path)==checksum_path.read_text().split()[0]
    print(f'PASS {fmt}: {unique_count} cards, {png_count} PNGs; geometry, source pixels, profiles and ZIP hashes',flush=True)


def write_release_index():
    archives=[]
    for fmt in FORMATS:
        _,archive_path,checksum_path=release_paths(fmt)
        archives.append(dict(format=fmt,path=archive_path.name,
            sha256=poker.sha(archive_path),bytes=archive_path.stat().st_size,
            checksum_file=checksum_path.name,
            faces=78 if fmt=='tarot' else 54,backs=5))
    release=dict(version=1,design='Design 1',release_version=RELEASE_VERSION,
                 formats=list(FORMATS),archives=archives,
                 total_active_faces=348,total_active_backs=30,total_active_pngs=378)
    path=OUT/f'design1-v{RELEASE_VERSION}.json'
    path.write_text(json.dumps(release,indent=2)+'\n',encoding='utf-8')
    sums=''.join(f"{a['sha256']}  {a['path']}\n" for a in archives)
    (OUT/f'design1-v{RELEASE_VERSION}-SHA256SUMS.txt').write_text(sums,encoding='ascii')
    print(f'Created Design 1 v{RELEASE_VERSION} release index for {len(archives)} archives',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--build',action='store_true');mode.add_argument('--check',action='store_true')
    selection=parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--format',choices=FORMATS);selection.add_argument('--all',action='store_true')
    args=parser.parse_args()
    selected=FORMATS if args.all else (args.format,)
    for fmt in selected:
        (build if args.build else check)(fmt)
    if args.all:
        write_release_index()


if __name__=='__main__':
    main()
