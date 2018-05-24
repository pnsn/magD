import math
import pandas as pd
import configparser
import numpy as np
import json
import csv
import pickle
import re
from pathlib import Path


from .origin import Origin
from .scnl import Scnl
from .seis import *
from .iris import get_noise_pdf


class MagD:
    '''
        initialize with config file and profile type
        for every sample point type is
        detection (lowest detection)
        gap (largest az gap out of reporting stations)
        distance (closest station of n reporting stations)
    '''
    def __init__(self, config_path, type=None):
        self.conf= configparser.ConfigParser()
        self.conf.read(config_path)
        c=self.conf['main']
        self.name=c.get('name')
        self.grid_resolution=c.getfloat('grid_resolution')
        self.lat_min=c.getfloat('lat_min') + self.grid_resolution
        self.lat_max=c.getfloat('lat_max')
        self.lon_min=c.getfloat('lon_min')
        self.lon_max=c.getfloat('lon_max') + self.grid_resolution
        self.num_detections=c.getint('num_detections')
        self.nyquist_correction= c.getfloat('nyquist_corretion') #0.4
        self.mu =c.getfloat('mu') #3e11
        self.qconst = c.getfloat('qconst') #300.0
        self.beta = c.getfloat('beta') #3.5  # km/s
        self.pickle_dir=c.get('pickle_dir')
        #types: detection, az_gap
        #stats on run
        self.summary_mag_list=[]
        self.verbose_output= c.getboolean('verbose_output')
        #diff with existing vector?
        self.diff_with=c.get('diff_with',None)
        self.type=type
        self.vector1=None
        self.vector2=None




    ''' list of lats from min, max in steps of grid_resolution'''
    def lat_list(self):
        return np.arange(self.lat_min, self.lat_max, self.grid_resolution)

    ''' list of lons from min, max in steps of grid_resolution'''
    def lon_list(self):
        return np.arange(self.lon_min, self.lon_max, self.grid_resolution)

    '''Can't rembember what the f' cn is but it seems important and scientific'''
    def cn(self):
        return 1/(4 * self.mu * self.beta * 1e7)

    '''expose list of scnls'''
    def scnl_collections(self):
        return Scnl.collections

    '''expose list of origins'''
    def origin_collection(self):
        return Origin.collection

    '''return 1dim list of mag levels used for heat map'''
    def build_detection_vector(self):
        return [o.min_detection(self.num_detections)
                for o in  self.origin_collection()]

    '''
        return 1dim list of tuples for heat map_center
        tuple (dist,max_gap)
        considers only stations that are part of the num_detections
        solution:
        dist is closest station in m
        max_gap is azimuthal gap
    '''
    def build_distance_and_gap_vector(self):
        distances=[]
        gaps=[]
        scnls=[]
        for o in self.origin_collection():
            #take 2nd element of detection tuple
            scnls=[d[1] for d in o.detections[0:self.num_detections]]
            distance,gap=dist_and_azimuthal_gap(scnls,o)
            distances.append(distance)
            gaps.append(gap)
        return distances,gaps



    # #combine both gap and distance
    # def make_gap_distance_vector(self, vector):
    #     #from Paul Bodin
    #     #0.5*[(gap - gap/n)/360] + log(d)/3]
    #     scored_vector=[]
    #     for tup in vector:
    #         gap=tup[0]
    #         distance=tup[1]
    #         gap=(gap-gap/self.num_detections)/360
    #         print(distance)
    #         score=0.5*(gap + math.log(distance)/3)
    #         print(math.log(distance))
    #         scored_vector.append(score)
    #     return scored_vector


    '''save detection_vector to compare/diff with another. Uses name from config file'''
    def pickle_vector(self,dir,vector):
        pickle_path=self.get_pickled_vector_path(dir,self.name,self.grid_resolution)
        self.set_pickle(pickle_path, vector)



    def set_pickle(self,path, data):
      #create pickle_dirs if they don't exist
      directory=re.search(r'\/.*\/',path).group()
      Path(directory).mkdir(parents=True, exist_ok=True)
      with open(path, 'wb') as f:
          pickle.dump(data, f)

    def get_pickle(self,path):
      try:
          with open(path, 'rb') as p:
              return pickle.load(p)
      except FileNotFoundError:
          raise


    def get_pickled_noise_path(self,dir,sta,chan,net,loc,start,end):
      return "{}/{}/{}_{}_{}_{}_{}_{}.pickle".format(self.pickle_dir,
                  dir,sta,chan,net,loc,start,end)

    '''
      create a path name to pickle mag grid must be of same length
      for comparison so resolution added
    '''
    def get_pickled_vector_path(self,dir,name,resolution):
      return "{}/{}/{}-res-{}.pickle".format(self.pickle_dir,
                  dir,name,resolution)

    def print_noise_not_found(self,sta,chan,loc,net,startime,endtime,code):
        print("{}:{}:{}:{} startime: {}, endtime {} returned HTTP code {}".format(
            sta,chan,loc,net,startime,endtime,code))


    #create and pickle all vectors
    def create_vectors(self):
        self.read_stations()
        self.get_noise()
        self.profile_noise()
        #since we ran through whole thing just save both matrices
        detection_vector=self.build_detection_vector()
        self.pickle_vector('detection_vector', detection_vector)
        distance_vector, gap_vector=self.build_distance_and_gap_vector()
        self.pickle_vector('distance_vector',distance_vector)
        self.pickle_vector('gap_vector',gap_vector)
        return self.print_summary(detection_vector, distance_vector,gap_vector)


    #read vectors from pickle file
    def read_vectors(self):
        self.read_stations()
        other_vector_path=None
        dir=self.type +'_vector'
        try:
            this_vector_path=self.get_pickled_vector_path(dir,
                        self.name, self.grid_resolution)
            this_vector_file= Path(this_vector_path)
            if self.diff_with:
                other_vector_path=self.get_pickled_vector_path(dir,
                            self.diff_with, self.grid_resolution)
                other_vector_file= Path(other_vector_path)

        except FileNotFoundError:
            print("Pickle file not found!")
            print("Expected: {}".format(other_vector_path))
            exit(1)
        self.vector1= self.get_pickle(this_vector_path)
        if self.diff_with:
            self.vector2= self.get_pickle(other_vector_path)



    #find all noise keys in config file
    def noise_keys(self):
        return [n for n in self.conf.sections()  if re.match(r'noise',n)]
    #Create Scnl collections, and assign power


    #read all station in from csv and add them to collection (init)
    def read_stations(self):
        for key in self.noise_keys():
            conf=self.conf[key]
            path=conf['csv_path']
            df_stas = pd.read_csv(path,converters={'location': lambda x: str(x)})
            #instantiate Scnl from each station
            for i, row in df_stas.iterrows():
                #loc is reserved, used location for column name
                #blank locs are eval as NaN
                # print(row.sta)
                # print(type(row.location))
                if len(row.location) ==0:
                    #if not isinstance(row.location, str) and math.isnan(float(row.location)):
                    row.location="--"
                Scnl(row.sta, row.chan, row.net,row.location,row.rate, row.lat,
                    row.lon, row.depth, key)

    def get_noise(self):
        # print noise_keys
        for key in self.noise_keys():
            conf=self.conf[key]
            for scnl in self.scnl_collections()[key]:
                starttime=conf['starttime']
                endtime=conf['endtime']
                if "template_sta" in conf:
                    sta=conf['template_sta']
                    chan=conf['template_chan']
                    net=conf['template_net']
                    loc=conf['template_loc']
                else:
                    sta =scnl.sta
                    chan=scnl.chan
                    net=scnl.net
                    loc=scnl.loc
                #try to load noise from pickle file,
                #if not there go to iris
                try:
                    pickle_path= self.get_pickled_noise_path("noise",sta,chan,net,loc,
                                starttime,endtime)
                    data=self.get_pickle(pickle_path)
                    scnl.set_powers(data)
                except FileNotFoundError:
                    resp = get_noise_pdf(sta,chan,net,loc,starttime,endtime)
                    if resp['code'] ==200:
                        self.set_pickle(pickle_path, resp['data'])
                        scnl.set_powers(resp['data'])
                    else: #remove from collections
                        if self.verbose_output:
                            self.print_noise_not_found(sta,chan,loc,net,starttime,endtime,resp['code'])
                        scnl.powers=None
            #remove scnls with no power
            pre_len=len(self.scnl_collections()[key])
            self.scnl_collections()[key] =[s for s in self.scnl_collections()[key] if s.powers !=None]
            post_len=len(self.scnl_collections()[key])
            if pre_len !=post_len and self.verbose_output:
                print("{} channel(s) found without noise pdf".format(pre_len-post_len))



    def profile_noise(self):
        for lat in self.lat_list():
            if self.verbose_output:
                print(lat)
            for lon in self.lon_list():
                origin = Origin(lat,lon)
                mindetect = []
                # for every scnl
                for key in self.scnl_collections():
                    for scnl in self.scnl_collections()[key]:
                        if scnl.powers==None:
                            continue
                        if len(scnl.powers)>0:
                            start_period = 0.001
                            end_period = 280

                            #Goes through all the freqs, i.e. from small to large Mw
                            #this way the first detection will be the min Mw
                            period = start_period
                            # origin = (source.lat, source.lon)
                            # destination = (scnl.lat, scnl.lon)
                            # Calculate distance between earthquake and station
                            delta_rad, delta_km = distance(origin, scnl)  # km
                            #case where delta is 0.0, oh it's happend
                            # if delta_rad==0.0 or delta_km==0.0:
                            #     continue
                            #for each period
                            while period <= end_period:
                                fc = 1/period
                                fault_rad = fault_radius(fc, self.beta)
                                Mo = moment(fault_rad)
                                Mw = round(moment_magnitude(Mo),2)
                                filtfc=signal_adjusted_frequency(Mw,fc)
                                nyquist=scnl.samprate*self.nyquist_correction

                                if filtfc >= nyquist:
                                  filtfc=nyquist

                                As = amplitude(fc, Mo, self.cn(), delta_km, filtfc)
                                As*=geometric_spreading(delta_km)
                                q = self.qconst*math.pow(nyquist, 0.35)  # Q value
                                As*=attenuation(delta_km, q, self.beta, filtfc)

                                # Pwave amp is 10 times smaller than S
                                # correction for matching brune scaling to PSD
                                #calculation normalization
                                As/=6.0
                                db = amplitude_power_conversion(As)

                                detection = min_detect(scnl,db, Mw, filtfc)
                                if(detection):
                                    origin.insertDetection((Mw,scnl))
                                    break

                                period = period * (2 ** 0.125)
                # origin.sort_detections_by_mw()
                value= origin.min_detection(self.num_detections)
                self.summary_mag_list.append(value)
                lon+=self.grid_resolution

            lat+=self.grid_resolution
        #Tally up each scnls detection success
        Origin.increment_solutions(self.num_detections)
        #sort all scnls by solutions in reverse (desc order)
        Scnl.sort_by_solutions()


    '''
        Summary output
    '''
    def print_summary(self,detection_vector,distance_vector,
                        gap_vector,station_summary=False):
        summary=[]
        if gap_vector:
            summary.append("Gap Min: %.2f"%min(gap_vector))
            summary.append("Gap Max: %.2f"%max(gap_vector))
            summary.append("Gap Ave: %.2f"%np.average(gap_vector))
        if distance_vector:
            summary.append("Dist Min: %.2f"%min(distance_vector))
            summary.append("Dist Max: %.2f"%max(distance_vector))
            summary.append("Dist Ave: %.2f"%np.average(distance_vector))
        if detection_vector:
            calcs=len(self.origin_collection())
            summary.append("Mag Min: %.2f"%min(self.summary_mag_list))
            summary.append("Mag Max: %.2f"%max(self.summary_mag_list))
            summary.append("Mag Ave: %.2f"%np.average(self.summary_mag_list))
        if station_summary:
            summary.append("\nSolution Summary for %i calculations:"%calcs)
            summary.append("Sta   Chan Hits    Productivity")
            for key in self.scnl_collections():
                #print("Data set {}".format(key))
                for scnl in self.scnl_collections()[key]:
                    #do some formating
                    if scnl.solutions==0:
                        percent="N/A"
                    else:
                        c=(scnl.solutions/calcs)*100
                        percent="%.2f%%"%c
                    sta=scnl.sta
                    while len(sta) < 4:
                        sta=sta + " "
                    sols=str(scnl.solutions)
                    while len(sols) < 6:
                        sols=" " + sols
                    summary.append("{}  {}  {}  {}".format(sta, scnl.chan, sols, percent))
        return "\n".join(summary)

    '''for set return lat,lon, and solutions
        as three unique lists'''
    def get_xyz_lists(self,key):
      lats=[]
      lons=[]
      sols=[]
      for scnl in self.scnl_collections()[key]:
          lats.append(scnl.lat)
          lons.append(scnl.lon)
          sols.append(scnl.solutions)
      return lats, lons, sols


    '''Assumes sorted! Find the index  where Scnls did not contribute.
    Find where # of solutions ==0, everything to the right of that
    will be 0 if sorted
    '''
    def get_no_solution_index(self,key):
      i=0
      for scnl in self.scnl_collections()[key]:
          if scnl.solutions > 0:
              i+=1
              next
          else:
              break
      return i



    #write dict to json file
    def write_json_to_file(self,dict, path):
        with open(path, 'w') as outfile:
            json.dump(dict, outfile, indent=4)


    #write out to csv
    def write_to_csv(self, path, lats, lons, vals):
        i=0
        with open(path, 'w') as csvfile:
            fieldnames = ['lat', 'lon', 'val']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for lat in lats:
                for lon in lons:
                    writer.writerow({'lat': lat, 'lon': lon, 'val': vals[i]})
                    i+=1
        print("done with csv and index = %i and length =%i"%(i, len(vals)))
