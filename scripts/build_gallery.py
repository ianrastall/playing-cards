"""Build static, download-manager-friendly galleries from the selected artwork.

Run with --write after changing inventory, or --check to verify checked-in pages.
No image files are modified. Every original PNG is linked in the initial HTML.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
from html import escape
import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FORMATS = ['poker', 'bridge', 'european-standard', 'travel', 'jumbo', 'tarot']
SUITS = ['spades', 'hearts', 'diamonds', 'clubs', 'batons', 'cups', 'swords', 'coins']
RANKS = ['ace', *map(str, range(2, 11)), 'jack', 'knight', 'queen', 'king', 'joker']
COLORS = ['prussian-blue', 'verdigris', 'madder-lake', 'manganese-violet', 'lamp-black']


def label(value):
    return value.replace('-', ' ').title()


def inventory():
    catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    assets = []
    for entry in catalog['assets']:
        a = dict(entry)
        if a['side'] == 'back':
            a.update(group=f"{a['design']}-backs", title=label(a['color']), detail=f"{label(a['format'])} · Card back")
        else:
            title = a.get('title') or (f"{label(a['color_variant'])} Joker" if a['rank'] == 'joker' else f"{label(a['rank'])} of {label(a['suit'])}")
            group = f"design1-{a['format']}" if a['design'] == 'design1' else 'design2-numbers'
            a.update(group=group, title=title, detail=f"{label(a['format'])} · {a['pixels'][0]} × {a['pixels'][1]}")
        assets.append(a)

    # Use the selected masters listed in their manifests, never studies or initial passes.
    sources = [('courts-v1/kings-manifest.json', 'king'), ('courts-v1/queens-manifest.json', 'queen'),
               ('courts-v1/jacks-manifest.json', 'jack'), ('aces-v1/manifest.json', 'ace'),
               ('jokers-v1/manifest.json', 'joker')]
    for manifest_path, rank in sources:
        manifest_file = ROOT / 'designs/design2/sources/generated' / manifest_path
        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
        for entry in manifest['cards']:
            path = manifest_file.parent / (entry.get('path') or entry['file'])
            suit = entry.get('suit') or path.stem.split('-')[-1]
            title = f'{label(suit)} Joker' if rank == 'joker' else f'{label(rank)} of {label(suit)}'
            with Image.open(path) as image:
                size = list(image.size)
            assets.append(dict(id=f'design2.master.{rank}.{suit}', design='design2', group='design2-courts',
                               path=path.relative_to(ROOT).as_posix(), pixels=size, title=title,
                               rank=rank, suit=suit, format='poker', side='face', detail=f'Artwork master · {size[0]} × {size[1]}'))
    for fmt in FORMATS:
        for color in ['lamp-black', 'madder-lake']:
            path = ROOT / f'designs/design2/sources/components/design2-face-frames-v1/{fmt}/{color}.png'
            with Image.open(path) as image:
                size = list(image.size)
            assets.append(dict(id=f'design2.frame.{fmt}.{color}', design='design2', group='face-frames',
                               path=path.relative_to(ROOT).as_posix(), pixels=size, title=f'{label(color)} frame',
                               format=fmt, color=color, side='frame', detail=f'{label(fmt)} · Blank face'))
    assert len({a['path'] for a in assets}) == len(assets), 'Duplicate gallery artwork'
    return assets


def order(a):
    return (FORMATS.index(a['format']), SUITS.index(a['suit']) if a.get('suit') in SUITS else 99,
            RANKS.index(a['rank']) if a.get('rank') in RANKS else int(a.get('number', 99)),
            COLORS.index(a['color']) if a.get('color') in COLORS else 99, a['path'])


def render(page, assets, design=None, numbers_only=False):
    def url(path):
        return escape(os.path.relpath(ROOT / path, page.parent).replace(os.sep, '/'), quote=True)

    def card(a):
        src = url(a['path'])
        w, h = a['pixels']
        filename = escape(a['id'].replace('.', '-') + '.png', quote=True)
        title, detail = escape(a['title']), escape(a['detail'])
        return f'''<figure class="artwork" data-design="{a['design']}">
<a class="artwork-image" href="{src}" data-artwork="{a['id']}" data-title="{title}" data-detail="{detail}" aria-label="View {title}, {detail}"><img src="{src}" alt="{title}" width="{w}" height="{h}" loading="lazy" decoding="async"></a>
<figcaption><span class="artwork-title">{title}</span><span class="artwork-detail">{detail}</span><a class="save" href="{src}" download="{filename}" aria-label="Download {title}, {detail}">PNG <span aria-hidden="true">↓</span></a></figcaption>
</figure>'''

    groups = OrderedDict()
    groups['design1-backs'] = ('Card backs', 'Five colorways, each in six formats.')
    for fmt in FORMATS:
        groups[f'design1-{fmt}'] = ('Tarot' if fmt == 'tarot' else f'{label(fmt)} faces',
                                   'The complete 78-card deck, including the major arcana.' if fmt == 'tarot' else 'Every suit, from ace to king, plus both Jokers.')
    groups.update({'design2-courts': ('Courts, aces & Jokers', 'All eighteen selected artworks, presented as full-resolution masters.'),
                   'design2-numbers': ('Number cards', 'Ranks 2–10 in all four suits. Poker format, with gold lotus borders.'),
                   'design2-backs': ('Card backs', 'Olive foliage and a beaded gold panel. Five colorways in six formats.'),
                   'face-frames': ('Blank face frames', 'Open ivory fields with gold lotus ornament, in all six formats.')})
    chosen = [a for a in assets if (design is None or a['design'] == design) and (not numbers_only or a['group'] == 'design2-numbers')]
    designs = [d for d in ['design1', 'design2'] if any(a['design'] == d for a in chosen)]
    title = 'Playing Cards' if design is None else 'Design 1 · Botanical ornament' if design == 'design1' else 'Design 2 · Lotus & silk'
    if numbers_only:
        title = 'Design 2 · Number cards'
    heading = 'The art of<br>the playing card.' if design is None else 'Botanical<br>ornament.' if design == 'design1' else 'Lotus &amp; silk.'
    if numbers_only:
        heading = 'Lotus<br>number cards.'
    intro = ('Two illustrated collections. Rich botanical fields, painted courts, and ornament made to be held in the hand.' if design is None else
             'Morris, Mucha, and Safavid-inspired ornament. A complete French-suited collection and a full Tarot deck.' if design == 'design1' else
             'Ming and Tang-inspired florals, olive acanthus leaves, and beaded gold. Courts, aces, Jokers, and every number card.')
    if numbers_only:
        intro = 'All four suits together, with open ivory fields and gold lotus borders. Open any card to inspect it or turn it over.'
    hero_design = design or 'design2'
    hero_back = next(a for a in assets if a['id'] == f'{hero_design}.back.poker.prussian-blue')
    hero_face = next(a for a in assets if a['id'] == ('design2.master.king.spades' if hero_design == 'design2' else 'design1.face.french-suited.poker.spades.king'))
    if numbers_only:
        hero_face = next(a for a in chosen if a['rank'] == '10' and a['suit'] == 'spades')
        hero_back = next(a for a in chosen if a['rank'] == '3' and a['suit'] == 'hearts')
    content = []
    for d in designs:
        design_assets = [a for a in chosen if a['design'] == d]
        name = 'Botanical ornament' if d == 'design1' else 'Lotus & silk'
        description = 'Morris · Mucha · Safavid' if d == 'design1' else 'Ming · Tang · Silk florals'
        jumps = ''.join(f'<a href="#{key}">{escape(info[0])}</a>' for key, info in groups.items() if any(a['group'] == key for a in design_assets))
        content.append(f'<section class="collection" id="{d}" aria-labelledby="{d}-title"><header class="collection-header"><div><p class="eyebrow">Design 0{d[-1]} / {description}</p><h2 id="{d}-title">{escape(name)}</h2></div><p class="collection-count">{len(design_assets)} artworks</p></header><nav class="section-links" aria-label="{d} sections">{jumps}</nav>')
        for key, (name, description) in groups.items():
            entries = sorted([a for a in design_assets if a['group'] == key], key=order)
            if not entries:
                continue
            content.append(f'<section class="artwork-section" id="{key}" aria-labelledby="{key}-title"><header class="group-header"><div><h3 id="{key}-title">{escape(name)}</h3><p>{escape(description)}</p></div><span class="group-count">{len(entries):02d} works</span></header><div class="artwork-grid">')
            content.extend(card(a) for a in entries)
            content.append('</div></section>')
        content.append('</section>')
    jump_links = ''.join(f'<a href="#{d}">Design 0{d[-1]} <span aria-hidden="true">↘</span></a>' for d in designs)
    collection_link = f'<a href="{url("index.html")}">Full collection</a>' if design else '<a href="#collection">Browse the collection <span aria-hidden="true">↓</span></a>'
    hero_images = ''.join(f'<a href="{url(a["path"])}" aria-label="Open {escape(a["title"])}"><img src="{url(a["path"])}" width="{a["pixels"][0]}" height="{a["pixels"][1]}" alt="{escape(a["title"])}" fetchpriority="high"></a>' for a in [hero_back, hero_face])
    collection_note = 'All selected artwork is below. Every PNG is linked at its original resolution, ready for individual or bulk downloading.'
    return f'''<!doctype html>
<!-- Generated by scripts/build_gallery.py; edit the builder or shared gallery assets. -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="description" content="An illustrated playing-card collection. Browse and download every selected card, court, ace, Joker, and back on one page.">
<title>{escape(title)} — The Card Studio</title><link rel="icon" href="data:,">
<link rel="stylesheet" href="{url('assets/gallery.css')}"><script src="{url('assets/gallery.js')}" defer></script></head>
<body><a class="skip-link" href="#collection">Skip to all artwork</a>
<header class="site-header"><a class="wordmark" href="{url('index.html')}"><span class="brand-mark" aria-hidden="true">✦</span> THE CARD STUDIO</a><nav aria-label="Collection navigation"><a href="{url('index.html')}#design1">Design 01</a><a href="{url('index.html')}#design2">Design 02</a><a href="https://github.com/ianrastall/playing-cards">GitHub <span aria-hidden="true">↗</span></a></nav></header>
<main><section class="hero" aria-labelledby="page-title"><div class="hero-copy"><p class="eyebrow">An illustrated collection</p><h1 id="page-title">{heading}</h1><p class="intro">{intro}</p><div class="hero-links">{collection_link}</div><p class="hero-meta">{len(chosen)} artworks <span>·</span> Original PNGs <span>·</span> MIT licensed</p></div><div class="viewing-table"><div class="hero-art">{hero_images}</div><p>On the viewing table <span>Design 0{hero_design[-1]}</span></p></div></section>
<section class="collection-intro" id="collection" aria-label="Browse artwork"><div><p class="eyebrow">The complete gallery</p><p>{collection_note}</p></div><nav aria-label="Jump to a design">{jump_links}</nav></section>
{''.join(content)}
</main><footer class="site-footer"><div><a class="wordmark" href="{url('index.html')}">THE CARD STUDIO</a><p>Made to be looked at. Made to be played.</p></div><nav aria-label="Resources"><a href="{url('README.md')}">Collection guide</a><a href="{url('catalog.json')}">Production catalog</a><a href="{url('LICENSE')}">MIT License</a><a href="#page-title">Back to top ↑</a></nav></footer>
<dialog class="viewer" aria-labelledby="viewer-title"><div class="viewer-shell"><header class="viewer-header"><div><h2 id="viewer-title"></h2><p id="viewer-detail"></p></div><button type="button" id="viewer-close" aria-label="Close artwork viewer">Close <span aria-hidden="true">×</span></button></header><div class="viewer-stage"><img id="viewer-image" alt=""></div><div class="viewer-controls"><button type="button" id="viewer-prev" aria-label="Previous artwork">← Previous</button><span id="viewer-position" role="status"></span><button type="button" id="viewer-next" aria-label="Next artwork">Next →</button><button type="button" id="viewer-turn" aria-pressed="false">Turn 180°</button><a id="viewer-download" download>Download PNG ↓</a><a id="viewer-original">Open original ↗</a></div></div></dialog>
</body></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    assets = inventory()
    pages = [('index.html', None, False), ('designs/design1/index.html', 'design1', False),
             ('designs/design2/index.html', 'design2', False), ('designs/design2/number-cards.html', 'design2', True)]
    for relative, design, numbers_only in pages:
        path = ROOT / relative
        html = render(path, assets, design, numbers_only)
        if args.write:
            path.write_text(html, encoding='utf-8', newline='\n')
        elif not path.exists() or path.read_text(encoding='utf-8') != html:
            raise SystemExit(f'Stale gallery: {relative}; run python scripts/build_gallery.py --write')
        print(f'PASS {relative}: {html.count("data-artwork=")} original PNG links in static HTML')


if __name__ == '__main__':
    main()
