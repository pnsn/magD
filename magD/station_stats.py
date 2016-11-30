import math
import numpy as np
from pprint import pprint
import json

class StationStats:
    def __init__(self):
        self.stations={}
        

    
    def increment_station(self, sta):
        if sta not in self.stations:
            self.stations[sta]=0
        self.stations[sta]+=1
        
        
    def write_json_to_file(self, path):
        with open(path, 'w') as outfile:
            json.dump(self.stations, outfile, indent=4)
    