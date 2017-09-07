# run with python 
import math
import sys
import os
import argparse
from pandas import DataFrame, read_csv
import pandas as pd 
import configparser
import numpy as np
import json
import csv
import re

from origin import Origin
from scnl import Scnl
import iris
import seis

sys.path.append(os.path.abspath('..'))


#entry point
def main(args=None):
    """The main routine."""
    parser = argparse.ArgumentParser(description="A routine to plot")
    parser.add_argument('-i','--input', help='Input file name',required=True)
    parser.add_argument('-s','--starttime', help='startime YYYY-MM-DD (inclusive)',required=True)
    parser.add_argument('-e','--endtime', help='endtime YYYY-MM-DD (exclusive)',required=True)
    # parser.add_argument('-c','--config_key', help='key for config section',required=True)
    
    # parser.add_argument('-o','--output',help='Output file name', required=True)
    args = parser.parse_args()## show values ##  
    #make config key the name of the csv file with out the .csv
    
    confParse = configparser.ConfigParser()
    confParse.read("config/config.ini")
    match =re.search(r'\/[^\.]*', args.input)
    config_key= match.group()[1:] #remove slash
    config = confParse[config_key]
    # Parameters for calculating the minimum earthquake detected.
    #lats will be parsed from N-S (large to small)
    lon_step= float(config['step']) #degree increments (resolution)
    lat_step= lon_step*-1 #go backwards
    lat_min=float(config['lat_min']) + lat_step
    lat_max=float(config['lat_max']) 
    lon_min=float(config['lon_min'])
    lon_max=float(config['lon_max']) + lon_step
    nyquist_correction= 0.4
    #number of stations for detection solution
    #create rows and columns array
    #reverse lat list (North is up)
    lat_list=np.arange(lat_max, lat_min, lat_step) 
    lon_list=np.arange(lon_min, lon_max, lon_step)
    #for each point record count
    value_list=[]
    
    
    mu = 3e11
    qconst = 300.0 
    beta = 3.5  # km/s
    cn = 1/(4 * mu * beta * 1e7)
    max_value=100
    #create dataframe from csv
    df_stas = pd.read_csv(args.input)
    # print(df_stas)
    # stations=iris.get_fdsn(STA_STRING, CHAN_STRING, NET_STRING)
    #instantiate Scnl from each station
    data=[]
    for i, row in df_stas.iterrows():
      Scnl(row.sta, row.chan, "7D","",row.rate, row.lat, row.lon, row.depth, row.inst_id, row.desc)
    for scnl in Scnl.collection:
      #
      noise = iris.get_noise_pdf(scnl, args.starttime, args.endtime)
      # print(type(noise[0]))
      if noise is not None:
        scnl.set_powers(noise)    
    #if #of stas < num_sta_detection use total num of stas
    num_stas=min(len(Scnl.collection), int(config['num_sta_detection']))
    #for every point in grid
    for lat in lat_list:
        print(lat)
        for lon in lon_list:
            origin = Origin(lat,lon)
            mindetect = []
            # for every scnl 
            for scnl in Scnl.collection:
                if len(scnl.powers)>0:
                    start_period = 0.001
                    end_period = 280

                    # Goes through all the freqs, i.e. from small to large Mw
                    #this way the first detection will be the min Mw
                    period = start_period
                    # origin = (source.lat, source.lon)
                    # destination = (scnl.lat, scnl.lon)
                    # Calculate distance between earthquake and station
                    delta_rad, delta_km = seis.distance(origin, scnl)  # km
                    #for each period
                    while period <= end_period:
                        fc = 1/period
                        fault_radius = seis.fault_radius(fc, beta)
                        Mo = seis.moment(fault_radius)
                        Mw = seis.moment_magnitude(Mo)
                        filtfc=seis.signal_adjusted_frequency(Mw,fc)
                        nyquist=scnl.samprate*nyquist_correction
                
                        if filtfc >= nyquist:
                          filtfc=nyquist
                
                        As = seis.amplitude(fc, Mo, cn, delta_km, filtfc)
                        As*=seis.geometric_spreading(delta_km)
                        q = qconst*math.pow(nyquist, 0.35)  # Q value
                        As*=seis.attenuation(delta_km, q, beta, filtfc)

                        # Pwave amp is 10 times smaller than S
                        # correction for matching brune scaling to PSD calculation normalization
                        As/=6.0
                        db = seis.amplitude_power_conversion(As)

                        detection = seis.min_detect(scnl,db, Mw, filtfc)
                        if(detection):
                            origin.insertDetection((Mw,scnl))
                            break

                        period = period * (2 ** 0.125)
            # origin.sort_detections_by_mw()
            value= origin.min_detection(num_stas)
            value_list.append(value)
            lon+=lon_step
        
        lat+=lat_step


    print("min val=%f"%min(value_list))
    max_val= max(value_list)
    print("max val=%f"%max_val)
    print("ave val=%f"%np.average(value_list))
    print("median val=%f"%np.median(value_list))
    scnl_dict=Scnl.collection_to_dict()
    write_json_to_file(scnl_dict, "./public/json/{}-scnls.json".format(config_key))
    mags_dict=Origin.build_map_grid(lat_list, lon_list, num_stas, True)
    write_json_to_file(mags_dict, "./public/json/{}-data.json".format(config_key))
    
    Origin.build_geojson_feature_collection(lat_list, lon_list, num_stas)
    # # layer.write_geojson_to_file("./public/json/geomagD.json")
    # layer.write_json_to_file("./public/json/magDgrid.json")
    # # stats.write_json_to_file("./public/json/stations_stats.json")
    # layer.write_to_csv("./test/data/detections.csv")


#write dict to json file
def write_json_to_file(d, path):
    with open(path, 'w') as outfile:
        json.dump(d, outfile, indent=4)
        

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

if __name__ == "__main__":
    main()
    
