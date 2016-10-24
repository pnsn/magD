import xml.etree.ElementTree as etree
import xml.etree.cElementTree as ET
import urllib2
import math
import sys
import os
import json
import contour
sys.path.append(os.path.abspath('..'))

station_freq = 0
mindetect = 0

# Finds all the station codes from Iris
# Returns station codes and lat/lon for each station.
def find_station_codes():
    all_stations = urllib2.urlopen(
        'http://service.iris.edu/fdsnws/station/1/query?net=UW&sta=*&loc=--&cha=BHZ&level=station&format=xml&includecomments=true&nodata=404')
    tree = ET.parse(all_stations)
    root = tree.getroot()
    stations = root[5].getchildren()
    station_codes = []

    # This grabs all the station codes from the stations, so they can be used in the urls later.
    for station in stations:
        attrib = station.attrib
        if len(attrib) > 0:
            children = station.getchildren()
            code = attrib["code"]
            station_codes.append(code)
            lat = 0
            lon = 0
            for child in children:
                if child.tag.find("Lat") != -1:
                    lat = float(child.text)
                elif child.tag.find("Lon") != -1:
                    lon = float(child.text)

            station_coordinates = [lat, lon]
            station_codes.append(station_coordinates)
    return station_codes


# Finds Iris noise file for that station.
# Needs a station code.
# Returns the noise data for that station.
def find_station(code):
    network = "UW"
    chanel = "BHZ"
    buckets = ""
    url = ''.join(["http://service.iris.edu/mustang/noise-pdf/1/query?net=", network, "&sta=", code,
                   "&loc=*&cha=" + chanel + "&quality=M&format=xml"])
    xml_file = urllib2.urlopen(url)
    tree2 = ET.parse(xml_file)
    root2 = tree2.getroot()
    buckets = root2.findall("Histogram")[0].getchildren()
    return buckets


# Creates individual station objects for each station, storing the noise info (pow and freq),
# The nyquist value, and the station code. Initially there is no min earthquake detected!!!
# Returns all the station objects.
def create_station_object(nyquist):
    # goes through all the station codes, queries IRIS and gets the frequency data
    station_codes = find_station_codes()
    station_objects = {}
    index = 0
    while (index < len(station_codes) - 1):

        code = station_codes[index]
        lat_lon = station_codes[index + 1]
        # LON and SEP dont play well with IRIS for some reason....? code !=  and "BABR"
        if code != "LON" and code != "SEP":
            buckets = find_station(code)
            mode = 0
            power = 0
            freq = buckets[0].attrib["freq"]
            noise = []
            pow_freq = []
            # creates a station object that contains freq pairs with the mode/power
            for bucket in buckets:
                freq2 = float(bucket.attrib["freq"])
                if freq2 == freq:
                    if int(bucket.attrib["hits"]) > mode:
                        mode = int(bucket.attrib["hits"])
                        power = int(bucket.attrib["power"])
                        pow_freq = []
                        pow_freq.append(freq)
                        pow_freq.append(power)
                else:
                    noise.append(pow_freq)
                    freq = freq2
                    mode = 0
                    pow_freq = []
            del noise[0]
            station_objects[code] = [nyquist, lat_lon, noise]
            # all_station_objects.append(station_object)
        index = index + 2
    return station_objects



# http://service.iris.edu/mustang/noise-pdf/1/query?net=UW&sta=BRAN&loc=--&cha=BHZ&quality=M&format=xml

