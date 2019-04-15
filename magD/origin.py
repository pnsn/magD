'''
Class for MagD origins
Instancea are points in a grid and have
lat, lon and asc list of sorted detectable values of mag or distance
from station or event. Origins make up elements of matrix

'''


class Origin:
    # collection = []
    # solutions is list of tuples (Mw, scnl)
    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon
        self.dist_solutions = []
        self.mag_solutions = []

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

    def sort_and_truncate_solutions(self, num_solutions):
        '''sort then keep only first num_solutions'''
        # print(", before: " + str(len(self.mag_solutions)), end='')
        self.dist_solutions.sort(key=lambda x: x.value)
        self.dist_solutions = self.dist_solutions[0:num_solutions]
        self.mag_solutions.sort(key=lambda x: x.value)
        self.mag_solutions = self.mag_solutions[0:num_solutions]
        # print("after: " + str(len(self.mag_solutions)), end='')

    def increment_solutions(self, num_stas, type):
        '''increment how many times a scnl was used as part of a solution'''
        solutions = self.mag_solutions
        # print(len(solutions))
        if type == 'distance':
            solutions = self.dist_solutions
        for solution in solutions:
            solution.obj.contrib_solutions += 1
            # print(solution.obj.sta, end='')
            # print("=" + str(solution.obj.contrib_solutions))
