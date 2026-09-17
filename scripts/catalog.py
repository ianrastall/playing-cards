"""Build/check the portable asset catalog without changing card images."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def build_catalog() -> dict:
    config = json.loads((ROOT / "deck.json").read_text(encoding="utf-8"))
    assets = []
    seen = set()
    for path in sorted((ROOT / "cards").rglob("*.png")):
        parts = path.relative_to(ROOT / "cards").parts
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
            if suit == "jokers":
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
        inches = size_info["trim_inches"]
        with Image.open(path) as im:
            im.load()
            pixels = list(im.size)
            if pixels != size_info["back_pixels"]:
                raise ValueError(f"Wrong dimensions for {record['side']}: {path}")
            # Integer cross-products with hundredths of inches avoid float ratio errors.
            if pixels[0] * round(inches[1]*100) != pixels[1] * round(inches[0]*100):
                raise ValueError(f"Wrong trim aspect ratio: {path}")
            record.update(path=path.relative_to(ROOT).as_posix(), media_type="image/png",
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
    expected_faces={f"face.french-suited.poker.{suit}.{rank}"
                    for suit in config["face_systems"]["french-suited"]["suits"]
                    for rank in config["face_systems"]["french-suited"]["ranks"]}
    expected_faces.update(f"face.french-suited.poker.joker.{variant}"
                          for variant in config["face_systems"]["french-suited"].get("jokers",[]))
    actual_faces={a["id"] for a in assets if a["side"]=="face"}
    if actual_faces!=expected_faces:
        raise ValueError(f"Face inventory mismatch: {actual_faces ^ expected_faces}")
    return dict(schema_version=1, deck_id=config["id"], path_base="repository-root",
                formats=config["formats"], back_colors=config["back_colors"],
                print_notes=dict(geometry="trim-size artwork", bleed_included=False,
                                 crop_marks_included=False, imposition_included=False,
                                 placement="Use trim_inches; do not infer physical size from DPI metadata."),
                assets=assets)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Rebuild catalog.json")
    mode.add_argument("--check", action="store_true", help="Fail if catalog.json is stale")
    args = parser.parse_args()
    catalog = build_catalog()
    output = ROOT / "catalog.json"
    if args.write:
        output.write_text(json.dumps(catalog, indent=2)+"\n", encoding="utf-8")
    elif json.loads(output.read_text(encoding="utf-8")) != catalog:
        raise SystemExit("Catalog differs from assets/configuration. Review changes, then run --write.")
    print(f"PASS catalog: {len(catalog['assets'])} PNGs, IDs, hashes, dimensions and inventory checked")


if __name__ == "__main__":
    main()
