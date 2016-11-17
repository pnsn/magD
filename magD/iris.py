'''simple module for  IRIS webservices
'''
import urllib2
import xml.etree.ElementTree as etree
import xml.etree.cElementTree as ET

#use fdsn webservice
# Returns stations with  lat/lon
def get_available_stations(sta, chan):
    fdsn_resp = urllib2.urlopen(
        'http://service.iris.edu/fdsnws/station/1/query?net=UW&sta=%s&loc=*&cha=%s&level=station&format=xml&includecomments=true&nodata=404'%(sta,chan))
    tree = ET.parse(fdsn_resp)
    root = tree.getroot()
    fdsn = root[5].getchildren()
    stations = []
    #create obj of form:
    #{sta: string, lat: float, lon:float }
    for station in fdsn:
        attrib = station.attrib
        if len(attrib) > 0:
            sta={}
            children = station.getchildren()
            sta['sta'] = attrib["code"]
            for child in children:
                if child.tag.find("Lat") != -1:
                    sta['lat'] = float(child.text)
                elif child.tag.find("Lon") != -1:
                    sta['lon'] = float(child.text)
            if 'lat' in sta.keys() and 'lon' in sta.keys():
              stations.append(sta)
    return stations


# Finds Iris noise file for that station.
# Needs a station name, chan, and network
# Returns the noise data for that station.
# http://service.iris.edu/mustang/noise-pdf/1/query?net=UW&sta=BRAN&loc=--&cha=BHZ&quality=M&format=xml

def get_noise_pdf(sta, chan, net):
    url = ''.join(["http://service.iris.edu/mustang/noise-pdf/1/query?net=", net, "&sta=", sta,
                   "&loc=*&cha=" + chan + "&quality=M&format=xml"])
    try:
      xml_file = urllib2.urlopen(url)
      tree2 = ET.parse(xml_file)
      root2 = tree2.getroot()
      return root2.findall("Histogram")[0].getchildren()
    except urllib2.HTTPError as err:
      if err.code == 404:
         print "error: %s for sta: %s"%(err,sta)
         return None
      else:
        raise err
        
        
''' Creates individual station objects for each station, storing the noise in list,
 The nyquist value, and the station code. 
The ratio of freq1/freq0 (base) are used to index modes
samples are in the following format
#<Bucket freq="0.0052556" hits="1" power="-199"/>
return list of objects of type
    {sta: {nyquist: nyquist, cords: (lat, lon), modes: [mode0,mode1,...,moden], freq0:float, base:float }
'''
def create_station_pdf_modes(nyquist, sta, chan, net):
    #get available stations for net/chan using 
    stations = get_available_stations(sta,chan)
    pdf_modes = {}
    for station in stations:    
        sta = station['sta']
        #get pdf for this station
        samples = get_noise_pdf(sta, chan, net)
        if samples is not None:
          mode = float(samples[0].attrib["hits"])
          power = float(samples[0].attrib["power"])
          freq=float(samples[0].attrib["freq"])
          freq0=freq
          base=float(samples[1].attrib["freq"])/freq0
          
          modes = [] 
          # creates a station object that contains freq pairs with the mode/power
          for sample in samples:
              freq2 = float(sample.attrib["freq"])
              if freq2 == freq:
                if int(sample.attrib["hits"]) > mode:
                  mode = int(sample.attrib["hits"])
                  power = int(sample.attrib["power"])
              else:
                  modes.append(power)
                  
                  freq = freq2
                  mode = int(sample.attrib["hits"])
                  power = int(sample.attrib["power"])
          pdf_modes[sta] = {'nyquist': nyquist, 'cords': (station['lat'],station['lon']), 'modes': modes, 'freq0:' freq0, 'base:' base}
      
    return pdf_modes
         