'''class for scnls'''
import math
import json
class Scnl:
  instances =[]
  def __init__(self,sta,chan,net,loc="",samprate=None,lat=None,lon=None):
      self.sta=sta
      self.chan=chan
      self.net=net
      self.loc=loc
      self.samprate=samprate
      self.lat=lat
      self.lon=lon
      self.base=None
      self.freq0=None
      self.powers = []
      Scnl.instances.append(self)
  
  def set_powers(self, sta, noise):
    mode = float(noise[0].attrib["hits"])
    power = float(noise[0].attrib["power"])
    freq=float(noise[0].attrib["freq"]) 
    self.freq0=freq
    # creates a station object that contains freq pairs with the mode/power
    for sample in noise:
        freq2 = float(sample.attrib["freq"])
        if freq2 == freq:
          if int(sample.attrib["hits"]) > mode:
            mode = int(sample.attrib["hits"])
            power = int(sample.attrib["power"])
        else:
          #we want freq1 to determine base
          if freq==self.freq0:
              self.base=freq2/self.freq0
          self.powers.append(power)
          freq = freq2
          mode = int(sample.attrib["hits"])
          power = int(sample.attrib["power"])
  
  '''For frequency, what is the associated modal power?
      with pdf noise input set modes (power with > hits)
      freq0 and base are used to index the powers(list) for a 
      O(1) lookup so freq? index= log(freq?/freq[0], freq[1]/freq[0]) returns the index 
      to power 
  '''
  def frequency_power(self, freq):
    return self.powers[int(round(math.log(freq/self.freq0, self.base)))]
    
  #create a dictionary for json output
  @classmethod
  def instances_to_dict(cls):
    col={"name": "scnl_data", "scnls": []}
    for scnl in Scnl.instances:
      col["scnls"].append({"sta": scnl.sta, "chan": scnl.chan, "net": scnl.net, 
           "loc": scnl.loc, "lat": scnl.lat, "lon": scnl.lon})
    return col
      
      
  @classmethod
  def write_json_to_file(cls, path):
    dic=cls.instances_to_dict()
    with open(path, 'w') as outfile:
      json.dump(dic, outfile, indent=4)
  

       
      