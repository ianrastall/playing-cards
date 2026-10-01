"""Install the ten balanced Celtic courts/Jokers into the Poker card hierarchy."""
import argparse
import json
import shutil
from PIL import Image
import numpy as np
import register_kings as common

ROOT = common.ROOT
MANIFESTS = ('sources/components/queens-registration-v1/manifest.json',
             'sources/components/jacks-jokers-registration-v1/manifest.json')
DOC = ROOT/'docs/design/installed-courts-v1.json'


def entries():
    for name in MANIFESTS:
        manifest = ROOT/name
        for card in json.loads(manifest.read_text(encoding='utf-8'))['cards']:
            source = manifest.parent/card['path']
            assert common.sha(source) == card['sha256'], source
            folder = 'jokers' if card['rank'] == 'joker' else card['suit']
            filename = card['suit'] if card['rank'] == 'joker' else card['rank']
            target = ROOT/f'cards/faces/french-suited/poker/{folder}/{filename}.png'
            yield card, source, target


def install():
    cards = list(entries())
    for card, source, target in cards:
        assert not target.exists() or common.sha(target) == card['sha256'], target
    for card, source, target in cards:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(source, target)
    common.write_json(DOC, dict(status='review', cards=[dict(rank=c['rank'], suit=c['suit'],
        source=s.relative_to(ROOT).as_posix(), path=t.relative_to(ROOT).as_posix(),
        sha256=c['sha256']) for c,s,t in cards]))
    audit()


def audit():
    cards = list(entries())
    assert len(cards) == 10
    assert {(c['rank'],c['suit']) for c,_,_ in cards} == {
        *((r,s) for r in ('queen','jack') for s in ('spades','hearts','diamonds','clubs')),
        ('joker','black'),('joker','red')}
    outline = np.array(Image.open(common.COMP/'outline-mask.png'))
    for card, source, target in cards:
        assert common.sha(target) == card['sha256'], target
        with Image.open(target) as im:
            assert im.mode == 'RGBA' and im.size == common.SIZE
            assert all(abs(d-300)<.01 for d in im.info['dpi'])
            a = np.array(im)
        assert np.array_equal(a,a[::-1,::-1])
        assert np.array_equal(a[:,:,3],outline)
    print('PASS ten installed courts/Jokers: exact copies, 300 ppi, rounded alpha and half-turn symmetry')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    audit() if args.check else install()
