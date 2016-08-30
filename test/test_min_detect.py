import unittest
# import numpy as np
import sys, os
sys.path.append(os.path.abspath('..'))
from MagD.core import parse_json_file
from MagD.contour import Contour
from pprint import pprint
import numpy as np
import json
from topojson import topojson
from geojson import is_valid

class TestMinDetect(unittest.TestCase):
    def setUp(self):
        self.station_objects = 
        self.levels=[1,2,3,4,5]
    
    def tearDown(self):
        self.json_in = None
        self.levels =None
    
    def test_find_station(self):
    
    def test_find_station_codes(self):
        
    def test_create_station_object(self):
        self.assertTrue(15, station_object[code][0])
        
    def test_distance(self):
        #checks to see if the a calculated distance matches the one from the method.
        self.assertEqual(distance,self.distance(origin, destination))
        
    def test_calculate_geometric_spreading(self, delta, As):
        geometric_spreading = (1.0/math.pow(delta,0.5))*As
        self.assertEqual(geometric_spreading,self.calculate_geometric_spreading(As, delta))
        
    def test_compute_amplitude(self, filtfc, delta, station_freq):
        #Calculates all the parameters.
        mu = 3*math.pow(10,11)
        q = 640.0*math.pow(15,0.35) #Q value
        beta = 3.5 #km/s
        cn= 1/(4*mu*beta*1e7)
        fc = 1.0
        nyquist = 15
        fault_radius = 2.34*beta/(2*math.pi*fc)
        Mo = 2.29*100000000*math.pow((1e5*fault_radius),3)
        #checks to see if the method computes the correct amplitude.
        self.assertEqual(amplitude,self.compute_amplitude(fc,Mo,cn,filtfc,delta,station_freq,nyquist))
        
    def test_compute_attenuation(self, delta):
        q = 640.0*math.pow(15,0.35) #Q value
        beta = 3.5 #km/s
        fc = 1.0
        
        self.assertEqual(attenuation,self.compute_attenuation(fc,delta,beta,q))
        
    def test_amplitude_power_conversion(self, As):
        power = As*As
        self.assertEqual(power,self.amplitude_power_conversion(As))
        
    def test_distance_signal_adjustment(self):
        
    def test_magnitude_signal_adjustment(self):
        
    def test_min_detect(self):
                                        
    def test_generate_earthquake(self):                