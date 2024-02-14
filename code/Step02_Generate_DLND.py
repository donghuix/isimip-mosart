import numpy as np
import os
import netCDF4
from netCDF4 import Dataset
from datetime import date
from datetime import datetime
import create_nc
import getpass

def main():
	impact_models    = ['H08'] #['CLASSIC', 'CWatM', 'H08', 'HydroPy', 'JULES-W2', 'JULES-W2-DDM30', 'MIROC-INTEG-LAND']
	climate_forcing  = 'gswp3-w5e5'
	climate_scenario = 'obsclim'
	periods          = ['1901_1910', '1911_1920', '1921_1930', '1931_1940', '1941_1950', \
	                    '1951_1960', '1961_1970', '1971_1980', '1981_1990', '1991_2000', \
	                    '2001_2010', '2011_2019']
	varname     = 'qtot'
	num_models  = len(impact_models)
	num_periods = len(periods)

	if not os.path.exists('../data'):
		os.mkdir('../data')
	if not os.path.exists('../data/dlnd'):
		os.mkdir('../data/dlnd')

	for i in range(num_models):
		if not os.path.exists('../data/dlnd/'+impact_models[i]):
			os.mkdir('../data/dlnd/'+impact_models[i])

		for j in range(num_periods):
			model = impact_models[i]
			fname = model.lower() + '_' + climate_forcing.lower() + '_' + climate_scenario + \
					'_histsoc_default_' + varname + '_global_daily_' + periods[j] + '.nc'
			
			print('Processing ' + model + ' ' + periods[j])

			ncio = netCDF4.Dataset('../data/isimip3a/'+impact_models[i] + '/' + fname)
			qtot = ncio.variables[varname][:] # UNIT: [kg m-2 s-1] --> [mm/s]
			lon  = ncio.variables['lon'][:]
			lat  = ncio.variables['lat'][:]
			assert(lon[0] < 0)
			assert(lat[1] < lat[0])
			# For DLND, need to shift the lon from -179.75~179.75 to 0.25~359.75 [11/29/2023, no need to convert to 0 to 360]
			# ISIMIP3a lat varies from 90 to -90, need to change it to -90 to 90
			#lon  = np.arange(0.25,360,0.5)
			lat  = np.arange(-89.75,90,0.5)
			qtot = np.flip(qtot,axis=1)
			yr_start = int(periods[j][:4])
			yr_end   = int(periods[j][5:])
			dn1      = date.toordinal(date(yr_start,1,1))
			dn2      = date.toordinal(date(yr_end,12,31))
			assert(dn2-dn1+1 == qtot.shape[0])
			#dn       = np.arange(dn1,dn2+1,1)
			dn       = np.arange(0,dn2-dn1+1,1)
			dn       = dn.astype('float64') 
			startdate = str(yr_start) + '-01-01'
			fout      = '../data/dlnd/'+impact_models[i]+'/'+model.lower()+'.daily.'+periods[j]+'.nc'
			create_dlnd2d(fout,qtot,dn,lat,lon,startdate,True)
			ncio.close()

if __name__ == '__main__':
    main()