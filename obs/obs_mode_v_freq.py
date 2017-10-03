''' 
  routine for noise analysis of Ocean Bottom Seismometers
  plots min mode vs freq

'''
# import math
import sys
import os
import argparse
from pandas import DataFrame, read_csv
import pandas as pd 
import re
import configparser
import math
sys.path.append(os.path.abspath('.'))
from plotly import tools
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
    confParse = configparser.ConfigParser()
    confParse.read("config/config.ini")
    parser = argparse.ArgumentParser(description="A script to plot min mode vs depth for obs's")
    parser.add_argument('-i','--input', help='Input file name',required=True)
    
    args = parser.parse_args()## show values ##
    print("Input file: {}".format(args.input))
    match =re.search(r'\/[^\.]*', args.input)
    experiment= match.group()[1:] #remove slash
   
    df_stas = pd.read_csv(args.input)
    config = confParse[experiment]
    
    dates =  config["dates"].split()
    #expected tremor signal
    SPECTRAL_FREQ=[10.0, 5.0, 3.3, 2.5, 2.0, 1.67, 1.43, 1.25, 1.11, 1]
    SPECTRAL_POWER=[-149, -145, -143, -145, -150, -153, -155, -159, -160, -158]

    columns=3
    fig = tools.make_subplots(rows= int(math.ceil(len(dates)/columns)), cols=columns, subplot_titles=(dates[:-1]))
    for i in range(len(dates)-1):
      row = int(i/columns) + 1
      col= int(i%columns + 1)
      # print(data)
      # print(row)
      # print(col)
      data=[]
      Scnl.collection=[]
      for j, r in df_stas.iterrows():
          Scnl(r.sta, r.chan, "7D","",r.rate, r.lat, r.lon, r.depth, r.inst_id, r.desc)
      
      # print("data = {}".format(data))
      for scnl in Scnl.collection:
        print("STA {}, CHAN {}".format(scnl.sta, scnl.chan))
        resp = iris.get_noise_pdf(scnl, dates[i], dates[i+1])
        if resp is not None:
          noise= resp['data']
          scnl.set_powers(noise)
          #find min and max index and slice
          min_i=scnl.find_min_index(SPECTRAL_FREQ[-1])
          max_i=scnl.find_max_index(SPECTRAL_FREQ[0])
          #find min value in powers
          min_mode=scnl.powers[min_i]
          k=0
          min_index=k
          for k, p in enumerate(scnl.powers[min_i:max_i]):
            if p < min_mode:
              min_mode=p
              min_index=k
          print(min_mode)
          print(min_index)
          trace = go.Scatter(
            y= min_mode,
            x = scnl.frequencies[min_i:max_i][min_index],
            mode = 'markers',
            name = "{} ({})".format(scnl.sta,scnl.inst_id)
          )
          fig.append_trace(trace, row, col)
          # data.append(trace)

      # #predicted curve
#       tremor_trace = go.Scatter(
#         x = SPECTRAL_FREQ,
#         y = SPECTRAL_POWER,
#         mode = 'lines+markers',
#         name = 'Tremor Profile',
#         line = dict(
#           color = ('rgb(205, 12, 24)'),
#           width = 4,
#           dash = 'dash'
#           )
#         )
#       # layout = dict(
#       #               xaxis = dict(title = 'Hertz'),
#       #               yaxis = dict(title = 'Power (db)'),
#       #               )
#       fig.append_trace(tremor_trace, row, col)
#       # data.append(tremor_trace)
#       # subfig = dict(data=data, layout=layout)
    filename="obs-min_mode-v-freq-{}".format(experiment)
    py.plot(fig, filename=filename)


if __name__ == "__main__":
    main()
    
