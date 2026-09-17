import unittest
import numpy as np
from PIL import Image
import expand_faces as faces
import package_decks as packages
import package_poker as poker


class RegistrationPackageTests(unittest.TestCase):
    def test_king_painting_is_registered_before_badge(self):
        for fmt in ('poker','jumbo','travel','bridge'):
            size=faces.size_for(fmt)
            painting=faces.court_interior('spades','king',size)
            before=np.array(painting).copy()
            target=(np.array(size)-1)/2
            self.assertLess(np.max(np.abs(np.array(faces.painted_center(painting))-target)),.1)
            faces.court_art('spades','king',size)
            np.testing.assert_array_equal(np.array(painting),before)

    def test_non_poker_trim_and_crop_marks(self):
        for fmt in packages.FORMATS:
            g=packages.geometry(fmt)
            native=Image.new('RGBA',tuple(g['native']),(250,235,215,255))
            native.putpixel((17,23),(1,2,3,255))
            clean,guide=poker.print_images(native)
            self.assertEqual(list(clean.size),g['bleed'])
            self.assertEqual(list(guide.size),g['guides'])
            self.assertEqual(clean.getpixel((75+34,75+46)),(1,2,3))
            self.assertEqual(clean.getpixel((75+35,75+47)),(1,2,3))
            self.assertEqual(guide.getpixel((150+g['trim'][0],30)),poker.BLUE)
            self.assertEqual(guide.getpixel((g['guides'][0]-30,150+g['trim'][1])),poker.BLUE)

    def test_tarot_is_not_packaged(self):
        with self.assertRaises(ValueError): packages.geometry('tarot')


if __name__=='__main__': unittest.main()
