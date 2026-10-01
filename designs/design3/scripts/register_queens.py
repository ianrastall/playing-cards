"""Balance Celtic Queen review faces against the approved Kings' components."""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin
import register_kings as kings

ROOT = kings.ROOT
SOURCE = ROOT / 'sources/generated/queens-v1'
OUTPUT = ROOT / 'sources/components/queens-registration-v1'
DOC = ROOT / 'docs/design/queens-registration-v1.json'
SUITS = ('spades', 'hearts', 'diamonds', 'clubs')


def index(suit):
    layer = Image.new('RGBA', kings.SIZE)
    color = (173, 21, 30, 255) if suit in ('hearts', 'diamonds') else (17, 18, 16, 255)
    for text, bounds, center in [('Q', (49, 48), (69.5, 119.5)),
            ({'spades': '♠', 'hearts': '♥', 'diamonds': '♦', 'clubs': '♣'}[suit],
             (44, 47), (69.5, 181.5))]:
        sprite = kings.glyph(text, bounds, color)
        layer.alpha_composite(sprite, tuple(round(c-(n-1)/2) for c, n in zip(center, sprite.size)))
    return kings.symmetric(layer)


def compose(source, anchor, suit):
    frame = Image.open(kings.COMP / 'shared-frame.png').convert('RGBA')
    field = Image.open(kings.COMP / 'field-mask.png').convert('L')
    result = Image.composite(kings.joined(kings.mapped(source, anchor)).convert('RGBA'), frame, field)
    result.alpha_composite(index(suit))
    result.alpha_composite(Image.open(kings.COMP / 'paired-side-medallions.png'))
    result.alpha_composite(Image.open(kings.COMP / 'center-medallion.png'), (323, 473))
    result.putalpha(Image.open(kings.COMP / 'outline-mask.png'))
    return result


def build():
    cards, sources = [], []
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for suit in SUITS:
        path = SOURCE / f'queen-{suit}-v1.png'
        with Image.open(path) as image:
            # Fit at the same normalized location and scale as the Kings.
            normalized = image.resize((1060, 1484), kings.LANCZOS)
            fitted = kings.rim_center(normalized)
            anchor = [fitted[0] * (image.width-1)/1059, fitted[1] * (image.height-1)/1483]
            result = compose(image, anchor, suit)
            pixels = list(image.size)
        target = OUTPUT / f'{suit}/queen.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        info = PngImagePlugin.PngInfo()
        info.add_text('Renderer', 'design3-queens-registration-v1')
        info.add_text('Status', 'review')
        info.add_text('Center', json.dumps(kings.CENTER))
        result.save(target, dpi=(300, 300), pnginfo=info)
        sources.append(dict(rank='queen', suit=suit, format='poker', path=path.name,
                            pixels=pixels, sha256=kings.sha(path), status='review-source-master'))
        cards.append(dict(rank='queen', suit=suit, format='poker', status='review',
                          path=target.relative_to(OUTPUT).as_posix(), pixels=list(kings.SIZE),
                          sha256=kings.sha(target), source=path.relative_to(ROOT).as_posix(),
                          source_sha256=kings.sha(path), source_center=anchor,
                          center=list(kings.CENTER), half_turn_exact=True))
    kings.write_json(SOURCE / 'manifest.json', dict(renderer='built-in-imagegen', status='review', cards=sources))
    kings.write_json(OUTPUT / 'manifest.json', dict(status='review', cards=cards))
    kings.write_json(DOC, dict(renderer='design3-queens-registration-v1', status='review',
                              pixels=list(kings.SIZE), center=list(kings.CENTER),
                              components=[dict(path=p.relative_to(ROOT).as_posix(), sha256=kings.sha(p))
                                          for p in sorted(kings.COMP.glob('*.png'))], cards=cards))
    sheet = Image.new('RGB', (1560, 595), '#e9dfcf')
    draw = ImageDraw.Draw(sheet)
    for i, card in enumerate(cards):
        image = Image.open(OUTPUT / card['path']).resize((375, 525), kings.LANCZOS)
        sheet.paste(image, (i*390+7, 15), image)
        draw.text((i*390+20, 556), f"Queen of {card['suit'].title()}", fill='black')
    sheet.save(ROOT / 'docs/design/queens-v1-proof.png')
    audit()


def audit():
    spec = json.loads(DOC.read_text(encoding='utf-8'))
    assert [c['suit'] for c in spec['cards']] == list(SUITS)
    for component in spec['components']:
        assert kings.sha(ROOT / component['path']) == component['sha256']
    frame = np.array(Image.open(kings.COMP / 'shared-frame.png'))
    field = np.array(Image.open(kings.COMP / 'field-mask.png'))
    outline = np.array(Image.open(kings.COMP / 'outline-mask.png'))
    center = np.array(Image.open(kings.COMP / 'center-medallion.png'))
    reports = []
    for card in spec['cards']:
        source, path = ROOT / card['source'], OUTPUT / card['path']
        assert kings.sha(source) == card['source_sha256']
        assert kings.sha(path) == card['sha256']
        with Image.open(path) as image:
            assert image.mode == 'RGBA' and image.size == kings.SIZE
            assert all(abs(d-300) < .01 for d in image.info['dpi'])
            a = np.array(image)
        assert np.array_equal(a, a[::-1, ::-1]), path
        assert np.array_equal(a[:, :, 3], outline), path
        shared = (field == 0) & (np.array(index(card['suit']))[:, :, 3] == 0)
        assert np.array_equal(a[shared], frame[shared]), path
        opaque = center[:, :, 3] == 255
        assert np.array_equal(a[473:577, 323:427][opaque], center[opaque]), path
        with Image.open(source) as image:
            assert np.array_equal(a, np.array(compose(image, card['source_center'], card['suit']))), path
        reports.append(dict(suit=card['suit'], shared_border_exact=True, half_turn_exact=True,
                            center=list(kings.CENTER), source_hash_unchanged=True))
    kings.write_json(ROOT / 'docs/design/queens-registration-v1-audit.json', dict(status='passed', cards=reports))
    print('PASS four Queen review faces: shared King frame and center, half-turn, rounded alpha, 300 ppi, unchanged masters')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    audit() if args.check else build()
