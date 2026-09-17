"""Regression checks for failures discovered while rebuilding the deck."""
import unittest

import numpy as np
from PIL import Image

from rebuild_deck import flood_region, put_at, silhouette, turquoise


class RebuildRegressionTests(unittest.TestCase):
    def test_flood_fill_works_with_readonly_array_backing(self):
        mask=np.zeros((9,9),dtype=bool)
        mask[1:4,1:4]=True
        mask[6:8,6:8]=True
        result=flood_region(mask,(2,2))
        self.assertEqual(int(result.sum()),9)
        self.assertFalse(result[6,6])

    def test_remote_cyan_speck_cannot_enlarge_central_jewel(self):
        a=np.zeros((100,100,4),dtype=np.uint8)
        a[45:55,45:55]=(10,160,170,255)
        a[2,95]=(0,200,200,255)
        center,box=turquoise(Image.fromarray(a))
        self.assertEqual(center,(49.5,49.5))
        self.assertEqual(box,(45,45,55,55))

    def test_fractional_translation_is_rejected(self):
        canvas=Image.new('RGBA',(20,20))
        sprite=Image.new('RGBA',(4,4),(0,0,0,255))
        with self.assertRaises(ValueError):
            put_at(canvas,sprite,(10,10))
        put_at(canvas,sprite,(9.5,9.5))
        self.assertEqual(canvas.getbbox(),(8,8,12,12))

    def test_outer_corner_mask_is_reciprocal_for_odd_and_even_sizes(self):
        for size in ((750,1050),(825,1425),(675,1050)):
            a=np.array(silhouette(size))
            self.assertTrue(np.array_equal(a,a[::-1,::-1]))
            self.assertEqual(a[0,0],0)
            self.assertEqual(a[size[1]//2,size[0]//2],255)
            self.assertTrue(np.any((a>0)&(a<255)))


if __name__=='__main__':
    unittest.main()
