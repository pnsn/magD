import numpy as np
import math
import copy
import pandas as pd
from .pickle import get_grid_path, set_pickle, get_noise_path, get_pickle
from .seis import focal_distance, trigger_time, find_distance, azimuthal_gap, \
    fault_radius, moment, moment_magnitude, signal_adjusted_frequency, \
    geometric_spreading, amplitude, attenuation, amplitude_power_conversion, \
    min_detect
from .origin import Origin
from .iris import get_noise_pdf
from .solution import Solution
from .city import City
from .event import Event
from .scnl import Scnl


class MagD:
    '''Creates object plotting seismic station metrics

        MagD creates an object than can be pickled
        and saved to local file system. The object not only describes a grid
        to contour but also describes the data used for each solution in the
        grid, station, magnitude, and map attributes such as icon and color
    '''

    def __init__(self, type, name, resolution, lat_min, lat_max, lon_min,
                 lon_max, num_solutions, pickle_root, nyquist_correction=None,
                 mu=None, qconst=None, beta=None, save_mag_curve=False
                 ):
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
        self.origins = []
        self.firstn_solutions = []
        self.save_mag_curve = save_mag_curve

    def build_origins(self):
        for lat in self.lat_list():
            for lon in self.lon_list():
                self.origins.append(Origin(lat, lon))

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

    def transform_to_blindzone(self, velocity_p, velocity_s, depth):
        '''Calculate blindzone radius for each origin

            calc blindzone distances in km
            which is just uses pythagoreon theorem:
                Xbz=((focal_distance*vs/vp)^2 -depth^2)^1/2
        '''
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

    def transform_to_trigger_time(self, velocity_p, processing_time, depth):
        '''For each origin in grid (event at depth), calculate how long it

        takes for p-wave to reach 4th station
        Input: distance matrix
        output: time(s) matrix
        '''
        m = self.matrix
        for r in range(len(m)):
            for c in range(len(m[r])):
                epi_distance = m[r][c]
                tt = trigger_time(epi_distance, velocity_p, processing_time,
                                  depth)
                m[r][c] = tt

    def transform_to_s_travel_time(self, velocity_s, depth):
        '''For all origins use matrix, which is epi-distance from event

        and calculate s-arrival to that origin. Will be concentric circles
        around event.
        Input: Distance matrix
        Output: Time(s) matrix
        '''
        m = self.matrix
        for r in range(len(m)):
            for c in range(len(m[r])):
                epi_distance = m[r][c]
                fd = focal_distance(epi_distance, depth)
                m[r][c] = fd / velocity_s

    def transform_to_azmuthul_gap(self):
        '''transform the matrix to AZ gap but iterating though each origin

        Considers only channels that are part of solution
        '''
        m = self.matrix
        for r in range(len(m)):
            for c in range(len(m[r])):
                # find the origin index associated with this element
                origin = self.origins[(r * c) + c]
                scnls = [solution.obj for solution in origin.solutions]
                # we don't give a crap about distance or mag
                # i.e. that value at m[r][c] just clobber with az gap
                m[r][c] = azimuthal_gap(scnls, origin)

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

    def build_matrix(self):
        '''create and pickle map_grids'''
        if self.type == 'detection':
            self.get_noise()
            self.profile_noise()
            detection_vector = self.build_detection_vector()
            self.make_matrix(detection_vector)

        # evaluate spatially
        else:
            self.profile_spatially()
        if self.type == 'gap':
            self.make_matrix(self.build_gap_vector())
        else:  # distance
            distance_matrix = self.build_distance_matrix()
            if self.type == 'dist_min':
                self.make_matrix([np.min(row) for row in distance_matrix])
            elif self.type == 'dist_med':
                self.make_matrix([np.median(row) for row in distance_matrix])
            elif self.type == 'dist_ave':
                self.make_matrix([np.average(row) for row in distance_matrix])
            elif self.type == 'dist_max':
                self.make_matrix([np.max(row) for row in distance_matrix])

    def build_markers(self, data_srcs):
        '''read all marker data (stations or event) in from csv

          accepts a dict of created from config file:
            data_src ={
                        'name':{
                             'csv_path': path/relative/to/approot,
                             'starttime': startime of pdf query, (optional)
                             'endtime:' endtime of pdf query, (optional)
                             'color': marker color,
                             'label': marker label,
                             'symbol': marker symbol,
                             'size': marker size,
                             'unit': unit of measurement
                             'template_sta': proxy_sta,
                             'template_chan': proxy_chan,
                             'template_net': proxy_net,
                             'template_loc': proxy_loc
                        }

                    }


            create a marker structure:
            self.markers = {
                'config1_name':
                    'color': marker_color,
                    'size': marker_size,
                    'label': marker_label,
                    'symbol': marker_symbol
                    'starttime': start of pdf (optional)
                    'endtime': end of pdf (optional)
                    'collection': [mkr_obj1, mkr_obj2,..., mkr_objn]
            }
         '''

        for key in data_srcs:
            src = data_srcs[key]
            path = src['csv_path']
            # stub out marker dict
            self.markers[key] = {}
            self.markers[key]['collection'] = []
            self.markers[key]['color'] = src['color']
            self.markers[key]['symbol'] = src['symbol']
            self.markers[key]['label'] = src['label']
            self.markers[key]['size'] = src['size']
            if 'unit' in src:
                self.markers[key]['unit'] = src['unit']
            if 'starttime' in src and 'endtime' in src:
                self.markers[key]['starttime'] = src['starttime']
                self.markers[key]['endtime'] = src['endtime']

            if src['klass'] == 'event':
                df_event = pd.read_csv(path)
                # instantiate dests

                for i, row in df_event.iterrows():
                    event = Event(row.name, row.lat, row.lon, row.depth,
                                  row.mag)
                    self.markers[key]['collection'].append(event)

            if src['klass'] == 'city':
                df_city = pd.read_csv(path)
                # instantiate dests
                for i, row in df_city.iterrows():
                    city = City(row.name, row.lat, row.lon)
                    self.markers[key]['collection'].append(city)

            if src['klass'] == 'scnl':
                df_stas = pd.read_csv(path, converters={
                                      'location': lambda x: str(x)})
                # instantiate dests
                proxy_scnl = None
                if "template_sta" in src:
                    proxy_scnl = Scnl(src['template_sta'],
                                      src['template_chan'],
                                      src['template_net'],
                                      src['template_loc'])
                for i, row in df_stas.iterrows():
                    if len(row.location) == 0:
                        row.location = "--"
                    if not hasattr(row, 'depth'):
                        row.depth = 0
                    scnl = Scnl(row.sta, row.chan, row.net, row.location,
                                row.rate, row.lat, row.lon, row.depth, key,
                                proxy_scnl)

                    self.markers[key]['collection'].append(scnl)

    def build_detection_vector(self):
        '''find all sorted origins at index self.num_solutions -1'''
        detections = []
        index = self.num_solutions - 1
        for o in self.origins:
            detections.append(o.solutions[index].value)
        return np.array(detections)

    def build_distance_matrix(self):
        '''Add all distances to stas that contributed to solution

            considers only stations that are part of the num_solutions
            solution returns distance matrix (2dim np array)
            with the distances of all stations to the origin to allow for
            min/med/ave/max distance matrices
        '''
        distances = []
        for o in self.origins:
            dists = []
            for solution in o.solutions[0:self.num_solutions]:
                if solution.value is None:
                    rad, d = find_distance(o, solution.obj)
                    solution.value = d
                dists.append(solution.value)
            dists.sort()
            distances.append(dists)
        return np.array(distances)

    def build_gap_vector(self):
        '''Return 1 dim array of azimuthal gaps using distance solutions '''
        gaps = []
        for o in self.origins:
            scnls = [d.obj for d in o.solutions[0:self.num_solutions]]
            max_gap = azimuthal_gap(scnls, o)
            gaps.append(max_gap)
        return np.array(gaps)

    def get_noise(self):
        '''retrieve all noise pdfs and pickle

            if pickled pdf exists, intantiate it
        '''
        for key in self.markers:
            marker_set = self.markers[key]
            starttime = marker_set['starttime']
            endtime = marker_set['endtime']
            for scnl in marker_set['collection']:
                s = scnl
                if scnl.proxy_scnl is not None:
                    s = scnl.proxy_scnl
                sta = s.sta
                chan = s.chan
                net = s.net
                loc = s.loc
                # try to load noise from pickle file, if not there go to iris
                try:
                    root_path = self.pickle_root
                    pickle_path = get_noise_path(root_path, "noise", sta, chan,
                                                 net, loc, starttime, endtime)
                    data = get_pickle(pickle_path)
                    scnl.set_powers(data)
                except FileNotFoundError:
                    resp = get_noise_pdf(sta, chan, net, loc, starttime,
                                         endtime)
                    if resp['code'] == 200:
                        set_pickle(pickle_path, resp['data'])
                        scnl.set_powers(resp['data'])
                    else:  # remove from collections
                        self.print_noise_not_found(sta, chan, loc, net,
                                                   starttime, endtime,
                                                   resp['code'])
                        scnl.powers = None
            # remove markers with no power
            pre_len = len(self.markers[key]['collection'])
            self.markers[key]['collection'] = \
                [s for s in self.markers[key]['collection']
                    if s.powers is not None]
            post_len = len(self.markers[key]['collection'])
            if pre_len != post_len:
                print("{} channel(s) found without noise pdf"
                      .format(pre_len - post_len))

    def print_noise_not_found(self, sta, chan, loc, net,
                              startime, endtime, code):
        '''message for noise pdf not found'''
        print("{}:{}:{}:{} startime: {}, endtime {} returned HTTP code {}"
              .format(sta, chan, loc, net, startime, endtime, code))

    def profile_noise(self):
        '''Walk the grid.

            For each point on map, find smallest detectable
            earthquake for every station. Sort stations low mag to high mag at
            end. Then use index of array as num solutions. For example if
            num_solutions =5 then use index 4 for the lowest mag detectable
            at this point.
        '''
        print('Profiling by noise...')
        lat = None
        for origin in self.origins:
            if lat != origin.lat or lat is None:
                lat = origin.lat
                # rounding needed since float percision is off
                if round(lat % 1.0, 1) == 0.0:
                    print(str(lat) + ", ", end="")
            # for every scnl
            for key in self.markers:
                for scnl in self.markers[key]['collection']:
                    if scnl.powers is None:
                        continue
                    if len(scnl.powers) > 0:
                        start_period = 0.001
                        end_period = 280
                        # Goes through all the freqs, i.e. from small to large
                        # Mw this way the first detection will be the min Mw
                        period = start_period
                        # Calculate distance between earthquake and station
                        delta_rad, delta_km = find_distance(origin, scnl)  # km
                        # for each period
                        while period <= end_period:
                            fc = 1 / period
                            fault_rad = fault_radius(fc, self.beta)
                            Mo = moment(fault_rad)
                            Mw = round(moment_magnitude(Mo), 2)
                            filtfc = signal_adjusted_frequency(Mw, delta_rad)
                            nyquist = scnl.samprate * self.nyquist_correction

                            if filtfc >= nyquist:
                                filtfc = nyquist

                            As = amplitude(fc, Mo, self.cn(), delta_km, filtfc)
                            As *= geometric_spreading(delta_km)
                            # q value
                            q = self.qconst * math.pow(nyquist, 0.35)
                            As *= attenuation(delta_km, q, self.beta, filtfc)

                            # Pwave amp is 10 times smaller than S
                            # correction for matching brune scaling to PSD
                            # calculation normalization
                            As /= 6.0
                            db = amplitude_power_conversion(As)
                            # used to plot a specific PDF with mag_curves
                            # we only need a small samples so use mod to filter
                            # on 0.5 mag and deg
                            # print(delta_km)
                            if self.save_mag_curve:

                                # deg = round(delta_rad * (180 / math.pi), 1)

                                Mw = round(Mw, 1)
                                km = round(delta_km)
                                if km % 10 == 0 and Mw % 0.5 == 0:
                                    # use fc instead of instrument corrected
                                    # freq
                                    origin.append_to_mag_curve(Mw, fc, db, km)
                                if Mw > 3.0:  # we don't need to go beyond this
                                    origin.solutions.append(Solution(scnl, Mw))
                                    break
                            else:
                                detection = min_detect(scnl, db, Mw, filtfc)
                                if(detection):
                                    origin.solutions.append(Solution(scnl, Mw))
                                    break

                            period = period * (2 ** 0.125)
            # since we are considering detection, sort by mag asc
            origin.sort_and_truncate_solutions(self.num_solutions)
        print("Feel the noise!")

    def profile_spatially(self):
        '''profile all origin solutions by distance to origin.

        Does NOT consider site characteristics such as noise.
        '''
        print('Profiling spatially...')
        lat = None
        print("lat: ", end="")
        for origin in self.origins:
            if lat != origin.lat or lat is None:
                lat = origin.lat
                # rounding needed since float percision is off
                if round(lat % 1.0, 1) == 0.0:
                    print(str(lat) + ", ", end="")
            for key in self.markers:
                for d in self.markers[key]['collection']:
                    delta_rad, delta_km = find_distance(origin, d)  # km
                    origin.append_to_solutions(Solution(d, delta_km))
            if len(origin.solutions) > 1:  # case for event object
                origin.sort_and_truncate_solutions(self.num_solutions)
        # if this is a single point, keep the first n solutions
        # for better plotting
        if len(self.origins) == 1:
            self.firstn_solutions = origin.solutions

    def productive_scnls(self, num=None, type='magnitude'):
        '''iterate through all origins and increment each solution's object'''
        origins = self.origins
        # make a list of all scnls
        scnls = []
        for key in self.markers:
            for obj in self.markers[key]['collection']:
                if hasattr(obj, 'sta'):
                    # zero it out
                    obj.contrib_solutions = 0
                    scnls.append(obj)

        # increment each scnl that took part in a solution

        for o in origins:
            o.increment_solutions(self.num_solutions)

        scnls.sort(key=lambda x: x.contrib_solutions, reverse=True)
        return scnls[0:num]
