import numpy as np
import os
from urllib.request import urlretrieve
import netCDF4
from netCDF4 import Dataset
from datetime import date
from datetime import datetime
import getpass
import scipy.io
from scipy import interpolate
import matplotlib
import matplotlib.pyplot as plt

fdir = '../data/isimip3a/GSWP3-W5E5/obsclim/'
nctemp = netCDF4.Dataset(fdir + 'gswp3-w5e5_obsclim_tas_global_daily_1901_1910.nc')
nctmax = netCDF4.Dataset(fdir + 'gswp3-w5e5_obsclim_tasmax_global_daily_1901_1910.nc')
nctmin = netCDF4.Dataset(fdir + 'gswp3-w5e5_obsclim_tasmin_global_daily_1901_1910.nc')

i = 134
j = 123
mat = scipy.io.loadmat('../data/sunrise_set_isimip3a.mat')
hr_max = mat['hr_max']
hr_min = mat['hr_min']
temp   = nctemp.variables['tas'][:31,j,i]
tmax   = nctmax.variables['tasmax'][:31,j,i]
tmin   = nctmin.variables['tasmin'][:31,j,i]
a      = nctmin.variables['tasmin'][0,1,1]

print('a = ',a)

hmax = int(round(hr_max[i,j,0]/3))
hmin = int(round(hr_min[i,j,0]/3))

print(not np.isnan(hr_max[1,1,0]))
numd = len(temp)
tday = np.arange(0.5,numd,1)
dt   = 3 / 24
t3hr = np.arange(dt/2,numd,dt)

tintp     = np.empty(((numd+1)*2,))
tempintp  = np.empty(((numd+1)*2,))

tintp[0]  = t3hr[0]
tintp[-1] = t3hr[-1]
tempintp[0] = temp[0]
tempintp[-1] = temp[-1]

temp3hr = np.empty((31*8,360,720))
for i in range(numd):

    if hmax > hmin:
        tintp[2*i + 1]    = t3hr[i*8 + hmin] 
        tintp[2*i + 2]    = t3hr[i*8 + hmax] 
        tempintp[2*i + 1] = tmin[i]
        tempintp[2*i + 2] = tmax[i]
    else:
        tintp[2*i + 1]    = t3hr[i*8 + hmax] 
        tintp[2*i + 2]    = t3hr[i*8 + hmin] 
        tempintp[2*i + 1] = tmax[i]
        tempintp[2*i + 2] = tmin[i]

f = interpolate.PchipInterpolator(tintp, tempintp, axis=0, extrapolate=None)
temp3hr[:,j,i] = f(t3hr)
f2 = interpolate.interp1d(tday,temp,kind='nearest',fill_value="extrapolate",axis=0) # fill_value="extrapolate"
tempnear = f2(t3hr)

plt.figure(figsize=(12,5))
plt.plot(tintp, tempintp,'rx')
plt.plot(t3hr,temp3hr[:,j,i],'b-')
plt.plot(t3hr,tempnear,'g-')

plt.savefig('test_interpolation.png')