import sys
import core
from pprint import pprint 


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]
  
    data=core.parse_json_file('data/data.json')
        
    lats=[]
    lons=[]
    counts=[]
    
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
        if point['lng'] not in lons:
            lons.append(point['lng'])
            
    # print len(lons)
    # print len(lats)
    # print len(counts)
    print(min_level)
    print(max_level)
    levels=[1,2,3,4,5]
    contours=core.get_contours(lats,lons,counts,levels)
    # for contour in contours:
    #     print(len(contour))
    geoj=core.geojson_multiline_string(contours,levels)
    pprint(len(geoj['geometries']))
    # topoj=core.geojson_to_topo_json(geoj, "data/topo_contours.js")

if __name__ == "__main__":
    main()