'''
Class takes rows list (lats), cols list (lons), values list, mag_bin (what to bin magnitudes on e.g .5 would 0,.5, 1.0,. 1.5...)
Creates contours using Matplotlib
Create geojson file 
'''
import numpy as np
from pprint import pprint
import json
import csv


class MapLayer:
    def __init__(self, lats, lons, vals, mag_bin):
        #round lat/lons to 4 decimals
        self.lats =np.round(np.array(lats),4) 
        self.lons =np.round(np.array(lons),4)
        self.vals= vals
        self.mag_bin= 1.0/mag_bin
        self.levels=[]
        #get unique values and sort
        # self.geojson_mls={"type": "GeometryCollection", "geometries": []}
        self.grid3={}
        self.featured_collection={"type": "FeatureCollection", "features": []}
   
    
    #create 2dim grid of values (mags)
    def make_grid3(self, name):
        self.grid3['lat_start']=self.lats[0]
        self.grid3['lon_start']=self.lons[0]
        self.grid3['lat_step']=self.lats[1]-self.lats[0]
        self.grid3['lon_step']=self.lons[1]-self.lons[0]
        vals=self.vals
        self.grid3['max']= round(max(self.vals),2)
        # print self.grid3['max']
        self.grid3['min'] = round(min(vals),2)
        lats_len=len(self.lats)
        lons_len=(len(self.lons))
        
        self.grid3["grid"]=np.reshape(vals, (len(self.lats), len(self.lons))).tolist()
        print self.grid3["grid"]
         
    def build_geojson_feature_collection(self):
     #convert our data grid to GeoJSON
     index=0     
     for lat in self.lats:
       for lon in self.lons:
          newPoint = { 
            "geometry": {
              "type": "Point",
              "coordinates": [lat,lon]},
              "properties": { "z": round(self.vals[index],2)},
              "type": "Feature"
            }
          index+=1
          self.featured_collection['features'].append(newPoint);
   
    def write_geojson_to_file(self, path):
        with open(path, 'w') as outfile:
            json.dump(self.featured_collection, outfile, indent=4)
   
    def write_json_to_file(self, path):
        with open(path, 'w') as outfile:
            json.dump(self.grid3, outfile, indent=4)
            
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