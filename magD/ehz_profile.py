import sys
import os
# sys.path.append(os.path.abspath('.'))

from plotMagD import PlotMagD
from magD import MagD
config_path="../config/ehz_profile/ehz_all.ini"
outfile="../plots/all_bb_ehz.jpg"

magD=MagD(config_path)
magD.get_noise()
magD.find_detections()
sum=magD.print_summary()
print(sum)
# plotmagd=PlotMagD(magD)
# plt=plotmagD.figure(6,10)
# plt.rc("font", size=14)
#
# map=plotmagD.basemap()
# map.drawcoastlines(zorder=0)
# map.drawstates(zorder=2)
#
# X,Y,Z,levels=plotmagD.create_contour_levels()
# cs =map.contour(X,Y,Z,levels,colors="k",zorder=3,linewidths=0.5)
#
#
# #incresing from 10 t0
# plt.clabel(cs, inline=1, fontsize=12,fmt='%1.1f')
#
# meridian_interval=np.linspace(lon_min,lon_max,4,dtype = int)
# #set linewidth to 0  to get only labels
# map.drawmeridians(meridian_interval,labels=[0,0,0,1],
# dashes=[90,8], linewidth=0.0)
# parallel_interval=np.linspace(lat_min,lat_max,4,dtype = int)
# map.drawparallels(parallel_interval,labels=[1,0,0,0],
# dashes=[90,8], linewidth=0.0)
# #m.drawmapboundary()
# #zorder puts it at lowest plot level
# map.fillcontinents(color='0.7',zorder=1)
#
# plt.title("{} station Detection Thresholds".format(num_stas))
# #should we add no solution symbol to legend?
# no_solution=False
# for key in magD.scnl_collections:
#   #plot station data
#   lats, lons, sols=magD.get_xyz_lists(key)
#   #stas are sorted by number of solutions. Find where they go to
#   #zero, these will be marked as 'o'
#
# no_i=magD.get_no_solution_index()
#
#
#   if no_i < len(lons)-1:
#       no_solution=True
#   print("no_i {}".format(no_i))
#   Sx,Sy=m(lons[:no_i], lats[:no_i])
#   Sxn,Syn=m(lons[no_i:], lats[no_i:])
#   color='c'
#   label='label'
#   stas=plt.scatter(Sx, Sy, s=70, marker='^', c=color, label=label,zorder=11)
#   print(Sx)
#   plt.scatter(Sxn, Syn, s=30, marker='o', facecolors='none', edgecolors=color,zorder=11)
# #plot star at origin of interest
# i_lat=44.5
# i_lon=-124.5
# Sxi,Syi=m(i_lon, i_lat)
# plt.scatter(Sxi, Syi, s=200, marker='*', color='r', label="Interface Earthquakes")
# #plt.colorbar(stas, orientation='horizontal', shrink=0.4)
# if no_solution:
#   plt.scatter([-1],[-1], s=30, marker='o',facecolors='none',edgecolor='k',label="No solution")
# plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.,scatterpoints=1)
# plt.savefig("{}.png".format(args.outfile))
# plt.show()
