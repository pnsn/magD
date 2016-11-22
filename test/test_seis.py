import unittest
import sys, os
sys.path.append(os.path.abspath('..'))
import MagD.seis as seis
import math
import fixtures.seis_data as seis_data

class TestSeis(unittest.TestCase):
    # def setUp(self):
    
    # def tearDown(self):
    
    # def test_find_station(self):
    
    # def test_find_station_codes(self):
        
    # def test_create_station_object(self):
    #     self.assertTrue(15, station_object[code][0])
        
    def test_distance(self):
        '''should be ~1% baselines from http://www.nhc.noaa.gov/gccalc.shtml '''
        deg,dist=seis.distance((45,-122), (45,-123))
        ratio= dist/79
        self.assertTrue(ratio > .99 and ratio < 1.01)
        deg,dist=seis.distance((41,-116), (49,-128))
        ratio=dist/1293
        self.assertTrue(ratio > .99 and ratio < 1.01)
    
    def test_signal_adjusted_frequency(self):
        #signal_adjusted_frequency(Mw, rad):
        '''should return correct value'''
        rad=1*(math.pi/180)
        sav=seis.signal_adjusted_frequency(1.5, rad)
        self.assertEqual(sav, 2.6)
        rad=2*(math.pi/180)
        sav=seis.signal_adjusted_frequency(0, rad)
        self.assertEqual(sav, 2.2)
        rad=31*(math.pi/180)
        sav=seis.signal_adjusted_frequency(10, rad)
        self.assertEqual(sav, 0.3)
        
        
    def test_power_indexing(self):
        """should return correct index using logs"""
        freq0=seis_data.freq_modes[0][0]
        base = seis_data.freq_modes[1][0]/freq0
        for i in range(len(seis_data.freq_modes)):
            test_freq=seis_data.freq_modes[i][0]
            test_index=seis.get_frequency_index(test_freq,seis_data.freq_modes[0][0], base)
            self.assertEqual(i,test_index)
            self.assertEqual(seis_data.modes[test_index],seis_data.freq_modes[test_index][1])
        
        #now test where frequencies are close but not=
        for i in range(len(seis_data.freq_modes)):
            test_freq=seis_data.freq_modes[i][0] 
            test_freq+=test_freq/100
            test_index=seis.get_frequency_index(test_freq,seis_data.freq_modes[0][0], base)
            self.assertEqual(i,test_index)
        
    
    
    # def test_calculate_geometric_spreading(self, delta, As):
    #     geometric_spreading = (1.0/math.pow(delta,0.5))*As
    #     self.assertEqual(geometric_spreading,self.calculate_geometric_spreading(As, delta))
    #
    # def test_compute_amplitude(self, filtfc, delta, station_freq):
    #     #Calculates all the parameters.
    #     mu = 3*math.pow(10,11)
    #     q = 640.0*math.pow(15,0.35) #Q value
    #     beta = 3.5 #km/s
    #     cn= 1/(4*mu*beta*1e7)
    #     fc = 1.0
    #     nyquist = 15
    #     fault_radius = 2.34*beta/(2*math.pi*fc)
    #     Mo = 2.29*100000000*math.pow((1e5*fault_radius),3)
    #     #checks to see if the method computes the correct amplitude.
    #     self.assertEqual(amplitude,self.compute_amplitude(fc,Mo,cn,filtfc,delta,station_freq,nyquist))
    #
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
    # def test_generate_earthquake(self):
    
   
if __name__ == '__main__':
    unittest.main()