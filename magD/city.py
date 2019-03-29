from .location import Location

'''
Class for cities, earthquakes...
'''


class City(Location):
    def __init__(self, name, lat, lon):
        self.lat = lat
        self.lon = lon
        self.name = name
