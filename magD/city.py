from .location import Location


class City(Location):
    '''Class for city

        Attributes:
            lat: (float) latitude of station
            lon: (float) longitude of station
            name: (string) name of event

    '''
    def __init__(self, name, lat, lon):
        self.lat = lat
        self.lon = lon
        self.name = name
