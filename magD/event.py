'''
Class for earthquakes...
'''
class Event:
    def __init__(self, name, lat, lon, depth, mag, color, symbol, label, size):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.depth = depth
        self.mag = mag
        self.color = color
        self.symbol = symbol
        self.label = label
        self.size = size
