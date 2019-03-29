'''
Class to manage running a single magD process, which can have many outputs.
The class excepts a list of instatiated MapGrid objects:
    If detection map is needed, detection MUST be the first grid object,
     so that all other grids use results from detection analysis.
    [MagGrid,...,MapGrid]

And a dictionary for data source:

    {
        'data1':{
            'csv_path': some/path (string),
            'starttime': YYYY-mm-dd (string),
            'endtime': YYYY-mm-dd (string),
        },
        'data2':{
            'csv_path': some/path (string),
            'starttime': YYYY-mm-dd (string),
            'endtime': YYYY-mm-dd (string),
            #optional keys for templating
            'template_sta': template_station (string),
            'template_chan': template_channel (string),
            'template_net': template_network (string),
            'template_loc': template_loc (string)

        }
    }
    An list to output summary is also instatiated on init.

    For noise, A PDF is first looked for in the pickle_directory, configurable
    on the client github.com/pnsn/magd_client. If not found, process will
    retrieve from IRIS and then pickle.

    MagD outputs grid(s) MapGrid and pickles for
'''


import math
import pandas as pd
import numpy as np
import json
import csv
import re

from .origin import Origin
from .scnl import Scnl
from .seis import find_distance, azimuthal_gap, fault_radius, moment, \
    moment_magnitude, signal_adjusted_frequency, geometric_spreading, \
    amplitude, attenuation, amplitude_power_conversion, min_detect
from .iris import get_noise_pdf
from .pickle import get_noise_path, get_pickle, set_pickle
from .solution import Solution
from .city import City
from .event import Event


