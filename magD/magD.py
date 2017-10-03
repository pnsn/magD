# run with python

#to install basemap on osx
#brew install geos
# pip3 install https://github.com/matplotlib/basemap/archive/v1.1.0.tar.gz
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
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


from origin import Origin
from scnl import Scnl
import iris
import seis

sys.path.append(os.path.abspath('..'))
#lat lon grid resolution in  degrees
step=0.1



#entry point
def main(args=None):
    """The main routine."""
    parser = argparse.ArgumentParser(description="A routine to plot")
    parser.add_argument('-i','--input', help='Input file name',required=True)
    parser.add_argument('-p','--plot',
        help="plot contours in matplotlib", action='store_true')

    # parser.add_argument('-o','--output',help='Output file name',
        #required=True)
    args = parser.parse_args()## show values ##
    #make config key the name of the csv file with out the .csv
    confParse = configparser.ConfigParser()
    confParse.read("config/config.ini")


    # Parameters for calculating the minimum earthquake detected.
    #start and end
    #lats will be parsed from N-S (large to small)


    lon_step= float(step) #degree increments (resolution)
    lat_step= lon_step*-1 #go backwards
    lat_min=38+lat_step
    lat_max=53
    lon_min=-135
    lon_max= -116+lon_step

    # lat_min=float(config['lat_min']) + lat_step
    # lat_max=float(config['lat_max'])
    # lon_min=float(config['lon_min'])
    # lon_max=float(config['lon_max']) + lon_step
    nyquist_correction= 0.4
    #number of stations for detection solution
    #create rows and columns array
    #reverse lat list (North is up)
    lat_list=np.arange(lat_max, lat_min, lat_step)
    lon_list=np.arange(lon_min, lon_max, lon_step)
    #for each point record count
    value_list=[]
    plot=True

    mu = 3e11
    qconst = 300.0
    beta = 3.5  # km/s
    cn = 1/(4 * mu * beta * 1e7)
    max_value=100

    ########
    #create dataframe from csv
    paths=args.input.split(",")
    for path in paths:
        match =re.search(r'\/[^\.]*', path)
        ds= match.group()[1:] #remove slash
        config=confParse[ds]
        df_stas = pd.read_csv(path)
        #instantiate Scnl from each station
        for i, row in df_stas.iterrows():
          Scnl(row.sta, row.chan, row.net, row.loc,row.rate, row.lat,
            row.lon, row.depth, ds)
        for scnl in Scnl.collections[ds]:
            sta=scnl.sta
            chan=scnl.chan
            net=scnl.net
            starttime=config['starttime']
            endtime=config['endtime']
            #Do we want to use a template, i.e. another noise-pdf?
            #we still want to keep the orig lat/lon but use a template pdf
            if "template_sta" in config:
                sta=config['template_sta']
                chan=config['template_chan']
                net=config['template_net']
            resp = iris.get_noise_pdf(sta,chan,net,starttime,endtime)
            # print(type(noise[0]))
            if resp is not None:
                noise= resp['data']
                scnl.set_powers(noise)
            else: #remove from collections
                print("deleting {}".format(scnl.sta))
                Scnl.collections[ds].remove(scnl)
        ##########################
    #if #of stas < num_sta_detection use total num of stas
    # num_stas=min(len(Scnl.collections), int(config['num_sta_detection']))
    num_stas=int(config['num_sta_detection'])
    #for every point in grid

    for lat in lat_list:
        print(lat)
        for lon in lon_list:
            origin = Origin(lat,lon)
            mindetect = []
            # for every scnl
            for key in Scnl.collections:
                for scnl in Scnl.collections[key]:
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
                        #case where delta is 0.0, oh it's happend
                        # if delta_rad==0.0 or delta_km==0.0:
                        #     continue
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
                            # correction for matching brune scaling to PSD
                            #calculation normalization
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

    print("{} to {}".format(starttime,endtime))
    print("min val=%f"%min(value_list))
    max_val= max(value_list)
    print("max val=%f"%max_val)
    print("ave val=%f"%np.average(value_list))
    print("median val=%f"%np.median(value_list))
    # scnl_dict=Scnl.collection_to_dict()
    # write_json_to_file(scnl_dict,
    #     "./public/json/{}-scnls.json".format(config_key))
    mags_dict=Origin.build_map_grid(lat_list, lon_list, num_stas, True)
    # write_json_to_file(mags_dict,
    #     "./public/json/{}-data.json".format(config_key))

    #build station stats by getting list of contrib scnls
    #ordered by number of contribs
    #then add scnls that brought nothing to table
    Origin.increment_solutions(num_stas)
    Scnl.sort_by_solutions()
    #print out the solutions
    for key in Scnl.collections:
        print(key)
        for scnl in Scnl.collections[key]:
            print("-{}, {}".format(scnl.sta, scnl.solutions))




    if args.plot:
      print('plotting.......')
      #center of map
      lon_0=0.5*(lon_max-lon_min) + lon_min
      lat_0=0.5*(lat_max-lat_min) + lat_min
      #create basemap
      m = Basemap(llcrnrlon=lon_min+2,llcrnrlat=lat_min+2,urcrnrlon=lon_max-2,
                    urcrnrlat=lat_max-2, resolution='i',projection='merc',
                    lon_0=lon_0,lat_0=lat_0)
      m.drawcoastlines(zorder=0)
      m.drawstates(zorder=2)
      z=[o.min_detection(num_stas) for o in  Origin.collection]

      npz=np.asarray(z)
      Z=np.reshape(npz, ((len(lat_list), len(lon_list))))
      X,Y=m(*np.meshgrid(lon_list,lat_list))
      #create list of floats from min max mag
      mag_min=int(np.amin(npz)*10)
      mag_max=int(np.amax(npz)*10)
      levels=[x / 10.0 for x in range(mag_min, mag_max, 1)]
      cs =m.contour(X,Y,Z,levels,colors="k",zorder=3)
      plt.clabel(cs, inline=1, fontsize=10,fmt='%1.1f')

      meridian_interval=np.linspace(lon_min,lon_max,4,dtype = int)
      #set linewidth to 0  to get only labels
      m.drawmeridians(meridian_interval,labels=[0,0,0,1],
        dashes=[90,8], linewidth=0.0)
      parallel_interval=np.linspace(lat_min,lat_max,4,dtype = int)
      m.drawparallels(parallel_interval,labels=[1,0,0,0],
        dashes=[90,8], linewidth=0.0)
      m.drawmapboundary()
      #zorder puts it at lowest plot level
      m.fillcontinents(color='0.7',zorder=1)

      plt.title("{} station Detection Thresholds".format(num_stas))
      for key in Scnl.collections:
          config = confParse[key]
          print(key)
          #plot station data
          lats, lons, sols=Scnl.get_xyz_lists(key)
          no_i=Scnl.get_no_solution_index(key)
          print("no_i {}".format(no_i))
          Sx,Sy=m(lons[:no_i], lats[:no_i])
          Sxn,Syn=m(lons[no_i:], lats[no_i:])
          color=config['marker_color']
          stas=plt.scatter(Sx, Sy, s=70, marker='^', c=color, label=key,zorder=11)
          plt.scatter(Sxn, Syn, s=30, marker='o', facecolors='none', edgecolors=color, label="No solution", zorder=11)
      #plot star at origin of interest
      i_lat=44.5
      i_lon=-124.5
      Sxi,Syi=m(i_lon, i_lat)
      plt.scatter(Sxi, Syi, s=200, marker='*', color='r', label="Event")
      plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
      #plt.colorbar(stas, orientation='horizontal', shrink=0.4)
      plt.show()





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
