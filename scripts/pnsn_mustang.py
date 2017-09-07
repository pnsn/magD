#!/usr/bin/env python
#this is the inital script that the classes were built off of. I can probably be removed

#NOTE TO SELF: ask Jon about whether you need all the bucket frequencies or you just need the mode...
import xml.etree.ElementTree as etree
import xml.etree.cElementTree as ET
import urllib2
import math


#Grabs all UW stations from IRIS
all_stations = urllib2.urlopen('http://service.iris.edu/fdsnws/station/1/query?net=UW&sta=*&loc=--&cha=BHZ&level=station&format=xml&includecomments=true&nodata=404')
 
tree = ET.parse(all_stations)
root = tree.getroot() 
stations = root[5].getchildren()
station_codes = []
stations_noise = {}
station_object = []
mindetect = 0
#calculates the distance between 2 points.
#Returns the distance
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 #km
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2* math.atan2(math.sqrt(a),math.sqrt(1-a))
    d = radius*c
    
    return d

#This grabs all the station codes from the stations, so they can be used in the urls later.
for station in stations:
        attrib = station.attrib
        if len(attrib) > 0:
            code = attrib["code"]
            station_codes.append(code)

#goes through all the station codes, queries IRIS and gets the frequency data     
nyquist = 15
for code in station_codes:
    #LON and SEP dont play well with IRIS for some reason....? code !=  and "BABR"
    if code != "LON" and code !="SEP":
        network = "UW"
        station = code
        chanel = "BHZ"
        #requests the data.
        url = ''.join(["http://service.iris.edu/mustang/noise-pdf/1/query?net=",network,"&sta=",station,"&loc=*&cha="+ chanel+ "&quality=M&format=xml"])
        xml_file = urllib2.urlopen(url)
        tree2 = ET.parse(xml_file) 
        root2 = tree2.getroot()
        buckets = root2.findall("Histogram")[0].getchildren()
        
        mode = 0
        power = 0
        
        print code
        print url
        freq = buckets[0].attrib["freq"]
        noise = []
        pow_freq = []
        #creates a station object that contains freq pairs with the mode/power
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
        station_object.append(nyquist)
        station_object.append(noise)
        stations_noise[code] = station_object
        # print station_object
        break
  
