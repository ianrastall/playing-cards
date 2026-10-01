"""Inspect unchanged transparent pip masters and render large/small review proofs."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'sources/components/pips-v1'
MANIFEST = SOURCE/'manifest.json'
SUITS = ('spades', 'hearts', 'diamonds', 'clubs')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measurements(path):
    with Image.open(path) as image:
        assert image.mode == 'RGBA', path
        a = np.array(image)
        alpha = a[:, :, 3]
        assert (alpha == 0).mean() > .1, f'Insufficient transparent exterior: {path}'
        assert (alpha >= 250).mean() > .2, f'Insufficient near-opaque body: {path}'
        # ImageGen's alpha includes faint edge residue and a near-opaque interior.
        # Inspect it honestly without modifying the original transparency.
        edge_max = int(max(alpha[0].max(), alpha[-1].max(), alpha[:, 0].max(), alpha[:, -1].max()))
        assert edge_max < 8, f'Visible artwork touches canvas edge: {path}'
        yy, xx = np.nonzero(alpha >= 128)
        bounds = [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)]
        weights = alpha.astype(float)
        rows, cols = np.indices(alpha.shape)
        centroid = [float((weights*cols).sum()/weights.sum()), float((weights*rows).sum()/weights.sum())]
        return dict(pixels=list(image.size), mode=image.mode, sha256=sha(path),
                    opaque_bounds=bounds, alpha_centroid=centroid,
                    transparent_fraction=float((alpha==0).mean()),
                    fully_opaque_fraction=float((alpha==255).mean()),
                    near_opaque_fraction=float((alpha>=250).mean()),
                    faint_alpha_pixels=int(((alpha>0)&(alpha<8)).sum()),
                    exterior_edge_max_alpha=edge_max, visible_edges_clear=True)


def build():
    cards = []
    sheet = Image.new('RGB', (1560, 550), '#eee5d5')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/times.ttf', 22)
    small_font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
    for i, suit in enumerate(SUITS):
        path = SOURCE/f'{suit}-master.png'
        data = measurements(path)
        cards.append(dict(rank='pip', suit=suit, title=f'{suit.title()} pip', format='poker',
                          path=path.name, status='review-component', prompt_file=f'{suit}-prompt.json', **data))
        with Image.open(path) as image:
            # Crop only the proof's copy; the saved master remains byte-for-byte unchanged.
            crop = image.crop(data['opaque_bounds'])
            large = crop.copy()
            large.thumbnail((340, 335), Image.Resampling.LANCZOS)
            x = i*390 + (390-large.width)//2
            sheet.paste(large, (x, 18+(335-large.height)//2), large)
            draw.text((i*390+20, 369), suit.title(), fill='#29251e', font=font)
            small = crop.resize((round(crop.width*100/crop.height), 100), Image.Resampling.LANCZOS)
            sheet.paste(small, (i*390+(390-small.width)//2, 415), small)
            draw.text((i*390+20, 527), '100 px silhouette preview', fill='#514a3c', font=small_font)
        assert sha(path) == data['sha256']
    MANIFEST.write_text(json.dumps(dict(generator='built-in image_gen', status='review-components',
                                       layout_policy='Preserve alpha and aspect ratio; bounds and alpha centroids are measured, not central-medallion anchors.',
                                       cards=cards), indent=2)+'\n', encoding='utf-8')
    sheet.save(ROOT/'docs/design/pips-v1-proof.png')
    audit()


def audit():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    assert [c['suit'] for c in manifest['cards']] == list(SUITS)
    for card in manifest['cards']:
        data = measurements(SOURCE/card['path'])
        assert all(card[key] == value for key, value in data.items()), card['path']
        prompt = json.loads((SOURCE/card['prompt_file']).read_text(encoding='utf-8'))
        assert prompt['transparent_background'] is True and prompt['prompt']
    print('PASS four unchanged large pip masters: RGBA, transparent exterior, near-opaque body, visible edge clearance, hashes and exact prompts')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    audit() if args.check else build()
