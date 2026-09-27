"""Regression tests for Minchiate ordering and the replacement layout."""
import unittest
import render_minchiate as minchiate


class MinchiateTests(unittest.TestCase):
    def test_inventory_and_printed_indices_are_distinct(self):
        cards = minchiate.inventory()['cards']
        self.assertEqual(len(cards), 97)
        self.assertEqual(sum(c['kind'] == 'court' for c in cards), 16)
        trumps = [c for c in cards if c['kind'] == 'trump']
        self.assertEqual([c['rank_order'] for c in trumps], list(range(1, 41)))
        self.assertEqual([c['printed_index'] for c in trumps[-5:]], ['']*5)
        self.assertEqual(trumps[34]['printed_index'], 'XXXV')
        fool = next(c for c in cards if c['kind'] == 'fool')
        self.assertEqual(fool['printed_index'], '')
        self.assertEqual(minchiate.active_path(fool).name, '00-the-fool.png')

    def test_long_suits_have_countable_crosses_at_shared_center(self):
        for suit in ('swords', 'batons'):
            for rank in range(2, 11):
                card = dict(suit=suit, rank=str(rank), primary_asset='baton')
                items = minchiate.long_suit_instances(card)
                self.assertEqual(len(items), rank)
                self.assertEqual(sum(i['rotation'] == -30 for i in items), rank//2)
                self.assertEqual(sum(i['rotation'] == 30 for i in items), rank//2)
                self.assertAlmostEqual(sum(i['center'][1] for i in items)/rank, 712)
                self.assertTrue(all(i['center'][0] == 412 for i in items))
                if suit == 'swords':
                    self.assertTrue(all(i['component'] == 'sword-straight' for i in items))

    def test_incomplete_art_cannot_be_promoted(self):
        with self.assertRaises(AssertionError):
            minchiate.check(dict(missing=['the-world'], cards=[]))

    def test_hanged_man_keeps_user_selected_art(self):
        self.assertEqual(minchiate.REUSE_TRUMPS['the-hanged-man'], 'the-hanged-man')


if __name__ == '__main__':
    unittest.main()