class MagD:
    '''intatiate a run'''
    def __init__(self, grids, data_srcs):
        self.grids = grids
        self.data_srcs = data_srcs
        self.origins = []
        self.markers = {}
        self.summary_mag_list = []

    '''
        return 1dim list of mag levels used for heat map
        simply find the nth element of sorted Solutions
        where n is the number of stations required
        so if n = 4, find the fourth largest magnitude
    '''
    def build_detection_vector(self):
        detections = []
        index = self.grids[0].num_solutions - 1
        for o in self.origins:
            detections.append(o.mag_solutions[index].value)
        return np.array(detections)

    ''' Add all distances to stas that contributed to solution
        considers only stations that are part of the num_solutions
        solution returns distance matrix (2dim np array)
        with the distances of all stations to the origin to allow for
        min/med/ave/max distance matrices
    '''

    def build_distance_matrix(self):
        grid = self.grids[0]
        distances = []
        for o in self.origins:
            dists = []
            for solution in o.dist_solutions[0:grid.num_solutions]:
                if solution.value is None:
                    rad, d = find_distance(o, solution.obj)
                    solution.value = d
                dists.append(solution.value)
            dists.sort()
            distances.append(dists)
        return np.array(distances)

    '''
        Return 1 dim array of azimuthal gaps using distance solutions
    '''
    def build_gap_vector(self):
        grid = self.grids[0]
        gaps = []
        for o in self.origins:
            scnls = [d.obj for d in o.dist_solutions[0:grid.num_solutions]]
            max_gap = azimuthal_gap(scnls, o)
            gaps.append(max_gap)
        return np.array(gaps)

    # message for noise pdf not found
    def print_noise_not_found(self, sta, chan, loc, net,
                              startime, endtime, code):
        print("{}:{}:{}:{} startime: {}, endtime {} returned HTTP code {}"
              .format(sta, chan, loc, net, startime, endtime, code))

    # create and pickle all map_grids
    def build_grids(self):
        detection_vector = None
        for grid in self.grids:
            if grid.type == 'detection':
                self.get_noise()
                self.profile_noise()
                detection_vector = self.build_detection_vector()
                break

        # evaluate spatially
        if detection_vector is None:
            self.profile_spatially()
        # distance and gap grids can't be built until it is determined whether
        # stations are prioritized by detection or just spatially
        for grid in self.grids:
            if re.match("^dist", grid.type) is not None:
                distance_matrix = self.build_distance_matrix()
                break

        for grid in self.grids:
            if grid.type == 'gap':
                grid.make_matrix(self.build_gap_vector())
            elif grid.type == 'dist_min':
                grid.make_matrix([np.min(row) for row in distance_matrix])
            elif grid.type == 'dist_med':
                grid.make_matrix([np.median(row) for row in distance_matrix])
            elif grid.type == 'dist_ave':
                grid.make_matrix([np.average(row) for row in distance_matrix])
            elif grid.type == 'dist_max':
                grid.make_matrix([np.max(row) for row in distance_matrix])
            elif grid.type == 'detection':
                grid.make_matrix(detection_vector)
            grid.markers = self.markers
            grid.save()
        return self.grids

    def read_markers(self):
        '''read all marker data (stations or location) in from csv

            create a marker structure:
            self.markers = {
                'config1_name':
                    'color': marker_color,
                    'size': marker_size,
                    'label': marker_label,
                    'symbol': marker_symbol
                    'collection': [mkr_obj1, mkr_obj2,..., mkr_objn]
            }
         '''

        for key in self.data_srcs:
            path = self.data_srcs[key]['csv_path']
            # stub out marker dict
            self.markers[key] = {}
            self.markers[key]['collection'] = []
            self.markers[key]['color'] = self.data_srcs[key]['color']
            self.markers[key]['symbol'] = self.data_srcs[key]['symbol']
            self.markers[key]['label'] = self.data_srcs[key]['label']
            self.markers[key]['size'] = self.data_srcs[key]['size']
            if self.data_srcs[key]['klass'] == 'event':
                df_event = pd.read_csv(path)
                # instantiate dests

                for i, row in df_event.iterrows():
                    event = Event(row.name, row.lat, row.lon, row.depth,
                                  row.mag)
                    self.markers[key]['collection'].append(event)

            if self.data_srcs[key]['klass'] == 'city':
                df_city = pd.read_csv(path)
                # instantiate dests
                for i, row in df_city.iterrows():
                    city = City(row.name, row.lat, row.lon)
                    self.markers[key]['collection'].append(city)

            if self.data_srcs[key]['klass'] == 'scnl':
                df_stas = pd.read_csv(path, converters={
                                      'location': lambda x: str(x)})
                # instantiate dests
                for i, row in df_stas.iterrows():
                    if len(row.location) == 0:
                        row.location = "--"
                    if not hasattr(row, 'depth'):
                        row.depth = 0
                    scnl = Scnl(row.sta, row.chan, row.net, row.location,
                                row.rate, row.lat, row.lon, row.depth, key)

                    self.markers[key]['collection'].append(scnl)

    def get_noise(self):
        '''retrieve and pickle all pdfs

            if pickled pdf exists use it instead of querying iris
        '''
        for key in self.data_srcs:
            src = self.data_srcs[key]
            for scnl in self.markers[key]['collection']:
                starttime = src['starttime']
                endtime = src['endtime']
                if "template_sta" in src:
                    sta = src['template_sta']
                    chan = src['template_chan']
                    net = src['template_net']
                    loc = src['template_loc']
                else:
                    sta = scnl.sta
                    chan = scnl.chan
                    net = scnl.net
                    loc = scnl.loc
                # try to load noise from pickle file, if not there go to iris
                try:
                    root_path = self.grids[0].pickle_root
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
                    if s.powers is None]
            post_len = len(self.markers[key]['collection'])
            if pre_len != post_len:
                print("{} channel(s) found without noise pdf"
                      .format(pre_len - post_len))
    '''
        Walk the grid and for each point on map, find smallest detectable
        earthquake for each station. Sort stations low mag to high mag at end.
        Then use index of array as num solutions. For example if
        num_solutions =5 then use index 4 for the lowest mag detectable
        at this point.
    '''

    def make_origins(self):
        # find first, all have same attrs
        grid = self.grids[0]
        for lat in grid.lat_list():
            for lon in grid.lon_list():
                self.origins.append(Origin(lat, lon))

    def profile_noise(self):
        print('Profiling by noise...')
        grid = self.grids[0]
        lat = None
        print("lat:", end="")
        for origin in self.origins:
            if lat != origin.lat or lat is None:
                lat = origin.lat
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
                            fault_rad = fault_radius(fc, grid.beta)
                            Mo = moment(fault_rad)
                            Mw = round(moment_magnitude(Mo), 2)
                            filtfc = signal_adjusted_frequency(Mw, fc)
                            nyquist = scnl.samprate * grid.nyquist_correction

                            if filtfc >= nyquist:
                                filtfc = nyquist

                            As = amplitude(fc, Mo, grid.cn(), delta_km, filtfc)
                            As *= geometric_spreading(delta_km)
                            # q value
                            q = grid.qconst * math.pow(nyquist, 0.35)
                            As *= attenuation(delta_km, q, grid.beta, filtfc)

                            # Pwave amp is 10 times smaller than S
                            # correction for matching brune scaling to PSD
                            # calculation normalization
                            As /= 6.0
                            db = amplitude_power_conversion(As)

                            detection = min_detect(scnl, db, Mw, filtfc)
                            if(detection):
                                origin.add_to_mag_solutions(Solution(scnl, Mw,
                                                            'magnitude'))
                                origin.add_to_dist_solutions(Solution(scnl,
                                                             delta_km,
                                                             'distance'))
                                break

                            period = period * (2 ** 0.125)
            # since we are considering detection, sort by mag asc
            Solution.sort_by_value(origin.mag_solutions)
            Solution.sort_by_value(origin.dist_solutions)

    def profile_spatially(self):
        '''profile all origin solutions by distance to origin.

        Does NOT consider site characteristics such as noise.
        '''
        print('Profiling spatially...')
        lat = self.origins[0].lat
        for origin in self.origins:
            if lat != origin.lat and origin.lat % 2.0 == 0.0:
                lat = origin.lat
            # for every scnl
            for key in self.markers:
                for d in self.markers[key]['collection']:
                    delta_rad, delta_km = find_distance(origin, d)  # km
                    origin.add_to_dist_solutions(Solution(d, delta_km,
                                                          'distance'))
            Solution.sort_by_value(origin.dist_solutions)
        # if this is a single point, keep the first n solutions
        # for better plotting
        if len(self.origins) == 1:
            for g in self.grids:
                solutions = origin.dist_solutions[0:g.num_solutions]
                g.append_to_solutions(solutions)

    '''Summary output FIXME with new grid objects'''
    def print_summary(self, station_summary=False):
        summary = []
        for grid in self.grids:
            summary.append("%s min: %.2f" % (grid.type, min(grid.matrix)))
            summary.append("%s max: %.2f" % (grid.type, max(grid.matrix)))
            summary.append("%s mve: %.2f" % (grid.type,
                                             np.average(grid.matrix)))

        if station_summary:
            # not sure where calcs came from but defining it to make the
            # errors go away
            calcs = None
            summary.append("\nSolution Summary for %i calculations:" % calcs)
            summary.append("Sta   Chan Hits    Productivity")
            for key in self.markers:
                # print("Data set {}".format(key))
                for scnl in self.markers[key]['collection']:
                    # do some formating
                    if scnl.contrib_solutions == 0:
                        percent = "N/A"
                    else:
                        c = (scnl.contrib_solutions / calcs) * 100
                        percent = "%.2f%%" % c
                    sta = scnl.sta
                    while len(sta) < 4:
                        sta = sta + " "
                    sols = str(scnl.contrib_solutions)
                    while len(sols) < 6:
                        sols = " " + sols
                    summary.append("{}  {}  {}  {}".format(sta, scnl.chan,
                                                           sols, percent))
        return "\n".join(summary)

    '''Assumes sorted! Find the index  where Scnls did not contribute.
    Find where # of solutions ==0, everything to the right of that
    will be 0 if sorted
    '''

    def get_no_solution_index(self, key):
        i = 0
        for scnl in self.markers[key]['collection']:
            if scnl.contrib_solutions > 0:
                i += 1
                next
            else:
                break
        return i

    # write dict to json file
    def write_json_to_file(self, dict, path):
        with open(path, 'w') as outfile:
            json.dump(dict, outfile, indent=4)

    # write out to csv
    def write_to_csv(self, path, lats, lons, vals):
        i = 0
        with open(path, 'w') as csvfile:
            fieldnames = ['lat', 'lon', 'val']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for lat in lats:
                for lon in lons:
                    writer.writerow({'lat': lat, 'lon': lon, 'val': vals[i]})
                    i += 1
        print("done with csv and index = %i and length =%i" % (i, len(vals)))
