"""Check single-card pages, portable links, and the complete static file inventory."""
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import unittest
from urllib.parse import parse_qs, unquote, urlsplit

import build_gallery

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.assets, self.images, self.links, self.ids, self.downloads = [], [], [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
            if 'data-artwork' in attrs:
                self.assets.append(attrs['href'])
            if 'download' in attrs:
                self.downloads.append(attrs['href'])
        if tag == 'img' and attrs.get('src'):
            self.images.append(attrs['src'])


class GalleryTests(unittest.TestCase):
    def test_bulk_gallery_has_every_production_card_and_selected_master_once(self):
        page = Page((ROOT / 'all.html').read_text(encoding='utf-8'))
        paths = [urlsplit(url).path for url in page.assets]
        catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
        production = {a['path'] for a in catalog['assets']}
        self.assertTrue(production <= set(paths))
        self.assertEqual(len(page.assets), 886)
        self.assertEqual(len(set(page.assets)), 886)
        self.assertTrue(set(page.assets) <= set(page.downloads))
        self.assertEqual(len(page.images), 1)
        self.assertIn('designs/design2/sources/generated/courts-v1/king-spades-floral-jian-v3.png', paths)
        self.assertFalse(any('initial' in path or 'study' in path for path in page.assets))
        self.assertEqual(sum('design2/sources/generated/courts-v1/' in path for path in page.assets), 12)
        self.assertEqual(sum('design3/sources/generated/kings-v2/' in path for path in page.assets), 4)
        self.assertFalse(any('design3/sources/generated/courts-v1/' in path for path in page.assets))
        self.assertEqual(sum('/aces-v1/' in path for path in page.assets), 4)
        self.assertEqual(sum('/jokers-v1/' in path for path in page.assets), 2)

    def test_all_pages_have_portable_existing_links_and_complete_downloads(self):
        for relative, _ in build_gallery.page_specs():
            with self.subTest(page=relative):
                file = ROOT / relative
                page = Page(file.read_text(encoding='utf-8'))
                self.assertEqual(len(page.ids), len(set(page.ids)))
                self.assertTrue(set(page.assets) <= set(page.downloads))
                for link in page.links + page.images:
                    parsed = urlsplit(link)
                    if parsed.scheme:
                        continue
                    self.assertFalse(parsed.path.startswith('/'), link)
                    target = (file.parent / unquote(parsed.path)).resolve() if parsed.path else file
                    self.assertTrue(target.is_relative_to(ROOT), link)
                    self.assertTrue(target.is_file(), link)
                    if parsed.fragment:
                        target_page = Page(target.read_text(encoding='utf-8'))
                        self.assertIn(parsed.fragment, target_page.ids, link)

    def test_pages_match_shared_builder(self):
        assets = build_gallery.inventory()
        for relative, options in build_gallery.page_specs():
            file = ROOT / relative
            self.assertEqual(file.read_text(encoding='utf-8'), build_gallery.render(file, assets, **options))

    def test_celtic_official_kings_are_separate_from_unchanged_masters(self):
        assets = build_gallery.inventory()
        celtic = [a for a in assets if a['design'] == 'design3' and a['rank'] == 'king']
        self.assertEqual(len(celtic), 8)
        self.assertEqual({a['rank'] for a in celtic}, {'king'})
        self.assertEqual({a['suit'] for a in celtic}, {'spades', 'hearts', 'diamonds', 'clubs'})
        masters = [a for a in celtic if '.master.' in a['id']]
        faces = [a for a in celtic if a['side'] == 'face']
        self.assertEqual(len(masters), 4)
        self.assertEqual(len(faces), 4)
        self.assertTrue(all('/kings-v2/' in a['path'] for a in masters))
        self.assertTrue(all(a['pixels'] == [750, 1050] and a['status'] == 'approved' for a in faces))
        self.assertFalse(any('initial' in a['path'] or 'repair' in a['path'] for a in celtic))
        catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len([a for a in catalog['assets'] if a['design'] == 'design3']), 54)
        file = ROOT / 'designs/design3/poker.html'
        page = Page(file.read_text(encoding='utf-8'))
        self.assertEqual(len(page.assets), 54)
        self.assertIn('index.html', page.links)
        self.assertNotIn('tarot.html', page.links)
        html = file.read_text(encoding='utf-8')
        self.assertIn('"set":"faces"', html)
        self.assertIn('"kind":"masters"', html)
        self.assertIn('cards/faces/french-suited/poker/spades/queen.png', html)

    def test_celtic_queens_use_installed_faces_in_catalog_and_review_page(self):
        queens = [a for a in build_gallery.inventory() if a['design'] == 'design3' and a['rank'] == 'queen']
        self.assertEqual(len(queens), 4)
        self.assertEqual({a['suit'] for a in queens}, {'spades', 'hearts', 'diamonds', 'clubs'})
        self.assertTrue(all(a['side'] == 'face' and a['status'] == 'review' for a in queens))
        self.assertTrue(all(a['pixels'] == [750, 1050] for a in queens))
        html = (ROOT / 'designs/design3/queens.html').read_text(encoding='utf-8')
        self.assertEqual(len(Page(html).assets), 4)
        self.assertIn('"set":"review-queens"', html)
        self.assertEqual(Page(html).images[0].split('?')[0], 'cards/faces/french-suited/poker/spades/queen.png')
        catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(sum(a['design'] == 'design3' and a['rank'] == 'queen' for a in catalog['assets']),4)

    def test_celtic_jack_and_joker_review_pages_keep_ranks_and_colors_separate(self):
        assets = build_gallery.inventory()
        for rank, count in [('jack', 4), ('joker', 2)]:
            selected = [a for a in assets if a['design'] == 'design3' and a.get('rank') == rank]
            self.assertEqual(len(selected), count)
            self.assertTrue(all(a['side'] == 'face' and a['status'] == 'review' for a in selected))
            html = (ROOT / f'designs/design3/{rank}s.html').read_text(encoding='utf-8')
            page = Page(html)
            self.assertEqual(len(page.assets), count)
            self.assertTrue(all('cards/faces/french-suited/poker/' in url for url in page.assets))
            self.assertIn(f'"set":"review-{rank}s"', html)
            self.assertIn('cards/faces/french-suited/poker/', page.images[0])
        jokers = [a for a in assets if a['design'] == 'design3' and a.get('rank') == 'joker']
        self.assertEqual({a['title'] for a in jokers}, {'Black Joker', 'Red Joker'})
        self.assertEqual({a['color_variant'] for a in jokers}, {'black', 'red'})

    def test_celtic_poker_folders_contain_all_54_catalogued_faces(self):
        catalog = json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
        cards = [a for a in catalog['assets'] if a['design'] == 'design3']
        self.assertEqual(len(cards),54)
        base = ROOT/'designs/design3/cards/faces/french-suited/poker'
        for suit in build_gallery.SUITS[:4]:
            self.assertEqual({p.stem for p in (base/suit).glob('*.png')},
                             {'ace',*map(str,range(2,11)),'jack','queen','king'})
        self.assertEqual({p.name for p in (base/'jokers').glob('*.png')},{'black.png','red.png'})
        for asset in cards:
            self.assertEqual(hashlib.sha256((ROOT/asset['path']).read_bytes()).hexdigest(),asset['sha256'])

    def test_every_page_has_one_stage_and_navigation(self):
        for relative, _ in build_gallery.page_specs():
            page = Page((ROOT / relative).read_text(encoding='utf-8'))
            self.assertEqual(len(page.images), 1, relative)
            for control in ('viewer-image', 'design-select', 'format-select', 'set-select',
                            'card-select', 'card-range', 'viewer-download', 'viewer-turn'):
                self.assertIn(control, page.ids)
        root = Page((ROOT / 'index.html').read_text(encoding='utf-8'))
        for design in ('design1', 'design2'):
            self.assertIn(f'designs/{design}/index.html', root.links)
            page = Page((ROOT / f'designs/{design}/index.html').read_text(encoding='utf-8'))
            for fmt in build_gallery.FORMATS:
                self.assertIn(f'{fmt}.html', page.links)
            self.assertIn('all.html', page.links)

    def test_celtic_large_pips_are_components_separate_from_finished_cards(self):
        pips = [a for a in build_gallery.inventory() if a['design'] == 'design3' and a['side'] == 'pip']
        self.assertEqual(len(pips), 4)
        self.assertEqual({a['suit'] for a in pips}, {'spades', 'hearts', 'diamonds', 'clubs'})
        html = (ROOT/'designs/design3/pips.html').read_text(encoding='utf-8')
        self.assertEqual(len(Page(html).assets), 4)
        self.assertIn('"set":"pips"', html)
        self.assertIn('pips-v1/spades-master.png', Page(html).images[0])
        poker = Page((ROOT/'designs/design3/poker.html').read_text(encoding='utf-8'))
        self.assertFalse(any('/pips-v1/' in url for url in poker.assets))

    def test_celtic_a10_review_inventory_has_ten_cards_per_suit(self):
        assets = [a for a in build_gallery.inventory() if a['design'] == 'design3'
                  and a['side'] == 'face' and a['rank'] in build_gallery.RANKS[:10]]
        self.assertEqual(len(assets), 40)
        for suit in build_gallery.SUITS[:4]:
            self.assertEqual({a['rank'] for a in assets if a['suit'] == suit}, set(build_gallery.RANKS[:10]))
        self.assertTrue(all(a['status'] == 'review' and a['pixels'] == [750, 1050] for a in assets))
        file = ROOT/'designs/design3/a-10.html'
        html = file.read_text(encoding='utf-8')
        paths = {(file.parent/urlsplit(url).path).resolve().relative_to(ROOT).as_posix()
                 for url in Page(html).assets}
        self.assertEqual(paths, {a['path'] for a in assets})
        self.assertIn('"set":"a10"', html)
        self.assertIn('spades/ace.png', Page(html).images[0])

    def test_size_galleries_partition_cards_without_mislabeling_masters(self):
        assets = build_gallery.inventory()
        for design in ['design1', 'design2']:
            found = []
            for fmt in build_gallery.FORMATS:
                file = ROOT / f'designs/{design}/{fmt}.html'
                page = Page(file.read_text(encoding='utf-8'))
                paths = [(file.parent / urlsplit(url).path).resolve().relative_to(ROOT).as_posix() for url in page.assets]
                expected = {a['path'] for a in assets if a['design'] == design and a['format'] == fmt and '.master.' not in a['id']}
                self.assertEqual(set(paths), expected)
                self.assertEqual(len(paths), len(expected))
                found.extend(paths)
            self.assertEqual(len(found), 397 if design == 'design1' else 409)
            self.assertEqual(len(found), len(set(found)))
        masters = Page((ROOT / 'designs/design2/masters.html').read_text(encoding='utf-8'))
        self.assertEqual(len(masters.assets), 18)

    def test_minchiate_is_complete_and_sorted_by_rank_order(self):
        assets = build_gallery.inventory()
        for design in ('design1', 'design2'):
            faces = [a for a in assets if a['design'] == design and a.get('system') == 'tarot' and a['side'] == 'face']
            self.assertEqual(len(faces), 97)
            self.assertTrue(all(a['format'] == 'tarot' and a['pixels'] == [825, 1425] for a in faces))
            if design == 'design2':
                self.assertTrue(all(a['chinese_title'] and a['chinese_language'] == 'zh-Hant' for a in faces))
            self.assertTrue(all(a['tradition']=='florentine-minchiate-97' for a in faces))
            trumps = sorted([a for a in faces if a['arcana'] == 'major'], key=build_gallery.order)
            self.assertEqual([a['number'] for a in trumps], list(range(41)))
            self.assertEqual(sum(a['printed_index'] == '' for a in trumps), 6)
            self.assertEqual(trumps[-1]['slug'], 'the-trumpets')
            for suit in ('swords', 'batons', 'cups', 'coins'):
                suited = sorted([a for a in faces if a['suit'] == suit], key=build_gallery.order)
                self.assertEqual([a['rank'] for a in suited], ['ace', *map(str, range(2, 11)), 'page', 'knight', 'queen', 'king'])

    def test_back_urls_track_actual_png_bytes_in_previews_and_downloads(self):
        for relative, _ in build_gallery.page_specs():
            file = ROOT / relative
            page = Page(file.read_text(encoding='utf-8'))
            for url in set(page.images + page.assets + page.downloads):
                parsed = urlsplit(url)
                if '/backs/' not in parsed.path:
                    continue
                path = file.parent / unquote(parsed.path)
                expected = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
                self.assertEqual(parse_qs(parsed.query).get('v'), [expected], url)


if __name__ == '__main__':
    unittest.main()
