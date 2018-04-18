
# usage:
#to install basemap on osx
#brew install geos
# pip3 install https://github.com/matplotlib/basemap/archive/v1.1.0.tar.gz
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np


from magD import MagD

class PlotMagD():
    def __init__(self, magD, outfile):
        self.magD=magD
        self.outfile=outfile


    #returns center of map based on config min/max
    def map_center(self):
        lat=0.5*(self.magD.lat_max-self.magD.lat_min) + self.magD.lat_min
        lon=0.5*(self.magD.lon_max-self.magD.lon_min) + self.magD.lon_min
        return lat,lon

    #create fig obj, width, height in inches
    def figure(self, width, height):
        return plt.figure(figsize=(width,height))

    #create basemap
    def basemap(self,projection='merc'):
        lat_0,lon_0=self.map_center
        return Basemap(llcrnrlon=lon_min+2,llcrnrlat=lat_min+2,urcrnrlon=lon_max-2,
                    urcrnrlat=lat_max-2, resolution='i',projection=projection,
                    lon_0=lon_0,lat_0=lat_0)


    #returns X,Y,Z and levels (list of contours)
    def create_contour_levels(self):
        z=[o.min_detection(num_stas) for o in  magD.origin_collection]
        npz=np.asarray(z)
        Z=np.reshape(npz, ((len(magD.lat_list), len(magD.lon_list))))
        X,Y=m(*np.meshgrid(magD.lon_list,magD.lat_list))
        #create list of floats from min max mag
        mag_min=int(np.amin(npz)*10)
        mag_max=int(np.amax(npz)*10)
        levels=[x / 10.0 for x in range(mag_min, mag_max, 2)]
        return X,Y,Z,levels
