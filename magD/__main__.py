# run with python -m magD
import math
import sys
import os
from map_layer import MapLayer
from station_stats import StationStats
import numpy as np
import iris
import seis
from pprint import pprint
from scnl import Scnl

sys.path.append(os.path.abspath('..'))

#entry point
def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    STA_STRING="*"
    # STA_STRING="UMAT"
    CHAN_STRING="BHZ,HHZ"
    NET_STRING="UW,CC,NC"

    # Parameters for calculating the minimum earthquake detected.
    #lats will be parsed from N-S (large to small)
    lon_step=0.05 #degree increments (resolution)
    lat_step= lon_step*-1 #go backwards
    lat_min=42.0 + lat_step
    lat_max=49.0  
    lon_min=-126.0
    lon_max=-115.0 + lon_step
    nyquist_correction= 0.4
    num_sta_detection=5
    #create rows and columns array
    lat_list=np.arange(lat_max, lat_min, lat_step) #reverse lat list
    lon_list=np.arange(lon_min, lon_max, lon_step)
    #for each point record count
    value_list=[]
    #number of stations for detection solution
    stats= StationStats()
    
    mu = 3e11
    qconst = 300.0 
    beta = 3.5  # km/s
    cn = 1/(4 * mu * beta * 1e7)
    max_value=100
    iris.get_available_scnls(STA_STRING, CHAN_STRING, NET_STRING)
    iris.create_scnl_pdf_modes(Scnl.instances)
    
    #if #of stas < num_sta_detection use total num of stas
    num_stas=min(len(Scnl.instances), num_sta_detection) 
    #for every point in grid
    for lat in lat_list:
        print lat
        for lon in lon_list:
            mindetect = []

            # for every scnl 
            for scnl in Scnl.instances:
                if len(scnl.powers)>0:
                    start_period = 0.001
                    end_period = 280

                    # Goes through all the freqs, i.e. from small to large Mw
                    #this way the first detection will be the min Mw
                    period = start_period
                    origin = (lat, lon)
                    destination = (scnl.lat, scnl.lon)
                    # Calculate distance between earthquake and station
                    delta_rad, delta_km = seis.distance(origin, destination)  # km
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
                            mindetect.append((Mw,scnl))
                            break

                        period = period * (2 ** 0.125)
            mindetect = sorted(mindetect, key=lambda tup: tup[0])
            value = mindetect[num_stas-1][0]
            value_list.append(value)
            lon+=lon_step
        
        lat+=lat_step


    print "min val=%f"%min(value_list)
    max_val= max(value_list)
    print "max val=%f"%max_val
    print "ave val=%f"%np.average(value_list)
    print "median val=%f"%np.median(value_list)
    layer = MapLayer(lat_list, lon_list, value_list, .25)
    # layer.make_grid3("mag_detect")
    layer.build_geojson_feature_collection()
    layer.write_geojson_to_file("./public/json/geomagD.json")
    layer.write_json_to_file("./public/json/magDgrid.json")
    # stats.write_json_to_file("./public/json/stations_stats.json")
    # print stats.stations
    Scnl.write_json_to_file("./public/json/scnls.json")
    layer.write_to_csv("./test/data/detections.csv")

if __name__ == "__main__":
    main()