import unittest
# import numpy as np
import sys
import os
sys.path.append(os.path.abspath('..'))
from MagD.core import parse_json_file
from MagD.contour import Contour
from pprint import pprint
import numpy as np
import json
from geojson import is_valid




class TestContour(unittest.TestCase):
    
    def setUp(self, file="data/data_large.json",levels=[1,2,3,4,5]):
        self.json_in=parse_json_file(file)
        self.levels=levels
    
    def tearDown(self):
        self.json_in = None
        self.levels =None
        
        
    """Test case for geojson conversions"""
    
    def test_coords_to_point(self):
        """convert numpy array to valid geojson point"""
        cn=Contour(self.json_in,self.levels)
        coord = np.array([-122.0, 45])
        point =cn.coords_to_point(coord[0], coord[1])
        valid =is_valid(point)
        self.assertEqual(valid['valid'], 'yes', valid['message'])
        
    
    def test_dim2_to_linestring(self):
        """convert  2dim list or numpy to valid geojson obj"""
        cn=Contour(self.json_in,self.levels)
        np_coord = np.array([-122.0, 45])
        coord = [-122.0, 45]
        #np list
        linestring_np=cn.dim2_to_linestring([np_coord, np_coord])
        valid=is_valid(linestring_np)
        self.assertEqual(valid['valid'], 'yes', valid['message'])
        # python list
        linestring=cn.dim2_to_linestring([coord, coord])
        valid=is_valid(linestring)
        self.assertEqual(valid['valid'], 'yes', valid['message'])

    def test_build_geometry_collection(self):
        """convert from contours to collection of MLS objects"""
        cn=Contour(self.json_in,self.levels)
        geocol=cn.build_geometry_collection()
        self.assertTrue(json.loads(json.dumps(geocol)))
        for mls in geocol["geometries"]:
            valid=is_valid(mls)
            self.assertEqual(valid['valid'], 'yes', valid['message'])


    
   
    def test_make_topojson(self):
        cn=Contour(self.json_in, self.levels)
        geoj=cn.build_geometry_collection()
        # pathin="../data/test/geotest.json"
        pathout = "data/topotest.json"
        topo =cn.make_topojson(geoj, pathout)

        
if __name__ == '__main__':
    unittest.main()