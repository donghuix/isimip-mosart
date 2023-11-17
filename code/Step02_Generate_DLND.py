import numpy as np
import os
import netCDF4
from netCDF4 import Dataset
from datetime import date
from datetime import datetime
import getpass

def main():
	impact_models    = ['CLASSIC', 'CWatM', 'H08', 'HydroPy', 'JULES-W2', 'JULES-W2-DDM30', 'MIROC-INTEG-LAND']
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

def create_dlnd2d(fname,qtot,time,lat,lon,startdate,isleap):
	ncid = Dataset(fname, 'w')
	nlon = len(lon)
	nlat = len(lat)
	# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define dimensions
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	ncid.createDimension('time', None)
	ncid.createDimension('lat',nlat)
	ncid.createDimension('lon',nlon)
	# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	var = dict()
	var['QDRAI']   = ncid.createVariable('QDRAI',   np.float32, ('time', 'lat', 'lon'))
	var['QOVER']   = ncid.createVariable('QOVER',   np.float32, ('time', 'lat', 'lon'))
	var['QRUNOFF'] = ncid.createVariable('QRUNOFF', np.float32, ('time', 'lat', 'lon'))
	var['lat']     = ncid.createVariable('lat',     np.float32, ('lat',))
	var['lon']     = ncid.createVariable('lon',     np.float32, ('lon',))
	var['time']    = ncid.createVariable('time',    np.float64, ('time',))
	var['QDRAI'].setncattr('standard_name', 'subsurface runoff')
	var['QDRAI'].setncattr('units', 'mm/s')
	var['QOVER'].setncattr('standard_name', 'surface runoff')
	var['QOVER'].setncattr('units', 'mm/s')
	var['QRUNOFF'].setncattr('standard_name', 'total runoff')
	var['QRUNOFF'].setncattr('units', 'mm/s')
	var['time'].setncattr('standard_name', 'time')
	if isleap:
		var['time'].setncattr('calendar', 'gregorian')
	else:
		var['time'].setncattr('calendar', 'noleap')
	var['time'].setncattr('units', 'days since ' + startdate + ' 00:00:00')
	var['time'].setncattr('axis', 'T')
	var['lat'].setncattr('standard_name', 'latitude')
	var['lat'].setncattr('long_name', 'latitude')
	var['lat'].setncattr('units', 'degrees_north')
	var['lat'].setncattr('axis','Y')
	var['lon'].setncattr('standard_name', 'longitude')
	var['lon'].setncattr('long_name', 'longitude')
	var['lon'].setncattr('units', 'degrees_east')
	var['lon'].setncattr('axis','X')
	

	user_name = getpass.getuser()
	ncid.setncattr('Created_by',user_name)
	ncid.setncattr('Created_on',datetime.now().strftime('%c'))

	# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Copy variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	qdrai = qtot / 2.0
	qover = qtot - qdrai
	var['QDRAI'][:]   = qdrai
	var['QOVER'][:]   = qover
	var['QRUNOFF'][:] = qtot
	var['time'][:]    = time
	var['lat'][:]     = lat
	var['lon'][:]     = lon

	ncid.close()

if __name__ == '__main__':
    main()