'''create a csv file for MagD with csv scnl file of form:
#sta, chan, net, loc
to
#sta, chan, net, loc, lat, lon, depth, [on_date], [off_date], rate
'''

import csv
import iris

outfile  = open('./csv/pnsn_onshore.csv', "w")
infile= open('./csv/onshore_scnls.csv')
writer=csv.writer(outfile)
header=True
with  infile as csvfile:
    reader=csv.reader(csvfile)
    for row in reader:
        if header:
            writer.writerows([[ "sta","chan","net","loc","lat","lon","depth","on_date","off_date","rate"]])
            header=False
        else:
            station=iris.get_fdsn(row[0], row[1], row[2])
            if station['code'] ==200 and len(station['data']) >0:
                row.extend(station['data'][0][4:10])
                writer.writerows([row])
infile.close()
outfile.close()
