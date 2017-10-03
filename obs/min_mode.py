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
import re
import configparser
import math
from numpy import polyfit
from numpy import polyval
sys.path.append(os.path.abspath('.'))
# from plotly import tools
# import plotly.plotly as py
# import plotly.graph_objs as go
import matplotlib.pyplot as plt



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
    #axix range
    ymin= -200
    ymax=-100
    xmin=0
    xmax=3
    columns=3
    print(len(dates))
    rows = int((len(dates)-1)/columns)
    print("rows={}".format(rows))
    
    f, axarr = plt.subplots(rows, columns)
    print(axarr)
    for i in range(len(dates)-1):
      x=[]
      y=[]
      row_i = int(i/columns)
      col_i= int(i%columns) 
      print("row_i={}".format(row_i))
      print("col_i={}".format(col_i))
    
      
      Scnl.collection=[]
      for j, r in df_stas.iterrows():
          Scnl(r.sta, r.chan, "7D","",r.rate, r.lat, r.lon, r.depth, r.inst_id, r.desc)
      
      for scnl in Scnl.collection:
        
        # print("STA {}, CHAN {}".format(scnl.sta, scnl.chan))
        resp = iris.get_noise_pdf(scnl, dates[i], dates[i+1])
        if resp is not None:
          noise= resp['data']
          scnl.set_powers(noise)
          #find min and max index and slice
          min_i=scnl.find_min_index(SPECTRAL_FREQ[-1])
          max_i=scnl.find_max_index(SPECTRAL_FREQ[0])
          #find min value in freq range and range of ymin to ymax
          # min_mode=scnl.powers[min_i]
          min_mode=None
          for p in scnl.powers[min_i:max_i]:
            if p>=ymin and p<=ymax and (min_mode==None or p < min_mode):
              min_mode=p
          if min_mode:
            y.append(min_mode)
            x.append(scnl.depth/1000*-1)
          # ax.scatter(min_mode, scnl.depth, alpha=0.8, c=(0,0,0), edgecolors='none', s=30, label=scnl.sta)
      (m,b) = polyfit(x,y,1)
      yp = polyval([m,b],x)
      label="m: {}".format(round(m,3))
      print(label)
      #for some reason, when there is only a single row, list is 1d
      if rows==1:
        axarr[col_i].scatter(x, y, c='r')
        axarr[col_i].plot(x, yp, c='b', label=label)
        axarr[col_i].set_title(dates[i])
        axarr[col_i].set_xlim([xmin,xmax])
        axarr[col_i].set_ylim([ymin,ymax])
        axarr[col_i].legend(loc="upper right")
        
      
      else:
        axarr[row_i,col_i].scatter(x, y, c='r')
        axarr[row_i,col_i].plot(x, yp, c='b', label=label)
        axarr[row_i,col_i].set_title(dates[i])
        axarr[row_i,col_i].set_xlim([xmin,xmax])
        axarr[row_i,col_i].set_ylim([ymin,ymax])
        axarr[row_i,col_i].legend(loc="upper right")
        
        
        
              
          
    count=0
    for ax in axarr.flat:
        if count%columns==0:
          ax.set(ylabel='Power (db)')          
        if count==len(axarr)-1:
          ax.set(xlabel='Depth (km)')
          count+=1
    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for ax in axarr.flat:
        ax.label_outer()
    
    f.suptitle('Min modal noise vs. Depth')

    print('plotting.....')
    plt.show()
    


if __name__ == "__main__":
    main()
    
