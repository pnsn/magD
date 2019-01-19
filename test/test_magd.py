import unittest
import sys
import os
sys.path.append(os.path.abspath('..'))

from magD.magD import MagD
from magD.mapGrid import MapGrid
import configparser




class TestMagD(unittest.TestCase):
    def setup(self):
        pass

    # def test_initiation(self):
    #     magd=MagD("config/test.ini")
    #     self.assertEqual(magd.lat_min, 36.0 + magd.grid_resolution)
    #     self.assertEqual(magd.lat_max, 46.0)
    #     self.assertEqual(magd.lon_min, -130.0)
    #     self.assertEqual(magd.lon_max, -120.0 + magd.grid_resolution)
    #     self.assertEqual(magd.grid_resolution, 1.0)
    #     self.assertEqual(magd.num_solutions, 2)
    #     self.assertEqual(magd.nyquist_correction, 0.4)
    #     self.assertEqual(magd.mu, 3e11)
    #     self.assertEqual(magd.qconst, 300.0)
    #     self.assertEqual(magd.beta, 3.5)


    '''
    1001,HHZ,UW,--,46.349,-124.051
    1002,HHZ,UW,--,46.492,-124.049
    1003,HHZ,UW,--,46.771,-124.081
    1005,HHZ,UW,--,47.114,-124.166
    1218,HHZ,UW,--,47.33,-123.791
    Distances (km) from https://www.geodatasource.com/distance-calculator
    ---------------------------------------------------------------
    1218    110.85  95.22   65.92   37.13   0

    1005    85.5    69.73   38.68   0       37.13

    1003    46.98   31.12   0       38.68   65.92

    1002    15.9    0       31.12   69.73   95.22

    1001    0       15.9    46.98   85.5    110.85

            1001    1002    1003    1005    1218
    ---------------------------------------------------------------------

    '''


    def test_spatial_distance(self):
        config_dir = "config/spatial"
        grid_conf= configparser.ConfigParser()
        grid_conf.read(config_dir + "/grid.ini")
        data_conf= configparser.ConfigParser()
        data_conf.read(config_dir + "/data.ini")
        grids = []
        data_srcs ={}
        for type in [grid_conf['grid']['grid_types']]:
            grids.append(MapGrid(grid_conf['grid'], type))
        for key in data_conf.sections():
            data_srcs[key]=data_conf[key]
        magD=MagD(grids, data_srcs)
        magD.read_stations()
        magD.make_origins()
        testo = magD.origins[-1]
        testo.lat = 46.349
        testo.lon = -124.051
        magD.origins[-1] = testo

        #overide lat/lon of one origin and test it for distance
        # giv it lat/lon of one of the stations (1001)
        grids = magD.build_grids()

        testo = magD.origins[-1]
        self.assertEqual(testo.lat, 46.349)
        self.assertEqual(testo.lon, -124.051)
        '''
        These should be in order from closest to furthest
        We are using the lat/lon of first station as test
        0. self 0
        1. 1002 15.9
        2. 1003 46.98
        3. 1005 85.5
        4. 1218 110.85
        '''
        s = testo.solutions
        self.assertEqual(str(s[0].scnl.sta), '1001')
        self.assertEqual(s[0].distance, 0.0)

        self.assertEqual(str(s[1].scnl.sta), '1002')
        self.assertEqual(round(s[1].distance,1), 15.9)

        self.assertEqual(str(s[2].scnl.sta), '1003')
        self.assertEqual(round(s[2].distance,1), 47.0)

        self.assertEqual(str(s[3].scnl.sta), '1005')
        self.assertEqual(round(s[3].distance,1), 85.5)

        self.assertEqual(str(s[4].scnl.sta), '1218')
        self.assertEqual(round(s[4].distance,1), 110.9)

        '''
        #    since we pulled the last origin (corner of matrix)
        #    compare. For four station it should be sta 1005 or 85.5 km
        '''
        mat = magD.grids[0].matrix
        self.assertEqual( round( mat[-1][-1], 1 ), 85.5 )




if __name__ == '__main__':
    unittest.main()
