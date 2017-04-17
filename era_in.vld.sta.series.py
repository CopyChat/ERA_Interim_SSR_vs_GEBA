#!/usr/bin/env python
"""
========
Ctang, A map of mean max and min of ensembles
        from ERA_IN AFR-44, in Southern Africa
        Data was restored on titan
========
"""
import pdb
import math
import subprocess
import datetime
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from matplotlib.ticker import AutoMinorLocator
from matplotlib.dates import YearLocator,MonthLocator,DateFormatter,drange
from mpl_toolkits.basemap import Basemap , addcyclic
import textwrap

# to load my functions
import sys 
sys.path.append('/Users/ctang/Code/Python/')
import ctang

#================================================== Definitions

N_model = 1
VAR ='rsds' 

LINE=423
#=================================================== reading data
# reading ERA_IN

obs='era_in.rsds.csv'
Dir='/Users/ctang/climate/GLOBALDATA/OBSDATA/ERA_Interim/ERA_Interim_SSR_vs_GEBA/'
ERA_INfile=Dir+obs

ERA_IN = np.array(pd.read_csv(ERA_INfile,index_col=False))
#ID,StaID,year,Jan,Feb,Mar,Api,May,Jun,July,Aug,Sep,Oct,Nov,Dec

ERA_IN_Data = ERA_IN[:,3:15]
STATION=ERA_IN[:,1]

print ERA_IN_Data.shape # (462,12)

#=================================================== 
# reading GEBA

GEBA_flag='flag.mon.GEBA.csv'
GEBA_rsds='rsds.mon.GEBA.csv'

print Dir+GEBA_flag

GEBA_FLAG = np.array(pd.read_csv(Dir+GEBA_flag,index_col=False)) # (462,18)
GEBA_RSDS = np.array(pd.read_csv(Dir+GEBA_rsds,index_col=False))
#StaID,obsID,year,Jan,Feb,Mar,Api,May,Jun,July,Aug,Sep,Oct,Nov,Dec,sta,country,ID

print GEBA_FLAG.shape
#=================================================== 
# reading station

stationfile = 'GEBA.station.gt.1mon.SA'
#NO.,staID,lat,lon,N_month,staID,altitude
station = np.array(pd.read_csv(Dir+stationfile,index_col=False))

station_id = station[:,1]
lats = station[:,2]
lons = station[:,3]
altitude = station[:,6]
print station.shape

# get station_name:
station_name=[ 't' for i in range(len(station_id))]
for i in range(len(station_id)):
    for j in range(LINE):
        if GEBA_FLAG[j,0] == station_id[i]:
            station_name[i] = str(GEBA_FLAG[j,16])+"@"+str(GEBA_FLAG[j,17])
print station_name

#--------------------------------------------------- 
# good data: 1
# bad data: -1
# missing data: 0

def justice(flag):
    jjj=90908                     # default
    s=list(str(int(flag)))
    if len(s) > 1:
        if s[4] == '8':
            if s[3] == '7' or s[3] == '8' :
                if s[2] == '5' or s[2] == '7' or s[2] == '8':
                    if s[1] == '5':
                        if s[0] == '5':
                            jjj = 1
                        else:
                            jjj = -1
                    else:
                        jjj = -1
                else:
                    jjj = -1
            else:
                jjj = -1
        else:
            jjj = -1
    else:                             # single flag 0 or 8
        if s[0] > 0:
            jjj = -1
        else:
            jjj = 0
    return jjj 
#--------------------------------------------------- 

