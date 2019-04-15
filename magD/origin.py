'''
Class for MagD origins

Instances are each evaluated point in the grid:
attrs:
    lat: float
    lon: float
    solutions: list of solutions for origin. There will be one element for
    each station evaluated. List can then be sorted and truncated.
    For example, if MagD is using a 4 station solution, for either distance or
    mag, sort asc, then truncate [:4] The 4th element will be the lowest
    detection/distance in a four station solution

'''


class Origin:
    def __init__(self, lat, lon, solutions=[]):
        self._lat = lat
        self._lon = lon
        self.solutions = solutions

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

    def add_to_solutions(self, solution):
        self.solutions.append(solution)

    def sort_and_truncate_solutions(self, num_solutions):
        '''sort then keep only first num_solutions'''
        self.solutions.sort(key=lambda s: s.value)
        self.solutions = self.solutions[0:num_solutions]

    def increment_solutions(self, num_stas):
        '''increment the solutions object

            For reporting a scnls productivity
        '''

        for solution in self.solutions:
            solution.obj.contrib_solutions += 1
