#!/usr/bin/env python
"""
========
rtang, A map of mean max and min of ensembles
        from ERA_IN AFR-44, in Southern Africa
        Data was restored on titan
========
"""
import math
import pdb
import subprocess
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from matplotlib.ticker import AutoMinorLocator
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

GEBA_FLAG = np.array(pd.read_csv(Dir+GEBA_flag,index_col=False)) # (423,18)
GEBA_RSDS = np.array(pd.read_csv(Dir+GEBA_rsds,index_col=False))
#StaID,obsID,year,Jan,Feb,Mar,Api,May,Jun,July,Aug,Sep,Oct,Nov,Dec,mean,station,country,NO

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
    vmin=100
    vmax=385

    # plot box and labels:
    ax.set_xlim(vmin,vmax)
    ax.set_ylim(vmin,vmax)

    ax.set_xticks(range(vmin,vmax,50))
    ax.set_yticks(range(vmin,vmax,50))

    # ax.set_xlabel('GEBA',fontsize=7)
    # ax.set_ylabel('CM_SAF',fontsize=7)

    ax.tick_params(direction='in',length=2,width=1,labelsize=6)

    
    ax.set_axisbelow(True)
    ax.set_aspect('equal')

    # remove bad data: justice function
    rsds=[]
    era_in=[]
    for k in range(x1.shape[0]):
        if y[k] > 0:                    # rm missing data 1988-12
            if justice(x1[k]) == 1:
                rsds.append(x[k])
                era_in.append(y[k])
            else:
                a=000
        else:
            print k,y[k],"removing missing value 1988-12"

    x=rsds
    y=era_in

    print i,title[i],len(x),len(y),"=====remove 198812 & bad ======= in VS"

    if len(x) == 0:             # in the case: only 1988,12 is good in GEBA
        return -90908
    if len(x) < 0:
        ctang.empty_plot(ax)
    else:
        vmin2=np.min(y)
        vmax2=np.max(y)

        vmin1=np.min(x)
        vmax1=np.max(x)

        vmin=np.min([vmin1,vmin2])
        vmax=np.max([vmax1,vmax2])
    
        ax.scatter(x,y,s=1,facecolors='blue',zorder=2)

        # print(type(x))
        # print(type(y))
        # meanbias=np.mean(y-x)
        # ax.text( 150,350,str(meanbias),ha='center', rotation=0)   # plot vs line

        # no. of records
        NO=len(list(x))
        ax.text( 380,165,'#:'+str(NO),ha='right', fontsize=8, rotation=0)   

        # set title
        # ax.set_title(str(i+1)+". "+title[i],fontsize=6)
        ax.text( 110,360,str(i+1)+". "+title[i],ha='left', fontsize=6, rotation=0)   

        # set location, lat,lon
        ax.text( 110,340,'('+str(format(lats[i],'.2f'))+", "+str(format(lons[i],'.2f'))+')',ha='left', fontsize=6, rotation=0)   

        # set location, altitude
        ax.text( 110,320,'('+str(int(altitude[i]))+" m)",ha='left', fontsize=6, rotation=0)   
        # ref line:

        k=np.linspace(100,400,301)
        ax.plot(k,k,'k-',zorder=5,color='black') # identity line

        # linear regression:
        if len(x) > 12:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

            print slope,intercept,r_value,p_value,std_err

            yy=[t*slope+intercept for t in range(400)]
            ax.plot(range(400),yy,'--',color='red',zorder=10,label='fitting')
            # legend = ax.legend(loc='upper left', shadow=False,prop={'size':8})

            if p_value < 0.01:
                ax.text( 370,135,'r='+str(format(r_value,'.2f'))+'(p<0.01)',ha='right', fontsize=8, rotation=0)   
            else:
                ax.text( 370,135,'r='+str(format(r_value,'.2f'))+'(p='+str(format(p_value,'.2f'))+')',ha='right', fontsize=8, rotation=0)   


        # cof=float(np.ma.corrcoef(x,y)[0,1])
        # ax.text( 380,135,'cof:'+str(format(cof,'.2f')),ha='right', fontsize=8, rotation=0)   # plot vs line
        return format(100,'.2f')
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
            figsize=(ncol*2,nrow*2),facecolor='w', edgecolor='k') # (w,h)
        fig.text(0.5, 0.04, 'GEBA', ha='center')
        fig.text(0.03, 0.7, 'ERA_IN', va='center', rotation='vertical')
        fig.subplots_adjust(left=0.07,bottom=0.07,right=0.93,top=0.93,wspace=0,hspace=0)
        axes = axes.flatten() # reshape plots to 1D if needed

        # fig = plt.figure(figsize=(ncol+1, nrow+1)) # (w,h)
        # gs = gridspec.GridSpec(nrow, ncol,\
            # sharex=True, sharey=True,\
            # wspace=0.0, hspace=0.0,\
            # top=1.-0.5/(nrow+1), bottom=0.5/(nrow+1),\
            # left=0.5/(ncol+1), right=1-0.5/(ncol+1)) 

        for j in range(ncol*nrow):
            if j < (len(station_id)):

                # ax = plt.subplot(gs[j])
                sta=station_id[j]

                # prepare cm_saf
                ERA_IN_array=ERA_IN
                ERA_IN_sta1=np.array(ERA_IN_array[np.where(ERA_IN_array[:,1]==sta)])
                ERA_IN_sta=ERA_IN_sta1[:,3:15].flatten()
            
                # prepare obs
                GEBA_PlotFlag1=np.array(GEBA_FLAG[np.where(GEBA_FLAG[:,0]==sta)])
                GEBA_PlotFlag=GEBA_PlotFlag1[:,3:15].flatten()

                GEBA_PlotRsds1=np.array(GEBA_RSDS[np.where(GEBA_RSDS[:,0]==sta)])
                GEBA_PlotRsds=GEBA_PlotRsds1[:,3:15].flatten()

                # check
                print("-------input:",j,sta,ERA_IN_sta.shape,GEBA_PlotRsds.shape)

#=================================================== 
                # to plot
                COF[i,j]=VS(\
                    np.array(np.float32(GEBA_PlotRsds)),\
                    np.array(np.float32(GEBA_PlotFlag)),\
                    np.array(np.float32(ERA_IN_sta)),\
                    axes[j],j,title)
                    # ax,j,title)
            else:
                ctang.empty_plot(axes[j])

        plt.suptitle('ERA_Interim vs GEBA monthly SSR (W/m2) in 44 stations ',fontsize=14)

        outfile='validation.ERA_IN.GEBA'
        plt.savefig(outfile+'.png')
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
