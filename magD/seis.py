'''
Module for the min detect algo
'''
import math

#FIXME These should be network specific?
# frequency dependent amplification factors based on the NEIC auto picker filters.
# key is the magnitude, and the lists are the adjustment values
#listed in 2 deg steps from 0 to 30 deg angular distance
signal_adjusted_values = {
    1.5: [2.6, 2.2, 1.8, 1.5, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    2.0: [2.6, 2.2, 1.8, 1.5, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    2.5: [2.6, 2.1, 1.8, 1.5, 1.3, 1.2, 1.0, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    3.0: [2.5, 2.1, 1.8, 1.5, 1.3, 1.2, 1.0, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    3.5: [2.4, 2.0, 1.7, 1.5, 1.3, 1.1, 1.0, 0.9, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    4.0: [2.1, 1.8, 1.6, 1.4, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6, 0.5],
    4.5: [1.8, 1.5, 1.4, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6, 0.5, 0.5],
    5.0: [1.5, 1.3, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.7, 0.7, 0.7, 0.6, 0.6, 0.5, 0.5, 0.3]
}



# Calculates the distance between two locations with a lat/lon
#return both angular distance(rad) and distance in km
def distance(origin, destination):
    lat1, lon1 = origin.lat, origin.lon
    lat2, lon2 = destination.lat, destination.lon
    radius = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.pow(math.sin(dlat / 2),2)  + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.pow(math.sin(dlon / 2),2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return (c,d)

#retrun fault radius in cm
#
def fault_radius(fc, beta):
  return  2.34 * beta/(2 * math.pi * fc)

def moment(fault_radius):
  return 2.29 * 100000000 * math.pow((1e5 * fault_radius), 3) #in dyn*cm

def moment_magnitude(Mo):
  return .667 * math.log10(Mo) - 10.7

# calculates the geometric spreading term
# Needs an amplitude and a distance.
# Returns the adjusted amplitude.
def geometric_spreading(delta):
    return  1.0 / math.pow(delta*1e5, 0.5)


# use Brune model to compute aplitude
# amp=cn*m0*filtfc[i]*pow(fc,2)/  (pow(filtfc[i],2)+pow(fc,2)) /distkm[i];

def amplitude(fc, Mo, cn, delta, filtfc):
    fc2=math.pow(fc,2)
    filtfc2=math.pow(filtfc,2)
    
    # return  Mo * cn * filtfc * (math.pow(fc,2)) / (math.pow(filtfc,2)) + (math.pow(fc,2)/ delta)
    return  Mo * cn * filtfc * fc2 / (filtfc2 + fc2)/ delta
    
# calculates the attenuation factor
# returns the adjusted amplitude.
def attenuation(delta, q, beta, filtfc):
    # Compute the attenuation term:
    return math.pow(2.7182818, ((-1 * math.pi * filtfc * (delta*1e5)) / (q * beta * 1e5)))

# Converts amplitude to power
def amplitude_power_conversion(As):
    # Converting amplitude to power
    power = As * As
    if power == 0.0:
        db = -200
    else:
        db = 10.0 * math.log10(power)
    return db

#use mag and angular distance to lookup adjusted frequecy in the signal_adjusted_values obj
def signal_adjusted_frequency(Mw, rad):
    keys = signal_adjusted_values.keys()  # sav stands for Signal_Adjustment_Values
    keys.sort()
    Mw=max(keys[0], min(Mw, keys[-1]))
    for i in range(len(keys)-1):
        if Mw >= keys[i] and Mw < keys[i + 1]:
            mag_key = keys[i]
    if Mw==keys[-1]:
        mag_key=keys[-1]
    deg=rad*(180/math.pi)
    index=int(deg/2)
    index = max(0, min(index, 15))
    return signal_adjusted_values[mag_key][index]
    

'''
Calculates the min detection at this point for this given station
db=attenuated noise at station
sta=station
Mw=mag
sta_fc=nyqist or station adjusted value 
'''
def min_detect(scnl, db, Mw, freq):
    stafc=scnl.frequency_power(freq)
    # stafc = station_objects[sta]['modes'][index]
    vel_stafc = stafc -(20*math.log10(freq*2*math.pi))
    if stafc < -170:
        vel_stafc = -99.1111
        stafc = -99.1111

    if db >= vel_stafc:
        mindetect = Mw
        return True
    return False
    