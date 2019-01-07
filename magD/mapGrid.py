'''
MapGrid is a matrix for contouring with other attributesself.
It is instantiated with a conf file, and a 'type'
conf file is of form:

These are saved as a pickled file

'''
import numpy as np
import copy
from .pickle import *


'''
    init:

'''

class MapGrid:
    def __init__(self, conf, type):
        self.type = type
        self.name = conf['name']
        self.resolution = float(conf['grid_resolution'])
        self.lat_min = float(conf['lat_min']) + self.resolution
        self.lat_max = float(conf['lat_max'])
        self.lon_min = float(conf['lon_min'])
        self.lon_max = float(conf['lon_max']) + self.resolution
        self.num_solutions = int(conf['num_solutions'])
        self.nyquist_correction = float(conf['nyquist_corretion'])
        self.mu = float(conf['mu'])
        self.qconst = float(conf['qconst'])
        self.beta = float(conf['beta'])
        self.pickle_path = conf['pickle_path']
        self.matrix = []
        self.scnls = []


    ''' list of lats from min, max in steps of grid_resolution'''
    def lat_list(self):
        return np.arange(self.lat_min, self.lat_max, self.resolution)

    ''' list of lons from min, max in steps of grid_resolution'''
    def lon_list(self):
        return np.arange(self.lon_min, self.lon_max, self.resolution)

    '''Can't rembember what the f' cn is but it seems important and scientific'''
    def cn(self):
        return 1/(4 * self.mu * self.beta * 1e7)

    def numrows(self):
        return len(self.lat_list())

    def numcols(self):
        return len(self.lon_list())

    #return the dimensions of matrix
    def dimension(self):
        return(self.numrows(), self.numcols())

    #reshape to 2dim list
    def make_matrix(self, z):
        self.matrix = np.reshape(z, (self.numrows(), self.numcols()))

    def min(self):
        np.min(self.matrix)

    def max(self):
        np.max(self.matrix)

    # make deep copy, must pass in type
    def copy(self, type, name=None):
        c= copy.deepcopy(self)
        c.type = type
        if name:
            c.name = name
        return c

    '''pickle to object'''
    def save(self):
        path = get_grid_path(self.pickle_path, self.type, self.name,
                self.numrows(), self.numcols(), self.resolution)
        set_pickle(path, self)
