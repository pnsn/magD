'''class for scnls'''
import math
class Scnl:
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
      # print(freq, self.freq0, self.base, self.powers)
      return self.powers[int(round(math.log(freq/self.freq0, self.base)))]

         
        