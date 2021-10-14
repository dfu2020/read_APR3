"""
Created on Tue May 20 03:27:40 2020
@author(s): Arka Mitra (arkam2), Puja Roy (pujaroy2)
"""

"""
Code that reads nadir hires scans from APR-3 W-Band Radar and creates plots for radar reflectivity and 
doppler velocity.

"""
#!pip install metpy

import h5py
import math
import glob
import datetime
import numpy as np
import matplotlib
import pandas as pd
import matplotlib.colors as cm
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from metpy.plots import ctables

def roundup(x):
    for i in range(len(x)):
        x[i] = int(math.ceil(x[i] / 100.0)) * 100 
    return x

ht_gridded = np.linspace(10000.,-5000.,500)

start = 0
end = 20000

def grid_altitude(alt3D, W_refl, vel):
    z_gridded = np.zeros((len(ht_gridded),np.shape(alt3D)[1]))
    z_gridded[:,:] = np.nan
    v_gridded = np.zeros((len(ht_gridded),np.shape(alt3D)[1]))
    v_gridded[:,:] = np.nan
    for i in range(np.shape(alt3D)[1]):
        ht = alt3D[:,i]
        z = W_refl[:,i]
        v = vel[:,i]
        for j in range(len(ht)):
            if(np.isnan(z[j])==False and ht[j]>-5000. and ht[j]<10000.):
                m = int((10000.-ht[j])/30.)
                z_gridded[m,i] = z[j]
                v_gridded[m,i] = v[j]
    return z_gridded, v_gridded

# READ AND PARSE HERE
cmap = ctables.registry.get_colortable('NWSReflectivity')

all_files = glob.glob('APR3/plotting/*Wn.h5')
all_files.sort()

W_ref = []
W_vel = []
UTC = []
stitch_z = []
stitch_v = []

for i in np.arange(0,len(all_files)):
    with h5py.File(all_files[i], mode='r') as f:

        params_W = f['params_W']
        #print out the variables within params_W
        # for key in params_W.keys():
        #      print(key, params_W[key][:])

        hires = f['hires']
        #print out the variables within geolocation
        # for key in hires.keys():
        #      print(key)

        lat = hires['lat'][0,:]
        lon = hires['lon'][0,:]
        p_vel = hires['gsp_mps'][0,:]

        W_refl = hires['z95n']
        W_refl_ = W_refl[:,0,start:end]

        vel = hires['vel95n']
        vel_ = vel[:,0,start:end]

        alt3D = hires['alt3D']
        alt3D_ = alt3D[:,0,start:end]
        z_gridded, v_gridded = grid_altitude(alt3D_,W_refl_,vel_)

        alt_nav = hires['alt_nav'][0,:]

        if (i == 0):                                                                    
                stitch_z=z_gridded                                                      
                stitch_v=v_gridded
        else:  
                stitch_z=np.concatenate((stitch_z,z_gridded),axis=1)
                stitch_v=np.concatenate((stitch_v,v_gridded),axis=1)

        time = hires['scantime']
        time = time[:,start:end]
        for i in range(time.shape[1]):
            UTC = np.append(UTC,datetime.datetime.utcfromtimestamp(time[0,i]).strftime('%H:%M:%S'))