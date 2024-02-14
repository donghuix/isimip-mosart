from netCDF4 import Dataset
import numpy as np
import getpass
from datetime import datetime

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
	var['QDRAI']   = ncid.createVariable('QDRAI',   np.float64, ('time', 'lat', 'lon'),fill_value=0)
	var['QOVER']   = ncid.createVariable('QOVER',   np.float64, ('time', 'lat', 'lon'),fill_value=0)
	var['QRUNOFF'] = ncid.createVariable('QRUNOFF', np.float64, ('time', 'lat', 'lon'),fill_value=0)
	var['lat']     = ncid.createVariable('lat',     np.float64, ('lat',))
	var['lon']     = ncid.createVariable('lon',     np.float64, ('lon',))
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
	
def create_datm2d(fname,data,time,lat,lon,startdate,isleap):
	
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
    ncid.createDimension('scalar',1)
	
    varnames = list(data.keys())

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    var = dict()
    if varnames[0] == 'Prec':
        var['Prec'] = ncid.createVariable('PRECTmms', np.float64, ('time', 'lat', 'lon'),fill_value=1e20)
        var['Prec'].setncattr('long_name', 'PRECTmms total precipitation')
        var['Prec'].setncattr('units', 'mm H2O / sec')
        var['Prec'].setncattr('mode', 'time-dependent')
    elif varnames[0] == 'FSDS':
        var['FSDS'] = ncid.createVariable('FSDS', np.float64, ('time', 'lat', 'lon'),fill_value=1e20)
        var['FSDS'].setncattr('long_name', 'total incident solar radiation')
        var['FSDS'].setncattr('units', 'W/m**2')
        var['FSDS'].setncattr('mode', 'time-dependent')
    elif len(varnames) == 4 and 'PSRF' in varnames and 'TBOT' in varnames and 'WIND' in varnames and 'QBOT' in varnames:  
        var['PSRF'] = ncid.createVariable('PSRF', np.float64, ('time', 'lat', 'lon'),fill_value=1e20)
        var['PSRF'].setncattr('long_name', 'surface pressure at the lowest atm level')
        var['PSRF'].setncattr('units', 'Pa')
        var['PSRF'].setncattr('mode', 'time-dependent')

        var['TBOT'] = ncid.createVariable('TBOT', np.float64, ('time', 'lat', 'lon'),fill_value=1e20)
        var['TBOT'].setncattr('long_name', 'temperature at the lowest atm level')
        var['TBOT'].setncattr('units', 'K')
        var['TBOT'].setncattr('mode', 'time-dependent')

        var['WIND'] = ncid.createVariable('WIND', np.float64, ('time', 'lat', 'lon'),fill_value=1e20)
        var['WIND'].setncattr('long_name', 'wind at the lowest atm level')
        var['WIND'].setncattr('units', 'm/s')
        var['WIND'].setncattr('mode', 'time-dependent')

        var['QBOT'] = ncid.createVariable('QBOT', np.float64, ('time', 'lat', 'lon'),fill_value=1e20)
        var['QBOT'].setncattr('long_name', 'specific humidity at the lowest atm level')
        var['QBOT'].setncattr('units', 'kg/kg')
        var['QBOT'].setncattr('mode', 'time-dependent')
    else:
        raise Exception("Variables and variable names are not correct!")    
    
    var['time'] = ncid.createVariable('time', np.float64, ('time',))
    var['time'].setncattr('long_name', 'time')
    if isleap:
        var['time'].setncattr('calendar', 'gregorian')
    else:
        var['time'].setncattr('calendar', 'noleap')
    var['time'].setncattr('units', 'days since ' + startdate + ' 00:00:00')

    var['LATIXY'] = ncid.createVariable('lat', np.float64, ('lat',))
    var['LATIXY'].setncattr('long_name', 'latitude')
    var['LATIXY'].setncattr('units', 'degrees_north')
    var['LATIXY'].setncattr('mode', 'time-dependent')

    var['LONGXY']  = ncid.createVariable('lon', np.float64, ('lon',))
    var['LONGXY'].setncattr('long_name', 'longitude')
    var['LONGXY'].setncattr('units', 'degrees_east')
    var['LONGXY'].setncattr('mode', 'time-dependent')

    var['EDGEE']  = ncid.createVariable('EDGEE', np.float64, ('scalar',))
    var['EDGEE'].setncattr('long_name', 'eastern edge in atmospheric data')
    var['EDGEE'].setncattr('units', 'degrees_east')
    var['EDGEE'].setncattr('mode', 'time-dependent')

    var['EDGEW']  = ncid.createVariable('EDGEW', np.float64, ('scalar',))
    var['EDGEW'].setncattr('long_name', 'western edge in atmospheric data')
    var['EDGEW'].setncattr('units', 'degrees_east')
    var['EDGEW'].setncattr('mode', 'time-dependent')

    var['EDGES']  = ncid.createVariable('EDGES', np.float64, ('scalar',))
    var['EDGES'].setncattr('long_name', 'southern edge in atmospheric data')
    var['EDGES'].setncattr('units', 'degrees_north')
    var['EDGES'].setncattr('mode', 'time-dependent')

    var['EDGEN']  = ncid.createVariable('EDGEN', np.float64, ('scalar',))
    var['EDGEN'].setncattr('long_name', 'northern edge in atmospheric data')
    var['EDGEN'].setncattr('units', 'degrees_north')
    var['EDGEN'].setncattr('mode', 'time-dependent')

    user_name = getpass.getuser()
    ncid.setncattr('Created_by',user_name)
    ncid.setncattr('Created_on',datetime.now().strftime('%c'))

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Copy variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    if varnames[0] == 'Prec':
        var['Prec'][:] = data['Prec']
    elif varnames[0] == 'FSDS':
        var['FSDS'][:] = data['FSDS']
    elif len(varnames) == 4 and 'PSRF' in varnames and 'TBOT' in varnames and 'WIND' in varnames and 'QBOT' in varnames:
        var['PSRF'][:] = data['PSRF']
        var['TBOT'][:] = data['TBOT']
        var['WIND'][:] = data['WIND']
        var['QBOT'][:] = data['QBOT']
    
    var['time'][:]    = time
    var['LATIXY'][:]  = lat
    var['LONGXY'][:]  = lon

    ncid.close()