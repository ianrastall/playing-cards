"""Export a generated face at the repository's nominal 300-DPI format size.

Example: python scripts/export_face.py sources/generated/poker/jacks/spades.png cards/faces/french-suited/poker/spades/jack.png
Existing destination files are never overwritten.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    config = json.loads((ROOT / "deck.json").read_text(encoding="utf-8"))
    parser.add_argument("--format", choices=config["formats"], default="poker")
    args = parser.parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite {destination}")
    size = tuple(config["formats"][args.format]["back_pixels"])
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    with Image.open(source) as original:
        if original.width * size[1] != original.height * size[0]:
            raise ValueError("Source aspect ratio differs; cropping or stretching is not allowed")
        if original.mode not in ("RGB", "RGBA"):
            raise ValueError(f"Unsupported source mode: {original.mode}")
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("Software", "scripts/export_face.py; Pillow Lanczos resize")
        metadata.add_text("SourceSHA256", source_hash)
        source_label = source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else source.name
        metadata.add_text("Source", source_label)
        metadata.add_text("NominalDPI", "300")
        options = {"icc_profile": original.info["icc_profile"]} if original.info.get("icc_profile") else {}
        exported = original.resize(size, Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as output:
            exported.save(output, format="PNG", dpi=(300, 300), pnginfo=metadata, **options)
    with Image.open(destination) as checked:
        checked.load()
        if checked.size != size or any(abs(d - 300) > .001 for d in checked.info["dpi"]):
            raise ValueError("Export dimensions or density verification failed")
    if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
        raise ValueError("Source master changed")
    print(f"PASS {destination.name}: {size[0]} x {size[1]}, nominal 300 DPI; master unchanged")


if __name__ == "__main__":
    main()
