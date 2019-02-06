'''
Class for MagD origins
Instanced are points in a grid and have
lat, lon and asc list of sorted detectable values of mag or distance

'''
import numpy as np


class Origin:
    # collection = []
    # solutions is list of tuples (Mw, scnl)
    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon
        self.dist_solutions = []
        self.mag_solutions = []

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


    def add_to_mag_solutions(self, solution):
        self.mag_solutions.append(solution)

    def add_to_dist_solutions(self, solution):
        self.dist_solutions.append(solution)
    '''
        Go through each origin and tally up each station that contributed
        to a solution. Only go to the index < num_stas since we are only want stations
        that are part of {num_stas} solution.
        This is to keep stats on which stations are earning their keep
        !!!!FIXME: This hasn't been refactored since introducing generic objects rather
        than simply using scnl
    '''
    # def increment_solutions(self,num_stas):
    #     i=0
    #     for solution in self.solutions:
    #         if i < num_stas:
    #             solution.obj.contrib_solutions+=1
    #             i+=1