#print station_xml_files[0]
#http://service.iris.edu/mustang/noise-pdf/1/query?net=UW&sta=BRAN&loc=--&cha=BHZ&quality=M&format=xml
mu = 3*math.pow(10,11)
q = 640.0*math.pow(15,0.35) #Q value
beta = 3.5 #km/s
cn= 1/(4*mu*beta*1e7)
#signal adjustment values, key is the magnitude, and the lists are the adjustment values.
signal_adjuments_values = {
    1.5:[2.6, 2.2, 1.8, 1.5, 1.3, 1.2, 1.1, 1.0, 0.9 ,0.8, 0.7 ,0.7, 0.6, 0.6, 0.6, 0.5],
    2.0:[2.6, 2.2, 1.8, 1.5, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    2.5:[2.6, 2.1, 1.8, 1.5, 1.3, 1.2, 1.0, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    3.0:[2.5, 2.1, 1.8, 1.5, 1.3, 1.2, 1.0, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    3.5:[2.4, 2.0, 1.7, 1.5, 1.3, 1.1, 1.0, 0.9, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    4.0:[2.1, 1.8, 1.6, 1.4, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    4.5:[1.8, 1.5, 1.4, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6, 0.5, 0.5],
    5.0:[1.5, 1.3, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.7, 0.7, 0.7, 0.6, 0.6, 0.5, 0.5, 0.3]
}
i = 42 # i is lattitude.
while i <= 49:
    j = -125 #j is longitude
    while j < -117:
        #Goes through all the stations.
        for station in stations:
            nyquist = station_object[0]
            if len(station.attrib) > 0:
                children = station.getchildren()
                code = station.attrib["code"]
                #Sets the lat and lon for the station.
                lat = 0
                lon = 0
                for child in children:
                    if child.tag.find("Lat") != -1:
                        lat = float(child.text)
                    elif child.tag.find("Lon") != -1:
                        lon = float(child.text)
                #station_freq = station_power[code][1]
                station_coordinates = [lat,lon]
                map_coordinates = [i,j]
                
                # Finds the distance between the point on the map and the station.
                delta = distance(station_coordinates,map_coordinates)
                start_period = 0.05
                end_period = 280

                #Goes through all the frequncies.
                period = start_period
                mincheck = False
                while period <= end_period:
                    fc = 1/period #Converts period to frequency
                    
                    #Does most of the calculations, fault radius, Mo, Mw
                    fault_radius = 2.34*beta/(2*math.pi*fc)
                    Mo = 2.29*100000000*math.pow((1e5*fault_radius),3)
                    Mw = .667*math.log10(Mo)-10.7
                    # print "Mag. generated: " + str(Mw)
                    #ask about the ANGULAR FREQUENCY! fa is currently the angular frequency.
                    gama = 0
                    deltas = []
                    for k in range(0,16):
                        deltas.append(111.0*k)
                      
                    #This goes through the degree array and finds the index corresponding to the col in the adjustments table.
                    delta_index = 0
                    for k in range(0,16):
                        if (delta >= deltas[k] and delta < deltas[k+1]):
                            delta_index = k
                    if delta_index == 0:
                        delta_index= 15
                    
                    mw_index = 0
                    sav = signal_adjuments_values.keys() #sav stands for Signal_Adjustment_Values
                    sav.sort()
                    for k in range(0,7):
                        if Mw >= sav[k] and Mw < sav[k+1]:
                            mw_index = k
                    # what is nummw and what does it stand for????
                    if mw_index == 0:
                        mw_index= 6
                    # print signal_adjuments_values.keys()
                    actual_mw_index = sav[mw_index]
                       
                    # Find the proper filtered value for the frequency.
                    filtfc = signal_adjuments_values[actual_mw_index][delta_index]
                    #print filtfc
                    #print station_object[0]
                    # Calculates the proper amplitude, using the filtered frequency.
                    freq_2 = math.pow(fc,2)
                    if nyquist >= filtfc:
                        As = Mo*cn*filtfc*(freq_2)/(math.pow(filtfc,2)) + freq_2/delta
                        station_freq = filtfc
                    else:
                        As = Mo*cn*station_freq*(freq_2)/(math.pow(station_freq,2)) + freq_2/delta
                    # frequencies = stations_noise[code][2]
                    #print frequencies
                    #Finding gama as shown in the paper.
                    if delta <= 70:
                        gama = -1.0
                    elif delta > 70 and delta <=150:
                        gama = 1.1
                    else:
                        gama = 0.5

                    #geometric spreading Term:
                    geom = 1.0/math.pow(delta,0.5)
                    As = As*geom

                    #Compute the attenuation term:
                    atten = math.pow(math.e,((-1*math.pi*fc*delta)/(q*beta*math.pow(10,5))))
                    As = As*atten
                    
                    #Pwave amp is 10 times smaller than S
                    #correction for matching brune scaling to PSD calculation normalization
                    As=As/6.0

                    #Converting amplitude to power
                    power = As*As
                    if power == 0.0:
                        db = -200
                    else:
                        db = 10.0*math.log10(power)
                    vel_stafc_db90 = 0
                    mindetect = 0
                    
                    number_frequencies = len(station_object[1])
                    for number in range(number_frequencies-2):
                        freq1 =  station_object[1][number][0]
                        freq2 =  station_object[1][number + 1][0]
                        print station_object[1].sort()
                        print str(station_object[1]) + "/n"
                        print station_object[1][number + 1][0]
                        if mincheck == TRUE:
                            break
                        if nyquist >= freq2 and nyquist <= freq1:
                            stafc_db90 = station_object[1][number][1]
                            # vel_stafc_db90 = stafc_db90-10*math.log10(nyquist*2*math.pi)*stafc_db90
                            if stafc_db90 < -170:
                                vel_stafc_db90 =-99.1111
                                stafc_db90 =-99.1111
            	    
                            if db >= stafc_db90 and mincheck == False: 
                                mindetect = Mw
                                mincheck = True
                                print Mw
                        
                        # /* printf(" HERE    %f %f %f\n", db, fc, mindetect[i]);*/
                    period = period*(2**0.125)
                station_object.append(mindetect)    
                
                    
        j = j + .1
        
    i = i + .1
    
# start_period = 1/20
# end_period = 280
# index = 0
# while start_period <= end_period:
#     if index % 8 == 0 or index == 0:
#         print start_period
#         start_period = start_period + start_period*(2**0.125)