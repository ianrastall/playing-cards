"""Geometry/inventory regressions for the completed poker release."""
import unittest

import numpy as np
from PIL import Image

import complete_poker as complete
import package_poker as package
import rebuild_deck as base


class PokerCompletionTests(unittest.TestCase):
    def test_back_aperture_has_no_designation_cutouts(self):
        _,field=complete.back_frame(base.SIZE)
        a=np.array(field)
        self.assertTrue(np.array_equal(a,a[::-1]))
        self.assertTrue(np.array_equal(a,a[:,::-1]))
        self.assertEqual(a[145,110],255)
        self.assertEqual(a[905,639],255)

    def test_print_trim_is_preserved_without_resampling(self):
        # A one-pixel impulse detects scaling, placement, or asymmetric margins.
        native=Image.new('RGBA',(750,1050),(250,235,215,255))
        native.putpixel((374,524),(1,2,3,255))
        clean,guide=package.print_images(native)
        self.assertEqual(clean.size,(1650,2250))
        self.assertEqual(clean.getpixel((75+748,75+1048)),(1,2,3))
        self.assertEqual(clean.getpixel((75+749,75+1049)),(1,2,3))
        self.assertEqual(clean.getpixel((74,100)),package.GROUND)
        self.assertEqual(clean.getpixel((1575,100)),package.GROUND)
        self.assertEqual(guide.getpixel((900,150)),package.BLUE)
        self.assertNotEqual(clean.getpixel((825,75)),package.BLUE)

    def test_transparent_corners_print_as_antique_white(self):
        native=Image.new('RGBA',(750,1050),(0,0,0,0))
        clean,_=package.print_images(native)
        self.assertTrue(np.all(np.array(clean)==package.GROUND))

    def test_jokers_flatten_to_distinct_unsuited_filenames(self):
        black=dict(side='face',rank='joker',suit=None,color_variant='black')
        red=dict(side='face',rank='joker',suit=None,color_variant='red')
        self.assertEqual(package.release_name(black),'faces/joker-black.png')
        self.assertEqual(package.release_name(red),'faces/joker-red.png')


if __name__=='__main__':
    unittest.main()
