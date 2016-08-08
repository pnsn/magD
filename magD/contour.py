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





class Contour:
    def __init__(self, json_in, levels):
        self.min_level=None
        self.max_level=None
        self.lats =[]
        self.lons =[]
        self.vals=[]
        self.matplotlib_contours = []
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
    
    #takes 4dim list of contours for matplotlib and builds GeometryCollection
    #the numpy arrays need to be converted to python lists before conversion
    #{"type": "GeometryCollection"
    #     "geometries": [
    #             {
    #                 "type": "MultiLineString",
    #
    #                 "coordinates[
    #                     [
    #                        [x,y],[x,y]
    #                      ], 
    #                           [x,y], [x,y]....
    #                      ]
    #                    ],
    #                  "properties":{
    #                     "level": contour_val 
    #                  }
    #             },
    #             {
    #                 "type": "MultiLineString",
    #
    #                 "coordinates[
    #                     [
    #                        [x,y],[x,y]
    #                      ], 
    #                           [x,y], [x,y]....
    #                      ]
    #                    ],
    #                  "properties":{
    #                     "level": contour_val 
    #                  }
    #             }
    #     ]
    #
    # }
    def build_geometry_collection(self):
        geocol={"type": "GeometryCollection", "geometries": []}
        index=0
        for contour in self.matplotlib_contours:
            if len(contour)>0:
                mls={'type': 'MultiLineString'
                      ,'coordinates': contour
                      ,'properties': {
                        'level': str(self.levels[index])
                      } 
                    }
                geocol["geometries"].append(mls)
                index +=1
            else:
                #remove this level from levels
                del self.levels[index]
        return geocol
    

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
              
    #using matplotlib pull out contours in 4 dim array:
    #[ #levels
        #[ level 
            #[ #contour
                #[lon,lat] #points
                #...
            #] 
            #...
        #]
        #...
    #]

    def parse_contours(self):
        X, Y = np.meshgrid(self.lons, self.lats)
        Z= np.reshape(self.vals, (len(self.lats), len(self.lons)))
        contours= plt.contour(X,Y,Z, self.levels)
        for contour in contours.collections:
            paths = []
            # for each separate section of the contour line
            for path in contour.get_paths():
                # a line must have more than one point!
                if len(path)>1:
                    #path object
                    xy = []
                    # for each segment of that section
                    for vv in path.iter_segments():
                        xy.append(vv[0])
                    #save np as python list
                    paths.append(np.vstack(xy).tolist())
            self.matplotlib_contours.append(paths)
     
        
    
    #write json_obj to 
    def write_json_to_file(self, json_obj, path):
        with open(path, 'w') as outfile:
            json.dump(json_obj, outfile, indent=4)