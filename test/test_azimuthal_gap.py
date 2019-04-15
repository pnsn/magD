import unittest
from obspy.geodetics.base import gps2dist_azimuth as distaz
import magD.seis as seis
from magD.scnl import Scnl
from magD.origin import Origin


class TestAzimuthalGap(unittest.TestCase):
    def setup(self):
        pass

    def mind_the_gap(self, lats, lons, source_lat=41, source_lon=-116):
        scnls = []
        for i in range(len(lats)):
            scnl = Scnl("sta", "chan", "net", "loc", 0, lats[i], lons[i])
            scnls.append(scnl)
        source = Origin(source_lat, source_lon)
        return seis.azimuthal_gap(scnls, source)

    '''
        lat/lon 1 is station
        lat/lon 2 is source
        a is azimuth
        b is back azimuth
               0
               |
         270  -   -  90
               |
              180

    '''
    def test_azimuth(self):
        source_lat = 41
        source_lon = -116
        lat1 = 40.09
        lon1 = -116
        lat2 = 41.01
        lon2 = -116
        lat3 = 41
        lon3 = -115.99
        lat4 = 41
        lon4 = -116.01

        dist, a, b = distaz(source_lat, source_lon, lat1, lon1)
        if round(b) == 360:
            b = 0
        self.assertEqual(a, 180)
        self.assertEqual(b, 0)
        dist, a, b = distaz(source_lat, source_lon, lat2, lon2)
        if round(a) == 360:
            a = 0
        self.assertEqual(round(a), 0)
        self.assertEqual(round(b), 180)
        dist, a, b = distaz(source_lat, source_lon, lat3, lon3)
        self.assertEqual(round(a), 90)
        self.assertEqual(round(b), 270)
        dist, a, b = distaz(source_lat, source_lon, lat4, lon4)
        self.assertEqual(round(a), 270)
        self.assertEqual(round(b), 90)

    def test_equal_gaps(self):
        lats = [40.09, 41.01, 41.0, 41.0]
        lons = [-116, -116, -115.99, -116.01]
        gap = self.mind_the_gap(lats, lons)
        self.assertEqual(round(gap), 90)
    # https://www.movable-type.co.uk/scripts/latlong.html

    def test_large_small_gap(self):
        lats = [42, 42]
        lons = [-116.1, -115.9]
        gap = self.mind_the_gap(lats, lons)
        self.assertEqual(round(gap), 351)

    def test_large_small_gap2(self):
        lats = [42, 42]
        lons = [-115.97, -115.9]
        gap = self.mind_the_gap(lats, lons)
        self.assertEqual(round(gap), 357)

    def test_two_similar_points(self):
        lats = [42, 42]
        lons = [-115.9, -115.9]
        gap = self.mind_the_gap(lats, lons)
        self.assertEqual(round(gap), 360)


if __name__ == '__main__':
    unittest.main()
