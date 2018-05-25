'''
Class for MagD grid
These are saved as a pickled file

'''
import numpy as np
'''
    init:
     name = name of run
     type = type of product (detection, gap, distance)
     numrows = number of rows in matrix
     numcols = number of cols in matrix
     res = resultion of grid in degrees
'''

class MapGrid:
    def __init__(self, name, type, numrows, numcols, resolution):
        self.name = name
        self.type = type
        self.numrows = numrows
        self.numcols = numcols
        self.resolution=resolution
        self.matrix = []

    #return the dimensions of matrix
    def dimension(self):
        return(self.dimrow, self.dimcol)

    def make_matrix(self, vector):
        z = np.asarray(vector);
        self.matrix = np.reshape(z, (self.numrows, self.numcols))






    # #combine both gap and distance
    # def make_gap_distance_vector(self, vector):
    #     #from Paul Bodin
    #     #0.5*[(gap - gap/n)/360] + log(d)/3]
    #     scored_vector=[]
    #     for tup in vector:
    #         gap=tup[0]
    #         distance=tup[1]
    #         gap=(gap-gap/self.num_detections)/360
    #         print(distance)
    #         score=0.5*(gap + math.log(distance)/3)
    #         print(math.log(distance))
    #         scored_vector.append(score)
    #     return scored_vector
