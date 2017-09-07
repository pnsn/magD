'''
Class for Mag origins
Instanced are points in a grid and have
 lat, lon and asc list of sorted detectable magnitudes

 
'''
import numpy as np

#detections is list of tuples (Mw, scnl)
class Origin:
  collection=[]
  
  def __init__(self, lat, lon):
      self.lat=lat
      self.lon=lon
      self.detections=[]
      Origin.collection.append(self)
      
  '''
      insert by asc mag order  detections
      takes a tuple of (mag, scnl )
      where mag is float and scnl is instance 
      of class Scnl
  '''
  def insertDetection(self,detection):
    index=0
    for d in range(len(self.detections)):
      if detection[0] <  self.detections[index][0]:
        break
      index+=1
    self.detections.insert(index, detection)
        
     
  '''Use index of list to pull out min magnitude detection
    Assumes list is sorted'''
  def min_detection(self,num_stas):
    return self.detections[num_stas-1][0]
  
  '''slice list from 0 to min detection'''
  def slice_detections(self, num_stas):
    return [x[1].sta for x in self.detections][0:num_stas]
  
  '''create a dict with 2dim array of mags using
      collection and lat lon list
      optional with_stas will produce 3dim array of reporting stations for 
      each origin TODO add array of reporting stations to object'''
    
  @classmethod
  def build_map_grid(cls,lats,lons,num_stas,with_stas=False):
    grid={}
    grid['lat_start']=lats[0]
    grid['lon_start']=lons[0]
    grid['lat_step']=lats[1]-lats[0]
    grid['lon_step']=lons[1]-lons[0]
    min_mags=[o.min_detection(num_stas) for o in  cls.collection]
    grid['max']= round(max(min_mags),2)
    grid['min'] = round(min(min_mags),2)
    grid["grid"]=np.reshape(min_mags, (len(lats), len(lons))).tolist()
    if with_stas:
      # stas=[o.slice_detections(num_stas) for o in  cls.collection]
      print(len(lats))
      # print len(lats)
      # print len(lons)
      # grid['stations']=np.reshape(stas, (len(lats), len(lons))).tolist()
    return grid
    

  @classmethod
  def build_geojson_feature_collection(cls,lats,lons, num_stas):
    #convert our data grid to GeoJSON
    featured_collection={"features": []}
    index=0
    min_mags=[o.min_detection(num_stas) for o in  cls.collection]
    
    for lat in lats:
      for lon in lons:
        point = {
        "geometry": {
        "type": "Point",
        "coordinates": [lat,lon]},
        "properties": { "z": round(min_mags[index],2)},
        "type": "Feature"
        }
      index+=1
      featured_collection['features'].append(point);
    return featured_collection