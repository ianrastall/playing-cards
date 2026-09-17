"""Regressions for native format placement and palette isolation."""
import unittest
import numpy as np
from PIL import Image
import expand_faces as faces
from frame_palette import color_frame, face_color


class FaceFormatsTests(unittest.TestCase):
    def test_odd_width_centers_and_pairs(self):
        for size in ((675,1050),(525,750),(1050,1500)):
            a=faces.native_point((234.5,244.5),size)
            b=faces.native_point((514.5,804.5),size)
            self.assertEqual(tuple(a[i]+b[i] for i in range(2)),tuple(n-1 for n in size))
            sprite=faces.pip_component('spades','10',size)
            canvas=Image.new('RGBA',size)
            faces.base.put_at(canvas,sprite,a)
            self.assertIsNotNone(canvas.getbbox())

    def test_frame_palette_protects_bright_pigments_and_alpha(self):
        pixels=np.array([[(250,235,215,0),(210,160,30,255),(170,15,20,255),(4,4,4,255)]],dtype=np.uint8)
        result=np.array(color_frame(Image.fromarray(pixels),'madder-lake'))
        np.testing.assert_array_equal(result[:,:3],pixels[:,:3])
        np.testing.assert_array_equal(result[:,:,3],pixels[:,:,3])
        self.assertGreater(int(result[0,3,0]),int(result[0,3,1])+40)

    def test_jokers_follow_their_own_color(self):
        self.assertEqual(face_color('jokers','red'),'madder-lake')
        self.assertEqual(face_color('jokers','black'),'lamp-black')
        self.assertEqual(face_color('hearts','queen'),'madder-lake')

    def test_european_reads_bridge_pixels(self):
        source=Image.new('RGBA',(675,1050),(20,40,60,255))
        result=faces.european(source)
        self.assertEqual(result.size,(696,1074))
        self.assertEqual(result.getpixel((348,537)),(20,40,60,255))


if __name__=='__main__':
    unittest.main()
