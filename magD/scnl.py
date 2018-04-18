'''class for managing channel data (scnls)

'''
import math
import pandas as pd

class Scnl:
  collections ={}
  def __init__(self,sta,chan,net,loc="",samprate=None,lat=None,lon=None,
                    depth=None,data_set=None, inst_id=None,desc=None):
      self.sta=sta
      self.chan=chan
      self.net=net
      self.loc=loc
      self.samprate=samprate
      self.lat=lat
      self.lon=lon
      self.depth=depth
      self.inst_id=inst_id
      self.desc=desc
      self.base=None
      self.freq0=None
      self.df=None
      self.powers = []
      self.frequencies = []
      self.solutions=0
      self.data_set=data_set
      Scnl.add_to_collections(self)



# #TODO make noise dataframe
#
#   '''create dataframe of noise from iris pdf xml
#      blow up frame by creating a line for each hit
#  '''
#   def make_noise_df(self, noise):
#     data=[]
#     for sample in noise:
#       for i in range(int(sample.attrib["hits"]))
#         data.append((float(sample.attrib["freq"]), float(sample.attrib["power"])))
#     self.df =pd.DataFrame(d, columns=('freq', 'power'))
# def make_scnl_dataframe(xml):


  '''Accepts list of noise buckets, see iris.py for structure
      Finds mode( greatest # hits) to for each freq and use the power
      for that freq
      '''
  def set_powers(self, noise):
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
          self.frequencies.append(freq)
          self.powers.append(power)
          freq = freq2
          mode = int(sample.attrib["hits"])
          power = int(sample.attrib["power"])

  '''For frequency, what is the associated modal power?
      with pdf noise input set modes (power with > hits)
      freq0 and base are used to index the powers(list) for a
      O(1) lookup so freq? index= log(freq?/freq[0], freq[1]/freq[0])
      returns the index to power
  '''
  def frequency_power(self, freq):
    return self.powers[int(round(math.log(freq/self.freq0, self.base)))]

  '''for min frequency, what is the index of power and frequecies '''
  def find_min_index(self,min):
    index=0
    for i, val in enumerate(self.frequencies):
      if val>=min:
        index=i
        break
    return index

  '''for max frequency, what is the index of power and frequecies
    non inclusive since array.slice stops after the last wanted value
    '''
  def find_max_index(self,max):
    index=0
    for i, val in enumerate(self.frequencies):
      if val>max:
        index=i
        break
    return index


  @classmethod
  #in place sort collections
  def sort_by_solutions(cls):
      for key in cls.collections:
          cls.collections[key].sort(key=lambda x: x.solutions, reverse=True)

  #create a dictionary for json output
  #FIXME this needs to change to collections object
  @classmethod
  def collections_to_dict(cls):
    col={"name": "scnl_data", "scnls": []}
    for scnl in Scnl.collections:
      col["scnls"].append({"sta": scnl.sta, "chan": scnl.chan, "net": scnl.net,
           "loc": scnl.loc, "lat": scnl.lat, "lon": scnl.lon})
    return col

  @classmethod
  #add scnl to collections keyed on data_set
  def add_to_collections(cls, obj):
     if obj.data_set in cls.collections:
         cls.collections[obj.data_set].append(obj)
     else:
         cls.collections[obj.data_set]=[obj]
