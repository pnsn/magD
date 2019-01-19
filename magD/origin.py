'''
Class for MagD origins
Instanced are points in a grid and have
lat, lon and asc list of sorted detectable magnitudes

'''
import numpy as np


class Origin:
    # collection = []
    # solutions is list of tuples (Mw, scnl)
    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon
        self.solutions = []

    #We want to put setters on these for testing

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, value):
        self._lat = value

    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, value):
        self._lon = value


    '''
        Use index of list to pull out min magnitude detection
        Assumes list is sorted
    '''

    def min_detection(self, num_stas):
        return self.solutions[num_stas - 1].min_mag


    def slice_detections(self, num_stas):
        return [x[1].sta for x in self.solutions][0:num_stas]

    def add_to_collection(self, solution):
        self.solutions.append(solution)

    '''
      clear collection. Jupyter seems to hang on to them between runs
    '''
    # @classmethod
    # def clear_collection(self):
    #     self.collection = []

    '''
        Go through each origin and tally up each station that contributed
        to a solution. Only go to the index < num_stas since we are only want stations
        that are part of {num_stas} solution.
    '''
    def increment_solutions(self,num_stas):
        i=0
        for solution in o.solutions:
            if i < num_stas:
                solution.scnl.contrib_solutions+=1
                i+=1