# Calculates the distance between two locations with a lat/lon
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.pow(math.sin(dlat / 2),2)  + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.pow(math.sin(dlon / 2),2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d


# calculates the geometric spreading term
# Needs an amplitude and a distance.
# Returns the adjusted amplitude.
def calculate_geometric_spreading(As, delta):
    geom = 1.0 / math.pow(delta*1e5, 0.5)
    As = As * geom
    return As


# Calculates the amplitude of a given earthquake.
# Needs a frequency, Mo, cn, filterfc, distance, station freq, and the nyquist value.
# Returns the amplitude.
def compute_amplitude(fc, Mo, cn, delta, nyquist,filtfc):
    freq_2 = math.pow(fc, 2)
    if nyquist >= filtfc:
        As = Mo * cn * filtfc * (freq_2) / ((math.pow(filtfc, 2)) + freq_2)/ delta
        station_freq = filtfc
    else:
        As = Mo * cn * nyquist * (freq_2) / ((math.pow(nyquist, 2)) + freq_2)/ delta
        station_freq = nyquist
    return [As,station_freq]

# calculates the attenuation factor
# returns the adjusted amplitude.
def compute_attenuation(fc, delta, q, beta,Amplitude,station_freq):
    # Compute the attenuation term:
    atten = math.pow(2.7182818, ((-1 * math.pi * station_freq * (delta*1e5)) / (q * beta * 1e5)))
    As_att = Amplitude * atten
    return As_att

# Converts amplitude to power
def amplitude_power_conversion(As):
    # Converting amplitude to power
    power = As * As
    if power == 0.0:
        db = -200
    else:
        db = 20.0 * math.log10(power)
    return db

# Calculates the signal adjustment for the distance the station is away from
# the source of the earthquake.
def distance_signal_adjustment(delta):
    deltas = []
    for k in range(0, 15):
        deltas.append(111.0 * k)

    # This goes through the degree array and finds the index corresponding to the col in the adjustments table.
    delta_index = 0
    for k in range(0, 15):
        if (((delta/111.19)*(math.pi/180)) >= deltas[k] and ((delta/111.19)*(math.pi/180)) < deltas[k + 1]):
            delta_index = k
    if delta_index == 0:
        delta_index = 15
    return delta_index

# Calculates the signal adjustment, with respsect to the magnitude generated.
# Retruns the appropriate index
def magnitude_signal_adjustment(signal_adjuments_values,Mw):
    sav = signal_adjuments_values.keys()  # sav stands for Signal_Adjustment_Values
    sav.sort()
    mw_index = 0
    for k in range(0, 7):
        if Mw >= sav[k] and Mw < sav[k + 1]:
            mw_index = sav[k]
    # what is nummw and what does it stand for????
    if mw_index == 0:
        mw_index = 5.0
    return mw_index

# Calculates the min
def min_detect(db, code, Mw,station_freq):

    number_frequencies = len(station_objects[code][2])
    for number in range(number_frequencies - 2):
        if station_objects[code][2][number] and station_objects[code][2][number + 1]:
            freq1 = station_objects[code][2][number][0]
            freq2 = station_objects[code][2][number + 1][0]
            if station_freq >= freq1 and station_freq <= freq2:
                stafc_db90 = station_objects[code][2][number][1]
                vel_stafc_db90 = stafc_db90-(20*math.log10(station_freq*2*math.pi))
                if stafc_db90 < -170:
                    vel_stafc_db90 = -99.1111
                    stafc_db90 = -99.1111

                if db >= vel_stafc_db90:
                    mindetect = Mw
                    station_objects[code].append(mindetect)
                    return True
    return False

# Parameters for calculating the minimum earthquake detected.
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

station_objects = create_station_object(15)
mindetect_matrix = []
data = {}
points = []
# Calculates the minimum detection.
i = 42  # i is lattitude.
lat_index = 0
while i <= 49:
    lon_index = 0
    j = -125  # j is longitude
    while j <= -117:
        all_mindetect = []
        codes = station_objects.keys()
        #codes = ["RATT"]

        # Goes through all the stations.
        for code in codes:
            start_period = 0.005
            end_period = 280

            # Goes through all the frequncies.
            period = start_period
            mincheck = False
            origin = [i, j]
            destination = station_objects[code][1]
            # Calculate distance between earthquake and station
            delta = distance(origin, destination)  # km

            while period <= end_period:
                fc = 1 / period

                # Does most of the calculations, fault radius, Mo, Mw
                fault_radius = 2.34 * beta / ((2 * math.pi) * fc)
                Mo = 2.29 * 100000000 * math.pow((1e5 * fault_radius), 3) #in dyn*cm
                Mw = .667 * math.log10(Mo) - 10.7

                # delta_index = distance_signal_adjustment(delta)
                # mw_index = magnitude_signal_adjustment(signal_adjuments_values,Mw)
                # filtfc = signal_adjuments_values[mw_index][delta_index]
                As = compute_amplitude(fc, Mo, cn, delta,station_objects[code][0],fc)
                Amplitude = As[0]
                station_freq = As[1]
                Amplitude = calculate_geometric_spreading(Amplitude, delta)
                Amplitude = compute_attenuation(fc, delta, q, beta,Amplitude,station_freq)

                # Pwave amp is 10 times smaller than S
                # correction for matching brune scaling to PSD calculation normalization
                Amplitude = Amplitude / 6.0
                db = amplitude_power_conversion(Amplitude)

                mindetect = min_detect(db,code,Mw,station_freq)

                # /* printf(" HERE    %f %f %f\n", db, fc, mindetect[i]);*/
                if(mindetect):
                    station_objects[code].append(Mw)
                    all_mindetect.append(Mw)
                    break

                period = period * (2 ** 0.125)
        all_mindetect.sort()
        mindetect_matrix.append(all_mindetect)
        value = all_mindetect[0]
        point = {
            "lat": i,
            "lng": j,
            "count": value
        }
        points.append(point)
        data['points'] = points
        lon_index = lon_index + 1
        j = j + 0.5
    lat_index = lat_index + 1
    i = i + 0.5
print data
print len(codes)
total_number = 0
sum = 0

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
c  = contour.Contour(data,levels)
geocol = c.build_geometry_collection()
c.write_json_to_file(geocol, "../test/data/contours.json")