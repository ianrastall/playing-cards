"""Balance six Celtic Jack/Joker review faces with the approved common court layout."""
import argparse
import json
import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin
import register_kings as kings

ROOT = kings.ROOT
OUTPUT = ROOT / 'sources/components/jacks-jokers-registration-v1'
DOC = ROOT / 'docs/design/jacks-jokers-registration-v1.json'
IDENTITIES = [('jack', s) for s in ('spades', 'hearts', 'diamonds', 'clubs')] + [('joker', c) for c in ('black', 'red')]


def index(rank, identity):
    layer = Image.new('RGBA', kings.SIZE)
    color = (173, 21, 30, 255) if identity in ('hearts', 'diamonds', 'red') else (17, 18, 16, 255)
    if rank == 'joker':
        # Five letters fit the existing cream index panel without a suit pip.
        entries = [(letter, (27, 20), (69.5, 101.5 + i*24)) for i, letter in enumerate('JOKER')]
    else:
        entries = [('J', (49, 48), (69.5, 119.5)),
                   ({'spades': '♠', 'hearts': '♥', 'diamonds': '♦', 'clubs': '♣'}[identity],
                    (44, 47), (69.5, 181.5))]
    for text, bounds, center in entries:
        sprite = kings.glyph(text, bounds, color)
        layer.alpha_composite(sprite, tuple(round(c-(n-1)/2) for c, n in zip(center, sprite.size)))
    return kings.symmetric(layer)


def compose(source, anchor, rank, identity):
    frame = Image.open(kings.COMP / 'shared-frame.png').convert('RGBA')
    field = Image.open(kings.COMP / 'field-mask.png').convert('L')
    result = Image.composite(kings.joined(kings.mapped(source, anchor)).convert('RGBA'), frame, field)
    result.alpha_composite(index(rank, identity))
    result.alpha_composite(Image.open(kings.COMP / 'paired-side-medallions.png'))
    result.alpha_composite(Image.open(kings.COMP / 'center-medallion.png'), (323, 473))
    result.putalpha(Image.open(kings.COMP / 'outline-mask.png'))
    return result


def build():
    cards, sources = [], {'jack': [], 'joker': []}
    for rank, identity in IDENTITIES:
        source_dir = ROOT / f'sources/generated/{rank}s-v1'
        source = source_dir / f'{rank}-{identity}-v1.png'
        with Image.open(source) as image:
            fitted = kings.rim_center(image.resize((1060, 1484), kings.LANCZOS))
            anchor = [fitted[0]*(image.width-1)/1059, fitted[1]*(image.height-1)/1483]
            result = compose(image, anchor, rank, identity)
            pixels = list(image.size)
        target = OUTPUT / rank / f'{identity}.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        info = PngImagePlugin.PngInfo()
        info.add_text('Renderer', 'design3-jacks-jokers-registration-v1')
        info.add_text('Status', 'review')
        info.add_text('Center', json.dumps(kings.CENTER))
        result.save(target, dpi=(300, 300), pnginfo=info)
        title = f'Jack of {identity.title()}' if rank == 'jack' else f'{identity.title()} Joker'
        sources[rank].append(dict(rank=rank, suit=identity, title=title, format='poker',
                                  path=source.name, pixels=pixels, sha256=kings.sha(source),
                                  prompt_file=f'{rank}-{identity}-prompt.json', status='review-source-master'))
        cards.append(dict(rank=rank, suit=identity, title=title, format='poker', status='review',
                          path=target.relative_to(OUTPUT).as_posix(), pixels=list(kings.SIZE),
                          sha256=kings.sha(target), source=source.relative_to(ROOT).as_posix(),
                          source_sha256=kings.sha(source), source_center=anchor,
                          center=list(kings.CENTER), half_turn_exact=True))
    for rank, records in sources.items():
        kings.write_json(ROOT / f'sources/generated/{rank}s-v1/manifest.json',
                         dict(generator='built-in image_gen', status='review', cards=records))
    kings.write_json(OUTPUT / 'manifest.json', dict(status='review', cards=cards))
    kings.write_json(DOC, dict(renderer='design3-jacks-jokers-registration-v1', status='review',
                              pixels=list(kings.SIZE), center=list(kings.CENTER),
                              components=[dict(path=p.relative_to(ROOT).as_posix(), sha256=kings.sha(p))
                                          for p in sorted(kings.COMP.glob('*.png'))], cards=cards))
    proof(cards[:4], 'jacks-v1-proof.png')
    proof(cards[4:], 'jokers-v1-proof.png')
    audit()


def proof(cards, name):
    sheet = Image.new('RGB', (390*len(cards), 595), '#e9dfcf')
    draw = ImageDraw.Draw(sheet)
    for i, card in enumerate(cards):
        image = Image.open(OUTPUT/card['path']).resize((375, 525), kings.LANCZOS)
        sheet.paste(image, (i*390+7, 15), image)
        draw.text((i*390+20, 556), card['title'], fill='black')
    sheet.save(ROOT/'docs/design'/name)


def audit():
    spec = json.loads(DOC.read_text(encoding='utf-8'))
    assert [(c['rank'], c['suit']) for c in spec['cards']] == IDENTITIES
    for component in spec['components']:
        assert kings.sha(ROOT/component['path']) == component['sha256']
    frame = np.array(Image.open(kings.COMP/'shared-frame.png'))
    field = np.array(Image.open(kings.COMP/'field-mask.png'))
    outline = np.array(Image.open(kings.COMP/'outline-mask.png'))
    medallion = np.array(Image.open(kings.COMP/'center-medallion.png'))
    reports = []
    for card in spec['cards']:
        path, source = OUTPUT/card['path'], ROOT/card['source']
        assert kings.sha(path) == card['sha256']
        assert kings.sha(source) == card['source_sha256']
        with Image.open(path) as image:
            assert image.mode == 'RGBA' and image.size == kings.SIZE
            assert all(abs(d-300)<.01 for d in image.info['dpi'])
            a = np.array(image)
        assert np.array_equal(a, a[::-1, ::-1]), path
        assert np.array_equal(a[:, :, 3], outline), path
        shared = (field == 0) & (np.array(index(card['rank'], card['suit']))[:, :, 3] == 0)
        assert np.array_equal(a[shared], frame[shared]), path
        opaque = medallion[:, :, 3] == 255
        assert np.array_equal(a[473:577, 323:427][opaque], medallion[opaque]), path
        with Image.open(source) as image:
            assert np.array_equal(a, np.array(compose(image, card['source_center'], card['rank'], card['suit']))), path
        reports.append(dict(title=card['title'], shared_border_exact=True, half_turn_exact=True,
                            center=list(kings.CENTER), source_hash_unchanged=True))
    kings.write_json(ROOT/'docs/design/jacks-jokers-registration-v1-audit.json', dict(status='passed', cards=reports))
    print('PASS six Celtic Jack/Joker review faces: common border, exact center, half-turn, alpha, 300 ppi and source hashes')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    audit() if args.check else build()
