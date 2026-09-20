"""Recolor archived Prussian Blue backs without moving or resampling pixels.

Requires Pillow and NumPy. Example:
    python scripts/recolor_card_backs.py --colors lamp-black verdigris
    python scripts/recolor_card_backs.py --verify-archive

Writes review candidates and verification reports under work/recolored-backs.
The archive is never overwritten by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "deck.json").read_text(encoding="utf-8"))
SIZES = {name: tuple(spec["back_pixels"]) for name, spec in CONFIG["formats"].items()}
ACTIVE_COLORS = CONFIG["back_colors"]
# Digital interpretations of historical pigments, not colorimetric ink matches.
# Preserve the original red, green, and purple mappings exactly.
PALETTES = {
    "madder-lake": (1.0566037735849056, 0.22784810126582278, 0.1836734693877551),
    "viridian": (0.20, 0.70, 0.38),
    "manganese-violet": (0.77, 0.24, 1.04),
    "burnt-umber": (0.72, 0.43, 0.27),
    "yellow-ochre": (1.55, 1.03, 0.25),
    "burnt-sienna": (1.42, 0.58, 0.30),
    "lamp-black": (0.38, 0.36, 0.33),
    "verdigris": (0.22, 0.90, 0.88),
    "green-earth": (0.76, 0.84, 0.43),
}
ALIASES = {"red": "madder-lake", "green": "viridian", "purple": "manganese-violet"}
LABELS = {name: name.replace("-", " ").title() for name in ("prussian-blue", *PALETTES)}
# QA patch anchors only: retain the original dot even when it is off-center.
DOT_PATCH_CENTERS = {
    "bridge": (337, 529), "european-standard": (347, 541),
    "jumbo": (525, 747), "poker": (374, 522),
    "tarot": (412, 685), "travel": (262, 375),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recolor(pixels: np.ndarray, color: str) -> tuple[np.ndarray, np.ndarray]:
    """Pointwise blue-chroma mapping, with the original neutral component.

    Only blue-dominant pixels qualify. Feathering at the cyan/green boundary
    avoids a hard color seam in antialiased edges. No spatial operations occur.
    """
    color = ALIASES.get(color, color)
    rgb = pixels[..., :3].astype(np.float64)
    r, g, b = np.moveaxis(rgb, -1, 0)
    chroma = b - r
    mask = (b > r) & (b > g)
    q = np.divide(g-r, chroma, out=np.zeros_like(r), where=mask)
    strength = np.clip((1-q)/0.2, 0, 1) * mask
    target = r[..., None] + chroma[..., None] * np.array(PALETTES[color])
    mapped = np.rint(np.clip(rgb+(target-rgb)*strength[..., None], 0, 255)).astype(np.uint8)
    result = pixels.copy()
    result[..., :3] = mapped
    return result, mask


def source_path(size: str) -> Path:
    return ROOT / f"cards/backs/{size}/prussian-blue.png"


def generate(color: str) -> None:
    out = ROOT / "work/recolored-backs" / color
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "color": color, "label": LABELS[color], "palette_rgb_chroma": PALETTES[color],
        "method": "Pointwise blue-chroma replacement; no geometric transforms",
        "dimension_basis": "Original dimension-table inch column at nominal 300 DPI",
        "png_density_note": "PNG encodes nominal 300 DPI as 299.9994 DPI",
        "cards": [],
    }
    previews = []
    for size, expected in SIZES.items():
        source = source_path(size)
        source_hash = sha256(source)
        with Image.open(source) as original:
            if original.size != expected or original.mode not in ("RGB", "RGBA"):
                raise ValueError(f"Unexpected source dimensions/mode: {source}")
            pixels = np.asarray(original)
            mapped, mask = recolor(pixels, color)
            result = Image.fromarray(mapped)
            metadata = PngImagePlugin.PngInfo()
            metadata.add_text("Software", "recolor_card_backs.py; pointwise recoloring without resampling")
            metadata.add_text("Source", source.relative_to(ROOT).as_posix())
            metadata.add_text("SourceSHA256", source_hash)
            metadata.add_text("Color", color)
            metadata.add_text("NominalDPI", "300")
            metadata.add_text("DimensionsInches", f"{expected[0]/300:g} x {expected[1]/300:g}")
            destination = out / f"{color}_{size}.png"
            options = {"icc_profile": original.info["icc_profile"]} if "icc_profile" in original.info else {}
            result.save(destination, dpi=(300, 300), pnginfo=metadata, **options)
        with Image.open(destination) as saved:
            actual = np.asarray(saved)
            x, y = DOT_PATCH_CENTERS[size]
            dot = np.s_[y-5:y+6, x-5:x+6]
            checks = {
                "dimensions_match": saved.size == expected,
                "dpi_matches": all(abs(d-300) < 0.001 for d in saved.info["dpi"]),
                "lossless_roundtrip": np.array_equal(actual, mapped),
                "nonblue_pixels_unchanged": np.array_equal(actual[~mask], pixels[~mask]),
                "alpha_unchanged": pixels.shape[-1] == 3 or np.array_equal(actual[..., 3], pixels[..., 3]),
                "central_dot_patch_identical": np.array_equal(actual[dot], pixels[dot]),
                "blue_original_unchanged": sha256(source) == source_hash,
                "color_applied": bool(np.any(actual != pixels)),
            }
            if not all(checks.values()):
                raise ValueError(f"Validation failed for {color}/{size}: {checks}")
            report["cards"].append({
                "size": size, "source": source.relative_to(ROOT).as_posix(),
                "source_sha256": source_hash, "output_sha256": sha256(destination),
                "archive_path": f"cards/backs/{size}/{color}.png",
                "pixels": expected, "inches": [n/300 for n in expected],
                "millimeters": [round(n/300*25.4, 4) for n in expected],
                "encoded_dpi": saved.info["dpi"],
                "changed_pixels": int(np.any(actual[..., :3] != pixels[..., :3], axis=2).sum()),
                "unchanged_nonblue_pixels": int((~mask).sum()),
                "central_dot_check_box_xyxy_exclusive": [x-5, y-5, x+6, y+6],
                "checks": checks, "checks_passed": True,
            })
            # Only the contact-sheet preview is reduced, never the asset PNGs.
            preview = saved.convert("RGB")
            preview.thumbnail((280, 400))
            previews.append((size, preview.copy()))
        print(f"PASS {color}/{size}: {expected[0]} x {expected[1]}, original dot preserved")
    (out / "validation.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    sheet = Image.new("RGB", (900, 920), "#e8e4dc")
    draw = ImageDraw.Draw(sheet)
    draw.text((15, 8), f"{LABELS[color].upper()} / SIX CARD SIZES", fill="#27221c")
    for i, (size, preview) in enumerate(previews):
        x, y = (i % 3)*300, (i // 3)*450+20
        draw.text((x+15, y+12), size, fill="#27221c")
        sheet.paste(preview, (x+(300-preview.width)//2, y+35))
    sheet.save(out / f"{color}-backs-preview.jpg", quality=95)


def verify_archive() -> dict:
    """Check the real archive against the source pixels and palette definition."""
    records = []
    for size, expected in SIZES.items():
        source = source_path(size)
        with Image.open(source) as original:
            pixels = np.asarray(original)
            for color in ACTIVE_COLORS:
                path = ROOT / f"cards/backs/{size}/{color}.png"
                target, mask = (pixels, np.zeros(pixels.shape[:2], dtype=bool)) if color == "prussian-blue" else recolor(pixels, color)
                with Image.open(path) as saved:
                    actual = np.asarray(saved)
                    x, y = DOT_PATCH_CENTERS[size]
                    checks = {
                        "dimensions_match": saved.size == expected,
                        "dpi_matches": all(abs(d-300) < 0.001 for d in saved.info["dpi"]),
                        "matches_palette_pixel_for_pixel": np.array_equal(actual, target),
                        "nonblue_pixels_unchanged": np.array_equal(actual[~mask], pixels[~mask]),
                        "central_dot_patch_identical": np.array_equal(actual[y-5:y+6, x-5:x+6], pixels[y-5:y+6, x-5:x+6]),
                        "alpha_unchanged": pixels.shape[-1] == 3 or np.array_equal(actual[..., 3], pixels[..., 3]),
                    }
                    if not all(checks.values()):
                        raise ValueError(f"Archive verification failed: {path}: {checks}")
                    records.append({
                        "color": color, "label": LABELS[color], "size": size,
                        "archive_path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path),
                        "source": source.relative_to(ROOT).as_posix(), "source_sha256": sha256(source),
                        "pixels": expected, "inches": [n/300 for n in expected],
                        "millimeters": [round(n/300*25.4, 4) for n in expected],
                        "encoded_dpi": saved.info["dpi"], "checks": checks,
                        "central_dot_check_box_xyxy_exclusive": [x-5, y-5, x+6, y+6],
                        "checks_passed": True,
                    })
    print(f"PASS archive: {len(records)} cards, {len(ACTIVE_COLORS)} colors x {len(SIZES)} sizes")
    return {"method": "Exact pixel comparison to source and named palette", "cards": records}


def preview_palette() -> Path:
    """Render a labeled comparison; downsampling is limited to this preview."""
    order = ACTIVE_COLORS
    def font(name: str, size: int):
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{name}.ttf", size)
        except OSError:
            return ImageFont.load_default(size=size)
    sheet_height = 210 + ((len(order) + 4) // 5) * 520
    sheet = Image.new("RGB", (1800, sheet_height), "#eee7d9")
    draw = ImageDraw.Draw(sheet)
    draw.text((54, 32), "The Printer's Palette", font=font("georgia", 45), fill="#302a24")
    draw.text((56, 91), f"{len(order)} PIGMENT-INSPIRED COLORS  /  {len(SIZES)} FORMATS", font=font("arial", 18), fill="#66584a")
    draw.line((54, 130, 1746, 130), fill="#b8a588", width=2)
    for i, color in enumerate(order):
        x, y = 40+(i%5)*350, 160+(i//5)*520
        path = ROOT / f"cards/backs/poker/{color}.png"
        with Image.open(path) as im:
            preview = im.convert("RGB")
            preview.thumbnail((300, 420))
            sheet.paste(preview, (x+(320-preview.width)//2, y))
        draw.text((x+160, y+440), LABELS[color], font=font("georgia", 23), fill="#302a24", anchor="mt")
    draw.text((54, sheet_height - 40), "Digital interpretations of historical pigments. Poker format shown; artwork geometry preserved in every size.",
              font=font("arial", 17), fill="#66584a")
    out = ROOT / "work/palette/palette-preview.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=96)
    print(out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--colors", nargs="+", choices=[*PALETTES, *ALIASES],
                        default=[color for color in ACTIVE_COLORS if color != "prussian-blue"])
    parser.add_argument("--verify-archive", action="store_true", help="Check archived files without modifying them")
    parser.add_argument("--preview", action="store_true", help="Create the labeled active-color comparison")
    args = parser.parse_args()
    if args.verify_archive:
        verify_archive()
        return
    if args.preview:
        preview_palette()
        return
    for color in dict.fromkeys(ALIASES.get(c, c) for c in args.colors):
        generate(color)


if __name__ == "__main__":
    main()
