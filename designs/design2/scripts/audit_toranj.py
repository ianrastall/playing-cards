"""Independent checks for balanced toranj back exports."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CARD_RADIUS = 3.5 / 25.4 * 300


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def silhouette(width: int, height: int) -> np.ndarray:
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


def reciprocal_from_top(array: np.ndarray) -> np.ndarray:
    result = array.copy()
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


def audit(out: Path) -> None:
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["revision"] == "toranj-v1"
    assert manifest["outer_margin_px"] == 23
    assert manifest["border_width_px"] == 50
    assert len(manifest["cards"]) == 30
    records = []
    bridge_arrays = {}
    for card in manifest["cards"]:
        path = out / card["path"]
        width, height = card["pixels"]
        with Image.open(path) as image:
            assert image.mode == "RGBA" and image.size == (width, height)
            assert all(abs(value - 300) < 0.01 for value in image.info["dpi"])
            array = np.asarray(image)
        assert digest(path) == card["sha256"]
        assert np.array_equal(array, array[::-1, ::-1]), path
        if card["format"] != "european-standard":
            assert np.array_equal(array[:, :, 3], silhouette(width, height)), path
        cx, cy = (width - 1) / 2, (height - 1) / 2
        yy, xx = np.indices((height, width))
        central = (np.abs(xx - cx) <= width * 0.12) & (np.abs(yy - cy) <= width * 0.12)
        rgb = array[:, :, :3].astype(float)
        weight = np.maximum(rgb[:, :, 0] + rgb[:, :, 1] - 1.5 * rgb[:, :, 2] - 80, 0) * central
        assert np.count_nonzero(weight) > 40
        measured = [float((xx * weight).sum() / weight.sum()), float((yy * weight).sum() / weight.sum())]
        error = max(abs(measured[0] - cx), abs(measured[1] - cy))
        assert error < 1e-9, (path, measured)
        if card["format"] == "bridge":
            bridge_arrays[card["color"]] = array
        if card["format"] == "european-standard":
            bridge = Image.fromarray(bridge_arrays[card["color"]], "RGBA")
            expected = np.asarray(bridge.resize((width, height), Image.Resampling.LANCZOS))
            expected = reciprocal_from_top(expected)
            assert np.array_equal(array, expected), path
        records.append({
            "path": card["path"],
            "center_expected": [cx, cy],
            "center_measured": measured,
            "center_error_px": error,
            "rgba_half_turn_exact": True,
            "alpha_matches_physical_silhouette": card["format"] != "european-standard",
            "alpha_inherited_from_bridge_resize": card["format"] == "european-standard",
            "outer_margin_px": 23 if card["format"] != "european-standard" else None,
            "border_width_px": 50 if card["format"] != "european-standard" else None,
            "derived_from_bridge": card["format"] == "european-standard",
        })
    report = {
        "status": "passed",
        "revision": "toranj-v1",
        "card_count": len(records),
        "max_measured_center_error_px": max(record["center_error_px"] for record in records),
        "native_formats": ["poker", "bridge", "travel", "jumbo", "tarot"],
        "european_standard_derived_from_bridge": True,
        "method": "Independent PNG hashes, dimensions, native alpha silhouettes, exact half-turn pixels, localized central centroids, common registered geometry, and full RGBA Bridge resize comparison.",
        "cards": records,
    }
    (out / "registration-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    if out == ROOT:
        (ROOT / "docs/design/design2-registration-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS 30 toranj PNGs: exact centers and half-turns; five native formats; European Standard is Bridge resized.")
