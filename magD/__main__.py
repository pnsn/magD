# run with python -m magD
import math
import sys
import os
import json
from contour import Contour
import numpy as np
import iris
import seis
sys.path.append(os.path.abspath('..'))


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]
#move this to __main__.py

station_freq = 0
mindetect = 0
CHAN_STRING="BHZ"
NETWORK_STRING="UW"

#entry point
# Parameters for calculating the minimum earthquake detected.
lat_min=42.0
lat_max=49.0
lon_min=-125.0
lon_max=-117.0
lat_step=0.5 #degree increments (resolution)
lon_step=lat_step
#create rows and columns array
lat_list=np.arange(lat_min, lat_max, lat_step)
lon_list=np.arange(lon_min, lon_max, lon_step)

mu = 3e11
q = 300.0 * math.pow(15, 0.35)  # Q value
beta = 3.5  # km/s
cn = 1 / (4 * mu * beta * 1e7)
# signal adjustment values, key is the magnitude, and the lists are the adjustment values.
signal_adjuments_values = {
    1.5: [2.6, 2.2, 1.8, 1.5, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    2.0: [2.6, 2.2, 1.8, 1.5, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    2.5: [2.6, 2.1, 1.8, 1.5, 1.3, 1.2, 1.0, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    3.0: [2.5, 2.1, 1.8, 1.5, 1.3, 1.2, 1.0, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    3.5: [2.4, 2.0, 1.7, 1.5, 1.3, 1.1, 1.0, 0.9, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    4.0: [2.1, 1.8, 1.6, 1.4, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    4.5: [1.8, 1.5, 1.4, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6, 0.5, 0.5],
    5.0: [1.5, 1.3, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.7, 0.7, 0.7, 0.6, 0.6, 0.5, 0.5, 0.3]
}

station_objects = iris.create_station_object(15, CHAN_STRING, NETWORK_STRING)
# print station_objects
mindetect_matrix = []
data = {}
points = []
station_names = station_objects.keys()

#for every point in grid
for lat in lat_list:
    for lon in lon_list:
        all_mindetect = []

        # for every station in list
        for sta in station_names:
            start_period = 0.005
            end_period = 280

            # Goes through all the frequncies.
            period = start_period
            mincheck = False
            origin = [lat, lon]
            destination = station_objects[sta][1]
            # Calculate distance between earthquake and station
            delta = seis.distance(origin, destination)  # km
            
            #for each period
            while period <= end_period:
                fc = 1 / period

                # Does most of the calculations, fault radius, Mo, Mw
                fault_radius = 2.34 * beta / ((2 * math.pi) * fc)
                Mo = 2.29 * 100000000 * math.pow((1e5 * fault_radius), 3) #in dyn*cm
                Mw = .667 * math.log10(Mo) - 10.7

                # delta_index = distance_signal_adjustment(delta)
                # mw_index = magnitude_signal_adjustment(signal_adjuments_values,Mw)
                # filtfc = signal_adjuments_values[mw_index][delta_index]
                As = seis.compute_amplitude(fc, Mo, cn, delta,station_objects[sta][0],fc)
                Amplitude = As[0]
                station_freq = As[1]
                Amplitude = seis.calculate_geometric_spreading(Amplitude, delta)
                Amplitude = seis.compute_attenuation(fc, delta, q, beta,Amplitude,station_freq)

                # Pwave amp is 10 times smaller than S
                # correction for matching brune scaling to PSD calculation normalization
                Amplitude = Amplitude / 6.0
                db = seis.amplitude_power_conversion(Amplitude)

                mindetect = seis.min_detect(db,sta,Mw,station_freq, station_objects)

                # /* printf(" HERE    %f %f %f\n", db, fc, mindetect[i]);*/
                if(mindetect):
                    station_objects[sta].append(Mw)
                    all_mindetect.append(Mw)
                    break

                period = period * (2 ** 0.125)
        all_mindetect.sort()
        mindetect_matrix.append(all_mindetect)
        value = all_mindetect[0]
        point = {
            "lat": lat,
            "lng": lon,
            "count": value
        }
        points.append(point)
        data['points'] = points
        lon+=lon_step
        
    lat+=lat_step

print type(data)
print len(station_names)
# total_number = 0
# sum = 0

# min = mindetect_matrix[0][0]
# max = mindetect_matrix[0][0]

# for array in mindetect_matrix:
#     number = array[2]
#     total_number = total_number + 1
#     sum = sum + number
#     if(number < min):
#         min = number
#     if(number > max):
#         max = number
#
# average = sum/float(total_number)
# print "Min: " + str(min) + " Max: " + str(max) + " Average: " + str(average)
levels = [1.0,1.5,2.0,2.5,3.0,3.3,3.5,3.8,4.0,4.3,4.6,5.0,5.5,6.0]
# print data['points']['count']
c  = Contour(data,levels)
geocol = c.build_geometry_collection()
c.write_json_to_file(geocol, "./test/data/contours.json")
 
if __name__ == "__main__":
    main()