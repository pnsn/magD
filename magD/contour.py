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
from pprint import pprint
import json
from topojson import topojson
from geojson import MultiLineString, LineString, Point





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
        self.parse_contours()
    
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
    
    #takes lon, lat and return geojson Point
    def coords_to_point(self, lat, lon):
        return Point((float(lon),float(lat)))
    
    #takes 2dim list of lng,lats and returns LineString
    #iterate through for to ensure lists and not np objects
    def dim2_to_linestring(self, points):
        coords=[]
        for point in points:
            if "tolist" in dir(point):
                point =point.tolist()
            coords.append(point)
        return LineString(coords)
    
    #takes list of lineStrings and returns MultiLineString
    def dim3_to_multilinestring(self, linestrings):
        lines=[]
        index=0
        for line in linestrings:
            if len(line)>0:
                if "tolist" in dir(line):
                    line=line.tolist()
                coords=[]
                for point in line:
                    if "tolist" in dir(point):
                        point =point.tolist()
                    coords.append(point)
                lines.append(coords)
                index +=1
            else:
                #remove this level from levels
                del self.levels[index]
        return MultiLineString(lines)        
    
    def geojson_stub(self):
        return  json.loads('{"type": \
                                "GeometryCollection", \
                                "features": \
                                    [{"type": "Feature", \
                                    "geometry": {} \
                            }]}')
  
    #read json data and populate attrs
    def parse_json(self, data):
      for point in data["points"]:
          if point['count'] > self.max_level:
              self.set_max_val(point['count'])
          if point['count']< self.min_level:
              self.set_min_val(point['count'])
          self.add_val(point['count'])
          if point['lat'] not in self.lats:
              self.add_lat(point['lat'])
          if point['lng'] not in self.lons:
              self.add_lon(point['lng'])
    
    #create 4 dim array of contours (self.contours)
    #[ #countours
        #[ contour 
            #[ #segment of contour
                #[lon,lat] #points
                #...
            #] 
            #...
        #]
        #...
    #]
    def parse_contours(self):
        # print [method for method in dir(cn.collections[0]) if callable(getattr(cn.collections[0], method))]
        X, Y = np.meshgrid(self.lons, self.lats)
        Z= np.reshape(self.vals, (len(self.lats), len(self.lons)))
        contours= plt.contour(X,Y,Z, self.levels)
        for contour in contours.collections:
            paths = []
            # for each separate section of the contour line
            for path in contour.get_paths():
                #path object
                xy = []
                # for each segment of that section
                for vv in path.iter_segments():
                    xy.append(vv[0])
                #save np as python list
                paths.append(np.vstack(xy).tolist())
            self.contours.append(paths)
     
        
        
    #from self.contour create geojson obj
    def make_geojson(self):
        geoj=self.geojson_stub()
        mls_obj=self.dim3_to_multilinestring(self.contours)
        geoj['geometry']=mls_obj
        return geoj
    
    #write json_obj to 
    def write_json_to_file(self, json_obj, path):
        with open(path, 'w') as outfile:
            json.dump(json_obj, outfile)
        
    def make_topojson(self, geojson, path):
        return topojson(geojson, path)

      # for each contour line
      