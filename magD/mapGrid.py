'''
MapGrid is a matrix for contouring with other attributes.
It is instantiated with a conf file, and a 'type'
conf file is of form:

These are saved as a pickled file

'''
import numpy as np
import math
import copy
from .pickle import get_grid_path, set_pickle
from .seis import focal_distance, trigger_time

'''
    init:

'''


class MapGrid:

    def __init__(self, type, name, resolution, lat_min, lat_max, lon_min,
                 lon_max, num_solutions, nyquist_correction, mu, qconst, beta,
                 pickle_root):
        self.type = type
        self.name = name
        self.resolution = resolution
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.num_solutions = num_solutions
        self.nyquist_correction = nyquist_correction
        self.mu = mu
        self.qconst = qconst
        self.beta = beta
        self.pickle_root = pickle_root
        self.matrix = []
        self.markers = {}
        self.firstn_solutions = []

    def append_to_solutions(self, list):
        self.firstn_solutions = list

    def lat_list(self):
        '''list of lats from min, max in steps of grid_resolution'''
        # single point case e.g. eq
        if self.lat_min == self.lat_max:
            return [self.lat_min]
        return np.arange(self.lat_min, self.lat_max, self.resolution)

    def lon_list(self):
        '''list of lons from min, max in steps of grid_resolution'''
        # single point case e.g. eq
        if self.lon_min == self.lon_max:
            return [self.lon_min]
        return np.arange(self.lon_min, self.lon_max, self.resolution)

    def cn(self):
        '''Can't rembember what the f' cn is but it seems important'''
        return 1 / (4 * self.mu * self.beta * 1e7)

    def numrows(self):
        return len(self.lat_list())

    def numcols(self):
        return len(self.lon_list())

    # return the dimensions of matrix
    def dimension(self):
        return(self.numrows(), self.numcols())

    # reshape to 2dim list
    def make_matrix(self, z):
        self.matrix = np.reshape(z, (self.numrows(), self.numcols()))

    def min(self):
        np.min(self.matrix)

    def max(self):
        np.max(self.matrix)

    '''
        Take distance matrix
        calc blindzone distances in km
        which is just uses pythagoreon theorem:
            Xbz=((focal_distance*vs/vp)^2 -depth^2)^1/2
    '''
    def transform_to_blindzone(self, velocity_p, velocity_s, depth):
        m = self.matrix
        for r in range(len(m)):
            for c in range(len(m[r])):
                epi_distance = m[r][c]
                fd = focal_distance(epi_distance, depth)
                vd2 = math.pow((velocity_s / velocity_p) * fd, 2)
                d2 = math.pow(depth, 2)
                if vd2 - d2 < 0:  # no imaginary numbers
                    m[r][c] = 0
                else:
                    m[r][c] = math.sqrt(vd2 - d2)

    '''Time to trigger.

    For every origin calculate the time to trigger using the distance matrix.
    Calculate distance to focus convert to time using p velocity then add
    processing time
    '''
    def transform_to_trigger_time(self, velocity_p, processing_time, depth):
        m = self.matrix
        for r in range(len(m)):
            for c in range(len(m[r])):
                epi_distance = m[r][c]
                tt = trigger_time(epi_distance, velocity_p, processing_time,
                                  depth)
                m[r][c] = tt

    def transform_to_s_travel_time(self, velocity_s, depth):
        '''
        Same as trigger time but subtract from s arrival to determine

        alert time. Transform form distance matrix '''
        m = self.matrix
        for r in range(len(m)):
            for c in range(len(m[r])):
                epi_distance = m[r][c]
                fd = focal_distance(epi_distance, depth)
                m[r][c] = fd / velocity_s

    def copy(self, type, name=None):
        '''pass in name and type. type is pickle folder, type is filename

            If name is None, name = type
        '''
        c = copy.deepcopy(self)
        c.type = type
        if name:
            c.name = name
        else:
            c.name = type
        return c

    # full path to pickle path
    def get_path(self):
        return get_grid_path(self.pickle_root, self.type, self.name,
                             self.numrows(), self.numcols(), self.resolution)
    '''pickle to object'''
    def save(self):
        set_pickle(self.get_path(), self)
