'''
Class for solutions. Solutions are the contributing objects (scnl, city)
and are refereced by an origin (source) value can be (distance or magnitude)
'''

class Solution:
    def __init__(self, obj, value, value_type):
      self.obj=obj
      self.value = value
      self.value_type = value_type

    @classmethod
    def sort_by_value(cls, collection):
        collection.sort(key=lambda s: s.value)
