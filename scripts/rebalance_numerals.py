"""Register poker numeral layouts to a common center and common perimeter.

The active targets are the 32 poker numeral faces from 2 through 9.  Their
ornate pips each contain one turquoise jewel, so the chroma-weighted mean of
all pip jewels is a reproducible layout anchor even on ranks without a center
pip.  Candidates use exact whole-pixel translation and the existing numeral
border from the Ten of Spades; no illustration is redrawn or resampled.

Run --analyze first, then --stage and inspect the preview/report.  --apply
installs only staged, hash-verified candidates and preserves the originals.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin

from align_courts import border_mask


ROOT = Path(__file__).resolve().parents[1]
FACES = ROOT / "cards/faces/french-suited/poker"
BACKUPS = ROOT / "sources/before-numeral-rebalancing/poker"
STAGE = ROOT / "work/numeral-rebalancing"
REPORT = ROOT / "docs/design/numeral-rebalancing.json"
REPAIR_REPORT = ROOT / "docs/design/numeral-rebalancing-repair.json"
REPAIR_STAGE = STAGE / "repair"
SUITS = ("spades", "hearts", "diamonds", "clubs")
RANKS = tuple(str(rank) for rank in range(2, 10))
TARGET = (375, 525)
TEMPLATE = FACES / "spades/10.png"
INTERIOR = (75, 72, 675, 967)
PANELS = ((28, 44, 132, 290), (618, 760, 722, 1008))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jewel_components(pixels: np.ndarray) -> list[dict]:
    """Return turquoise connected components inside the numbered-card field."""
    rgb = pixels[:, :, :3].astype(np.int16)
    red, green, blue = rgb.transpose(2, 0, 1)
    # The bounds exclude cartouches and the perimeter; the chroma threshold
    # isolates the cyan jewel rather than ivory petals or gold outlines.
    mask = ((green - red > 18) & (blue - red > 18) & (green > 65))
    mask[:95] = False
    mask[955:] = False
    mask[:, :135] = False
    mask[:, 615:] = False
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    components: list[dict] = []
    for start_y, start_x in zip(*np.nonzero(mask)):
        if seen[start_y, start_x]:
            continue
        queue = deque([(int(start_y), int(start_x))])
        seen[start_y, start_x] = True
        points: list[tuple[int, int]] = []
        while queue:
            y, x = queue.popleft()
            points.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    yy, xx = y + dy, x + dx
                    if (0 <= yy < height and 0 <= xx < width and mask[yy, xx]
                            and not seen[yy, xx]):
                        seen[yy, xx] = True
                        queue.append((yy, xx))
        # Jewel interiors are compact; isolated antialiasing pixels and any
        # large accidental cyan regions are deliberately rejected.
        if not 8 <= len(points) <= 800:
            continue
        yy = np.fromiter((point[0] for point in points), dtype=float)
        xx = np.fromiter((point[1] for point in points), dtype=float)
        weight = np.minimum(green[yy.astype(int), xx.astype(int)] - red[yy.astype(int), xx.astype(int)],
                            blue[yy.astype(int), xx.astype(int)] - red[yy.astype(int), xx.astype(int)])
        components.append(dict(
            pixels=len(points),
            centroid=[float((xx * weight).sum() / weight.sum()),
                      float((yy * weight).sum() / weight.sum())],
        ))
    return components


def anchor(pixels: np.ndarray, rank: str) -> tuple[tuple[int, int], list[float], list[dict]]:
    components = jewel_components(pixels)
    expected = int(rank)
    if len(components) != expected:
        raise ValueError(f"Expected {expected} turquoise pip jewels, found {len(components)}")
    centers = np.asarray([entry["centroid"] for entry in components], dtype=float)
    centroid = centers.mean(axis=0)
    rounded = tuple(int(np.floor(value + .5)) for value in centroid)
    return rounded, [round(float(value), 6) for value in centroid], components


def paths() -> list[Path]:
    return [FACES / suit / f"{rank}.png" for suit in SUITS for rank in RANKS]


def movable_mask() -> np.ndarray:
    """Central field that may move; cartouches and perimeter never move."""
    mask = np.zeros((1050, 750), dtype=bool)
    x0, y0, x1, y1 = INTERIOR
    mask[y0:y1, x0:x1] = True
    for x0, y0, x1, y1 in PANELS:
        mask[y0:y1, x0:x1] = False
    return mask


def nonwrapping_translate(pixels: np.ndarray, dx: int, dy: int) -> tuple[np.ndarray, np.ndarray]:
    """Translate the movable field exactly, retaining original exposed strips.

    Unlike np.roll this never draws pixels from the opposite edge into the
    field.  The returned validity mask identifies destinations copied from a
    movable source pixel; all other pixels remain from the source image.
    """
    movable = movable_mask()
    yy, xx = np.indices(movable.shape)
    source_y = yy - dy
    source_x = xx - dx
    in_bounds = ((source_y >= 0) & (source_y < pixels.shape[0]) &
                 (source_x >= 0) & (source_x < pixels.shape[1]))
    source_movable = np.zeros_like(movable)
    valid_coordinates = in_bounds
    source_movable[valid_coordinates] = movable[source_y[valid_coordinates],
                                                  source_x[valid_coordinates]]
    valid = movable & source_movable
    output = pixels.copy()
    output[valid] = pixels[source_y[valid], source_x[valid]]
    return output, valid


def analyze() -> list[dict]:
    results = []
    for path in paths():
        with Image.open(path) as image:
            if image.size != (750, 1050) or image.mode != "RGB":
                raise ValueError(f"Unexpected geometry or mode: {path}")
            rank = path.stem
            before_anchor, centroid, components = anchor(np.asarray(image), rank)
        dx, dy = TARGET[0] - before_anchor[0], TARGET[1] - before_anchor[1]
        results.append(dict(path=path.relative_to(ROOT).as_posix(), rank=rank,
                            before_anchor=list(before_anchor), before_centroid=centroid,
                            shift_xy=[dx, dy], jewel_components=components))
        print(f"{path.relative_to(FACES)}: {before_anchor} -> {TARGET}; "
              f"translation ({dx:+d},{dy:+d})")
    return results


def stage() -> None:
    if REPORT.exists() or (STAGE / "report.json").exists():
        raise FileExistsError("A numeral-rebalancing record already exists")
    entries = analyze()
    mask = border_mask()
    with Image.open(TEMPLATE) as template_image:
        template = np.asarray(template_image.convert("RGB"))
    if template.shape != (1050, 750, 3):
        raise ValueError("Unexpected numeral border template geometry")
    preview = Image.new("RGB", (1200, 3440), "#e7e2d7")
    draw = ImageDraw.Draw(preview)
    for index, entry in enumerate(entries):
        path = ROOT / entry["path"]
        backup = BACKUPS / path.relative_to(FACES)
        candidate = STAGE / "candidates" / path.relative_to(FACES)
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists() and digest(backup) != digest(path):
            raise ValueError(f"Existing backup differs: {backup}")
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        with Image.open(backup) as image:
            original = np.asarray(image.convert("RGB"))
            dx, dy = entry["shift_xy"]
            if max(abs(dx), abs(dy)) > 32:
                raise ValueError(f"Unexpectedly large shift: {path}: {dx},{dy}")
            translated, _ = nonwrapping_translate(original, dx, dy)
            output = translated.copy()
            output[mask] = template[mask]
            after_anchor, after_centroid, _ = anchor(output, entry["rank"])
            if after_anchor != TARGET:
                raise ValueError(f"Anchor alignment failed: {path}")
            if not np.array_equal(output[~mask], translated[~mask]):
                raise ValueError("Unmasked artwork differs from exact non-wrapping translation")
            if not np.array_equal(output[mask], template[mask]):
                raise ValueError("Shared border differs from template")
            metadata = PngImagePlugin.PngInfo()
            for key, value in image.text.items():
                metadata.add_text(key, str(value))
            metadata.add_text("RebalanceSourceSHA256", digest(backup))
            metadata.add_text("RebalanceShiftXY", f"{dx},{dy}")
            metadata.add_text("PipLayoutAnchorXY", "375,525")
            candidate.parent.mkdir(parents=True, exist_ok=True)
            options = {"icc_profile": image.info["icc_profile"]} if image.info.get("icc_profile") else {}
            Image.fromarray(output).save(candidate, dpi=(300, 300), pnginfo=metadata, **options)
        with Image.open(candidate) as saved:
            if not np.array_equal(np.asarray(saved.convert("RGB")), output):
                raise ValueError("PNG round trip changed pixels")
        entry.update(dict(
            backup=backup.relative_to(ROOT).as_posix(),
            candidate=candidate.relative_to(ROOT).as_posix(),
            before_sha256=digest(backup), after_sha256=digest(candidate),
            after_anchor=list(after_anchor), after_centroid=after_centroid,
            artwork_exact_after_integer_translation=True,
            shared_numeral_border_exact=True,
        ))
        x = (index % 4) * 300
        y = (index // 4) * 430
        with Image.open(candidate) as candidate_image:
            thumbnail = candidate_image.resize((292, 409), Image.Resampling.LANCZOS)
        preview.paste(thumbnail, (x + 4, y + 22))
        draw.text((x + 7, y + 4), f"{path.parent.name} / {path.stem}", fill="#24231f")
    STAGE.mkdir(parents=True, exist_ok=True)
    report = dict(
        schema_version=1,
        canvas=[750, 1050], nominal_dpi=300,
        target_pip_layout_anchor=list(TARGET),
        coordinate_basis="zero-based rounded chroma-weighted mean of all turquoise pip-jewel centroids",
        method="exact non-wrapping whole-pixel translation of the movable field plus shared numeral border copied under the established border mask",
        template_source=TEMPLATE.relative_to(ROOT).as_posix(),
        template_sha256=digest(TEMPLATE),
        border_mask="scripts.align_courts.border_mask",
        changed_pixels_allowed="only non-wrapping integer translation in the movable field; shared template pixels inside the border mask",
        cards=entries,
    )
    (STAGE / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    preview.save(STAGE / "preview-after.png")
    print("Staged 32 numeral cards; active assets unchanged.")


def apply() -> None:
    if REPORT.exists():
        raise FileExistsError("A numeral-rebalancing report already exists")
    report = json.loads((STAGE / "report.json").read_text(encoding="utf-8"))
    if digest(ROOT / report["template_source"]) != report["template_sha256"]:
        raise ValueError("Border template changed after staging")
    mask = border_mask()
    with Image.open(ROOT / report["template_source"]) as template_image:
        template = np.asarray(template_image.convert("RGB"))
    for entry in report["cards"]:
        path = ROOT / entry["path"]
        backup = ROOT / entry["backup"]
        candidate = ROOT / entry["candidate"]
        if digest(path) != entry["before_sha256"] or digest(backup) != entry["before_sha256"]:
            raise ValueError(f"Active input or backup changed: {path}")
        if digest(candidate) != entry["after_sha256"]:
            raise ValueError(f"Candidate changed: {candidate}")
        with Image.open(backup) as image:
            dx, dy = entry["shift_xy"]
            translated, _ = nonwrapping_translate(np.asarray(image.convert("RGB")), dx, dy)
        with Image.open(candidate) as image:
            output = np.asarray(image.convert("RGB"))
        if not np.array_equal(output[~mask], translated[~mask]):
            raise ValueError(f"Non-wrapping translated artwork check failed: {path}")
        if not np.array_equal(output[mask], template[mask]):
            raise ValueError(f"Shared border check failed: {path}")
        if tuple(entry["after_anchor"]) != TARGET:
            raise ValueError(f"Anchor check failed: {path}")
    for entry in report["cards"]:
        (ROOT / entry["path"]).write_bytes((ROOT / entry["candidate"]).read_bytes())
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS: 32 numeral layouts centered; shared numeral border exact.")


def repair_stage() -> None:
    """Stage a correction of the initial wraparound pass from its originals."""
    if REPAIR_REPORT.exists() or (REPAIR_STAGE / "report.json").exists():
        raise FileExistsError("A numeral-rebalancing repair record already exists")
    initial = json.loads(REPORT.read_text(encoding="utf-8"))
    if len(initial.get("cards", [])) != 32:
        raise ValueError("Initial rebalancing record is incomplete")
    if digest(ROOT / initial["template_source"]) != initial["template_sha256"]:
        raise ValueError("Border template changed since the initial pass")
    mask = border_mask()
    with Image.open(ROOT / initial["template_source"]) as template_image:
        template = np.asarray(template_image.convert("RGB"))
    entries: list[dict] = []
    preview = Image.new("RGB", (1200, 3440), "#e7e2d7")
    draw = ImageDraw.Draw(preview)
    for index, initial_entry in enumerate(initial["cards"]):
        path = ROOT / initial_entry["path"]
        backup = ROOT / initial_entry["backup"]
        candidate = REPAIR_STAGE / "candidates" / path.relative_to(FACES)
        if digest(backup) != initial_entry["before_sha256"]:
            raise ValueError(f"Preserved original changed: {backup}")
        dx, dy = initial_entry["shift_xy"]
        with Image.open(backup) as image:
            original = np.asarray(image.convert("RGB"))
            translated, valid = nonwrapping_translate(original, dx, dy)
            output = translated.copy()
            output[mask] = template[mask]
            after_anchor, after_centroid, _ = anchor(output, initial_entry["rank"])
            if after_anchor != TARGET:
                raise ValueError(f"Anchor alignment failed: {path}")
            if not np.array_equal(output[~mask], translated[~mask]):
                raise ValueError(f"Movable artwork differs from non-wrapping translation: {path}")
            if not np.array_equal(output[mask], template[mask]):
                raise ValueError(f"Shared border differs from template: {path}")
            # The exposed strips and fixed cartouches must remain source pixels.
            if not np.array_equal(output[~valid & ~mask], original[~valid & ~mask]):
                raise ValueError(f"Original exposed pixels were not preserved: {path}")
            metadata = PngImagePlugin.PngInfo()
            for key, value in image.text.items():
                metadata.add_text(key, str(value))
            metadata.add_text("RebalanceRepairSourceSHA256", digest(backup))
            metadata.add_text("RebalanceShiftXY", f"{dx},{dy}")
            metadata.add_text("PipLayoutAnchorXY", "375,525")
            candidate.parent.mkdir(parents=True, exist_ok=True)
            options = {"icc_profile": image.info["icc_profile"]} if image.info.get("icc_profile") else {}
            Image.fromarray(output).save(candidate, dpi=(300, 300), pnginfo=metadata, **options)
        with Image.open(candidate) as saved:
            if not np.array_equal(np.asarray(saved.convert("RGB")), output):
                raise ValueError("PNG round trip changed pixels")
        entry = dict(
            path=initial_entry["path"], rank=initial_entry["rank"], backup=initial_entry["backup"],
            candidate=candidate.relative_to(ROOT).as_posix(), shift_xy=[dx, dy],
            original_sha256=digest(backup), initial_glitched_sha256=initial_entry["after_sha256"],
            repaired_sha256=digest(candidate), after_anchor=list(after_anchor), after_centroid=after_centroid,
            movable_field_exact_after_nonwrapping_translation=True,
            exposed_strips_and_cartouches_preserved_from_original=True,
            shared_numeral_border_exact=True,
        )
        entries.append(entry)
        x = (index % 4) * 300
        y = (index // 4) * 430
        with Image.open(candidate) as candidate_image:
            thumbnail = candidate_image.resize((292, 409), Image.Resampling.LANCZOS)
        preview.paste(thumbnail, (x + 4, y + 22))
        draw.text((x + 7, y + 4), f"{path.parent.name} / {path.stem}", fill="#24231f")
    REPAIR_STAGE.mkdir(parents=True, exist_ok=True)
    report = dict(
        schema_version=1, canvas=[750, 1050], nominal_dpi=300,
        repair_of=REPORT.relative_to(ROOT).as_posix(), target_pip_layout_anchor=list(TARGET),
        coordinate_basis="zero-based rounded chroma-weighted mean of all turquoise pip-jewel centroids",
        method="non-wrapping whole-pixel translation from preserved originals; original pixels retained in exposed strips and fixed cartouches; shared numeral border copied under the established border mask",
        template_source=initial["template_source"], template_sha256=initial["template_sha256"],
        border_mask="scripts.align_courts.border_mask", movable_field_xyxy=list(INTERIOR),
        fixed_cartouches_xyxy=[list(panel) for panel in PANELS],
        cards=entries,
    )
    (REPAIR_STAGE / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    preview.save(REPAIR_STAGE / "preview-after.png")
    print("Staged 32 repaired numeral cards; active assets unchanged.")


def repair_apply() -> None:
    """Install only the verified non-wrapping repair candidates."""
    if REPAIR_REPORT.exists():
        raise FileExistsError("A numeral-rebalancing repair report already exists")
    report = json.loads((REPAIR_STAGE / "report.json").read_text(encoding="utf-8"))
    if digest(ROOT / report["template_source"]) != report["template_sha256"]:
        raise ValueError("Border template changed after repair staging")
    mask = border_mask()
    with Image.open(ROOT / report["template_source"]) as template_image:
        template = np.asarray(template_image.convert("RGB"))
    for entry in report["cards"]:
        path = ROOT / entry["path"]
        backup = ROOT / entry["backup"]
        candidate = ROOT / entry["candidate"]
        if digest(path) != entry["initial_glitched_sha256"]:
            raise ValueError(f"Active card differs from the recorded initial pass: {path}")
        if digest(backup) != entry["original_sha256"] or digest(candidate) != entry["repaired_sha256"]:
            raise ValueError(f"Repair source or candidate changed: {path}")
        dx, dy = entry["shift_xy"]
        with Image.open(backup) as image:
            original = np.asarray(image.convert("RGB"))
        translated, valid = nonwrapping_translate(original, dx, dy)
        with Image.open(candidate) as image:
            output = np.asarray(image.convert("RGB"))
        if not np.array_equal(output[~mask], translated[~mask]):
            raise ValueError(f"Non-wrapping translation check failed: {path}")
        if not np.array_equal(output[~valid & ~mask], original[~valid & ~mask]):
            raise ValueError(f"Exposed original pixels check failed: {path}")
        if not np.array_equal(output[mask], template[mask]):
            raise ValueError(f"Shared border check failed: {path}")
        if anchor(output, entry["rank"])[0] != TARGET:
            raise ValueError(f"Anchor check failed: {path}")
    for entry in report["cards"]:
        (ROOT / entry["path"]).write_bytes((ROOT / entry["candidate"]).read_bytes())
    REPAIR_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS: repaired 32 numeral layouts; no wraparound pixels; shared border exact.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--analyze", action="store_true")
    mode.add_argument("--stage", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--stage-repair", action="store_true")
    mode.add_argument("--apply-repair", action="store_true")
    args = parser.parse_args()
    if args.analyze:
        analyze()
    elif args.stage:
        stage()
    elif args.apply:
        apply()
    elif args.stage_repair:
        repair_stage()
    else:
        repair_apply()
