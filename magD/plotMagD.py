
'''
usage:
PlotMagD is a matplotlib wrapper specific to MapGrid plotting
It is not required to plot MapGrids
to install basemap on osx
brew install geos
pip3 install https://github.com/matplotlib/basemap/archive/v1.1.0.tar.gz

'''
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import datetime

# from .mapGrid import MapGrid


class PlotMagD():
    def __init__(self, mapGrid):
        self.mapGrid = mapGrid

    def plot(self):
        return plt

    def map_center(self):
        '''returns center of map based on config min/max'''
        lat = 0.5 * (self.mapGrid.lat_max - self.mapGrid.lat_min) + \
            self.mapGrid.lat_min
        lon = 0.5 * (self.mapGrid.lon_max - self.mapGrid.lon_min) + \
            self.mapGrid.lon_min
        return lat, lon

    def basemap(self, bounds, projection='merc'):
        lat_0, lon_0 = self.map_center()
        return Basemap(llcrnrlon=bounds[2] + 2, llcrnrlat=bounds[0] + 2,
                       urcrnrlon=bounds[3] - 2, urcrnrlat=bounds[1] - 2,
                       resolution='i', projection=projection, lon_0=lon_0,
                       lat_0=lat_0)

    def project_x_y(self, map):
        '''project x,y onto map coordinates returns x,y projected coords '''
        return map(*np.meshgrid(self.mapGrid.lon_list(),
                   self.mapGrid.lat_list()))

    def meridian_interval(self, lon_min, lon_max):
        return np.linspace(lon_min, lon_max, 4, dtype=int)

    def parallel_interval(self, lat_min, lat_max):
        return np.linspace(lat_min, lat_max, 4, dtype=int)

    def outfile_with_stamp(self, path):
        '''create unique path for outfile'''
        return "{}{}-{}-{}.png".format(path, self.mapGrid.name,
                                       datetime.datetime.now()
                                       .strftime("%Y%m%d%H%M%S"),
                                       self.mapGrid.type)
