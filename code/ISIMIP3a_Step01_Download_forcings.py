import numpy as np
import os
from urllib.request import urlretrieve
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()

climate_forcings  = ['GSWP3-W5E5', '20CRv3-W5E5', '20CRv3-ERA5', '20CRv3', 'CHELSA-W5E5v1.0']
# From higher priority to lower priority
climate_scenarios = ['obsclim', 'spinclim','counterclim','transclim']
varnames          = ['huss', 'pr', 'ps', 'rsds', 'sfcWind', 'tas', 'tasmax', 'tasmin']
# Specific humidity [kg kg-1], Precipitation flux [kg m-2 s-1], Surface air pressure [Pa], 
# Surface downwelling shortwave flux in air [W m-2], Wind speed [m s-1], Air temperature [k],
# Max air temperature, Min air temperature 

climate_forcing  = climate_forcings[0]
climate_scenario = climate_scenarios[0]

if climate_scenario == 'obsclim' or climate_scenario == 'counterclim':
    periods = [ '1901_1910', '1911_1920', '1921_1930', '1931_1940', '1941_1950', \
                '1951_1960', '1961_1970', '1971_1980', '1981_1990', '1991_2000', \
                '2001_2010', '2011_2019']
elif climate_scenario == 'spinclim':
    periods = [ '1801_1810', '1811_1820', '1821_1830', '1831_1840', '1841_1850', \
                '1851_1860', '1861_1870', '1871_1880', '1881_1890', '1891_1900' ]
elif climate_scenario == 'transclim':
    periods = ['1851_1860', '1861_1870', '1871_1880', '1881_1890', '1891_1900']

if size > 1:
	assert(size >= len(periods))

# GSWP3-W5E5/gswp3-w5e5_transclim_pr_global_daily_1851_1860.nc
server      = 'https://files.isimip.org/ISIMIP3a/InputData/climate/atmosphere/' + climate_scenario + '/global/daily/historical/'
num_periods = len(periods)

if not os.path.exists('../data'):
	os.mkdir('../data')
if not os.path.exists('../data/isimip3a'):
	os.mkdir('../data/isimip3a')
if not os.path.exists('../data/isimip3a/'+climate_forcing):
	os.mkdir('../data/isimip3a/'+climate_forcing)

if size == 1:	
	for i in range(num_periods):
		for j in range(varnames):
			fname = climate_forcing.lower() + '_' + climate_scenario + '_' + varnames[j] + \
					'_global_daily_' + periods[i] + '.nc'
			if os.path.isfile('../data/isimip3a/'+climate_forcing + '/' + fname):
				print(fname + ' is already downloaded!')
			else:
				url   = server + climate_forcing + '/' + fname 
				print('Downloading ' + fname)
				urlretrieve(url, '../data/isimip3a/'+climate_forcing + '/' + fname)
else:
	period = periods[rank]
	for j in range(varnames):
		fname = climate_forcing.lower() + '_' + climate_scenario + '_' + varnames[j] + \
				'_global_daily_' + period + '.nc'
		if os.path.isfile('../data/isimip3a/'+climate_forcing + '/' + fname):
			print(fname + ' is already downloaded!')
		else:
			url   = server + climate_forcing + '/' + fname 
			print('At rank = ' + str(rank) + ': Downloading ' + fname)
			urlretrieve(url, '../data/isimip3a/'+climate_forcing + '/' + fname)


