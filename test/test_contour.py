import unittest
import sys
import os
sys.path.append(os.path.abspath('..'))
from MagD.core import parse_json_file
from MagD.contour import Contour
from pprint import pprint
import json




class TestContour(unittest.TestCase):
    
    def setUp(self, file="data/data_large.json",levels=[1,2,3,4,5]):
        self.json_in=parse_json_file(file)
        self.levels=levels
    
    def tearDown(self):
        self.json_in = None
        self.levels =None
        
        
    """Test case for geojson conversions"""
    

    def test_build_geometry_collection(self):
        """convert from contours to collection of MLS objects"""
        cn=Contour(self.json_in,self.levels)
        geocol=cn.build_geometry_collection()
        self.assertTrue(json.loads(json.dumps(geocol)))
        self.assertEqual(cn.write_json_to_file(geocol, "data/contours.json"), None)
        
if __name__ == '__main__':
    unittest.main()