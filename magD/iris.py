'''Module for  IRIS webservices
   concerns : 1) connects to iris to get list of all available channels
                returns as 2d list of stations
              2)retrieves PDF for given scnl
                returns
'''

from urllib.request import urlopen
import urllib.error
import xml.etree.ElementTree as etree


'''use fdsn webservice
to build and return list of scnls by querying fdsn service
strings are passed directly to fdns without altering.
stations is a collection of station objects,
return dict
{code: int, data: 2dim list of station data}
where code is HTTP response, 2dim list contains:
[['UMAT', 'HHZ', 'UW', '', 100.0, 45.2904, -118.9595]...]

'''


def get_fdsn(sta_string, chan_string, net_string, loc_string="--"):
    stations = []
    url = "http://service.iris.edu/fdsnws/station/1/query?net=" + \
          net_string + "&sta=" + sta_string + "&loc=" + loc_string + \
          "&cha=" + chan_string + \
          "&level=channel&format=xml&includecomments=true&nodata=404"
    # print(url)
    try:
        fdsn_resp = urlopen(url)
    except urllib.error.HTTPError as err:
        return {"code": err, "data": []}
    ns = "{http://www.fdsn.org/xml/station/1}"
    tree = etree.parse(fdsn_resp)
    root = tree.getroot()
    # for each network
    for network in root.findall("%sNetwork" % ns):
        net = network.attrib['code']
        # for each station
        for station in network.findall("%sStation" % ns):
            # print(etree.tostring(station))
            sta = station.attrib['code']
            '''
                ensure we only return on channel per site.
                use precendence of chan_string with first station
                having more weight than the next.Ensure type of GEOPHYSICAL or
                CONTINOUS since
                type=TRIGGERED will not have PDF
                FIXME commenting out the Type for now since some legit channels
                don't have this tag'''
            prefchan = []
            for chan in chan_string.split(","):
                prefchan = station.findall("%sChannel[@code='%s']" %
                                           (ns, chan))
                if len(prefchan) > 0:
                    break
            if len(prefchan) > 0:
                channel = prefchan[0]
                chan = channel.attrib['code']
                loc = channel.attrib['locationCode']
                lat = lon = samp = None
                for node in channel.iter():
                    if node.find('%sLongitude' % ns) is not None:
                        lon = float(node.find('%sLongitude' % ns).text)
                    if node.find('%sLatitude' % ns) is not None:
                        lat = float(node.find('%sLatitude' % ns).text)
                    if node.find('%sSampleRate' % ns) is not None:
                        samp = float(node.find('%sSampleRate' % ns).text)
                    if node.find('%sDepth' % ns) is not None:
                        depth = float(node.find('%sDepth' % ns).text)

                # create new Scnl for each
                if lon is not None and lon is not None and samp is not None:
                    stations.append([sta, chan, net, loc, lat, lon, depth,
                                     "", "", samp])
    return {"code": fdsn_resp.getcode(), "data": stations}

'''Finds Iris noise file for that station.
 Accepts Scnl instance
 Returns list of noise elements for that station.
 [
 <Bucket freq="freq1" hits="1" power="-187"/>
 <Bucket freq="freq1" hits="3" power="-183"/>,
    ....,
  <Bucket freq="freqn" hits="1" power="-187"/>,
  <Bucket freq="freqn" hits="3" power="-183"/>

  ]
  See example
 http://service.iris.edu/mustang/noise-pdf/1/query?net=UW&sta=BRAN
        &loc=--&cha=BHZ&quality=M&format=xml &starttime=2014-03-01
        &endtime=2014-04-01
        returns {code: int, data: xml_root},
        where code is the HTML response code
'''


def get_noise_pdf(sta, chan, net, loc, starttime, endtime):
    if loc is None or loc == "":
        loc = "--"
    url = "http://service.iris.edu/mustang/noise-pdf/1/query?"\
        "net={}&sta={}&loc={}&cha={}""&quality=M&format=xml"\
        "&starttime={}&endtime={}".format(net, sta, loc, chan, starttime,
                                          endtime)
    try:
        xml_file = urlopen(url)
        tree2 = etree.parse(xml_file)
        root2 = tree2.getroot()
        return {'code': xml_file.getcode(),
                'data': root2.findall("Histogram")[0].getchildren()}
    except urllib.error.HTTPError as err:
        # if err.code == 404:
        # print("404 error: %s for scnl: %s:%s:%s"%(err,sta, chan, net))
        return {'code': err.code, 'data': {}}
