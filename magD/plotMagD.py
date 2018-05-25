
# usage:
#to install basemap on osx
#brew install geos
#pip3 install https://github.com/matplotlib/basemap/archive/v1.1.0.tar.gz
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import datetime
import math


from .magD import MagD

class PlotMagD():
    def __init__(self, magD, type):
        self.magD=magD
        c=magD.conf['plot']
        self.mag_min=float(c.get('mag_min'))
        self.mag_max=float(c.get('mag_max'))
        self.title=c.get('title')
        self.type=type
    #return plot object
    def plot(self):
        return plt

    #returns center of map based on config min/max
    def map_center(self):
        lat=0.5*(self.magD.lat_max-self.magD.lat_min) + self.magD.lat_min
        lon=0.5*(self.magD.lon_max-self.magD.lon_min) + self.magD.lon_min
        return lat,lon


    '''
        create basemap with bounding cords
        (lat_min, lat_max, lon_min, lon_max)
        and projection
    '''
    def basemap(self,bounds,projection='merc'):
        lat_0,lon_0=self.map_center()
        return Basemap(llcrnrlon=bounds[2]+2,llcrnrlat=bounds[0]+2,urcrnrlon=bounds[3]-2,
                    urcrnrlat=bounds[1]-2, resolution='i',projection=projection,
                    lon_0=lon_0,lat_0=lat_0)

    '''
        contour levels: min,max and steps
        create array of floats from min to max in steps of step
    '''
    def create_contour_levels(self, z, step):
        mag_min=int(np.amin(z)*10)
        mag_max=int(np.amax(z)*10)
        levels=[x / 10.0 for x in range(mag_min, mag_max, step)]
        return levels

    '''
        For turn vector(list) into matrix of len(lats) x len(lons)
        if two vectors exist diff
    '''

    def process_grid(self):
        this_grid=self.evaluate_grid(self.magD.grid)
        if self.magD.other_grid:
            other_grid=self.evaluate_grid(self.magD.other_grid)
            new_grid=[]
            for i in other_grid.matrix:
                row =[a - b  for a, b in zip(this_grid[i], other_grid[i])]
                new_grid.append(row)
            return new_grid
        else:
            return this_grid


    def evaluate_grid(self,grid):
        new_grid=[]
        max=np.max(grid.matrix)
        if grid.type=="distance":
            for row in grid.matrix:
                r=[math.log(distance)/math.log(max) for distance in row]
                new_grid.append(r)
        elif grid.type=="gap":
            for row in grid.matrix:
                r=[gap/max for gap in row]
                new_grid.append(r)
        else:
            new_grid=grid.matrix
        return new_grid


    '''
        project x,y onto map coordinates
        returns x,y projected coords
    '''
    def project_x_y(self,map):
        return map(*np.meshgrid(self.magD.lon_list(),self.magD.lat_list()))

    def meridian_interval(self,lon_min,lon_max):
        return np.linspace(lon_min,lon_max,4,dtype = int)

    def parallel_interval(self,lat_min,lat_max):
        return np.linspace(lat_min,lat_max,4,dtype = int)

    #make outfile unique to avoid clobbering
    def outfile_with_stamp(self,name):
        return "{}-{}-{}.png".format(name,
            datetime.datetime.now().strftime("%Y%m%d%H%M%S"),self.type)

    #for key what is plot color in config
    def plot_color_label(self,key):
        return MagD.conf[key]['color'], MagD.conf[key]['label']
