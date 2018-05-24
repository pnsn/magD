'''
Class for events. Used to display real or test event data

'''

class Event:
  collection = []
  def __init__(self, lat, mag, color, symbol):
      self.lat = lat
      self.lon = lon
      self.mag = mag
      self.color = color
      self.symbol = symbol
      Event.collection.append(self)
