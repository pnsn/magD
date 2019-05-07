from .location import Location


class Event(Location):
    '''Class for earthquakes

        Attributes:
            lat: (float) latitude of station
            lon: (float) longitude of station
            name: (string) name of event
            depth: (float) depth of station
            mag: (float) magnitude of event

    '''
    def __init__(self, name, lat, lon, depth, mag):
        self.lat = lat
        self.lon = lon
        self.name = name
        self.depth = depth
        self.mag = mag
