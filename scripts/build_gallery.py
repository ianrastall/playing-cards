"""Build a static single-card viewer and direct file directories.

Run with --write after changing inventory, or --check to verify checked-in pages.
No image files are modified. Every original PNG is linked in the initial HTML.
"""
from __future__ import annotations

import argparse
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
RANKS = ['ace', *map(str, range(2, 11)), 'jack', 'page', 'knight', 'queen', 'king', 'joker']
COLORS = ['prussian-blue', 'verdigris', 'madder-lake', 'manganese-violet', 'lamp-black']


def designs():
    return json.loads((ROOT / 'collection.json').read_text(encoding='utf-8'))['designs']


def design_formats(design):
    config = json.loads((ROOT / design['path'] / 'deck.json').read_text(encoding='utf-8'))
    return [fmt for fmt in FORMATS if fmt in config['formats']]


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
            group = f"design1-{a['format']}" if a['design'] == 'design1' else (
                f"{a['design']}-numbers" if a.get('system') == 'french-suited' and a['rank'] in list(map(str, range(2, 11))) else f"{a['design']}-faces")
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
            if fmt == 'tarot':
                path = ROOT / f'designs/design2/sources/components/tarot-faces-v1/frame/{color}.png'
            with Image.open(path) as image:
                size = list(image.size)
            assets.append(dict(id=f'design2.frame.{fmt}.{color}', design='design2', group='face-frames',
                               path=path.relative_to(ROOT).as_posix(), pixels=size, title=f'{label(color)} frame',
                               format=fmt, color=color, side='frame', detail=f'{label(fmt)} · Blank face'))
    for design in designs():
        root = ROOT / design['path']
        config = json.loads((root / 'deck.json').read_text(encoding='utf-8'))
        manifests = [(config[key], kind) for key, kind in [('master_manifest', 'master'), ('study_manifest', 'study'), ('pip_manifest', 'pip')] if config.get(key)]
        manifests.extend((path, 'study') for path in config.get('study_manifests', []))
        for manifest_path, source_kind in manifests:
            manifest_file = root / manifest_path
            manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
            for entry in manifest['cards']:
                path = manifest_file.parent / entry['path']
                if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
                    raise ValueError(f'Source manifest hash mismatch: {path}')
                with Image.open(path) as image:
                    size = list(image.size)
                if size != entry['pixels']:
                    raise ValueError(f'Source manifest dimensions mismatch: {path}')
                assets.append(dict(id=f"{design['id']}.{source_kind}.{entry['rank']}.{entry['suit']}",
                                   design=design['id'], group=f"{design['id']}-{source_kind}s",
                                   path=path.relative_to(ROOT).as_posix(), pixels=size,
                                   title=entry.get('title') or f"{label(entry['rank'])} of {label(entry['suit'])}",
                                   rank=entry['rank'], suit=entry['suit'], format=entry['format'],
                                   side=source_kind, status=entry.get('status', source_kind),
                                   **({'system': entry.get('system', 'french-suited')} if source_kind == 'study' else {}),
                                   detail=f'Artwork {source_kind} · {size[0]} × {size[1]}'))
    assert len({a['path'] for a in assets}) == len(assets), 'Duplicate gallery artwork'
    return assets


def order(a):
    return (FORMATS.index(a['format']), SUITS.index(a['suit']) if a.get('suit') in SUITS else 99,
            int(a['number']) if a.get('arcana') == 'major' else RANKS.index(a['rank']) if a.get('rank') in RANKS else 99,
            COLORS.index(a['color']) if a.get('color') in COLORS else 99, a['path'])


@lru_cache(maxsize=None)
def revision(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:16]


def page_specs():
    yield 'index.html', {}
    yield 'all.html', {'all_artwork': True}
    for record in designs():
        design = record['id']
        yield f"{record['path']}/index.html", {'design': design}
        yield f"{record['path']}/all.html", {'design': design, 'all_artwork': True}
        for fmt in design_formats(record):
            yield f"{record['path']}/{fmt}.html", {'design': design, 'fmt': fmt}
    yield 'designs/design2/masters.html', {'design': 'design2', 'masters_only': True}
    yield 'designs/design2/number-cards.html', {'design': 'design2', 'numbers_only': True}
    yield 'designs/design2/minchiate-review.html', {'design': 'design2', 'fmt': 'tarot'}
    for rank in ('queen', 'jack', 'joker'):
        yield f'designs/design3/{rank}s.html', {'design': 'design3', 'fmt': 'poker', 'studies_only': True, 'study_rank': rank}
    yield 'designs/design3/pips.html', {'design': 'design3', 'pips_only': True}
    yield 'designs/design3/a-10.html', {'design': 'design3', 'fmt': 'poker', 'a10_only': True}


