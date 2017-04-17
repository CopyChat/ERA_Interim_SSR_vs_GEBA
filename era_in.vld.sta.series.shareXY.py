#!/usr/bin/env python
"""
========
Ctang, A map of mean max and min of ensembles
        from CMSAF AFR-44, in Southern Africa
        Data was restored on titan
========
"""
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

#=================================================== Definitions

N_model = 1
VAR ='rsds' 
NYEAR=313

LINE=423
#=================================================== reading data
# reading CMSAF

obs='cmsaf.rsds.csv'
Dir='/Users/ctang/climate/GLOBALDATA/OBSDATA/CM_SAF/validation.CM_SAF.SA/'
CMSAFfile=Dir+obs

CMSAF = np.array(pd.read_csv(CMSAFfile,index_col=False))
#ID,StaID,year,Jan,Feb,Mar,Api,May,Jun,July,Aug,Sep,Oct,Nov,Dec

CMSAF_Data = CMSAF[:,3:15]
STATION=CMSAF[:,1]

print CMSAF_Data.shape # (462,12)

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

stationfile = 'GEBA.station.csv'
station = np.array(pd.read_csv(Dir+stationfile,index_col=False))
#staNO,staID,lat,lon,Nmonth

station_id = station[:,1]
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
    cmsaf=np.zeros((x.shape[0],x.shape[1]))

    for k in range(x.shape[0]):
        for j in range(x.shape[1]):
            rsds[k,j]=x[k,j]
            flag[k,j]=x1[k,j]
            cmsaf[k,j]=y[k,j]


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
        cmsaf_plot=[]
        date=[]

        for k in range(1,13,1):
            if cmsaf[j,k] > 0:                    # rm missing data 1988-12
                if justice(flag[j,k]) == 1:
                    rsds_plot.append(rsds[j,k])
                    cmsaf_plot.append(cmsaf[j,k])
                    date.append(dates[k-1])
                else:
                    a=000
            else:
                print k,dates[k-1],"removing missing value 1988-12"

        x_plot+=rsds_plot
        y_plot+=cmsaf_plot
        date_plot+=date
        # print i,title[i],len(date),len(rsds_plot),len(cmsaf_plot),"============ in VS"

    x=x_plot
    y=y_plot
    date=date_plot
    print i,title[i],len(date),len(x),len(y),"============ in VS"



    #=================================================== plot
    if len(x) > 0:

        vmin=100
        vmax=395

        # ax.set_ylabel('SSR (W/m2)',fontsize=8)
        # ax.set_xlabel('TIME',fontsize=8)

        ax.set_ylim((vmin,vmax))
        ax.set_yticks(range(vmin,vmax,50))

        ax.xaxis.set_major_locator(MonthLocator(1)) # interval = 5
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
        ax.fmt_xdata = DateFormatter('%Y-%m')


        ax.yaxis.grid(color='gray', linestyle='dashed',lw=0.5)
        ax.xaxis.grid(color='gray', linestyle='dashed',lw=0.5)

        ax.plot(date,x,linestyle='--',marker='s',markersize=2,lw=1,zorder=2,label='GEBA',color='blue')
        ax.plot(date,y,linestyle='-',marker='o',markersize=2,lw=1,zorder=2,label='CM_SAF',color='red')
        legend = ax.legend(loc='upper left', shadow=False ,prop={'size':5})
        ax.set_xlim(datetime.datetime(1982,12,01),datetime.datetime(2005,12,31))
        plt.setp( ax.xaxis.get_majorticklabels(), rotation=90)

        # ax.set_title(str(i+1)+". "+title[i],fontsize=6)
        ax.text(datetime.datetime(2005,06,15),350,str(i+1)+". "+title[i],ha='right', fontsize=10, rotation=0)   

    
    # no. of records
    NO=len(list(x))
    if i == 35:
        ax.text( datetime.datetime(1998,12,01),165,'#:'+str(NO),ha='right', fontsize=10, rotation=0)   
        # mean bias of records
        bias=np.array([np.abs(y[l]-x[l]) for l in range(len(x))]).mean()
        ax.text( datetime.datetime(1998,12,01),115,'MAB='+str(format(bias,'.2f')),ha='right', fontsize=10, rotation=0)   
    else:
        ax.text( datetime.datetime(2005,12,01),165,'#:'+str(NO),ha='right', fontsize=10, rotation=0)   
        # mean bias of records
        bias=np.array([np.abs(y[l]-x[l]) for l in range(len(x))]).mean()
        ax.text( datetime.datetime(2005,12,01),115,'MAB='+str(format(bias,'.2f')),ha='right', fontsize=10, rotation=0)   




    return format(bias,'.2f')
