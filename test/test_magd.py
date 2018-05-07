import unittest
import sys
import os
sys.path.append(os.path.abspath('..'))

from magD.magD import MagD



class TestMagD(unittest.TestCase):
    def setup(self):
        pass

    def test_initiation(self):
        magd=MagD("config/test.ini")
        self.assertEqual(magd.lat_min, 36.0 + magd.grid_resolution)
        self.assertEqual(magd.lat_max, 46.0)
        self.assertEqual(magd.lon_min, -130.0)
        self.assertEqual(magd.lon_max, -120.0 + magd.grid_resolution)
        self.assertEqual(magd.grid_resolution, 1.0)
        self.assertEqual(magd.num_detections, 2)
        self.assertEqual(magd.nyquist_correction, 0.4)
        self.assertEqual(magd.mu, 3e11)
        self.assertEqual(magd.qconst, 300.0)
        self.assertEqual(magd.beta, 3.5)


    '''Simple test to check errors'''
    def test_find_noise_and_detections(self):
        magd=MagD("config/test.ini")
        magd.get_noise()
        magd.find_detections()
        sum=magd.print_summary()
        print(sum)


if __name__ == '__main__':
    unittest.main()
