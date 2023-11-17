import numpy as np
import os
from urllib.request import urlretrieve

impact_models    = ['CLASSIC', 'CWatM', 'H08', 'HydroPy', 'JULES-W2', 'JULES-W2-DDM30', 'MIROC-INTEG-LAND']
climate_forcing  = 'gswp3-w5e5'
climate_scenario = 'obsclim'
periods          = ['1901_1910', '1911_1920', '1921_1930', '1931_1940', '1941_1950', \
                    '1951_1960', '1961_1970', '1971_1980', '1981_1990', '1991_2000', \
                    '2001_2010', '2011_2019']
varname     = 'qtot'
server      = 'https://files.isimip.org/ISIMIP3a/OutputData/water_global/'
num_models  = len(impact_models)
num_periods = len(periods)

if not os.path.exists('../data'):
	os.mkdir('../data')
if not os.path.exists('../data/isimip3a'):
	os.mkdir('../data/isimip3a')

for i in range(num_models):
	if not os.path.exists('../data/isimip3a/'+impact_models[i]):
		os.mkdir('../data/isimip3a/'+impact_models[i])

	for j in range(num_periods):
		model = impact_models[i]
		fname = model.lower() + '_' + climate_forcing.lower() + '_' + climate_scenario + \
		        '_histsoc_default_' + varname + '_global_daily_' + periods[j] + '.nc'

		url   = server + impact_models[i] + '/' + climate_forcing + '/historical/' + fname 

		print('Downloading ' + fname)
		urlretrieve(url, '../data/isimip3a/'+impact_models[i] + '/' + fname)
