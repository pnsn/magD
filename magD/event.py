'''
Class for earthquakes...
'''

from .location import Location


class Event(Location):
    def __init__(self, name, lat, lon, depth, mag):
        self.lat = lat
        self.lon = lon
        self.name = name
        self.depth = depth
        self.mag = mag
