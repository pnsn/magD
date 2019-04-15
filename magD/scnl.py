'''class for managing channel data (scnls)

'''
import math
from .location import Location


class Scnl(Location):
    def __init__(self, sta, chan, net, loc, samprate=None, lat=None, lon=None,
                 depth=None, data_set=None, inst_id=None, desc=None,
                 proxy_scnl=None):
        self.sta = sta
        self.chan = chan
        self.net = net
        self.loc = loc
        self.samprate = samprate
        self.lat = lat
        self.lon = lon
        self.depth = depth
        self.data_set = data_set
        self.inst_id = inst_id
        self.desc = desc
        # are we using another scnl as a proxy for noise
        self.proxy_scnl = proxy_scnl
        self.base = None
        self.freq0 = None
        self.df = None
        # FIXME: Power Should be a class?
        self.powers = []
        self.frequencies = []
        self.contrib_solutions = 0  # how many times sta contributed 2 solution

    # FIXME: this should be a class
    # Revist when refactoring using IRIS new webservice
    # that does stats on PDF
    def set_powers(self, noise):
        '''Accepts list of noise buckets, see iris.py for structure

            Finds mode( greatest # hits) to for each freq and use the power
            for that freq
        '''
        mode = float(noise[0].attrib["hits"])
        power = float(noise[0].attrib["power"])
        freq = float(noise[0].attrib["freq"])
        self.freq0 = freq
        for sample in noise:
            freq2 = float(sample.attrib["freq"])
            if freq2 == freq:
                if int(sample.attrib["hits"]) > mode:
                    mode = int(sample.attrib["hits"])
                    power = int(sample.attrib["power"])
            else:
                # we want freq1 to determine base
                if freq == self.freq0:
                    self.base = freq2 / self.freq0
                self.frequencies.append(freq)
                self.powers.append(power)
                freq = freq2
                mode = int(sample.attrib["hits"])
                power = int(sample.attrib["power"])

    # FIXME: This is dumb, use dict
    def frequency_power(self, freq):
        '''For frequency, what is the associated modal power?

            with pdf noise input set modes (power with > hits)
            freq0 and base are used to index the powers(list) for a
            O(1) lookup so freq? index= log(freq?/freq[0], freq[1]/freq[0])
            returns the index to power
        '''
        return self.powers[int(round(math.log(freq / self.freq0, self.base)))]

    def find_min_index(self, min):
        '''for min frequency, what is the index of power and frequecies '''
        index = 0
        for i, val in enumerate(self.frequencies):
            if val >= min:
                index = i
                break
        return index

    '''for max frequency, what is the index of power and frequecies
    non inclusive since array.slice stops after the last wanted value
    '''
    def find_max_index(self, max):
        index = 0
        for i, val in enumerate(self.frequencies):
            if val > max:
                index = i
                break
        return index

    @classmethod
    def sort_by_solutions(cls, collections):
        '''in place sort of scnl collections for station performance'''
        for key in collections:
            collections[key].sort(key=lambda x: x.contrib_solutions,
                                  reverse=True)
        return collections

    @classmethod
    def collections_to_dict(cls):
        '''create a dictionary for json output

            FIXME this needs to change to collections object
        '''
        col = {"name": "scnl_data", "scnls": []}
        for scnl in Scnl.collections:
            col["scnls"].append({"sta": scnl.sta, "chan": scnl.chan,
                                 "net": scnl.net, "loc": scnl.loc,
                                 "lat": scnl.lat, "lon": scnl.lon})
        return col

    @classmethod
    def add_to_collections(cls, obj):
        '''add scnl to collections keyed on data_set'''
        if obj.data_set in cls.collections:
            cls.collections[obj.data_set].append(obj)
        else:
            cls.collections[obj.data_set] = [obj]
