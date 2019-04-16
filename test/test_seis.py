import unittest
import magD.seis as seis

import math
# import fixtures.seis_data as seis_data
from magD.origin import Origin


class TestSeis(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_distance(self):
        '''should be ~1% baselines from

        http://www.nhc.noaa.gov/gccalc.shtml
        '''
        o1 = Origin(45, -122)
        o2 = Origin(45, -123)
        deg, dist = seis.find_distance(o1, o2)
        ratio = dist / 79
        self.assertTrue(ratio > .99 and ratio < 1.01)
        o1 = Origin(41, -116)
        o2 = Origin(49, -128)
        deg, dist = seis.find_distance(o1, o2)
        ratio = dist / 1293
        self.assertTrue(ratio > .99 and ratio < 1.01)

    def test_signal_adjusted_frequency(self):
        # signal_adjusted_frequency(Mw, rad):
        '''should return correct value'''
        rad = 1 * (math.pi / 180)
        sav = seis.signal_adjusted_frequency(1.5, rad)
        self.assertEqual(sav, 2.6)
        rad = 2 * (math.pi / 180)
        sav = seis.signal_adjusted_frequency(0, rad)
        self.assertEqual(sav, 2.2)
        rad = 31 * (math.pi / 180)
        sav = seis.signal_adjusted_frequency(10, rad)
        self.assertEqual(sav, 0.3)

    # def test_calculate_geometric_spreading(self, delta, As):
    #     geometric_spreading = (1.0 / math.pow(delta, 0.5)) * As
    #     self.assertEqual(geometric_spreading,
    #                      self.calculate_geometric_spreading(As, delta))

    # def test_compute_amplitude(self, filtfc, delta, station_freq):
    #     # Calculates all the parameters.
    #     mu = 3 * math.pow(10, 11)
    #     # q = 640.0 * math.pow(15, 0.35)  # Q value
    #     beta = 3.5  # km/s
    #     cn = 1 / (4 * mu * beta * 1e7)
    #     fc = 1.0
    #     nyquist = 15
    #     fault_radius = 2.34 * beta / (2 * math.pi * fc)
    #     Mo = 2.29 * 100000000 * math.pow((1e5 * fault_radius), 3)
    #     # checks to see if the method computes the correct amplitude.
    #
    #     self.assertEqual(amplitude, self.compute_amplitude(fc, Mo, cn,
    #                       filtfc, delta, station_freq, nyquist))

    # def test_compute_attenuation(self, delta):
    #     q = 640.0*math.pow(15,0.35) #Q value
    #     beta = 3.5 #km/s
    #     fc = 1.0
    #
    #     self.assertEqual(attenuation,self.compute_attenuation(fc,delta,beta,q))
    #
    # def test_amplitude_power_conversion(self, As):
    #     power = As*As
    #     self.assertEqual(power,self.amplitude_power_conversion(As))
    #
    # def test_distance_signal_adjustment(self):
    #
    # def test_magnitude_signal_adjustment(self):
    #
    # def test_min_detect(self):
    #


if __name__ == '__main__':
    unittest.main()
