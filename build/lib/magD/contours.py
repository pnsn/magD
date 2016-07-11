#!/usr/bin/env python

from pprint import pprint 
import matplotlib.pyplot as plt
import numpy as np
import json
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
lats=[]
lngs=[]
counts=[]

columns =[]
with open('data.json') as data_file:    
    data = json.load(data_file)
min_level=data['points'][0]['count']
max_level=data['points'][0]['count']
row_count=1
for point in data["points"]:
    if point['count'] > max_level:
        max_level=point['count']
    if point['count']< min_level:
        min_level=point['count']
    counts.append(point['count'])
    if point['lat'] not in lats:
        lats.append(point['lat'])
    if point['lng'] not in lngs:
        lngs.append(point['lng'])

# print len(lngs)
# print len(lats)
# print len(counts)
print min_level
print max_level
X, Y = np.meshgrid(lngs, lats)        
    # xyz.append([point['lat'], point['lng'], point['count']])
Z= np.reshape(counts, (len(lats), len(lngs)))
# levels=list(range(1,11))
levels=[1,2,3,4,5]



cn = plt.contour(X,Y,Z, levels)


contours = get_contour_verts(cn)
for contour in contours:
    print(len(contour))