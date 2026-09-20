"""Regression checks for design isolation and portable catalog paths."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import catalog


class CollectionCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(catalog, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.designs = []
        for design_id in ('design1', 'design2'):
            root = self.root/'designs'/design_id
            path = root/'cards/backs/poker/blue.png'
            path.parent.mkdir(parents=True)
            Image.new('RGBA', (50, 70), (26, 83, 117, 255)).save(path, dpi=(300, 300))
            config = dict(id=design_id, formats={'poker': dict(back_pixels=[50, 70], trim_inches=[2.5, 3.5])},
                          back_colors=['blue'], back_status='approved', face_systems={})
            (root/'deck.json').write_text(json.dumps(config), encoding='utf-8')
            self.designs.append(dict(id=design_id, name=design_id, path='designs/'+design_id))
        self.registry()

    def registry(self):
        (self.root/'collection.json').write_text(json.dumps(dict(designs=self.designs)), encoding='utf-8')

    def test_backs_only_designs_can_share_local_ids_without_collision(self):
        result = catalog.build_catalog()
        self.assertEqual({a['id'] for a in result['assets']},
                         {'design1.back.poker.blue', 'design2.back.poker.blue'})
        self.assertEqual(result['path_base'], 'repository-root')
        for asset in result['assets']:
            self.assertTrue((self.root/asset['path']).is_file())
            self.assertEqual(asset['local_id'], 'back.poker.blue')
            self.assertTrue(asset['path'].startswith('designs/'+asset['design']+'/'))
        local = catalog.build_design_catalog(self.root/'designs/design2')
        self.assertEqual(local['path_base'], 'design-root')
        self.assertEqual(local['assets'][0]['path'], 'cards/backs/poker/blue.png')

    def test_missing_card_fails_even_when_other_design_has_it(self):
        (self.root/'designs/design2/cards/backs/poker/blue.png').unlink()
        with self.assertRaisesRegex(ValueError, 'Back inventory mismatch'):
            catalog.build_catalog()

    def test_duplicate_design_ids_are_rejected(self):
        self.designs[1]['id'] = 'design1'
        self.registry()
        with self.assertRaisesRegex(ValueError, 'Duplicate design'):
            catalog.build_catalog()

    def test_design_paths_cannot_escape_designs_directory(self):
        self.designs[0]['path'] = '.'
        self.registry()
        with self.assertRaisesRegex(ValueError, 'inside designs'):
            catalog.build_catalog()

    def test_registry_and_manifest_must_identify_the_same_design(self):
        self.designs[1]['id'] = 'design3'
        self.registry()
        with self.assertRaisesRegex(ValueError, 'does not match registry'):
            catalog.build_catalog()


if __name__ == '__main__':
    unittest.main()
