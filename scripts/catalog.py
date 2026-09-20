"""Build/check the portable asset catalog without changing card images."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def build_design_catalog(root: Path) -> dict:
    config = json.loads((root / "deck.json").read_text(encoding="utf-8"))
    assets = []
    seen = set()
    for path in sorted((root / "cards").rglob("*.png")):
        parts = path.relative_to(root / "cards").parts
        if parts[0] == "backs" and len(parts) == 3:
            _, size, filename = parts
            color = Path(filename).stem
            if color not in config["back_colors"]:
                raise ValueError(f"Unknown back color: {path}")
            record = dict(id=f"back.{size}.{color}", side="back", format=size,
                          color=color, status=config["back_status"])
        elif parts[0] == "faces" and len(parts) == 5:
            _, system, size, suit, filename = parts
            rank = Path(filename).stem
            definition = config["face_systems"][system]
            if system == 'tarot':
                if size not in definition['formats']:
                    raise ValueError(f"Invalid Tarot format: {path}")
                if suit == 'trumps':
                    try:
                        number_text, slug = rank.split('-', 1)
                        number = int(number_text)
                    except ValueError as error:
                        raise ValueError(f"Invalid Tarot trump filename: {path}") from error
                    trump = next((t for t in definition['trumps']
                                  if t['number'] == number and t['slug'] == slug), None)
                    if trump is None:
                        raise ValueError(f"Invalid Tarot trump: {path}")
                    record = dict(id=f"face.tarot.{size}.trump.{number}.{slug}", side='face',
                                  system=system, format=size, arcana='major', suit=None,
                                  rank=str(number), number=number, slug=slug,
                                  title=trump['title'], color_variant=None,
                                  status=config['face_status'])
                else:
                    if suit not in definition['suits'] or rank not in definition['ranks']:
                        raise ValueError(f"Invalid Tarot suit/rank: {path}")
                    record = dict(id=f"face.tarot.{size}.{suit}.{rank}", side='face',
                                  system=system, format=size, arcana='minor', suit=suit,
                                  rank=rank, title=None, color_variant=None,
                                  status=config['face_status'])
            elif suit == "jokers":
                if rank not in definition.get("jokers", []):
                    raise ValueError(f"Invalid Joker variant: {path}")
                record = dict(id=f"face.{system}.{size}.joker.{rank}", side="face",
                              system=system, format=size, suit=None, rank="joker",
                              color_variant=rank, status=config["face_status"])
            else:
                if suit not in definition["suits"] or rank not in definition["ranks"]:
                    raise ValueError(f"Invalid suit/rank: {path}")
                record = dict(id=f"face.{system}.{size}.{suit}.{rank}", side="face",
                              system=system, format=size, suit=suit, rank=rank,
                              color_variant=None, status=config["face_status"])
        else:
            raise ValueError(f"Invalid asset hierarchy: {path}")
        size_info = config["formats"][size]
        if config.get('renderer') == 'face-formats-v1':
            if record['side'] == 'back':
                record['frame_color'] = record['color']
            elif record['system'] == 'tarot':
                record['frame_color'] = ('madder-lake' if record['suit'] in ('cups', 'coins')
                                         else 'lamp-black')
            else:
                record['frame_color'] = ('madder-lake' if record['suit'] in ('hearts', 'diamonds') or record.get('color_variant') == 'red' else 'lamp-black')
        inches = size_info["trim_inches"]
        with Image.open(path) as im:
            im.load()
            pixels = list(im.size)
            if pixels != size_info["back_pixels"]:
                raise ValueError(f"Wrong dimensions for {record['side']}: {path}")
            # Integer cross-products with hundredths of inches avoid float ratio errors.
            if pixels[0] * round(inches[1]*100) != pixels[1] * round(inches[0]*100):
                raise ValueError(f"Wrong trim aspect ratio: {path}")
            record.update(path=path.relative_to(root).as_posix(), media_type="image/png",
                          pixels=pixels, mode=im.mode, encoded_dpi=list(im.info.get("dpi", [])),
                          trim_inches=inches, trim_mm=[round(n*25.4, 4) for n in inches],
                          effective_ppi=[round(p/n, 4) for p, n in zip(pixels, inches)],
                          sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        if record["id"] in seen:
            raise ValueError(f"Duplicate ID: {record['id']}")
        seen.add(record["id"])
        assets.append(record)
    expected_backs = {f"back.{size}.{color}" for size in config["formats"]
                      for color in config["back_colors"]}
    actual_backs = {a["id"] for a in assets if a["side"] == "back"}
    if actual_backs != expected_backs:
        raise ValueError(f"Back inventory mismatch: {expected_backs ^ actual_backs}")
    french = config['face_systems'].get('french-suited', {})
    face_formats = french.get('formats', [])
    expected_faces = {f"face.french-suited.{fmt}.{suit}.{rank}"
                      for fmt in face_formats for suit in french['suits'] for rank in french['ranks']}
    expected_faces.update(f"face.french-suited.{fmt}.joker.{variant}"
                          for fmt in face_formats for variant in french.get('jokers', []))
    tarot = config['face_systems'].get('tarot')
    if tarot:
        expected_faces.update(f"face.tarot.{fmt}.{suit}.{rank}"
                              for fmt in tarot['formats']
                              for suit in tarot['suits'] for rank in tarot['ranks'])
        expected_faces.update(f"face.tarot.{fmt}.trump.{trump['number']}.{trump['slug']}"
                              for fmt in tarot['formats'] for trump in tarot['trumps'])
    actual_faces={a["id"] for a in assets if a["side"]=="face"}
    if actual_faces!=expected_faces:
        raise ValueError(f"Face inventory mismatch: {actual_faces ^ expected_faces}")
    return dict(schema_version=1, deck_id=config["id"], path_base="design-root",
                formats=config["formats"], back_colors=config["back_colors"],
                print_notes=dict(geometry="trim-size artwork", bleed_included=False,
                                 crop_marks_included=False, imposition_included=False,
                                 placement="Use trim_inches; do not infer physical size from DPI metadata."),
                assets=assets)


def design_roots():
    collection = json.loads((ROOT / 'collection.json').read_text(encoding='utf-8'))
    seen = set()
    for design in collection['designs']:
        if design['id'] in seen:
            raise ValueError(f"Duplicate design: {design['id']}")
        seen.add(design['id'])
        root = (ROOT / design['path']).resolve()
        if not root.is_relative_to(ROOT / 'designs'):
            raise ValueError('Design path must be inside designs/')
        yield design, root


def aggregate(catalogs):
    designs, assets = [], []
    for design, root, catalog in catalogs:
        if catalog['deck_id'] != design['id']:
            raise ValueError(f"Design manifest ID does not match registry: {design['id']}")
        prefix = root.relative_to(ROOT).as_posix()
        designs.append(dict(**design, catalog=prefix+'/catalog.json',
                            manifest=prefix+'/deck.json', gallery=prefix+'/index.html',
                            formats=catalog['formats'], back_colors=catalog['back_colors']))
        for asset in catalog['assets']:
            assets.append(dict(asset, id=design['id']+'.'+asset['id'], design=design['id'],
                               local_id=asset['id'], path=prefix+'/'+asset['path']))
    if len({a['id'] for a in assets}) != len(assets):
        raise ValueError('Duplicate collection asset IDs')
    return dict(schema_version=2, collection_id='playing-cards', path_base='repository-root',
                designs=designs, assets=assets)


def build_catalog():
    return aggregate([(design, root, build_design_catalog(root)) for design, root in design_roots()])


def main(design_root=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true', help='Refresh catalog metadata')
    mode.add_argument('--check', action='store_true', help='Validate assets and saved metadata')
    args = parser.parse_args()
    if design_root is None:
        catalogs = [(design, root, build_design_catalog(root)) for design, root in design_roots()]
        outputs = [(root/'catalog.json', catalog) for _, root, catalog in catalogs]
        outputs.append((ROOT/'catalog.json', aggregate(catalogs)))
    else:
        outputs = [(design_root/'catalog.json', build_design_catalog(design_root))]
    for output, catalog in outputs:
        if args.write:
            output.write_text(json.dumps(catalog, indent=2)+'\n', encoding='utf-8')
        elif json.loads(output.read_text(encoding='utf-8')) != catalog:
            raise SystemExit(f'{output}: stale catalog; review changes, then run --write.')
        print(f"PASS {output.relative_to(ROOT)}: {len(catalog['assets'])} PNGs; inventory, IDs, hashes and dimensions")


if __name__ == '__main__':
    main()
