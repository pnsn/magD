# run with python -m magD
import math
import sys
import os
import json
from map_layer import MapLayer
import numpy as np
import iris
import seis
from pprint import pprint
sys.path.append(os.path.abspath('..'))

#entry point
def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    STA_STRING="*"
    # STA_STRING="UMAT"
    CHAN_STRING="BHZ"
    NET_STRING="UW"

    # Parameters for calculating the minimum earthquake detected.
    lat_min=42.0
    lat_max=49.0
    lon_min=-125.0
    lon_max=-117.0
    lat_step=0.5#degree increments (resolution)
    #for testing (45.2904, -118.9595)
    # lat_min=43.2
    # lat_max=47.2
    # lon_min=-121
    # lon_max=-117
    # lat_step=0.01 #degree increments (resolution)

    lon_step=lat_step
    #create rows and columns array
    lat_list=np.arange(lat_min, lat_max, lat_step)
    lon_list=np.arange(lon_min, lon_max, lon_step)
    #for each point record count
    value_list=[]
    #number of stations for detection solution


    mu = 3e11
    qconst = 300.0 
    beta = 3.5  # km/s
    cn = 1/(4 * mu * beta * 1e7)
    max_value=100
    station_objects = iris.create_station_pdf_modes(50, STA_STRING, CHAN_STRING, NET_STRING)
    # print station_objects
    station_names = station_objects.keys()
    num_stas=min(len(station_names), 5)
    print station_names
    #for every point in grid
    for lat in lat_list:
        print lat
        for lon in lon_list:
            # # set boundary's artifically high to close contours
            # if lat ==lat_list[0] or lat ==lat_list[-1] or lon==lon_list[0] or lon==lon_list[-1]:
            #   value_list.append(max_value)
            #   continue
            mindetect = []

            # for every station in list
            for sta in station_names:
                start_period = 0.001
                end_period = 280

                # Goes through all the freqs, i.e. from small to large Mw
                #this way the first detection will be the min Mw
                period = start_period
                origin = (lat, lon)
                destination = station_objects[sta]['cords']
                # Calculate distance between earthquake and station
                delta_rad, delta_km = seis.distance(origin, destination)  # km
                #for each period
                while period <= end_period:
                    fc = 1/period
                    fault_radius = seis.fault_radius(fc, beta)
                    Mo = seis.moment(fault_radius)
                    Mw = seis.moment_magnitude(Mo)
                    # if period==start_period:
                    #     print Mw
                    filtfc=seis.signal_adjusted_frequency(Mw,fc)
                    nyquist=station_objects[sta]['nyquist']   
                
                    if filtfc >= nyquist:
                      filtfc=station_objects[sta]['nyquist']
                
                    As = seis.amplitude(fc, Mo, cn, delta_km, filtfc)
                    As*=seis.geometric_spreading(delta_km)
                    q = qconst*math.pow(nyquist, 0.35)  # Q value
                    As*=seis.attenuation(delta_km, q, beta, filtfc)

                    # Pwave amp is 10 times smaller than S
                    # correction for matching brune scaling to PSD calculation normalization
                    As/=6.0
                    db = seis.amplitude_power_conversion(As)

                    detection = seis.min_detect(db,sta, Mw, filtfc, station_objects)
                    # /* printf(" HERE    %f %f %f\n", db, fc, mindetect[i]);*/
                    if(detection):
                        # print"##########################"
                        # print fc
                        # print filtfc
                        # print Mw                    
                        mindetect.append(Mw)
                        break

                    period = period * (2 ** 0.125)
            mindetect.sort()
            # mindetect_matrix.append(mindetect)
            value = mindetect[num_stas-1]
            value_list.append(value)
            lon+=lon_step
        
        lat+=lat_step


    print "min val=%f"%min(value_list)
    max_val= max(value_list)
    print "max val=%f"%max_val
    print "ave val=%f"%np.average(value_list)
    print "median val=%f"%np.median(value_list)
    layer = MapLayer(lat_list, lon_list, value_list)
    layer.make_grid3("mag_detect")
    layer.grid3_to_file("./public/js/grid3.json")
    # layer.write_to_csv("./test/data/detections_5sta.csv")
    # layer.make_contours()
    # layer.contours_to_file("./public/js/contours.json")

if __name__ == "__main__":
    main()