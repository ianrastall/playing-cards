"""Build static, download-manager-friendly galleries from the selected artwork.

Run with --write after changing inventory, or --check to verify checked-in pages.
No image files are modified. Every original PNG is linked in the initial HTML.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
from functools import lru_cache
import hashlib
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


@lru_cache(maxsize=None)
def revision(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:16]


def page_specs():
    yield 'index.html', {}
    yield 'all.html', {'all_artwork': True}
    for design in ['design1', 'design2']:
        yield f'designs/{design}/index.html', {'design': design}
        yield f'designs/{design}/all.html', {'design': design, 'all_artwork': True}
        for fmt in FORMATS:
            yield f'designs/{design}/{fmt}.html', {'design': design, 'fmt': fmt}
    yield 'designs/design2/masters.html', {'design': 'design2', 'masters_only': True}
    yield 'designs/design2/number-cards.html', {'design': 'design2', 'numbers_only': True}


def render(page, assets, design=None, numbers_only=False, fmt=None, all_artwork=False, masters_only=False):
    def url(path):
        relative = os.path.relpath(ROOT / path, page.parent).replace(os.sep, '/')
        if Path(path).suffix in {'.png', '.css', '.js'}:
            relative += '?v=' + revision(path)
        return escape(relative, quote=True)

    chooser = not (numbers_only or fmt or all_artwork or masters_only)

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
    groups['design1-backs'] = ('Card backs', 'Five back colors.')
    for size in FORMATS:
        groups[f'design1-{size}'] = ('Tarot' if size == 'tarot' else f'{label(size)} faces',
                                    'The complete 78-card deck, including the major arcana.' if size == 'tarot' else 'Every suit, from ace to king, plus both Jokers.')
    groups.update({'design2-courts': ('Courts, aces & Jokers', '18 artwork masters at their original dimensions.'),
                   'design2-numbers': ('Number cards', 'Ranks 2–10 in all four suits. Poker format, with gold lotus borders.'),
                   'design2-backs': ('Card backs', 'Current toranj backs in five colors.'),
                   'face-frames': ('Blank face frames', 'Blank card templates in Lamp Black and Madder Lake.')})
    chosen = [a for a in assets if (design is None or a['design'] == design)
              and (not numbers_only or a['group'] == 'design2-numbers')
              and (not fmt or (a['format'] == fmt and '.master.' not in a['id']))
              and (not masters_only or '.master.' in a['id'])]
    designs = [d for d in ['design1', 'design2'] if any(a['design'] == d for a in chosen)]
    title = 'Playing Cards' if design is None else f'Design {design[-1]}'
    if numbers_only:
        title = 'Design 2 · Number cards'
    heading = 'Playing cards' if design is None else f'Design {design[-1]}'
    if numbers_only:
        heading = 'Number cards'
    intro = ('Two card designs available as PNG files.' if design is None else
             'French-suited cards in five sizes, a 78-card Tarot deck, and five back colors in each size.' if design == 'design1' else
             'Backs in six sizes, Poker number cards, blank face frames, and court, ace, and Joker artwork masters.')
    if numbers_only:
        intro = '36 Poker cards: ranks 2–10 in all four suits. Open a card to view, rotate, or download it.'
    if fmt:
        title = f'Design {design[-1]} · {label(fmt)}'
        heading = f'{label(fmt)} cards'
        intro = ('The complete Tarot deck and five matching backs.' if fmt == 'tarot' else 'Every suit, both Jokers, and five matching backs.') if design == 'design1' else (
            '36 number faces, five toranj backs, and two blank face frames. Court, ace, and Joker masters are available separately.' if fmt == 'poker' else
            'Five toranj backs and two blank face frames. Finished faces are not yet available in this size.')
    if masters_only:
        title = 'Design 2 · Artwork masters'
        heading = 'Artwork masters'
        intro = 'Eighteen selected courts, aces, and Jokers at their original dimensions. These are artwork masters, not finished size-specific cards.'
    if all_artwork:
        title = f'Design {design[-1]} · All files' if design else 'All files'
        heading = f'Design {design[-1]}: all files' if design else 'All files'
        intro = 'All sizes on one page, with direct PNG links for bulk downloading. Search by name, suit, or color to find individual cards.'
    if chooser:
        intro += ' Choose a size to browse individual cards, or open the full gallery for bulk downloading.' if design else ' Choose a design, then a card size.'
    hero_design = design or 'design2'
    hero_back = next(a for a in assets if a['id'] == f'{hero_design}.back.{fmt or "poker"}.prussian-blue')
    hero_face = next(a for a in assets if a['id'] == ('design2.master.king.spades' if hero_design == 'design2' else 'design1.face.french-suited.poker.spades.king'))
    if numbers_only:
        hero_face = next(a for a in chosen if a['rank'] == '10' and a['suit'] == 'spades')
        hero_back = next(a for a in chosen if a['rank'] == '3' and a['suit'] == 'hearts')
    if fmt:
        hero_face = next((a for a in chosen if a.get('rank') == 'king' and a.get('suit') == 'spades'), None) or next(
            (a for a in chosen if a['side'] == 'face'), None) or next(a for a in chosen if a['side'] == 'frame')
    content = []
    for d in ([] if chooser else designs):
        design_assets = [a for a in chosen if a['design'] == d]
        name = f'Design {d[-1]}'
        jumps = ''.join(f'<a href="#{key}">{escape(info[0])}</a>' for key, info in groups.items() if any(a['group'] == key for a in design_assets))
        content.append(f'<section class="collection" id="{d}" aria-labelledby="{d}-title"><header class="collection-header"><div><h2 id="{d}-title">{escape(name)}</h2></div><p class="collection-count">{len(design_assets)} artworks</p></header><nav class="section-links" aria-label="{d} sections">{jumps}</nav>')
        for key, (name, description) in groups.items():
            entries = sorted([a for a in design_assets if a['group'] == key], key=order)
            if not entries:
                continue
            content.append(f'<section class="artwork-section" id="{key}" aria-labelledby="{key}-title"><header class="group-header"><div><h3 id="{key}-title">{escape(name)}</h3><p>{escape(description)}</p></div><span class="group-count">{len(entries):02d} works</span></header><div class="artwork-grid">')
            content.extend(card(a) for a in entries)
            content.append('</div></section>')
        content.append('</section>')
    if chooser and not design:
        content.append('<div class="design-options">')
        for d, name, description in [('design1', 'Design 1', 'French-suited decks in five sizes and a 78-card Tarot deck. Five back colors in each size.'),
                                     ('design2', 'Design 2', 'Backs in six sizes, Poker number cards, blank face frames, and artwork masters.')]:
            back = next(a for a in assets if a['id'] == f'{d}.back.poker.prussian-blue')
            content.append(f'<a class="design-option" id="{d}" href="{url(f"designs/{d}/index.html")}"><img src="{url(back["path"])}" width="750" height="1050" alt="Design {d[-1]} Prussian Blue back" loading="lazy"><div><h2>{escape(name)}</h2><p>{description}</p><span class="choice-action">Choose a size →</span></div></a>')
        content.append('</div>')
    elif chooser:
        formats = json.loads((ROOT / f'designs/{design}/deck.json').read_text(encoding='utf-8'))['formats']
        content.append('<div class="size-options">')
        for size in FORMATS:
            spec = formats[size]
            width, height = spec['trim_inches']
            pixels = spec['back_pixels']
            count = sum(a['format'] == size and '.master.' not in a['id'] for a in chosen)
            availability = ('78 faces · 5 backs' if size == 'tarot' else '54 faces · 5 backs') if design == 'design1' else ('36 number faces · 5 backs · 2 blank frames' if size == 'poker' else '5 backs · 2 blank frames · No finished faces')
            content.append(f'<a class="size-option" href="{url(f"designs/{design}/{size}.html")}"><h2>{label(size)}</h2><p class="size-dimensions">{width:g} × {height:g} in <span>·</span> {pixels[0]} × {pixels[1]} px</p><p>{availability}</p><span class="choice-action">Browse {count} artworks →</span></a>')
        content.append('</div>')
    jump_links = f'<a href="{url(f"designs/{design}/index.html")}">Change size</a>' if design and not chooser else ''
    if fmt:
        jump_links += '<details class="size-switch"><summary>Jump to another size</summary><nav aria-label="Other sizes">' + ''.join(
            f'<a href="{url(f"designs/{design}/{size}.html")}"' + (' aria-current="page"' if size == fmt else '') + f'>{label(size)}</a>' for size in FORMATS) + '</nav></details>'
    collection_link = '<a href="#collection">Choose a size ↓</a>' if chooser and design else '<a href="#collection">Choose a design ↓</a>' if chooser else '<a href="#collection">Browse cards ↓</a>'
    hero_images = ''.join(f'<a href="{url(a["path"])}" aria-label="Open {escape(a["title"])}"><img src="{url(a["path"])}" width="{a["pixels"][0]}" height="{a["pixels"][1]}" alt="{escape(a["title"])}" fetchpriority="high"></a>' for a in [hero_back, hero_face])
    collection_note = 'Choose your format before opening the cards. Dimensions are trim size at nominal 300 ppi.' if chooser and design else 'Each design has its own size picker and galleries.' if chooser else 'Open a card to inspect or turn it. Save individual PNGs, or use a download manager on this page’s original image links.'
    section_title = 'Choose a size' if chooser and design else 'Choose a design' if chooser else 'Browse artwork'
    bulk_target = f'designs/{design}/all.html' if design else 'all.html'
    bulk_label = 'Open every size in this design' if design else f'Open all {len(assets)} artworks'
    if not all_artwork:
        collection_link += f'<a href="{url(bulk_target)}">Bulk download gallery →</a>'
    bulk = f'<aside class="download-options" aria-label="More ways to browse"><div><h2>Bulk downloads</h2><p>Open all sizes on one page to download the PNGs with a download manager.</p><a href="{url(bulk_target)}">{bulk_label} →</a></div>'
    if design == 'design2':
        bulk += f'<div><h2>Courts, aces &amp; Jokers</h2><p>Browse 18 selected artwork masters at their original dimensions.</p><a href="{url("designs/design2/masters.html")}">Browse artwork masters →</a></div>'
    bulk += '</aside>'
    if all_artwork:
        bulk = ''
    search = '' if chooser else '<div class="gallery-search" hidden><label for="card-search">Find a card</label><input id="card-search" type="search" placeholder="Try queen, hearts, or Prussian Blue" autocomplete="off"><p id="search-count" role="status"></p></div>'
    return f'''<!doctype html>
<!-- Generated by scripts/build_gallery.py; edit the builder or shared gallery assets. -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="description" content="Playing-card PNG files in two designs and six sizes. Browse individual cards or download files in bulk.">
<title>{escape(title)}</title><link rel="icon" href="data:,">
<link rel="stylesheet" href="{url('assets/gallery.css')}"><script src="{url('assets/gallery.js')}" defer></script></head>
<body><a class="skip-link" href="#collection">Skip to {section_title.lower()}</a>
<header class="site-header"><a class="wordmark" href="{url('index.html')}">PLAYING CARDS</a><nav aria-label="Collection navigation"><a href="{url('designs/design1/index.html')}">Design 1</a><a href="{url('designs/design2/index.html')}">Design 2</a><a href="https://github.com/ianrastall/playing-cards">GitHub <span aria-hidden="true">↗</span></a></nav></header>
<main><section class="hero" aria-labelledby="page-title"><div class="hero-copy"><h1 id="page-title">{heading}</h1><p class="intro">{intro}</p><div class="hero-links">{collection_link}</div><p class="hero-meta">{len(chosen)} PNG files <span>·</span> MIT licensed</p></div><div class="viewing-table"><div class="hero-art">{hero_images}</div><p>Examples <span>Design {hero_design[-1]}</span></p></div></section>
<section class="collection-intro" id="collection" aria-label="{section_title}"><div><h2 class="eyebrow">{section_title}</h2><p>{collection_note}</p></div><nav aria-label="Gallery navigation">{jump_links}</nav></section>
{search}{''.join(content)}{bulk}
</main><footer class="site-footer"><div><a class="wordmark" href="{url('index.html')}">PLAYING CARDS</a></div><nav aria-label="Resources"><a href="{url('README.md')}">Collection guide</a><a href="{url('catalog.json')}">Production catalog</a><a href="{url('LICENSE')}">MIT License</a><a href="#page-title">Back to top ↑</a></nav></footer>
<dialog class="viewer" aria-labelledby="viewer-title"><div class="viewer-shell"><header class="viewer-header"><div><h2 id="viewer-title"></h2><p id="viewer-detail"></p></div><button type="button" id="viewer-close" aria-label="Close artwork viewer">Close <span aria-hidden="true">×</span></button></header><div class="viewer-stage"><img id="viewer-image" alt=""></div><div class="viewer-controls"><button type="button" id="viewer-prev" aria-label="Previous artwork">← Previous</button><span id="viewer-position" role="status"></span><button type="button" id="viewer-next" aria-label="Next artwork">Next →</button><button type="button" id="viewer-turn" aria-pressed="false">Turn 180°</button><a id="viewer-download" download>Download PNG ↓</a><a id="viewer-original">Open original ↗</a></div></div></dialog>
</body></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    assets = inventory()
    for relative, options in page_specs():
        path = ROOT / relative
        html = render(path, assets, **options)
        if args.write:
            path.write_text(html, encoding='utf-8', newline='\n')
        elif not path.exists() or path.read_text(encoding='utf-8') != html:
            raise SystemExit(f'Stale gallery: {relative}; run python scripts/build_gallery.py --write')
        print(f'PASS {relative}: {html.count("data-artwork=")} original PNG links in static HTML')


if __name__ == '__main__':
    main()
