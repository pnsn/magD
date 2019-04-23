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
    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon
        self.solutions = []
        self.mag_curve = {}

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

    def append_to_mag_curve(self, mag, fc, pow, km):
        '''to plot mag curves on pdf

           create a stucture keyed on deg
           {
            mag: {
                    period: float,
                    pow: float
                }
           }
        '''
        if km not in self.mag_curve:
            self.mag_curve[km] = {}
        self.mag_curve[km][mag] = {}
        self.mag_curve[km][mag]['period'] = 1 / fc
        self.mag_curve[km][mag]['pow'] = pow

    def append_to_solutions(self, solution):
        self.solutions.append(solution)

    def sort_and_truncate_solutions(self, num_solutions):
        '''sort then keep only first num_solutions

            first ensure unique data sets, e.g. we don't
            want to use both instruments in a 6 channel station
            when duplicates exist, remove larger value
        '''
        self.solutions.sort(key=lambda s: s.value)
        # print([x.value for x in self.solutions])
        uniq_list = [self.solutions[0]]
        for s in self.solutions:
            found = False
            for u in uniq_list:
                if s.obj.sta == u.obj.sta:
                    found = True
            if not found:
                uniq_list.append(s)
        # print([x.value for x in uniq_list])
        self.solutions = uniq_list[0:num_solutions]

    def increment_solutions(self, num_stas):
        '''increment the solutions object

            For reporting a scnls productivity
        '''

        for solution in self.solutions:
            solution.obj.contrib_solutions += 1