#--------------------------------------------------- 
# functino to plot GEBA vs OBS
def VS(x,x1,y,ax,i,title):

    # rename the x, x1, y and convert to np.array
    rsds=np.zeros((x.shape[0],x.shape[1]))
    flag=np.zeros((x.shape[0],x.shape[1]))
    era_in=np.zeros((x.shape[0],x.shape[1]))

    for k in range(x.shape[0]):
        for j in range(x.shape[1]):
            rsds[k,j]=x[k,j]
            flag[k,j]=x1[k,j]
            era_in[k,j]=y[k,j]

    # to get x , y, and date for plot
    x_plot=[]
    y_plot=[]
    date_plot=[]

    years = x[:,0]
    for j in range(len(years)):
        year = int(years[j]-1)
        dates=pd.date_range((pd.datetime(year,12,1)\
            +pd.DateOffset(months=1)), periods=12, freq='MS')

        # print years[j],dates

        # remove bad data: justice function
        rsds_plot=[]
        era_in_plot=[]
        date=[]

        for k in range(1,13,1):
            if era_in[j,k] > 0:                    # rm missing data 1988-12
                if justice(flag[j,k]) == 1:
                    rsds_plot.append(rsds[j,k])
                    era_in_plot.append(era_in[j,k])
                    date.append(dates[k-1])
                else:
                    a=000
            else:
                print k,dates[k-1],"removing missing value 1988-12"

        x_plot+=rsds_plot
        y_plot+=era_in_plot
        date_plot+=date
        # print i,title[i],len(date),len(rsds_plot),len(era_in_plot),"============ in VS"

    x=x_plot
    y=y_plot
    date=date_plot
    print i,title[i],len(date),len(x),len(y),"============ in VS"



    #=================================================== plot
    if len(x) > 0:

        vmin=100
        vmax=390

        ax.set_ylabel('SSR (W/m2)',fontsize=8)
        # ax.set_xlabel('TIME',fontsize=8)

        ax.set_ylim((vmin,vmax))
        ax.set_yticks(range(vmin,vmax,50))

        ax.xaxis.set_major_locator(MonthLocator(1)) # interval = 5
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
        ax.fmt_xdata = DateFormatter('%Y-%m')


        ax.yaxis.grid(color='gray', linestyle='dashed',lw=0.5)
        ax.xaxis.grid(color='gray', linestyle='dashed',lw=0.5)

        ax.plot(date,x,linestyle='--',marker='s',markersize=2,zorder=2,label='GEBA',color='blue')
        ax.plot(date,y,linestyle='-',marker='o',markersize=2,zorder=2,label='ERA_IN',color='red')
        if len(x) == 1:
            legend = ax.legend(loc='upper right',shadow=False ,prop={'size':12})
        else:
            legend = ax.legend(loc='upper left', shadow=False ,prop={'size':12})

        ax.set_title(str(i+1)+". "+title[i]+' ('+str(format(lats[i],'.2f'))+', '+str(format(lons[i],'.1f'))+')'+' ('+str(int(altitude[i]))+' m)',fontsize=12)
        plt.setp( ax.xaxis.get_majorticklabels(), rotation=45)


    # if only one point, put text on the right of the date
    
    # no. of records
    NO=len(list(x))
    ax.text(date[-1],370,'#:'+str(NO),ha='right', fontsize=9, rotation=0)   

    # mean bias of records
    bias=np.array([np.abs(y[l]-x[l]) for l in range(len(x))]).mean()
    ax.text(date[-1],350,'MAB:'+str(format(bias,'.2f')),ha='right', fontsize=9, rotation=0)   

    # linear regression:
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    if len(x) > 10:
        ax.text( date[-1],330,'cof:'+str(format(r_value,'.2f')),ha='right', fontsize=9, rotation=0)   

    return format(bias,'.2f')
#--------------------------------------------------- 

#=================================================== plot by 21 models

def plot_by_model(title):
    COF=np.zeros((N_model,len(station_id)))

    for i in range(N_model):
        print("plotting in model",str(i+1))
        fig, axes = plt.subplots(nrows=9, ncols=5,\
            figsize=(30,28),facecolor='w', edgecolor='k') # (w,h)
        fig.subplots_adjust(left=0.05,bottom=0.05,right=0.98,top=0.95,wspace=0.3,hspace=0.5)
        # fig.subplots_adjust(left=0.05,bottom=0.05,right=0.98,top=0.95,wspace=0,hspace=0)
        axes = axes.flatten() # reshape plots to 1D if needed

        for j in range(len(station_id)):
            sta=station_id[j]

            # prepare cm_saf
            ERA_IN_array=ERA_IN
            ERA_IN_sta1=np.array(ERA_IN_array[np.where(ERA_IN_array[:,1]==sta)])
            ERA_IN_sta=ERA_IN_sta1[:,2:15]

            # prepare obs
            GEBA_PlotFlag1=np.array(GEBA_FLAG[np.where(GEBA_FLAG[:,0]==sta)])
            GEBA_PlotFlag=GEBA_PlotFlag1[:,2:15]

            GEBA_PlotRsds1=np.array(GEBA_RSDS[np.where(GEBA_RSDS[:,0]==sta)])
            GEBA_PlotRsds=GEBA_PlotRsds1[:,2:15]

            # check
            print("-------input:",j,sta,ERA_IN_sta.shape,GEBA_PlotRsds.shape)

#=================================================== 
            # to plot
            COF[i,j]=VS(\
                    np.array(np.float32(GEBA_PlotRsds)),\
                    np.array(np.float32(GEBA_PlotFlag)),\
                    np.array(np.float32(ERA_IN_sta)),\
                    axes[j],j,title)

        plt.suptitle('ERA_IN monthly SIS vs GEBA monthly RSDS (W/m2) in 44 stations ',fontsize=14)

        outfile='vld.sta.series.ERA_IN.GEBA'
        # plt.savefig(outfile+'.png')
        plt.savefig(outfile+'.eps', format='eps')
#=================================================== save cof
    # headers=['Sta_'+str(i+1) for i in range(len(station_id))]
    # with open('GEBA.validation.GEBA.1970-1999.cof.csv', 'w') as fp:
        # fp.write(','.join(headers) + '\n')
        # np.savetxt(fp, COF, '%5.2f', ',')
#=================================================== end plot by model
plot_by_model(station_name)

#=================================================== end
plt.show()
quit()
