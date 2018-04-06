import csv
import iris
import argparse


parser = argparse.ArgumentParser(description="Takes a csv file of form \n \
        sta,chan, net, loc and calls fdsn service. Outputs file in form \n \
        sta, chan, net, loc, lat, lon, depth, [on_date], [off_date], rate")
parser.add_argument('-i','--infile',help='input file name', required=True)
parser.add_argument('-o','--outfile', help='output file name',required=True)
args = parser.parse_args()## show values ##

outfile  = open(args.outfile, "w")
infile= open(args.infile)
# print(infile)
writer=csv.writer(outfile)
header=True
with  infile as csvfile:
    reader=csv.reader(csvfile)
    for row in reader:
        if header:
            writer.writerows([[ "sta","chan","net","loc","lat","lon","depth",
                            "on_date","off_date","rate"]])
            header=False
        else:
            if len(row[3])<2:
                loc="--"
            else:
                loc=row[3]
            station=iris.get_fdsn(row[0], row[1], row[2], loc)
            # print(station)
            if station['code'] ==200 and len(station['data']) >0:
                # print("huurray")
                row.extend(station['data'][0][4:10])
                writer.writerows([row])
            else:
                # print(row)
                print("Query for {}:{}:{}:{} failed with:{}".format(
                    row[0],row[1],row[2],loc,station['code']))
infile.close()
outfile.close()
