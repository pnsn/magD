'''
Class takes rows list (lats), cols list (lons), values list, and contour levels list
Creates contours using Matplotlib
Create geojson file 
'''
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
import json


class MapLayer:
    def __init__(self, lats, lons, vals, levels):
        self.lats = lats
        self.lons =lons
        self.vals=vals
        self.levels=levels
        self.geojson_mls={"type": "GeometryCollection", "geometries": []}
        self.heatmap={"coordinates": []}
   
    
    
    
    '''
    create obj of form
        {
        name: string
        coordinates:[
            [lat,lon,val],
            ...
            [lat,lon,val]
        
        ]    
        }    
        
    pass in name, returns dict
    '''
    #scale by max_value
    def make_heatmap(self, name, max_val=3):
        #scaler Heatmap expects largest value to be 1.0
        index=0
        self.heatmap["name"]= name
        for lat in self.lats:
            for lon in self.lons:
                val =round(self.vals[index]/max_val ,3)
                self.heatmap['coordinates'].append([lat, lon, str(val)])
                index+=1
        
    def get_heatmap(self):
        return self.heatmap
    
    
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

    def make_contours(self):
        mpl_contours=[]
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
            mpl_contours.append(paths)
        self.build_geometry_collection(mpl_contours)
    
    # #set very high number (> all levels) at edges to close
    # #contours that extend past border
    # def set_boundaries(self):
    #   for lat in self.lats:
    #     for lon in self.longs:
    #       #if 1st lat and
   
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
    def build_geometry_collection(self, contours):
        index=0
        for contour in contours:
            if len(contour)>0:
                mls={'type': 'MultiLineString'
                      ,'coordinates': contour
                      ,'properties': {
                        'level': str(self.levels[index])
                      } 
                    }
                self.geojson_mls["geometries"].append(mls)
                index +=1
            else:
                #remove this level from levels
                del self.levels[index]
    
    def contours_to_file(self, path):
        self.write_json_to_file(path, self.geojson_mls)
        
    def heatmap_to_file(self, path):
        self.write_json_to_file(path, self.heatmap)
    #write self.geojson to file of path path
    def write_json_to_file(self, path, dict):
        with open(path, 'w') as outfile:
            json.dump(dict, outfile, indent=4)