#--------------------------------------------------- 

#=================================================== plot by 21 models

ncol=5
nrow=9
def plot_by_model(title):
    COF=np.zeros((N_model,len(station_id)))

    for i in range(N_model):
        print("plotting in model",str(i+1))
        fig, axes = plt.subplots(nrows=nrow, ncols=ncol,\
            sharex=True, sharey=True,\
            figsize=(15,15),facecolor='w', edgecolor='k') # (w,h)
        fig.subplots_adjust(left=0.07,bottom=0.10,right=0.93,top=0.93,wspace=0,hspace=0)
        fig.text(0.5, 0.03, 'TIME', ha='center')
        fig.text(0.03, 0.5, 'SSR (W/m2)', va='center', rotation='vertical')
        axes = axes.flatten() # reshape plots to 1D if needed

        # fig = plt.figure(figsize=(ncol+1, nrow+1)) # (w,h)
        # gs = gridspec.GridSpec(nrow, ncol,\
            # sharex=True, sharey=True,\
            # wspace=0.0, hspace=0.0,\
            # top=1.-0.5/(nrow+1), bottom=0.5/(nrow+1),\
            # left=0.5/(ncol+1), right=1-0.5/(ncol+1)) 

        for j in range(ncol*nrow):
            if j < (len(station_id)):
                sta=station_id[j]

                # prepare cm_saf
                CMSAF_array=CMSAF
                CMSAF_sta1=np.array(CMSAF_array[np.where(CMSAF_array[:,1]==sta)])
                # CMSAF_sta=CMSAF_sta1[:,3:15].flatten()
                CMSAF_sta=CMSAF_sta1[:,2:15]

                # prepare obs
                GEBA_PlotFlag1=np.array(GEBA_FLAG[np.where(GEBA_FLAG[:,0]==sta)])
                # GEBA_PlotFlag=GEBA_PlotFlag1[:,3:15].flatten()
                GEBA_PlotFlag=GEBA_PlotFlag1[:,2:15]

                GEBA_PlotRsds1=np.array(GEBA_RSDS[np.where(GEBA_RSDS[:,0]==sta)])
                # GEBA_PlotRsds=GEBA_PlotRsds1[:,3:15].flatten()
                GEBA_PlotRsds=GEBA_PlotRsds1[:,2:15]

                # check
                print("-------input:",j,sta,CMSAF_sta.shape,GEBA_PlotRsds.shape)

    #=================================================== 
                # to plot
                COF[i,j]=VS(\
                        np.array(np.float32(GEBA_PlotRsds)),\
                        np.array(np.float32(GEBA_PlotFlag)),\
                        np.array(np.float32(CMSAF_sta)),\
                        axes[j],j,title)
            else:
                ctang.empty_plot(axes[j])

        plt.suptitle('CM SAF vs GEBA monthly SSR (W/m2) in 44 stations ',fontsize=14)

        outfile='validation.sta.series.CM_SAF.GEBA'
        # plt.savefig(outfile+'.png')
        plt.savefig(outfile+'.eps', format='eps')
#=================================================== save cof
    headers=['Sta_'+str(i+1) for i in range(len(station_id))]
    with open('cmsaf.vld.series.8305.MAB.csv','w,') as fp:
        fp.write(','.join(headers) + '\n')
        np.savetxt(fp, COF, '%5.2f', ',')
#=================================================== end plot by model

plot_by_model(station_name)

#=================================================== end
plt.show()
quit()
