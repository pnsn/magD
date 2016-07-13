import unittest
# import numpy as np
from geojson import is_valid
import sys, os
sys.path.append(os.path.abspath('..'))
from MagD.core import parse_json_file
from MagD.contour import Contour
from pprint import pprint
import numpy as np
import json


class TestContour(unittest.TestCase):
    
    def setUp(self):
        self.json_in=parse_json_file('../data/data.json')
        self.levels=[1,2,3,4,5]
    
    def tearDown(self):
        self.json_in = None
        self.levels =None
        
    """Test case for geojson conversions"""
    
    def test_geojson_stub(self):
        """does geojson stub return valid json?"""
        cn=Contour(self.json_in,self.levels)
        geoj=cn.geojson_stub()
        self.assertEqual(geoj['features'][0]['type'], 'Feature')
    
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

    def test_dim3_to_multilinestring_small(self):
        """convert from simple arrays to MultilineString"""
        cn=Contour(self.json_in,self.levels)
        np_coord = np.array([-122.0, 45])
        coord = [-122.0, 45]
        #np list
        linestring_np=cn.dim3_to_multilinestring([[np_coord, np_coord],[np_coord, np_coord]])
        valid=is_valid(linestring_np)
        self.assertEqual(valid['valid'], 'yes', valid['message'])
        
        linestring=cn.dim3_to_multilinestring([[coord, coord],[coord, coord]])
        valid=is_valid(linestring)
        self.assertEqual(valid['valid'], 'yes', valid['message'])
        
    def test_dim3_to_multilinestring(self):
        """convert from contours to MultilineString"""
        cn=Contour(self.json_in,self.levels)
        mls=cn.dim3_to_multilinestring(cn.contours)
        valid=is_valid(mls)
        self.assertEqual(valid['valid'], 'yes', valid['message'])
        
   
    def test_create_contour_obj(self):
        """Test Contour obj creation"""
        cn=Contour(self.json_in,self.levels)
        self.assertTrue(cn.levels==self.levels)
        self.assertTrue(len(cn.lats) > 0)
        self.assertTrue(len(cn.lons) > 0)
        self.assertTrue(len(cn.vals) > 0)
        self.assertTrue(len(cn.vals) == len(cn.lats) * len(cn.lons))
        self.assertTrue(len(cn.contours) == len(cn.levels))
        # print(cn.contours[1])
        
        
    def test_make_geojson(self):
        """Test creation of geojson obj with MultilineString obj"""
        cn=Contour(self.json_in, self.levels)
        geoj =cn.make_geojson()
        self.assertTrue(json.dumps(geoj))
        
    def test_write_json_to_file(self):
        cn=Contour(self.json_in, self.levels)
        geoj =cn.make_geojson()
        self.assertTrue(cn.write_json_to_file(geoj, "../data/test/geotest.json"))
        
        
        
        
        
if __name__ == '__main__':
    unittest.main()