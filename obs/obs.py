''' 
  routine for noise analysis of Ocean Bottom Seismometers (obs)
  that will do profound things 

'''
# import math
import sys
import os
import argparse
from pandas import DataFrame, read_csv
import pandas as pd 

sys.path.append(os.path.abspath('.'))
import plotly.plotly as py
import plotly.graph_objs as go

# from magD.origin import Origin
#
# import numpy as np
from magD.scnl import Scnl
import magD.iris as iris
# import seis
# from pprint import pprint
# import json
# import csv
#


#entry point
def main(args=None):
    """The main routine."""
    parser = argparse.ArgumentParser(description="A script to plot noise profiles for obs's")
    parser.add_argument('-i','--input', help='Input file name',required=True)
    parser.add_argument('-s','--starttime', help='startime YYYY-MM-DD (inclusive)',required=True)
    parser.add_argument('-e','--endtime', help='endtime YYYY-MM-DD (exclusive)',required=True)
    
    # parser.add_argument('-o','--output',help='Output file name', required=True)
    args = parser.parse_args()## show values ##
    print("Input file: {}".format(args.input))
    #print("Output file: {}".format(args.output))
    #args can be sta, chan, net or inputfile
    # STA_STRING="*"
    # CHAN_STRING="HHZ,HNZ"
    # NET_STRING="NV,OO"
    # NET_STRING="OO,NV,5E,7D"
    #expected tremor signal
    df_stas = pd.read_csv(args.input)
    print(df_stas)
    
    SPECTRAL_FREQ=[10.0, 5.0, 3.3, 2.5, 2.0, 1.67, 1.43, 1.25, 1.11, 1]
    SPECTRAL_POWER=[-149, -145, -143, -145, -150, -153, -155, -159, -160, -158]
    
    #read in csv file pandas
    # stations=[]
  #   for i, row in df_stas.iterrows():
  #     #loop through pandas thingy
  #     sta=iris.get_fdsn(row.sta, row.chan, row.net)
  #     stations+=sta
  #   print(stations)
    #calling instrument type network
    data=[]
    for i, row in df_stas.iterrows():
        Scnl(row.sta, row.chan, "7D","",row.rate, row.lat, row.lon, row.depth, row.inst_id, row.desc)
    print(Scnl.collection)
    for scnl in Scnl.collection:
      print("STA {}, CHAN {}".format(scnl.sta, scnl.chan))
      noise = iris.get_noise_pdf(scnl, args.starttime, args.endtime)
      if noise is not None:
        scnl.set_powers(noise)
        #find min and max index and slice
        min_i=scnl.find_min_index(SPECTRAL_FREQ[-1])
        max_i=scnl.find_max_index(SPECTRAL_FREQ[0])
        # print scnl.frequencies[min_i:max_i]
        trace = go.Scatter(
          x = scnl.frequencies[min_i:max_i],
          y = scnl.powers[min_i:max_i],
          mode = 'lines',
          name = "{} ({})".format(scnl.sta,scnl.inst_id)
        )
        data.append(trace)

    #predicted curve
    tremor_trace = go.Scatter(
      x = SPECTRAL_FREQ,
      y = SPECTRAL_POWER,
      mode = 'lines+markers',
      name = 'Tremor Profile',
      line = dict(
        color = ('rgb(205, 12, 24)'),
        width = 4,
        dash = 'dash'
        ) # dash options include 'dash', 'dot', and 'dashdot'
      )

    data.append(tremor_trace)
    py.plot(data, filename='obs-noise-profile 2014')
#
# #write dict to json file
# def write_json_to_file(d, path):
#     with open(path, 'w') as outfile:
#         json.dump(d, outfile, indent=4)
#
#
# #write out to csv
# def write_to_csv(self, path, lats, lons, vals):
#     i=0
#     with open(path, 'w') as csvfile:
#         fieldnames = ['lat', 'lon', 'val']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for lat in lats:
#             for lon in lons:
#                 writer.writerow({'lat': lat, 'lon': lon, 'val': vals[i]})
#                 i+=1
#     print("done with csv and index = {} and length ={}".format(i, len(vals)))
#
if __name__ == "__main__":
    main()
    
