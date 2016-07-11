'''
Class to read points from a json obj of form:
...
points:{
    point{
        lat: float,
        lng: float,
        count: float
    }
}

And creates geojson or topojson of contour lines
TODO:
Parameterize attr names
'''
import matplotlib.pyplot as plt
import numpy as np

class Contour:
    def __init__(self, json_in, levels):
        self.min_level=None
        self.max_level=None
        self.lats =[]
        self.lons =[]
        self.vals=[]
        self.contours = []
        self.levels=levels
        self.parse_json(json_in)
        self.make_contours
    
    def add_lat(self,lat):
        self.lats.append(lat)
   
    def add_lon(self,lon):
       self.lons.append(lon)

    def add_val(self,val):
       self.vals.append(val)
   
    def set_min_val(self,val):
        self.min_level=val
        
    def set_max_val(self,val):
       self.max_level=val
  
    #read json data and populate attrs
    def parse_json(self, data):
      for point in data["points"]:
          if point['count'] > self.max_level:
              self.set_max_val(point['count'])
          if point['count']< self.min_level:
              self.set_max_val(point['count'])
          self.add_val(point['count'])
          self.add_lat(point['lat'])
          self.add_lon(point['lng'])
          
    
    def make_contours(self):
        # print [method for method in dir(cn.collections[0]) if callable(getattr(cn.collections[0], method))]
        X, Y = np.meshgrid(self.lons, self.lats)        
        # xyz.append([point['lat'], point['lon'], point['count']])
        Z= np.reshape(vals, (len(self.lats), len(self.lons)))
        # levels=list(range(1,11))
        cn= plt.contour(X,Y,Z, self.levels)
        for cc in cn.collections:
            paths = []
            # for each separate section of the contour line
            for pp in cc.get_paths():
                #path object
                # print(pp)
                xy = []
                # for each segment of that section
                for vv in pp.iter_segments():
                    xy.append(vv[0])
                paths.append(np.vstack(xy))
            self.contours.append(paths)
        
        
        
        
    # def parse_mplot_contours(self):

      # for each contour line
      