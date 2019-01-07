import pickle
import re
from pathlib import Path


#pickle objects to path

def set_pickle(path, data):
  #create pickle_paths if it doesn't exist
  directory=re.search(r'\/.*\/',path).group()
  Path(directory).mkdir(parents=True, exist_ok=True)
  with open(path, 'wb') as f:
      pickle.dump(data, f)

def get_pickle(path):
  try:
      with open(path, 'rb') as p:
          return pickle.load(p)
  except FileNotFoundError:
      raise

#common paths
"create unique path based on name, type and resolution"
def get_grid_path(root_path, type, name, numrows, numcols, resolution):
  return "{}/{}/{}_grid/{}-{}x{}-res-{}.pickle".format(root_path, name,
        type ,name, numrows, numcols, resolution)


def get_noise_path(root_path,dir,sta,chan,net,loc,start,end):
  return "{}/{}/{}_{}_{}_{}_{}_{}.pickle".format(root_path,
              dir, sta, chan, net, loc, start, end)
