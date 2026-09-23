"""Register the toranj masters and export balanced Design 2 backs."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
REVISION = "toranj-v1"
SOURCE = ROOT / "sources/generated/design2-toranj-v1/native"
BUILD = ROOT / f"build/design2-{REVISION}"
COLORS = ["prussian-blue", "verdigris", "madder-lake", "manganese-violet", "lamp-black"]
NATIVE_FORMATS = ["poker", "bridge", "travel", "jumbo", "tarot"]
MARGIN = 23
BORDER = 50
INSET = MARGIN + BORDER
CARD_RADIUS = 3.5 / 25.4 * 300

# Measured on the Madder Lake masters. Color edits retain these landmarks.
# Coordinates are inclusive pixel centers: outer double frame, inner double frame.
SOURCE_GEOMETRY = {
    "poker": {"size": [1060, 1484], "outer": [28, 24, 1030, 1451], "inner": [118, 121, 941, 1362]},
    "bridge": {"size": [1006, 1564], "outer": [79, 29, 925, 1501], "inner": [164, 125, 841, 1438]},
    "travel": {"size": [1049, 1499], "outer": [30, 25, 1018, 1469], "inner": [119, 127, 929, 1371]},
    "jumbo": {"size": [1049, 1499], "outer": [29, 25, 1019, 1466], "inner": [117, 120, 931, 1378]},
    "tarot": {"size": [954, 1649], "outer": [32, 27, 922, 1580], "inner": [120, 133, 833, 1515]},
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def card_silhouette(width: int, height: int) -> np.ndarray:
    yy, xx = np.ogrid[:height, :width]
    count = np.zeros((height, width), dtype=np.uint8)
    for oy in range(8):
        for ox in range(8):
            x = xx + (ox + 0.5) / 8
            y = yy + (oy + 0.5) / 8
            dx = np.maximum(np.maximum(CARD_RADIUS - x, x - (width - CARD_RADIUS)), 0)
            dy = np.maximum(np.maximum(CARD_RADIUS - y, y - (height - CARD_RADIUS)), 0)
            count += dx * dx + dy * dy <= CARD_RADIUS * CARD_RADIUS
    return np.floor(count.astype(float) * 255 / 64 + 0.5).astype(np.uint8)


def axes(source_size: tuple[int, int], target_size: tuple[int, int], geometry: dict) -> tuple[np.ndarray, np.ndarray]:
    sw, sh = source_size
    tw, th = target_size
    outer = geometry["outer"]
    inner = geometry["inner"]
    tx = np.array([0, MARGIN, INSET, (tw - 1) / 2, tw - 1 - INSET, tw - 1 - MARGIN, tw - 1], float)
    ty = np.array([0, MARGIN, INSET, (th - 1) / 2, th - 1 - INSET, th - 1 - MARGIN, th - 1], float)
    sx = np.array([0, outer[0], inner[0], (sw - 1) / 2, inner[2], outer[2], sw - 1], float)
    sy = np.array([0, outer[1], inner[1], (sh - 1) / 2, inner[3], outer[3], sh - 1], float)
    return np.interp(np.arange(tw), tx, sx), np.interp(np.arange(th), ty, sy)


def bilinear(image: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    xs = np.clip(xs, 0, width - 1)
    ys = np.clip(ys, 0, height - 1)
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    x1 = np.minimum(x0 + 1, width - 1)
    y1 = np.minimum(y0 + 1, height - 1)
    fx = (xs - x0)[None, :, None].astype(np.float32)
    fy = (ys - y0)[:, None, None].astype(np.float32)
    top = image[y0[:, None], x0[None, :]].astype(np.float32) * (1 - fx) + image[y0[:, None], x1[None, :]].astype(np.float32) * fx
    bottom = image[y1[:, None], x0[None, :]].astype(np.float32) * (1 - fx) + image[y1[:, None], x1[None, :]].astype(np.float32) * fx
    return np.floor(top * (1 - fy) + bottom * fy + 0.5).astype(np.uint8)


def reciprocal_from_top(rgb: np.ndarray) -> np.ndarray:
    """Use one continuous top half, meeting at the central flower, then rotate it."""
    result = rgb.copy()
    height, width = result.shape[:2]
    half = height // 2
    if height % 2:
        row = result[half].copy()
        if width % 2:
            row[width // 2 + 1 :] = row[: width // 2][::-1]
        else:
            row[width // 2 :] = row[: width // 2][::-1]
        result[half] = row
        result[half + 1 :] = result[:half][::-1, ::-1]
    else:
        result[half:] = result[:half][::-1, ::-1]
    return result


def save_rgba(rgb: np.ndarray, path: Path) -> None:
    height, width = rgb.shape[:2]
    rgba = np.dstack((rgb, card_silhouette(width, height)))
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(path, dpi=(300, 300), compress_level=9)


def save_finished(rgba: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(path, dpi=(300, 300), compress_level=9)


def normalize(source_path: Path, target_size: tuple[int, int], geometry: dict) -> np.ndarray:
    source = np.asarray(Image.open(source_path).convert("RGB"))
    expected = tuple(geometry["size"])
    actual = source.shape[1::-1]
    adjusted = dict(geometry)
    if actual != expected:
        scale_x = (actual[0] - 1) / (expected[0] - 1)
        scale_y = (actual[1] - 1) / (expected[1] - 1)
        adjusted["outer"] = [
            geometry["outer"][0] * scale_x,
            geometry["outer"][1] * scale_y,
            geometry["outer"][2] * scale_x,
            geometry["outer"][3] * scale_y,
        ]
        adjusted["inner"] = [
            geometry["inner"][0] * scale_x,
            geometry["inner"][1] * scale_y,
            geometry["inner"][2] * scale_x,
            geometry["inner"][3] * scale_y,
        ]
    xs, ys = axes(actual, target_size, adjusted)
    return reciprocal_from_top(bilinear(source, xs, ys))


def resize_european(bridge_path: Path, size: tuple[int, int]) -> np.ndarray:
    with Image.open(bridge_path) as image:
        resized = image.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    return reciprocal_from_top(np.asarray(resized))


def render() -> dict:
    config = json.loads((ROOT / "deck.json").read_text())
    cards = []
    layout = {}
    source_records = {}
    for fmt in NATIVE_FORMATS:
        width, height = config["formats"][fmt]["back_pixels"]
        geometry = SOURCE_GEOMETRY[fmt]
        layout[fmt] = {
            "pixels": [width, height],
            "center_pixel": [(width - 1) / 2, (height - 1) / 2],
            "outer_margin_px": MARGIN,
            "border_width_px": BORDER,
            "inner_inset_px": INSET,
            "outer_bounds": [MARGIN, MARGIN, width - MARGIN, height - MARGIN],
            "inner_bounds": [INSET, INSET, width - INSET, height - INSET],
            "source_geometry": geometry,
            "method": "Piecewise registration to common outer and inner frames; top half rotated to construct an exact reciprocal bottom half.",
        }
        source_records[fmt] = {}
        for color in COLORS:
            source_path = SOURCE / color / f"{fmt}.png"
            source_records[fmt][color] = {
                "path": source_path.relative_to(ROOT).as_posix(),
                "sha256": digest(source_path),
                "pixels": list(Image.open(source_path).size),
            }
            rgb = normalize(source_path, (width, height), geometry)
            relative = Path("cards/backs") / fmt / f"{color}.png"
            destination = BUILD / relative
            save_rgba(rgb, destination)
            cards.append({
                "id": f"design2.back.{fmt}.{color}",
                "path": relative.as_posix(),
                "format": fmt,
                "color": color,
                "pixels": [width, height],
                "mode": "RGBA",
                "ppi": 300,
                "trim_inches": config["formats"][fmt]["trim_inches"],
                "center_pixel": [(width - 1) / 2, (height - 1) / 2],
                "sha256": digest(destination),
                "half_turn_exact": True,
                "common_margin_and_border": True,
                "native_format_master": True,
            })
        print(f"PASS {fmt}: five native masters registered to center, {MARGIN} px margin and {BORDER} px border")

    fmt = "european-standard"
    width, height = config["formats"][fmt]["back_pixels"]
    layout[fmt] = {
        "pixels": [width, height],
        "center_pixel": [(width - 1) / 2, (height - 1) / 2],
        "derived_from": "bridge",
        "method": "Direct Lanczos resize of the complete finished Bridge RGBA back, followed only by exact reciprocal rounding.",
    }
    for color in COLORS:
        relative = Path("cards/backs") / fmt / f"{color}.png"
        destination = BUILD / relative
        bridge = BUILD / "cards/backs/bridge" / f"{color}.png"
        save_finished(resize_european(bridge, (width, height)), destination)
        cards.append({
            "id": f"design2.back.{fmt}.{color}",
            "path": relative.as_posix(),
            "format": fmt,
            "color": color,
            "pixels": [width, height],
            "mode": "RGBA",
            "ppi": 300,
            "trim_inches": config["formats"][fmt]["trim_inches"],
            "center_pixel": [(width - 1) / 2, (height - 1) / 2],
            "sha256": digest(destination),
            "half_turn_exact": True,
            "derived_from": "bridge",
            "native_format_master": False,
        })
    print("PASS european-standard: five direct Bridge resizes")

    manifest = {
        "design": "Design 2",
        "status": "approved",
        "revision": REVISION,
        "renderer": "balanced-toranj-v1",
        "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "tool": "built-in image_gen"},
        "source_records": source_records,
        "formats": list(config["formats"]),
        "colors": COLORS,
        "corner_radius_mm": 3.5,
        "outer_margin_px": MARGIN,
        "border_width_px": BORDER,
        "construction": "Native Poker, Bridge, Travel, Jumbo and Tarot masters. European Standard is Bridge resized.",
        "layout": layout,
        "cards": cards,
    }
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def apply(manifest: dict) -> None:
    subprocess.run(["python", str(ROOT / "scripts/audit_design2_registration.py"), "--build"], check=True)
    for card in manifest["cards"]:
        source = BUILD / card["path"]
        destination = ROOT / card["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    shutil.copyfile(BUILD / "manifest.json", ROOT / "manifest.json")
    config_path = ROOT / "deck.json"
    config = json.loads(config_path.read_text())
    config["revision"] = REVISION
    config["renderer"] = "balanced-toranj-v1"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    subprocess.run(["python", str(ROOT / "scripts/audit_design2_registration.py")], check=True)

    baseline = json.loads((REPO / "docs/layout-migration.json").read_text())
    baseline_hashes = {record["path"]: record["sha256"] for record in baseline["assets"]}
    ledger_path = REPO / "docs/asset-revisions.json"
    ledger = json.loads(ledger_path.read_text())
    ledger["assets"] = [record for record in ledger["assets"] if not record["path"].startswith("designs/design2/")]
    for card in manifest["cards"]:
        repo_path = "designs/design2/" + card["path"]
        ledger["assets"].append({
            "path": repo_path,
            "migration_sha256": baseline_hashes[repo_path],
            "sha256": card["sha256"],
            "revision": REVISION,
            "manifest": "designs/design2/manifest.json",
        })
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
    subprocess.run(["python", str(REPO / "scripts/catalog.py"), "--write"], check=True)
    print("Promoted 30 balanced toranj backs and refreshed catalogs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Promote audited output into cards/backs")
    args = parser.parse_args()
    result = render()
    if args.apply:
        apply(result)
