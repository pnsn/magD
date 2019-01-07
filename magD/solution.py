'''
Class for solutions. Solutions are the contributing stations to an origin or scnl
and have a scnl object, distance (m), and min_mag

'''

class Solution:
    def __init__(self, scnl, min_mag=None, distance=None):
      self.scnl=scnl
      self.min_mag=min_mag
      self.distance=distance

    @classmethod
    def sort_by_mag(cls, collection):
        collection.sort(key=lambda s: s.min_mag)

    @classmethod
    def sort_by_distance(cls, collection):
        collection.sort(key=lambda s: s.distance)
