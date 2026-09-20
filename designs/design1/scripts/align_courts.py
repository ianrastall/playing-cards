"""Align court-card dot anchor pixels and reuse an existing ornamental border.

No image generation, scaling, interpolation or figure redraw. Run --stage,
inspect work/court-alignment/preview-after.png, then --apply.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
FACES = ROOT / "cards/faces/french-suited/poker"
BACKUPS = ROOT / "sources/before-court-alignment/poker"
STAGE = ROOT / "work/court-alignment"
REPORT = ROOT / "docs/design/court-alignment.json"
TARGET = (375, 525)
# Exclusive right/bottom coordinates. Preserve the card-specific index panels.
INTERIOR = (75, 72, 675, 967)
PANELS = ((28, 44, 132, 290), (618, 760, 722, 1008))
TEMPLATE = "spades/king.png"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dot_center(pixels):
    # Isolate the turquoise jewel from ivory petals and gold ring.
    roi = pixels[515:536, 365:386, :3].astype(float)
    r, g, b = roi.transpose(2, 0, 1)
    mask = (g-r > 18) & (b-r > 18) & (g > 65)
    if not 8 <= int(mask.sum()) <= 100:
        raise ValueError("Unexpected center-dot segmentation")
    weight = np.minimum(g-r, b-r) * mask
    yy, xx = np.indices(mask.shape)
    centroid = ((xx*weight).sum()/weight.sum()+365,
                (yy*weight).sum()/weight.sum()+515)
    anchor = tuple(int(np.floor(v+.5)) for v in centroid)
    return anchor, [round(float(v), 6) for v in centroid]


def border_mask():
    mask = np.ones((1050, 750), dtype=bool)
    x0, y0, x1, y1 = INTERIOR
    mask[y0:y1, x0:x1] = False
    for x0, y0, x1, y1 in PANELS:
        mask[y0:y1, x0:x1] = False
    return mask


def stage():
    paths = sorted(p for p in FACES.rglob("*.png") if p.stem in ("king", "queen", "jack"))
    if len(paths) != 12:
        raise ValueError("Expected all twelve court cards")
    if REPORT.exists():
        raise FileExistsError("Alignment already recorded; use a separately versioned pass")
    mask = border_mask()
    template = np.asarray(Image.open(FACES / TEMPLATE).convert("RGB"))
    entries = []
    for path in paths:
        rel = path.relative_to(FACES)
        backup = BACKUPS / rel
        if backup.exists() and digest(backup) != digest(path):
            raise ValueError(f"Existing backup differs: {backup}")
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        with Image.open(backup) as im:
            if im.size != (750, 1050) or im.mode != "RGB":
                raise ValueError(f"Unexpected image geometry/mode: {path}")
            pixels = np.asarray(im)
            anchor, centroid = dot_center(pixels)
            dx, dy = TARGET[0]-anchor[0], TARGET[1]-anchor[1]
            if max(abs(dx), abs(dy)) > 3:
                raise ValueError("Larger than expected translation; inspect before proceeding")
            # roll is exact integer indexing. Wrapped edge pixels are covered by mask.
            translated = np.roll(pixels, (dy, dx), axis=(0, 1))
            output = translated.copy()
            output[mask] = template[mask]
            after_anchor, after_centroid = dot_center(output)
            if after_anchor != TARGET:
                raise ValueError("Dot anchor alignment failed")
            if not np.array_equal(output[~mask], translated[~mask]):
                raise ValueError("Court/index pixels altered beyond translation")
            if not np.array_equal(output[mask], template[mask]):
                raise ValueError("Shared border differs")
            info = PngImagePlugin.PngInfo()
            for key, value in im.text.items():
                info.add_text(key, str(value))
            info.add_text("AlignmentSourceSHA256", digest(backup))
            info.add_text("AlignmentShiftXY", f"{dx},{dy}")
            info.add_text("DotAnchorXY", "375,525")
            options = {"icc_profile": im.info["icc_profile"]} if im.info.get("icc_profile") else {}
            candidate = STAGE / "candidates" / rel
            candidate.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(output).save(candidate, dpi=(300,300), pnginfo=info, **options)
        with Image.open(candidate) as saved:
            if not np.array_equal(np.asarray(saved), output):
                raise ValueError("PNG round-trip altered pixels")
        entries.append(dict(path=path.relative_to(ROOT).as_posix(),
                            backup=backup.relative_to(ROOT).as_posix(),
                            candidate=candidate.relative_to(ROOT).as_posix(),
                            before_sha256=digest(backup), after_sha256=digest(candidate),
                            before_dot_anchor=list(anchor), before_dot_centroid=centroid,
                            shift_xy=[dx,dy], after_dot_anchor=list(after_anchor),
                            after_dot_centroid=after_centroid,
                            court_pixels_exact_after_integer_translation=True,
                            shared_border_pixels_exact=True))
        print(f"{rel}: {anchor} -> {TARGET}; translation ({dx:+d},{dy:+d})")
    report = dict(schema_version=1, canvas=[750,1050], target_dot_anchor=list(TARGET),
                  coordinate_basis="Zero-based pixel column,row; rounded chroma-weighted dot centroid",
                  subpixel_note="Original painted dots differ in shading and shape; floating centroids are retained, not forced equal by resampling.",
                  method="Whole-pixel translation; shared existing border copied outside protected interior/index panels",
                  template_backup=(BACKUPS/TEMPLATE).relative_to(ROOT).as_posix(),
                  protected_interior_xyxy=list(INTERIOR),
                  protected_index_panels_xyxy=[list(b) for b in PANELS],
                  changed_pixels_allowed="Only integer translation plus replacement inside the common border mask",
                  cards=entries)
    STAGE.mkdir(parents=True, exist_ok=True)
    (STAGE/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    sheet=Image.new("RGB",(1100,1245),"#e7e2d7")
    draw=ImageDraw.Draw(sheet)
    for i,e in enumerate(entries):
        x=(i%4)*275; y=(i//4)*415
        with Image.open(ROOT/e["candidate"]) as im:
            view=im.resize((265,371),Image.Resampling.LANCZOS)
        sheet.paste(view,(x+5,y+27))
        draw.text((x+8,y+7),str(Path(e["path"]).parent.name)+" / "+Path(e["path"]).stem,fill="#24231f")
    sheet.save(STAGE/"preview-after.png")
    print("Staged all twelve. Original active assets unchanged.")


def apply():
    if REPORT.exists():
        raise FileExistsError("Alignment report exists; refusing a repeated application")
    report=json.loads((STAGE/"report.json").read_text(encoding="utf-8"))
    mask=border_mask()
    template=np.asarray(Image.open(ROOT/report["template_backup"]).convert("RGB"))
    # Preflight every file before changing any active asset.
    for e in report["cards"]:
        path=ROOT/e["path"]; backup=ROOT/e["backup"]; candidate=ROOT/e["candidate"]
        if digest(path)!=e["before_sha256"] or digest(backup)!=e["before_sha256"]:
            raise ValueError(f"Active input or backup changed: {path}")
        if digest(candidate)!=e["after_sha256"]:
            raise ValueError(f"Candidate changed: {candidate}")
        before=np.asarray(Image.open(backup))
        after=np.asarray(Image.open(candidate))
        dx,dy=e["shift_xy"]
        translated=np.roll(before,(dy,dx),axis=(0,1))
        if not np.array_equal(after[~mask],translated[~mask]):
            raise ValueError("Protected pixels differ")
        if not np.array_equal(after[mask],template[mask]) or dot_center(after)[0]!=TARGET:
            raise ValueError("Border or dot verification failed")
    for e in report["cards"]:
        (ROOT/e["path"]).write_bytes((ROOT/e["candidate"]).read_bytes())
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("PASS: all 12 anchors aligned; shared border exact; protected court/index pixels retained by translation.")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--stage",action="store_true")
    group.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    stage() if args.stage else apply()