def render(page, assets, design=None, numbers_only=False, fmt=None, all_artwork=False, masters_only=False, studies_only=False, study_rank=None, pips_only=False, a10_only=False):
    def url(path):
        relative = os.path.relpath(ROOT / path, page.parent).replace(os.sep, '/')
        if Path(path).suffix in {'.png', '.css', '.js'}:
            relative += '?v=' + revision(path)
        return relative

    initial_design = design or 'design1'
    initial_format = fmt or 'poker'
    initial_set = 'a10' if a10_only else 'pips' if pips_only else f'review-{study_rank}s' if studies_only and study_rank else 'studies' if studies_only else 'masters' if masters_only else 'numbers' if numbers_only else 'faces'
    if not masters_only and not numbers_only and not pips_only and not any(
            a['design'] == initial_design and a['format'] == initial_format and a['side'] == 'face' for a in assets):
        if any(a['design'] == initial_design and a['format'] == initial_format and a['side'] == 'study' for a in assets):
            initial_set = 'studies'
    data = []
    for a in sorted(assets, key=lambda a: (a['design'], order(a))):
        entry = {key: a[key] for key in ('id', 'design', 'format', 'pixels', 'title',
                 'detail', 'trim_inches', 'rank', 'suit', 'arcana', 'group', 'system', 'tradition',
                 'chinese_title', 'chinese_language', 'translation_status', 'proof_group', 'status') if key in a}
        entry['src'] = url(a['path'])
        entry['kind'] = 'masters' if '.master.' in a['id'] else a['side']
        data.append(entry)
    first = next(a for a in data if a['design'] == initial_design and a['format'] == initial_format
                 and (a['kind'] == 'face' and a.get('rank') in RANKS[:10] if a10_only else a['kind'] == 'pip' if pips_only else a['kind'] in ('face','study') and a.get('status') == 'review' and a.get('rank') in ('queen','jack','joker') and (not study_rank or a.get('rank') == study_rank) if studies_only else a['kind'] == 'masters' if masters_only else
                      a.get('rank') in list(map(str, range(2, 11))) and a['kind'] == 'face' if numbers_only else
                      a['kind'] in ('face', 'back', 'study')))
    chosen = [a for a in data if (not design or a['design'] == design)
              and (not fmt or (a['format'] == fmt and a['kind'] not in ('masters', 'pip')))
              and (not pips_only or a['kind'] == 'pip')
              and (not a10_only or a['kind'] == 'face' and a.get('system') == 'french-suited' and a.get('rank') in RANKS[:10])
              and (not masters_only or a['kind'] == 'masters')
              and (not studies_only or a['kind'] in ('face','study') and a.get('status') == 'review' and a.get('rank') in ('queen','jack','joker'))
              and (not study_rank or a.get('rank') == study_rank)
              and (not numbers_only or a['group'] == 'design2-numbers')]
    title = 'Playing cards' if not design else f'Design {design[-1]}' + (f' · {label(fmt)}' if fmt else '')
    directory = ''.join(f'<li><a href="{escape(a["src"], quote=True)}" data-artwork="{a["id"]}" download="{a["id"]}.png">Design {a["design"][-1]} · {label(a["format"])} · {escape(a["title"])}{ " · Original master" if a["kind"] == "masters" else ""}</a></li>' for a in chosen)
    registry = designs()
    selected_design = next(d for d in registry if d['id'] == initial_design)
    size_links = ''.join(f'<a href="{url(f"designs/{initial_design}/{size}.html")}">{label(size)}</a>' for size in design_formats(selected_design))
    design_links = ''.join(f'<a href="{url(d["path"] + "/index.html")}">{escape(d["name"])}</a>' for d in registry)
    design_options = ''.join(f'<option value="{escape(d["id"], quote=True)}">{escape(d["name"])}</option>' for d in registry)
    payload = json.dumps(dict(assets=data, design=initial_design, format=initial_format, set=initial_set), ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    return f'''<!doctype html>
<!-- Generated by scripts/build_gallery.py; edit the builder or shared gallery assets. -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="description" content="Browse playing cards one at a time. Choose a design, size and set, then download individual PNGs.">
<title>{escape(title)}</title><link rel="icon" href="data:,"><link rel="stylesheet" href="{url('assets/gallery.css')}">
<script id="card-data" type="application/json">{payload}</script><script src="{url('assets/gallery.js')}" defer></script></head>
<body><a class="skip-link" href="#collection">Skip to card viewer</a>
<header class="site-header"><a class="wordmark" href="{url('index.html')}">Playing cards<span class="brand-suits" aria-hidden="true"> ♠ ♡ ♣ ♢</span></a><nav aria-label="Collection">{design_links}<a href="https://github.com/ianrastall/playing-cards">GitHub ↗</a></nav></header>
<main id="collection"><aside class="browser-panel"><div><p class="eyebrow">The collection</p><h1>Card viewer</h1><p class="intro">Browse the faces and backs in each design.</p></div>
<div class="selectors" id="browser-controls" hidden>
<label for="design-select">Design</label><select id="design-select">{design_options}</select>
<label for="format-select">Size</label><select id="format-select">{''.join(f'<option value="{size}">{label(size)}</option>' for size in FORMATS)}</select>
<label for="set-select">View</label><select id="set-select"></select>
<div class="set-step"><button id="set-prev" type="button" aria-label="Previous view">← Previous view</button><button id="set-next" type="button" aria-label="Next view">Next view →</button></div>
<label for="card-search">Find a card in this view</label><input id="card-search" type="search" placeholder="Name, suit or color" autocomplete="off">
<label for="card-select">Card</label><select id="card-select"></select>
</div><p id="availability" class="muted"></p><p class="keyboard-note">Use ← and → to move through cards.<br>Drag the slider to jump through a set.</p>
<details class="page-links"><summary>Size pages &amp; file links</summary><nav aria-label="Size pages">{size_links}<a href="{url(f'designs/{initial_design}/all.html')}">All file links for this design</a><a href="{url('all.html')}">All file links</a><a href="{url('designs/design2/masters.html')}">Design 2 source masters</a></nav></details></aside>
<section class="card-view" aria-label="Card viewer"><header class="card-heading"><div><p class="eyebrow" id="viewer-context">Design {initial_design[-1]} / {label(initial_format)}</p><h2 id="viewer-title">{escape(first['title'])}</h2></div><span id="viewer-position" role="status" aria-live="polite"></span></header>
<div class="viewer-stage" id="viewer-stage"><img id="viewer-image" src="{escape(first['src'], quote=True)}" alt="{escape(first['title'], quote=True)}" width="{first['pixels'][0]}" height="{first['pixels'][1]}" fetchpriority="high"><p id="empty-state" hidden>No cards match. Try another name, or clear the search.</p></div>
<div class="card-step" id="card-navigation" hidden><button type="button" id="viewer-prev" aria-label="Previous card">← Previous</button><input id="card-range" type="range" min="1" max="1" value="1" aria-label="Card position"><button type="button" id="viewer-next" aria-label="Next card">Next →</button></div>
<div class="card-bottom"><p id="viewer-detail" class="muted">{escape(first['detail'])}</p><div class="viewer-actions"><button type="button" id="viewer-turn" aria-pressed="false" hidden>Turn 180°</button><a id="viewer-download" href="{escape(first['src'], quote=True)}" download="{first['id']}.png">Download PNG ↓</a></div></div>
<p id="image-status" role="status" class="muted"></p></section>
</main><footer><span>PNG artwork · <a href="{url('LICENSE')}">MIT License</a></span><a href="{url('README.md')}">Collection guide</a></footer>
<details class="file-directory"{' open' if all_artwork else ''}><summary>Direct PNG file links ({len(chosen)})</summary><p>Original files, grouped by design and size. Source masters retain their original dimensions.</p><ul>{directory}</ul></details>
<noscript><p class="no-script">Enable JavaScript for card navigation, or use the size pages and direct PNG links.</p></noscript>
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
