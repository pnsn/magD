import unittest
# import numpy as np
import json
from geojson import MultiLineString, LineString, is_valid
import sys, os
sys.path.append(os.path.abspath('..'))
from MagD.core import parse_json_file
from MagD.contour import Contour


class TestContour(unittest.TestCase):
    
    def setUp(self):
        self.json_in=parse_json_file('data/data.json')
        self.levels=[1,2,3,4,5]
    
    def tearDown(self):
        self.json_in = None
        self.levels =None
        
    # """Test case for JSON conversions"""
    # def test_np_to_linestring(self):
    #      """convert numpy to valid geojson obj"""
    #
    #    self.assertTrue(True)
        
    # def test_np_to_multilinestring(self):
    #     """convert from numpy to LineString to MultilineString"""
    #     self.assertTrue(True)
        
    def test_create_contour_obj(self):
        cn=Contour(self.json_in,self.levels)
        self.assertTrue(cn.levels==self.levels)
        self.assertTrue(len(cn.lats) > 0)
        self.assertTrue(len(cn.lons) > 0)
        self.assertTrue(len(cn.vals) > 0)
        self.assertTrue(len(cn.vals) == len(cn.lats) and len(cn.lats) == len(cn.lons))
        print(len(cn.contours))
        print(len(cn.levels))
        self.assertTrue(len(cn.contours) == len(cn.levels))
        
        
        
            
     
        
        
        
if __name__ == '__main__':
    unittest.main()