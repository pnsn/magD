'''simple module for  IRIS webservices
'''
import urllib2
import xml.etree.ElementTree as etree
import xml.etree.cElementTree as ET
from scnl import Scnl
from pprint import pprint


#use fdsn webservice
# Returns list of Scnl objects
def get_available_scnls(sta_string, chan_string,net_string):
    stations = []
    url ="http://service.iris.edu/fdsnws/station/1/query?net=" + net_string + \
        "&sta=" + sta_string + "&loc=*&cha=" + chan_string + "&level=channel" \
        "&format=xml&includecomments=true&nodata=404"
    fdsn_resp = urllib2.urlopen(url)
    ns="{http://www.fdsn.org/xml/station/1}"
    tree = ET.parse(fdsn_resp)
    root = tree.getroot()

    for network in root.findall("%sNetwork"%ns):
        net=network.attrib['code']
        for station in network.findall("%sStation"%ns):
            sta= station.attrib['code']
            #ensure we only return on channel per site.
            #use precendence of chan_string with first station 
            #having more weight than the next.Ensure type of GEOPHYSICAL since 
            #type=TRIGGERED will not have PDF
            prefchan=[]
            for chan in chan_string.split(","):
                prefchan=station.findall("%sChannel[@code='%s'][%sType='GEOPHYSICAL']"%(ns,chan,ns))
                if len(prefchan) > 0:
                    break
            
            if len(prefchan) > 0:
                channel=prefchan[0]
                chan=channel.attrib['code']
                loc=channel.attrib['locationCode']
                lat=lon=samp=None
                for node in channel.iter():                    
                    if node.find('%sLongitude'%ns) is not None:
                        lon=float(node.find('%sLongitude'%ns).text)
                    if node.find('%sLatitude'%ns) is not None:
                        lat=float(node.find('%sLatitude'%ns).text)
                    if node.find('%sSampleRate'%ns) is not None:
                        samp=float(node.find('%sSampleRate'%ns).text)                    
                if lon is not None and lon is not None and samp is not None:
                    stations.append(Scnl(sta,chan,net,loc,samp,lat,lon))


# Finds Iris noise file for that station.
# Needs a station name, chan, and network
# Returns the noise data for that station.
# http://service.iris.edu/mustang/noise-pdf/1/query?net=UW&sta=BRAN&loc=--&cha=BHZ&quality=M&format=xml

def get_noise_pdf(scnl):
    url = ''.join(["http://service.iris.edu/mustang/noise-pdf/1/query?net=", scnl.net, "&sta=", scnl.sta,
                   "&loc=*&cha=" + scnl.chan + "&quality=M&format=xml"])
    try:
      xml_file = urllib2.urlopen(url)
      tree2 = ET.parse(xml_file)
      root2 = tree2.getroot()
      return root2.findall("Histogram")[0].getchildren()
    except urllib2.HTTPError as err:
      if err.code == 404:
         print "error: %s for scnl: %s:%s:%s"%(err,scnl.sta, scnl.chan,scnl.net)
         print "using url %s"%url
         return None
      else:
        raise err
        
        
''' 
'''
def create_scnl_pdf_modes(scnls):
    for scnl in scnls:
        #get pdf for this station
        noise = get_noise_pdf(scnl)
        if noise is not None:
            scnl.set_powers(scnl, noise)