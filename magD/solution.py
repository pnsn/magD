class Solution:
    '''Class for solutions.

    Solutions are the contributing objects (scnl, city, event) and are
    refereced by an origin (source) value can be (distance or magnitude)
        Atributes:
            obj: magD object (event, city, scnl)
            value: value of the oject (distance or mag)
    '''
    def __init__(self, obj, value):
        self.obj = obj
        self.value = value
