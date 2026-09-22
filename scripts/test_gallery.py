"""Check that download tools can discover the complete gallery without JavaScript."""
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit

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
    def test_root_has_every_production_card_and_selected_master_once(self):
        page = Page((ROOT / 'index.html').read_text(encoding='utf-8'))
        catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
        production = {a['path'] for a in catalog['assets']}
        self.assertTrue(production <= set(page.assets))
        self.assertEqual(len(page.assets), 474)
        self.assertEqual(len(set(page.assets)), 474)
        self.assertEqual(set(page.assets), set(page.downloads))
        self.assertTrue(set(page.assets) <= set(page.images))
        self.assertIn('designs/design2/sources/generated/courts-v1/king-spades-floral-jian-v3.png', page.assets)
        self.assertFalse(any('initial' in path or 'study' in path for path in page.assets))
        self.assertEqual(sum('/courts-v1/' in path for path in page.assets), 12)
        self.assertEqual(sum('/aces-v1/' in path for path in page.assets), 4)
        self.assertEqual(sum('/jokers-v1/' in path for path in page.assets), 2)

    def test_all_pages_have_portable_existing_links_and_complete_downloads(self):
        for relative, count in [('index.html', 474), ('designs/design1/index.html', 378),
                                ('designs/design2/index.html', 96), ('designs/design2/number-cards.html', 36)]:
            with self.subTest(page=relative):
                file = ROOT / relative
                page = Page(file.read_text(encoding='utf-8'))
                self.assertEqual(len(page.assets), count)
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
        for relative, design, numbers in [('index.html', None, False), ('designs/design1/index.html', 'design1', False),
                                          ('designs/design2/index.html', 'design2', False), ('designs/design2/number-cards.html', 'design2', True)]:
            file = ROOT / relative
            self.assertEqual(file.read_text(encoding='utf-8'), build_gallery.render(file, assets, design, numbers))


if __name__ == '__main__':
    unittest.main()
