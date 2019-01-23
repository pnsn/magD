'''
MapGrid is a matrix for contouring with other attributes.
It is instantiated with a conf file, and a 'type'
conf file is of form:

These are saved as a pickled file

'''
import numpy as np
import copy
from .pickle import *
from .seis import *


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
        self.pickle_root = conf['pickle_root']
        self.matrix = []
        self.destinations = []


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

    '''
        Take distance matrix
        calc blindzone distances in km
        which is just uses pythagoreon theorem:
            Xbz=((focal_distance*vs/vp)^2 -depth^2)^1/2
    '''
    def transform_to_blindzone(self, velocity_p, velocity_s, depth):
        m =self.matrix
        for r in range(len(m)):
            for c in range(len(m[r])):
                epi_distance= m[r][c]
                fd = focal_distance(epi_distance, depth)
                vd2 = math.pow((velocity_s/velocity_p)*fd, 2)
                d2 = math.pow(depth, 2)
                if vd2 -d2 < 0: #no imaginary numbers
                    m[r][c]= 0
                else:
                    m[r][c] =math.sqrt(vd2 -d2)


    '''
    Time to trigger. For every origin calculate the time to trigger
    using the distance matrix. Calculate distance to focus convert to time using
    p velocity then add processing time
    '''
    def transform_to_trigger_time(self, velocity_p, processing_time, depth):
        m =self.matrix
        for r in range(len(m)):
            for c in range(len(m[r])):
                epi_distance= m[r][c]
                tt=trigger_time(epi_distance, velocity_p, processing_time, depth)
                m[r][c] = tt

    '''
    Same as trigger time but subtract from s arrival to determine alert time.
    Transform form distance matrix
    '''
    def transform_to_s_travel_time(self, velocity_s, depth):
        m =self.matrix
        for r in range(len(m)):
            for c in range(len(m[r])):
                epi_distance= m[r][c]
                fd = focal_distance(epi_distance, depth)
                m[r][c] = fd/velocity_s


    # make deep copy, must pass in type
    def copy(self, type, name=None):
        c= copy.deepcopy(self)
        c.type = type
        if name:
            c.name = name
        else:
            c.name = type
        return c

    def get_path(self):
        return get_grid_path(self.pickle_root, self.type, self.name,
                self.numrows(), self.numcols(), self.resolution)

    '''pickle to object'''
    def save(self):
        set_pickle(self.get_path(), self)
