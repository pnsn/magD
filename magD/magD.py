import math
import pandas as pd
import numpy as np
import json
import csv



from .origin import Origin
from .scnl import Scnl
from .seis import *
from .iris import get_noise_pdf
from .pickle import *


class MagD:
    '''
        init with an array of mapGrid objects
        builds and saves mapGrid for later use
        grids = list of MapGrid objects
        data_srs = dict of form

        {
            'data1':{
                'csv_path': some/path (string),
                'starttime': YYYY-mm-dd (string),
                'endtime': YYYY-mm-dd (string),
            },
            'data2':{
                'csv_path': some/path (string),
                'starttime': YYYY-mm-dd (string),
                'endtime': YYYY-mm-dd (string),
                #optional keys for templating
                'template_sta': template_station (string),
                'template_chan': template_channel (string),
                'template_net': template_network (string),
                'template_loc': template_loc (string)

            }
        }
    '''
    def __init__(self, grids, data_srcs):
        self.grids=grids
        self.data_srcs = data_srcs
        self.summary_mag_list=[]

    '''expose list of scnls'''
    def scnl_collections(self):
        return Scnl.collections

    '''expose list of origins'''
    def origin_collection(self):
        return Origin.collection

    '''return 1dim list of mag levels used for heat map'''
    def build_detection_vector(self):
        d = [o.min_detection(self.grids[0].num_detections)
                for o in  self.origin_collection()]
        return np.array(d)

    '''
        considers only stations that are part of the num_detections
        solution
        returns max_gap np array and distance matrix (2dim np array)
        with the distances of all stations to the origin to allow for
        min/med/ave/max distance matrices
    '''
    def build_distance_and_gap_vectors(self):
        grid=self.grids[0]
        distances = []
        gaps = []
        scnls = []
        for o in self.origin_collection():
            #take 2nd element of detection tuple
            scnls=[d[1] for d in o.detections[0:grid.num_detections]]
            dists,gap=dist_and_azimuthal_gap(scnls,o)
            distances.append(dists)
            gaps.append(gap)
        return np.array(distances), np.array(gaps)


    #message for noise pdf not found
    def print_noise_not_found(self,sta,chan,loc,net,startime,endtime,code):
        print("{}:{}:{}:{} startime: {}, endtime {} returned HTTP code {}".format(
            sta,chan,loc,net,startime,endtime,code))


    #create and pickle all map_grids
    def build_grids(self):
        self.read_stations()
        self.get_noise()
        self.profile_noise()
        distance_matrix, gap_vector=self.build_distance_and_gap_vectors()
        detection_vector=self.build_detection_vector()
        for grid in self.grids:
            if grid.type=='gap':
                grid.make_matrix(gap_vector)
            elif grid.type=='dist_min':
                grid.make_matrix([np.min(row) for row in distance_matrix])
            elif grid.type=='dist_med':
                grid.make_matrix([np.median(row) for row in distance_matrix])
            elif grid.type=='dist_ave':
                grid.make_matrix([np.average(row) for row in distance_matrix])
            elif grid.type=='dist_max':
                grid.make_matrix([np.average(row) for row in distance_matrix])
            elif grid.type=='detection':
                grid.make_matrix(detection_vector)
            grid.scnls=self.scnl_collections()
            grid.save()
        # return self.print_summary()






    #read all station in from csv and add them to collection (init)
    def read_stations(self):
        for key in self.data_srcs:
            path=self.data_srcs[key]['csv_path']
            df_stas = pd.read_csv(path,converters={'location': lambda x: str(x)})
            #instantiate Scnl from each station
            for i, row in df_stas.iterrows():
                if len(row.location) ==0:
                    #if not isinstance(row.location, str) and math.isnan(float(row.location)):
                    row.location="--"
                Scnl(row.sta, row.chan, row.net,row.location,row.rate, row.lat,
                    row.lon, row.depth, key)

    def get_noise(self):
        # print noise_keys
        for key in self.data_srcs:
            src = self.data_srcs[key]
            for scnl in self.scnl_collections()[key]:
                starttime=src['starttime']
                endtime=src['endtime']
                if "template_sta" in src:
                    sta=src['template_sta']
                    chan=src['template_chan']
                    net=src['template_net']
                    loc=src['template_loc']
                else:
                    sta =scnl.sta
                    chan=scnl.chan
                    net=scnl.net
                    loc=scnl.loc
                #try to load noise from pickle file,
                #if not there go to iris
                try:
                    root_path = self.grids[0].pickle_path
                    pickle_path= get_noise_path(root_path,"noise",sta,chan,net,loc,
                                starttime,endtime)
                    data=get_pickle(pickle_path)
                    scnl.set_powers(data)
                except FileNotFoundError:
                    resp = get_noise_pdf(sta,chan,net,loc,starttime,endtime)
                    if resp['code'] ==200:
                        set_pickle(pickle_path, resp['data'])
                        scnl.set_powers(resp['data'])
                    else: #remove from collections
                        self.print_noise_not_found(sta,chan,loc,net,starttime,endtime,resp['code'])
                        scnl.powers=None
            #remove scnls with no power
            pre_len=len(self.scnl_collections()[key])
            self.scnl_collections()[key] =[s for s in self.scnl_collections()[key] if s.powers !=None]
            post_len=len(self.scnl_collections()[key])
            if pre_len !=post_len:
                print("{} channel(s) found without noise pdf".format(pre_len-post_len))



    def profile_noise(self):
        grid=self.grids[0]
        for lat in grid.lat_list():
            if lat %1 ==0.0:
                print("{}, ".format(lat), end="")
            for lon in grid.lon_list():
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
                                fault_rad = fault_radius(fc, grid.beta)
                                Mo = moment(fault_rad)
                                Mw = round(moment_magnitude(Mo),2)
                                filtfc=signal_adjusted_frequency(Mw,fc)
                                nyquist=scnl.samprate*grid.nyquist_correction

                                if filtfc >= nyquist:
                                  filtfc=nyquist

                                As = amplitude(fc, Mo, grid.cn(), delta_km, filtfc)
                                As*=geometric_spreading(delta_km)
                                q = grid.qconst*math.pow(nyquist, 0.35)  # Q value
                                As*=attenuation(delta_km, q, grid.beta, filtfc)

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
                value= origin.min_detection(grid.num_detections)
                self.summary_mag_list.append(value)
                lon+=grid.resolution

            lat+=grid.resolution
        #Tally up each scnls detection success
        Origin.increment_solutions(grid.num_detections)
        #sort all scnls by solutions in reverse (desc order)
        Scnl.sort_by_solutions()


    '''
        Summary output FIXME with new grid objects
    '''
    def print_summary(self,station_summary=False):
        summary=[]
        for grid in self.grids:
            summary.append("%s min: %.2f"%(grid.type, min(grid.matrix)))
            summary.append("%s max: %.2f"%(grid.type, max(grid.matrix)))
            summary.append("%s mve: %.2f"%(grid.type, np.average(gid.matrix)))
            # if distance_vector:
            #     summary.append("Dist Min: %.2f"%min(distance_vector))
            #     summary.append("Dist Max: %.2f"%max(distance_vector))
            #     summary.append("Dist Ave: %.2f"%np.average(distance_vector))
            # if detection_vector:
            #     calcs=len(self.origin_collection())
            #     summary.append("Mag Min: %.2f"%min(self.summary_mag_list))
            #     summary.append("Mag Max: %.2f"%max(self.summary_mag_list))
            #     summary.append("Mag Ave: %.2f"%np.average(self.summary_mag_list))
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

    # '''for set return lat,lon, and solutions
    #     as three unique lists'''
    # def get_xyz_lists(self,key):
    #   lats=[]
    #   lons=[]
    #   sols=[]
    #   for scnl in self.scnl_collections()[key]:
    #       lats.append(scnl.lat)
    #       lons.append(scnl.lon)
    #       sols.append(scnl.solutions)
    #   return lats, lons, sols


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
