import math
import pandas as pd
import configparser
import numpy as np
import json
import csv
import pickle
import pathlib
import re

from .origin import Origin
from .scnl import Scnl
from .seis import *
from .iris import get_noise_pdf


class MagD:
    conf=None
    def __init__(self, config_path):
        if MagD.conf==None:
            MagD.conf= configparser.ConfigParser()
            MagD.conf.read(config_path)

        c=MagD.conf['main']
        self.name=c['name']
        self.title=c['title']
        self.grid_resolution=float(c['grid_resolution'])
        self.lat_min=float(c['lat_min']) + self.grid_resolution
        self.lat_max=float(c['lat_max'])
        self.lon_min=float(c['lon_min'])
        self.lon_max=float(c['lon_max']) + self.grid_resolution
        self.num_detections=int(c['num_detections'])
        self.nyquist_correction= float(c['nyquist_corretion']) #0.4
        self.mu =float(c['mu']) #3e11
        self.qconst = float(c['qconst']) #300.0
        self.beta = float(c['beta']) #3.5  # km/s
        self.pickle_dir=c['pickle_dir']
        self.summary_mag_list=[]
        self.plot_mag_min=float(c['plot_mag_min'])
        self.plot_mag_max=float(c['plot_mag_max'])
        if not c['output']=='verbose':
            self.output=None
        else:
            self.output='verbose'

        if len(c['diff_with'])==0:
            self.diff_with=None
        else:
            self.diff_with=c['diff_with']




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

    '''return 1dim list of mag levels used for contouring'''
    def get_mag_grid(self):
        return [o.min_detection(self.num_detections) for o in  self.origin_collection()]

    '''save mag_grid to compare/diff with another. Uses name of config file'''
    def pickle_mag_grid(self):
        dir="mag_grid"
        pickle_path=self.get_pickle_grid_path(dir,self.name,self.grid_resolution)
        self.set_pickle(pickle_path, self.get_mag_grid())

    '''retrieve mag_grid for diff with current run. Must use same size lists'''
    def unpickle_mag_grid(self,dir,name,resolution):
        pickle_path=get_pickle_grid_path(dir,name,resolution)
        return get_pickle(pickle_path)


    def print_noise_not_found(self,sta,chan,loc,net,startime,endtime,code):
      print("{}:{}:{}:{} startime: {}, endtime {} returned HTTP code {}".format(
              sta,chan,loc,net,startime,endtime,code))

    def set_pickle(self,path, data):
      #create pickle_dirs if they don't exist
      directory=re.search(r'\.\/.*\/',path).group()
      pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
      with open(path, 'wb') as f:
          pickle.dump(data, f)

    def get_pickle(self,path):
      try:
          with open(path, 'rb') as p:
              return pickle.load(p)
      except FileNotFoundError:
          raise


    def get_pickle_noise_path(self,dir,sta,chan,net,loc,start,end):
      return "./{}/{}/{}_{}_{}_{}_{}_{}.pickle".format(self.pickle_dir,
                  dir,sta,chan,net,loc,start,end)

    '''
      create a path name to pickle mag grid must be of same length
      for comparison so resolution added
    '''
    def get_pickle_grid_path(self,dir,name,resolution):
      return "./{}/{}/{}-res-{}.pickle".format(self.pickle_dir,
                  dir,name,resolution)

    #Create Scnl collections, and assign power

    def get_noise(self):
        data_keys=MagD.conf.sections()
        data_keys.remove('main')

        for key in data_keys:
            conf=MagD.conf[key]
            path=conf['csv_path']
            df_stas = pd.read_csv(path)
            #instantiate Scnl from each station
            for i, row in df_stas.iterrows():
                #loc is reserved, used location for column name
                #blank locs are eval as NaN
                if not isinstance(row.location, str) and math.isnan(float(row.location)):
                    row.location="--"
                Scnl(row.sta, row.chan, row.net,row.location,row.rate, row.lat,
                    row.lon, row.depth, key)
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
                    pickle_path= self.get_pickle_noise_path("noise",sta,chan,net,loc,
                                starttime,endtime)
                    data=self.get_pickle(pickle_path)
                    scnl.set_powers(data)
                except FileNotFoundError:
                    resp = get_noise_pdf(sta,chan,net,loc,starttime,endtime)
                    if resp['code'] ==200:
                        self.set_pickle(pickle_path, resp['data'])
                        scnl.set_powers(resp['data'])
                    else: #remove from collections
                        if self.output:
                            self.print_noise_not_found(sta,chan,loc,net,starttime,endtime,resp['code'])
                        scnl.powers=None
            #remove scnls with no power
            pre_len=len(self.scnl_collections()[key])
            self.scnl_collections()[key] =[s for s in self.scnl_collections()[key] if s.powers !=None]
            post_len=len(self.scnl_collections()[key])
            if pre_len !=post_len and self.output:
                print("{} channel(s) found without noise pdf".format(pre_len-post_len))



    def find_detections(self):
        for lat in self.lat_list():
            if self.output:
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
    def print_summary(self):
        summary=[]
        calcs=len(self.origin_collection())
        summary.append("Min: %.2f"%min(self.summary_mag_list))
        summary.append("Max: %.2f"%max(self.summary_mag_list))
        summary.append("Ave: %.2f"%np.average(self.summary_mag_list))
        summary.append("Med: %.2f"%np.median(self.summary_mag_list))
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
