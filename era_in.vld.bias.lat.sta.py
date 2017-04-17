#!/usr/bin/env python
"""
========
ctang, a map of geba stations in southern africa
========
"""
import math
import pdb
import datetime
import pandas as pd
import numpy as np
import matplotlib as mpl
from textwrap import wrap
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap , addcyclic
from matplotlib.dates import YearLocator,MonthLocator,DateFormatter,drange
import sys 
sys.path.append('/Users/ctang/Code/Python/')
import ctang

#=================================================== input
Valid_file='ERA_IN.GEBA.station.data'
DIR='/Users/ctang/climate/GLOBALDATA/OBSDATA/ERA_Interim/ERA_Interim_SSR_vs_GEBA/'
Valid=ctang.Loadmat(DIR+Valid_file+'.mat')
# staID, N_mon, lat, lon, alt, sta_name, meanbias,meanbiaslt0,meanbiasgt0,mab slope, intercept, r_value, P_value, std_err # allthebias, alltheAbsBias 

# convert string to float, doesn't works for station_name
# Valid=[[float(y) for y in x] for x in Valid]

# sort by lat:
# Valid=Valid[np.argsort(Valid[:,2])]

#=================================================== output
Out_Image='era_in.vld.bias.lat.sta'
#=================================================== plot
print Valid.shape

station_id = [float(y) for y in Valid[:,0]]
N_month    = [float(y) for y in Valid[:,1]]
lats       = [float(y) for y in Valid[:,2]]
altitude   = [float(y) for y in Valid[:,4]]
station_name = Valid[:,5]
meanbias   = [float(y) for y in Valid[:,6]]
meanbias1  = [float(y) for y in Valid[:,7]]
meanbias2  = [float(y) for y in Valid[:,8]]
mab        = [float(y) for y in Valid[:,9]]

# define a plot array
plot_array = np.array(np.column_stack((N_month,lats,station_name,meanbias,meanbias1,meanbias2,mab)))

# sort by lat, and inverse by [::-1]
# plot_array=plot_array[np.argsort(lats)][::-1]
plot_array=plot_array[np.argsort(lats)]

# re-define 
N_month      = [float(y) for y in plot_array[:,0]]
lats         = plot_array[:,1]
station_name = plot_array[:,2]
meanbias     = [float(y) for y in plot_array[:,3]]
mab          = [float(y) for y in plot_array[:,6]]

print meanbias
#=================================================== plotting
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(14,12),\
        facecolor='w', edgecolor='k') # figsize=(w,h)
fig.subplots_adjust(left=0.3,bottom=0.1,right=0.9,\
        hspace=0.15,top=0.9,wspace=0.43)

# ax.set_title('mean bias (W/m2) of CM SAF monthly SSR vs GEBA',fontsize=14)

ax.set_xlim((-45,45))
ax.set_xticks(range(-45,50,15)) 
ax.set_xlabel('Bias (W/m2)',fontsize=14)

ax.set_ylim((-1, len(station_id)))
ax.set_yticks(range(-1,len(station_id)+1,1))
ax.set_ylabel('station', fontsize=14)
plt.yticks(range(len(station_id)),station_name)

ax.set_axisbelow(True)
ax.yaxis.grid(color='gray', linestyle='dashed')
ax.xaxis.grid(color='gray', linestyle='dashed')


# ax.spines['left'].set_linewidth(2)
# ax.spines['bottom'].set_linewidth(2)

# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)
# ax.yaxis.set_ticks_position('left')
# ax.xaxis.set_ticks_position('bottom')
ax.tick_params(labeltop=True, labelright=True)

ax.axvline(x=-15,ymin=-1, ymax=len(station_id)+1,color='black',ls='--',linewidth=2)
ax.axvline(x=0,  ymin=-1, ymax=len(station_id)+1,color='black',linewidth=2)
ax.axvline(x=15, ymin=-1, ymax=len(station_id)+1,color='black',ls='--',linewidth=2)


for sta in range(len(station_id)):
    if N_month[sta] > 12:
        ax.plot(meanbias[sta],sta,marker='s',markersize=8,color='red')
        ax.plot(mab[sta],sta,marker='o',markersize=6,color='blue')

ax.plot(100,100,marker='s',markersize=8,color='red',label='meanbias')
ax.plot(100,100,marker='o',markersize=6,color='blue',label='MAB')
legend = ax.legend(loc='upper left',shadow=False ,prop={'size':12})
# cb=plt.colorbar(sc,orientation='horizontal',shrink=0.6)
# cb.ax.tick_params(labelsize=9) 
# cb.ax.set_title("Mean Absolute Bias (W/m2)")

ax2 = ax.twinx()
ax2.set_ylim((-1, len(station_id)))
ax2.set_ylabel('latitude', fontsize=14)
ax2.set_yticks(range(-1,len(station_id)+1,1))
ax2.set_yticks(range(-1,len(station_id)+1,1))
plt.yticks(range(len(station_id)),lats)

title='Mean Bias of ERA_Interim vs GEBA monthly SSR in southern Africa 1983-2005'
fig.suptitle(title,fontsize=12)

# plot record num of each station
# for sta in range(len(station_id)):
    # if N_month[sta] > 5 and mab[sta] > 15:
        # plt.annotate( format(mab[sta],'.1f'),xy=(lons[sta], lats[sta]), xytext=(4, 1),\
            # textcoords='offset points', ha='left', va='top',color='blue',\
            # # bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),\
            # # arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0')\
            # )
plt.savefig(Out_Image+'.eps',format='eps')
#===================================================  end of subplot 3
print "done"
plt.show()
quit()
