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
        var['Prec'] = ncid.createVariable('PRECTmms', np.float64, ('time', 'lat', 'lon'))
        var['Prec'].setncattr('long_name', 'PRECTmms total precipitation')
        var['Prec'].setncattr('units', 'mm H2O / sec')
        var['Prec'].setncattr('mode', 'time-dependent')
    elif varnames[0] == 'FSDS':
        var['FSDS'] = ncid.createVariable('FSDS', np.float64, ('time', 'lat', 'lon'))
        var['FSDS'].setncattr('long_name', 'total incident solar radiation')
        var['FSDS'].setncattr('units', 'W/m**2')
        var['FSDS'].setncattr('mode', 'time-dependent')
    elif len(varnames) == 4 and 'PSRF' in varnames and 'TBOT' in varnames and 'WIND' in varnames and 'QBOT' in varnames:  
        var['PSRF'] = ncid.createVariable('PSRF', np.float64, ('time', 'lat', 'lon'))
        var['PSRF'].setncattr('long_name', 'surface pressure at the lowest atm level')
        var['PSRF'].setncattr('units', 'Pa')
        var['PSRF'].setncattr('mode', 'time-dependent')

        var['TBOT'] = ncid.createVariable('TBOT', np.float64, ('time', 'lat', 'lon'))
        var['TBOT'].setncattr('long_name', 'temperature at the lowest atm level')
        var['TBOT'].setncattr('units', 'K')
        var['TBOT'].setncattr('mode', 'time-dependent')

        var['WIND'] = ncid.createVariable('WIND', np.float64, ('time', 'lat', 'lon'))
        var['WIND'].setncattr('long_name', 'wind at the lowest atm level')
        var['WIND'].setncattr('units', 'm/s')
        var['WIND'].setncattr('mode', 'time-dependent')

        var['QBOT'] = ncid.createVariable('QBOT', np.float64, ('time', 'lat', 'lon'))
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

def create_datm1d(fname,data,time,lat,lon,startdate,isleap):
	
    ncid = Dataset(fname, 'w')
    nlat,nlon = lat.shape
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
        var['Prec'] = ncid.createVariable('PRECTmms', np.float64, ('time', 'lat', 'lon'))
        var['Prec'].setncattr('long_name', 'PRECTmms total precipitation')
        var['Prec'].setncattr('units', 'mm H2O / sec')
        var['Prec'].setncattr('mode', 'time-dependent')
    elif varnames[0] == 'FSDS':
        var['FSDS'] = ncid.createVariable('FSDS', np.float64, ('time', 'lat', 'lon'))
        var['FSDS'].setncattr('long_name', 'total incident solar radiation')
        var['FSDS'].setncattr('units', 'W/m**2')
        var['FSDS'].setncattr('mode', 'time-dependent')
    elif len(varnames) == 4 and 'PSRF' in varnames and 'TBOT' in varnames and 'WIND' in varnames and 'QBOT' in varnames:  
        var['PSRF'] = ncid.createVariable('PSRF', np.float64, ('time', 'lat', 'lon'))
        var['PSRF'].setncattr('long_name', 'surface pressure at the lowest atm level')
        var['PSRF'].setncattr('units', 'Pa')
        var['PSRF'].setncattr('mode', 'time-dependent')

        var['TBOT'] = ncid.createVariable('TBOT', np.float64, ('time', 'lat', 'lon'))
        var['TBOT'].setncattr('long_name', 'temperature at the lowest atm level')
        var['TBOT'].setncattr('units', 'K')
        var['TBOT'].setncattr('mode', 'time-dependent')

        var['WIND'] = ncid.createVariable('WIND', np.float64, ('time', 'lat', 'lon'))
        var['WIND'].setncattr('long_name', 'wind at the lowest atm level')
        var['WIND'].setncattr('units', 'm/s')
        var['WIND'].setncattr('mode', 'time-dependent')

        var['QBOT'] = ncid.createVariable('QBOT', np.float64, ('time', 'lat', 'lon'))
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

    var['LATIXY'] = ncid.createVariable('lat', np.float64, ('lat','lon'))
    var['LATIXY'].setncattr('long_name', 'latitude')
    var['LATIXY'].setncattr('units', 'degrees_north')
    var['LATIXY'].setncattr('mode', 'time-dependent')

    var['LONGXY']  = ncid.createVariable('lon', np.float64, ('lat','lon'))
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

def create_landuse_timeseries(fin,irrigated,rainfed,urbanarea,yr_start,yr_end,scenario):

    ncid_inq = Dataset(fin, 'r')
    fout = '../inputdata/landuse.timeseries_isimip3a_' + scenario + '_simyr' + str(yr_start) + '_' + str(yr_end)
    ncid = Dataset(fout, 'w')
    nt,nlat,nlon = irrigated.shape

    assert(nt == yr_end-yr_start+1)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define dimensions
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ncid.createDimension('lsmlat',nlat)
    ncid.createDimension('lsmlon',nlon)
    ncid.createDimension('time', None)
    ncid.createDimension('natpft',15)
    ncid.createDimension('numurbl', 3)
    ncid.createDimension('nchar', 256)
    ncid.createDimension('cft', 2)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Define variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    var = dict()
    for varname in ncid_inq.variables:
        dtype = ncid_inq.variables[varname].dtype
        dims  = ncid_inq.variables[varname].dimensions
        if varname == 'PCT_URBAN':
            var[varname] = ncid.createVariable(varname, dtype, ('time', 'numurbl', 'lsmlat', 'lsmlon'))
        else:
            var[varname] = ncid.createVariable(varname, dtype, dims)
        for attname in ncid_inq.variables[varname].ncattrs():
            attvalue = ncid_inq.variables[varname].getncattr(attname)
            var[varname].setncattr(attname, attvalue)
    
    user_name = getpass.getuser()
    ncid.setncattr('Created_by',user_name)
    ncid.setncattr('Created_on',datetime.now().strftime('%c'))

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #                           Copy variables
    #
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    pct_crop    = irrigated + rainfed
    pct_cft     = np.empty((nt,2,nlat,nlon))
    pct_cft[:,0,:,:] = np.divide(rainfed   , pct_crop, out=np.zeros_like(rainfed )  , where=pct_crop!=0)
    pct_cft[:,1,:,:] = np.divide(irrigated , pct_crop, out=np.zeros_like(irrigated ), where=pct_crop!=0) 

    for varname in ncid_inq.variables:
        if varname == 'PCT_CROP':
            var['PCT_CROP'][:] = pct_crop
        elif varname == 'PCT_CFT':
            var['PCT_CFT'][:]  = pct_cft
        else:
            print(varname)
            var[varname][:]    =  ncid_inq.variables[varname][:]

    ncid.close()
    ncid_inq.close()

