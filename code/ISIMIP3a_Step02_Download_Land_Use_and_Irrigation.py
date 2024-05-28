import numpy as np
import os
from urllib.request import urlretrieve
import netCDF4
from create_nc import create_landuse_timeseries

scenarios = ['histsoc','1901soc','2015soc']
datasets  = ['totals','urbanareas']

if not os.path.exists('../data'):
	os.mkdir('../data')
if not os.path.exists('../data/isimip3a'):
	os.mkdir('../data/isimip3a')
if not os.path.exists('../data/isimip3a/landuse_and_irrigation'):
	os.mkdir('../data/isimip3a/landuse_and_irrigation')


# 1 Download the landuse data	
for i in range(len(scenarios)):
    if not os.path.exists('../data/isimip3a/landuse_and_irrigation/'+scenarios[i]):
        os.mkdir('../data/isimip3a/landuse_and_irrigation/'+scenarios[i])
    server = 'https://files.isimip.org/ISIMIP3a/InputData/socioeconomic/landuse/'

    for j in range(len(datasets)):
        fname1 = 'landuse-' + datasets[j] + '_' + scenarios[i] + '_annual_1850_1900.nc'
        fname2 = 'landuse-' + datasets[j] + '_' + scenarios[i] + '_annual_1901_2021.nc'

        if os.path.isfile('../data/isimip3a/landuse_and_irrigation/'+scenarios[i]+'/'+fname1):
            print(fname1 + ' is already downloaded!')
        else:
            url   = server + scenarios[i] + '/' + fname1
            print('Downloading ' + fname1)
            urlretrieve(url, '../data/isimip3a/landuse_and_irrigation/'+scenarios[i]+'/'+fname1)
        
        if os.path.isfile('../data/isimip3a/landuse_and_irrigation/'+scenarios[i]+'/'+fname2):
            print(fname2 + ' is already downloaded!')
        else:
            url   = server + scenarios[i] + '/' + fname2
            print('Downloading ' + fname2)
            urlretrieve(url, '../data/isimip3a/landuse_and_irrigation/'+scenarios[i]+'/'+fname2)


# 2 Process to landuse time series for histsoc
fname1 = '../data/isimip3a/landuse_and_irrigation/histsoc/landuse-totals_histsoc_annual_1901_2021.nc'
fname2 = '../data/isimip3a/landuse_and_irrigation/histsoc/landuse-urbanareas_histsoc_annual_1901_2021.nc'
ncid1 = netCDF4.Dataset(fname1)
ncid2 = netCDF4.Dataset(fname2)
irrigated = np.flip(ncid1.variables['cropland_irrigated'][:].filled(fill_value=0),axis=1)
rainfed   = np.flip(ncid1.variables['cropland_rainfed'][:].filled(fill_value=0),  axis=1)
urbanarea = np.flip(ncid2.variables['urbanareas'][:].filled(fill_value=0),        axis=1)

fin       = '/compyfs/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_0.5x0.5_HIST_simyr1850-2015_c211019.nc'
yr_start  = 1850
yr_end    = 2015
irrigated = irrigated * 100.0
rainfed   = rainfed * 100.0
urbanarea = urbanarea * 100.0
irrigated = np.concatenate((irrigated[:51,:,:],irrigated[:115,:,:]),axis=0)
rainfed   = np.concatenate((rainfed[:51,:,:]  ,rainfed[:115,:,:])  ,axis=0)

create_landuse_timeseries(fin,irrigated,rainfed,urbanarea,yr_start,yr_end,'histsoc')

# Spinlim
#for i in range(len(scenarios)):
#    fname1 = 'landuse-totals_'     + scenarios[i] + '_annual_1901_2021.nc'
#    fname2 = 'landuse-urbanareas_' + scenarios[i] + '_annual_1901_2021.nc'
#    ncid1 = netCDF4.Dataset(fname1)
#    ncid2 = netCDF4.Dataset(fname2)
#    np.concatenate((np.repeat(np.reshape(irrigated[0,:,:],(1,360,720)),50,axis=0),irrigated),axis=0).shape
