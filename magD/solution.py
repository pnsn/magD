'''
Class for solutions. Solutions are the contributing objects (scnl, city, event)
and are refereced by an origin (source) value can be (distance or magnitude)
'''


class Solution:
    def __init__(self, obj, value):
        self.obj = obj
        self.value = value
