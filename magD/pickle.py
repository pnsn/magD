import pickle
import re
from pathlib import Path

'''Functions to manage pickling and unpickling of magD objects'''


def set_pickle(path, data):
    '''set pickle path of object if it doesn't exist'''
    directory = re.search(r'\/.*\/', path).group()
    Path(directory).mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def get_pickle(path):
    '''retrieve pickle for filesystem'''
    try:
        with open(path, 'rb') as p:
            return pickle.load(p)
    except FileNotFoundError:
        raise


def get_grid_path(root_path, type, name, numrows, numcols, resolution):
    "create unique path based on name, type and resolution"
    return "{}/{}/{}_grid/{}x{}-res-{}.pickle".format(root_path, name,
                                                      type, numrows, numcols,
                                                      resolution)


def get_noise_path(root_path, dir, sta, chan, net, loc, start, end):
    '''return noise path'''
    return "{}/{}/{}_{}_{}_{}_{}_{}.pickle".format(root_path, dir, sta, chan,
                                                   net, loc, start, end)
