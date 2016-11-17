import unittest
import sys
import os
sys.path.append(os.path.abspath('..'))
# from MagD.core import parse_json_file
from MagD.map_layer import MapLayer
from pprint import pprint
import numpy as np
import json




class TestMapLayer(unittest.TestCase):
    
    def setUp(self, file="data/data_large.json",levels=[1,2,3,4,5]):
        self.levels=levels
        self.lats=np.arange(-125, 117, 0.5)
        self.lons=np.arange(42, 49, 0.5)
        self.vals = np.random.randint(0,5, size=(len(self.lats)*len(self.lons)))


    def tearDown(self):
        self.levels=None
        self.lats=None
        self.lons=None
        self.vals =None



    """Test case for geojson conversions"""
    def test_make_contours(self):
        layer=MapLayer(self.lats, self.lons, self.vals, self.levels)
        layer.make_contours()
        self.assertTrue(json.loads(json.dumps(layer.geojson_mls)))

    """Test case for heatmap conversions"""
    def test_make_heatmap(self):
        layer=MapLayer(self.lats, self.lons, self.vals, self.levels)
        layer.make_heatmap("heater")
        self.assertTrue(json.loads(json.dumps(layer.heatmap)))
        self.assertTrue(layer.heatmap["name"]=="heater")
        self.assertTrue(layer.heatmap['coordinates'][-1][0] == self.lats[-1])
        self.assertTrue(layer.heatmap['coordinates'][-1][1] == self.lons[-1])
        self.assertTrue(layer.heatmap['coordinates'][-1][2] == self.vals[-1])
        self.assertTrue(layer.heatmap_to_file("./data/test.json")==None)
        
   
if __name__ == '__main__':
    unittest.main()