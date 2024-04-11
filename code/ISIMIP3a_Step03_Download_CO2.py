import numpy as np
import os
from urllib.request import urlretrieve
import netCDF4
import shutil
from datetime import date
from create_nc import create_landuse_timeseries

climate_scenarios = ['obsclim', 'spinclim','counterclim','transclim']

if not os.path.exists('../data'):
	os.mkdir('../data')
if not os.path.exists('../data/isimip3a'):
	os.mkdir('../data/isimip3a')
if not os.path.exists('../data/isimip3a/CO2'):
	os.mkdir('../data/isimip3a/CO2')


# 1 Download the landuse data	
for i in range(len(climate_scenarios)):
    if not os.path.exists('../data/isimip3a/CO2/'+climate_scenarios[i]):
        os.mkdir('../data/isimip3a/CO2/'+climate_scenarios[i])
    server = 'https://files.isimip.org/ISIMIP3a/InputData/climate/atmosphere_composition/co2/'

    if climate_scenarios[i] == 'obsclim':
        fname = 'co2_'+climate_scenarios[i]+'_annual_1850_2021.txt'
    elif climate_scenarios[i] == 'spinclim':
        fname = 'co2_'+climate_scenarios[i]+'_annual_1850_2021.txt'
    elif climate_scenarios[i] == 'counterclim':
        fname = 'co2_'+climate_scenarios[i]+'_annual_1901_2021.txt'
    elif climate_scenarios[i] == 'transclim': 
        fname = 'co2_'+climate_scenarios[i]+'_annual_1850_1900.txt'

    if os.path.isfile('../data/isimip3a/CO2/'+climate_scenarios[i]+'/'+fname):
        print(fname + ' is already downloaded!')
    else:
        url   = server + climate_scenarios[i] + '/' + fname
        print(url)
        print('Downloading ' + fname)
        urlretrieve(url, '../data/isimip3a/CO2/'+climate_scenarios[i]+'/'+fname)

# 2 Process to landuse time series for histsoc
fname = '../data/isimip3a/CO2/obsclim/co2_obsclim_annual_1850_2021.txt'
fin   = '/compyfs/inputdata/atm/datm7/CO2/fco2_datm_1765-2007_c100614.nc'
fout  = '../inputdata/fco2_datm_1777-2021_obsclim.nc'
shutil.copyfile(fin, fout)

data  = np.loadtxt(fname)
ncid  = netCDF4.Dataset(fin)
tmp   = ncid.variables['CO2'][:]
co2   = np.empty((245,))
co2[:73] = tmp[:73].flatten()
co2[73:] = data[:,1].flatten()

time = np.empty((245,))
d0 = date(1765, 1, 1)
for i in range(245):
    d1 = date(1777+i,7,1)
    delta = d1 - d0
    time[i] = delta.days

ncid2 = netCDF4.Dataset(fout, 'r+')
ncid2['CO2'][:] = co2
ncid2['time'][:] = time
ncid2.close() 
ncid.close()



# Spinlim
#for i in range(len(scenarios)):
#    fname1 = 'landuse-totals_'     + scenarios[i] + '_annual_1901_2021.nc'
#    fname2 = 'landuse-urbanareas_' + scenarios[i] + '_annual_1901_2021.nc'
#    ncid1 = netCDF4.Dataset(fname1)
#    ncid2 = netCDF4.Dataset(fname2)
#    np.concatenate((np.repeat(np.reshape(irrigated[0,:,:],(1,360,720)),50,axis=0),irrigated),axis=0).shape
