"""Check that download tools can discover the complete gallery without JavaScript."""
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
        self.assertEqual(len(page.assets), 474)
        self.assertEqual(len(set(page.assets)), 474)
        self.assertEqual(set(page.assets), set(page.downloads))
        self.assertTrue(set(page.assets) <= set(page.images))
        self.assertIn('designs/design2/sources/generated/courts-v1/king-spades-floral-jian-v3.png', paths)
        self.assertFalse(any('initial' in path or 'study' in path for path in page.assets))
        self.assertEqual(sum('/courts-v1/' in path for path in page.assets), 12)
        self.assertEqual(sum('/aces-v1/' in path for path in page.assets), 4)
        self.assertEqual(sum('/jokers-v1/' in path for path in page.assets), 2)

    def test_all_pages_have_portable_existing_links_and_complete_downloads(self):
        for relative, _ in build_gallery.page_specs():
            with self.subTest(page=relative):
                file = ROOT / relative
                page = Page(file.read_text(encoding='utf-8'))
                self.assertEqual(len(page.ids), len(set(page.ids)))
                self.assertEqual(set(page.assets), set(page.downloads))
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

    def test_design_and_size_choices_precede_grids(self):
        root = Page((ROOT / 'index.html').read_text(encoding='utf-8'))
        self.assertEqual(root.assets, [])
        self.assertLessEqual(len(root.images), 4)
        self.assertIn('all.html', root.links)
        for design in ['design1', 'design2']:
            self.assertIn(f'designs/{design}/index.html', root.links)
            page = Page((ROOT / f'designs/{design}/index.html').read_text(encoding='utf-8'))
            self.assertEqual(page.assets, [])
            self.assertLessEqual(len(page.images), 2)
            for fmt in build_gallery.FORMATS:
                self.assertIn(f'{fmt}.html', page.links)
            self.assertIn('all.html', page.links)

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
            self.assertEqual(len(found), 378 if design == 'design1' else 78)
            self.assertEqual(len(found), len(set(found)))
        masters = Page((ROOT / 'designs/design2/masters.html').read_text(encoding='utf-8'))
        self.assertEqual(len(masters.assets), 18)

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
