# from Tkinter import *
import matplotlib.pyplot as plt
import numpy as np
import json
from pprint import pprint 
import geobuf
from geojson import MultiLineString, is_valid, LineString





def parse_json_file(path):
    with open(path) as data_file:    
        return json.load(data_file)


def get_contours(lats,lons,vals,levels):
    X, Y = np.meshgrid(lons, lats)        
    # xyz.append([point['lat'], point['lon'], point['count']])
    Z= np.reshape(vals, (len(lats), len(lons)))
    # levels=list(range(1,11))
    cn = plt.contour(X,Y,Z, levels)
    return get_contour_verts(cn)


def get_contour_verts(cn):
    # print [method for method in dir(cn.collections[0]) if callable(getattr(cn.collections[0], method))]
    contours = []
    # for each contour line
    for cc in cn.collections:
        paths = []
        # for each separate section of the contour line
        for pp in cc.get_paths():
            #path object
            # print(pp)
            xy = []
            # for each segment of that section
            for vv in pp.iter_segments():
                xy.append(vv[0])
            paths.append(np.vstack(xy))
        contours.append(paths)
    return contours
    
    
def geojson_multiline_string(contours,levels):
    geo={'type': 'GeometryCollection', 'geometries': []}
    print(is_valid(geo))
    for contour in contours:
        # print contour
        mls_array=[]
        py_array=[]
        #must turn back into python list before geo-jsonifying
        for np_array in contour:
            ls_array=[]
            for ls in np_array:
                ls_array.append((ls[0],ls[1]))
            # print np_array
            ls=LineString(np_array.tolist())
            py_array.append(ls)
            # pprint(py_array)
        mls=MultiLineString(py_array)
        print("***********")
        valid=is_valid(mls)
        print(len(py_array))
        if valid['valid'] != 'yes':
            print(valid['message'])
        geo['geometries'].append(mls)
    return geo
    
#takes geojson obj and writes topojson file
def geojson_to_topo_json(geoj, outfile):
    # topojson(geoj, outfile)
    print("hello")