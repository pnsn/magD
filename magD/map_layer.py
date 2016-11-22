'''
Class takes rows list (lats), cols list (lons), values list, and contour levels list
Creates contours using Matplotlib
Create geojson file 
'''
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
import json
import csv


class MapLayer:
    def __init__(self, lats, lons, vals):
        #round lat/lons to 4 decimals
        self.lats =np.round(np.array(lats),4) 
        self.lons =np.round(np.array(lons),4)
        self.vals= vals

        self.levels=[]
        #get unique values and sort
        self.geojson_mls={"type": "GeometryCollection", "geometries": []}
        self.grid3={}
   
    
    
    # #put vals into bins
    # #then set bondaries to lagest level
    # def fit_values(self, vals):
    #     vals=[round(x*4.0)/4.0 for x in vals]
    #     self.levels =sorted(list(set(vals)))
    #     lats_len=len(self.lats)
    #     lons_len=(len(self.lons))
    #     for i in range(lats_len):
    #         for j in range(lons_len):
    #             if i==0 or j==0 or i == lats_len-1 or lons_len -1:
    #                 vals[i*lons_len +j]=self.levels[-1]
    #     return vals
    #
    #


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
    
    
    def make_grid3(self, name, with_keys=False):
        self.grid3['lat_start']=self.lats[0]
        self.grid3['lon_start']=self.lons[0]
        self.grid3['lat_step']=abs(self.lats[1]-self.lats[0])
        self.grid3['lon_step']=abs(self.lons[1]-self.lons[0])
        self.grid3["grid"]=np.round(np.reshape(self.vals, (len(self.lons), len(self.lats))),2).tolist()
        # i=0
        # self.grid3["name"]= name
        # for lat in self.lats:
        #     for lon in self.lons:
        #         if with_keys:
        #             self.grid3['coordinates'].append({'lat':lat, 'lon':lon, 'count': round(self.vals[i],2)})
        #         else:
        #             self.grid3['coordinates'].append([lat, lon, round(self.vals[i],2)])
        #         i+=1
                
    def get_grid3(self):
        return self.grid3
    
    
    
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

    # def make_contours(self):
   #      mpl_contours=[]
   #      X, Y = np.meshgrid(self.lons, self.lats)
   #      #here
   #      Z= np.reshape(self.vals, (len(self.lats), len(self.lons)))
   #      contours= plt.contour(X,Y,Z, self.levels)
   #      for contour in contours.collections:
   #          paths = []
   #          # for each separate section of the contour line
   #          for path in contour.get_paths():
   #              # a line must have more than one point!
   #              if len(path)>1:
   #                  #path object
   #                  xy = []
   #                  # for each segment of that section
   #                  for vv in path.iter_segments():
   #                      xy.append(vv[0])
   #                  #save np as python list
   #                  paths.append(np.vstack(xy).tolist())
   #          mpl_contours.append(paths)
   #      self.build_geometry_collection(mpl_contours)
    
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
    # def build_geometry_collection(self, contours):
    #     index=0
    #     for contour in contours:
    #         if len(contour)>0:
    #             mls={'type': 'MultiLineString'
    #                   ,'coordinates': contour
    #                   ,'properties': {
    #                     'level': str(self.levels[index])
    #                   }
    #                 }
    #             self.geojson_mls["geometries"].append(mls)
    #             index +=1
    #         else:
    #             #remove this level from levels
    #             print "what the fuck..... level = %f"%self.levels[index]
    #             del self.levels[index]
    #     print self.geojson_mls
    #
    def contours_to_file(self, path):
        self.write_json_to_file(path, self.geojson_mls)
        
    def grid3_to_file(self, path):
        self.write_json_to_file(path, self.grid3)
    #write self.geojson to file of path path
    def write_json_to_file(self, path, dict):
        with open(path, 'w') as outfile:
            json.dump(dict, outfile, indent=4)
            
    def write_to_csv(self, path):
        i=0
        with open(path, 'w') as csvfile:
            fieldnames = ['lat', 'lon', 'val']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for lat in self.lats:
                for lon in self.lons:
                    writer.writerow({'lat': lat, 'lon': lon, 'val': self.vals[i]})
                    i+=1
        print "done with csv and index = %i and length =%i"%(i, len(self.vals))
