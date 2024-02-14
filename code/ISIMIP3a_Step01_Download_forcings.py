import numpy as np
import os
from urllib.request import urlretrieve
from mpi4py import MPI
import netCDF4
from netCDF4 import Dataset
from datetime import date
from datetime import datetime
import getpass
import scipy.io
from create_nc import create_datm2d
from disaggregate_tpqw import disaggregate_tpqw
import math


comm = MPI.COMM_WORLD
size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()

climate_forcings  = ['GSWP3-W5E5', '20CRv3-W5E5', '20CRv3-ERA5', '20CRv3', 'CHELSA-W5E5v1.0']
# From higher priority to lower priority
climate_scenarios = ['obsclim', 'spinclim','counterclim','transclim']
varnames          = ['huss', 'pr', 'ps', 'rsds', 'sfcwind', 'tas', 'tasmax', 'tasmin']
# Specific humidity [kg kg-1], Precipitation flux [kg m-2 s-1], Surface air pressure [Pa], 
# Surface downwelling shortwave flux in air [W m-2], Wind speed [m s-1], Air temperature [k],
# Max air temperature, Min air temperature 

climate_forcing  = climate_forcings[0]
climate_scenario = climate_scenarios[1]

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

if rank == 0:
	if not os.path.exists('../data'):
		os.mkdir('../data')
	if not os.path.exists('../data/isimip3a'):
		os.mkdir('../data/isimip3a')
	if not os.path.exists('../data/isimip3a/'+climate_forcing):
		os.mkdir('../data/isimip3a/'+climate_forcing)
	if not os.path.exists('../data/isimip3a/'+climate_forcing+'/'+climate_scenario):
		os.mkdir('../data/isimip3a/'+climate_forcing+'/'+climate_scenario)
	if not os.path.exists('../data/datm/'+climate_forcing):
		os.mkdir('../data/datm/'+climate_forcing)
	if not os.path.exists('../data/datm/'+climate_forcing+'/'+climate_scenario):
		os.mkdir('../data/datm/'+climate_forcing+'/'+climate_scenario)

# (1). Download daily atmospheric forcings from ISIMIP3a
if size == 1:	
	for i in range(num_periods):
		for j in range(len(varnames)):
			fname = climate_forcing.lower() + '_' + climate_scenario + '_' + varnames[j] + \
					'_global_daily_' + periods[i] + '.nc'
			if os.path.isfile('../data/isimip3a/'+climate_forcing + '/' + climate_scenario + '/' + fname):
				print(fname + ' is already downloaded!')
			else:
				url   = server + climate_forcing + '/' + fname 
				print('Downloading ' + fname)
				urlretrieve(url, '../data/isimip3a/'+climate_forcing + '/' + climate_scenario + '/' + fname)
else:
	period = periods[rank]
	for j in range(len(varnames)):
		fname = climate_forcing.lower() + '_' + climate_scenario + '_' + varnames[j] + \
				'_global_daily_' + period + '.nc'
		if os.path.isfile('../data/isimip3a/'+climate_forcing + '/' + climate_scenario + '/' + fname):
			print(fname + ' is already downloaded!')
		else:
			url   = server + climate_forcing + '/' + fname 
			print('At rank = ' + str(rank) + ': Downloading ' + fname)
			urlretrieve(url, '../data/isimip3a/'+climate_forcing + '/' + climate_scenario + '/' + fname)

		comm.Barrier()

# (2). Disaggregate daily to subdaily and generate for DATM format
res = '0.5x0.5'
if datetime.now().month < 10:
	timetag = 'c' + str(datetime.now().year-2000) + '0' + str(datetime.now().month)
else:
	timetag = 'c' + str(datetime.now().year-2000) + str(datetime.now().month)

if size == 1:
	nps = len(periods)
else:
	nps = 1

for i in range(nps):
	fdir  = '../data/isimip3a/'+climate_forcing + '/' + climate_scenario + '/'
	if size == 1:
		period = periods[i]
	else:
		period = periods[rank]

	fprec = climate_forcing.lower() + '_' + climate_scenario + '_pr_global_daily_'      + period + '.nc'
	fsolr = climate_forcing.lower() + '_' + climate_scenario + '_rsds_global_daily_'    + period + '.nc'
	ftemp = climate_forcing.lower() + '_' + climate_scenario + '_tas_global_daily_'     + period + '.nc'
	ftmax = climate_forcing.lower() + '_' + climate_scenario + '_tasmax_global_daily_'  + period + '.nc'
	ftmin = climate_forcing.lower() + '_' + climate_scenario + '_tasmin_global_daily_'  + period + '.nc'
	fpres = climate_forcing.lower() + '_' + climate_scenario + '_ps_global_daily_'      + period + '.nc'
	fhuss = climate_forcing.lower() + '_' + climate_scenario + '_huss_global_daily_'    + period + '.nc'
	fwind = climate_forcing.lower() + '_' + climate_scenario + '_sfcwind_global_daily_' + period + '.nc'

	yr_start = int(period[:4])
	yr_end   = int(period[5:])
	dn1      = date.toordinal(date(yr_start,1,1))
	dn2      = date.toordinal(date(yr_end,12,31))
	yr = np.empty((dn2-dn1+1,), dtype=np.int64)
	mo = np.empty((dn2-dn1+1,), dtype=np.int64)
	dy = np.empty((dn2-dn1+1,), dtype=np.int64)
	for i in np.arange(dn1,dn2+1,1):
		dd  = date.fromordinal(i)
		idx = i-dn1
		yr[idx] = dd.year
		mo[idx] = dd.month
		dy[idx] = dd.day
	
	# Prec and Solr use daily.
	# TPQW use 3-hourly, and spline interpolation for temperature.
	ncprec = netCDF4.Dataset(fdir + fprec)
	ncsolr = netCDF4.Dataset(fdir + fsolr)
	nctemp = netCDF4.Dataset(fdir + ftemp)
	nctmax = netCDF4.Dataset(fdir + ftmax)
	nctmin = netCDF4.Dataset(fdir + ftmin)
	ncpres = netCDF4.Dataset(fdir + fpres)
	nchuss = netCDF4.Dataset(fdir + fhuss)
	ncwind = netCDF4.Dataset(fdir + fwind)

	mat = scipy.io.loadmat('../data/sunrise_set_isimip3a.mat')
	hr_max = mat['hr_max']
	hr_min = mat['hr_min']

	for iy in np.arange(min(yr),max(yr)+1,1):
		for im in np.arange(1,12+1,1):
			if iy == min(yr) and im == 1:
				longxy = ncprec.variables['lon'][:]
				latixy = ncprec.variables['lat'][:]
				assert(latixy[0] > 80 and latixy[-1] < -80)
				# ISIMIP3a lat varies from 90 to -90, need to change it to -90 to 90
				latixy = np.arange(-89.75,90,0.5)

			if im < 10:
				datetag = str(iy) + '-0' + str(im)
			else:
				datetag = str(iy) + '-' + str(im)

			dprec = 'clmforc.' + climate_forcing.lower() + '.' + climate_scenario + '.' + \
						timetag + '.' + res + '.Prec.' + datetag + '.nc'
			dsolr = 'clmforc.' + climate_forcing.lower() + '.' + climate_scenario + '.' + \
						timetag + '.' + res + '.Solr.' + datetag + '.nc'
			
			if  os.path.isfile('../data/datm/'+climate_forcing + '/' + climate_scenario + '/' + dprec) and \
				os.path.isfile('../data/datm/'+climate_forcing + '/' + climate_scenario + '/' + dsolr):
				print(dprec + ' and ' + dsolr + ' are already processed!')
			else:
				print('Processing ' + dprec + ' and ' + dsolr)
				ind  = np.where(np.logical_and(yr == iy, mo == im))[0]
				prec = {"Prec": np.flip(ncprec.variables['pr'][ind,:,:],axis=1)}
				solr = {"FSDS": np.flip(ncsolr.variables['rsds'][ind,:,:],axis=1)}
				numd = len(ind)
				tday = np.arange(0.5,numd+1-0.5,1)

				create_datm2d('../data/datm/'+climate_forcing + '/' + climate_scenario + '/' + dprec,prec,tday,latixy,longxy,datetag+'-01',True)
				create_datm2d('../data/datm/'+climate_forcing + '/' + climate_scenario + '/' + dsolr,solr,tday,latixy,longxy,datetag+'-01',True)

			dtpqw = 'clmforc.' + climate_forcing.lower() + '.' + climate_scenario + '.' + \
						timetag + '.' + res + '.TPQW.' + datetag + '.nc'

			if  os.path.isfile('../data/datm/'+climate_forcing + '/' + climate_scenario + '/' + dtpqw):
				print(dtpqw + ' are already processed!')
			else:
				print('Processing ' + dtpqw)
				ind  = np.where(np.logical_and(yr == iy, mo == im))[0]

				tday = np.arange(0.5,len(ind),1)
				dt       = 3 / 24
				t3hr = np.arange(dt/2,len(ind),dt)

				temp = nctemp.variables['tas'][ind,:,:]
				tmax = nctmax.variables['tasmax'][ind,:,:]
				tmin = nctmin.variables['tasmin'][ind,:,:]
				pres = ncpres.variables['ps'][ind,:,:]
				huss = nchuss.variables['huss'][ind,:,:]
				wind = ncwind.variables['sfcwind'][ind,:,:]

				nt,n,m = temp.shape
				temp3hr = np.empty((nt*8,n,m))
				pres3hr = np.empty((nt*8,n,m))
				huss3hr = np.empty((nt*8,n,m))
				wind3hr = np.empty((nt*8,n,m))
				for j in range(n):
					for i in range(m):
						if np.isnan(hr_max[i,j,im-1]) or np.isnan(hr_min[i,j,im-1]):
							hmax = 5
							hmin = 2
						elif int(math.floor(hr_max[i,j,im-1]/3)) == int(math.floor(hr_min[i,j,im-1]/3)):
							ll = 1
							if hr_max[i,j,im-1] >= hr_min[i,j,im-1]:
								hmin = int(math.floor(hr_min[i,j,im-1]/3))
								hmax = hmin + ll
							elif hr_max[i,j,im-1] < hr_min[i,j,im-1]:
								hmax = int(math.floor(hr_max[i,j,im-1]/3))
								hmin = hmax + ll
						else:
							hmax = int(math.floor(hr_max[i,j,im-1]/3))
							hmin = int(math.floor(hr_min[i,j,im-1]/3))

						if not np.ma.isMaskedArray(temp[0,j,i]):
							temp3hr[:,j,i], pres3hr[:,j,i], huss3hr[:,j,i], wind3hr[:,j,i] = \
							disaggregate_tpqw(tday,temp[:,j,i],tmax[:,j,i],tmin[:,j,i],pres[:,j,i], \
												huss[:,j,i],wind[:,j,i],hmax,hmin,t3hr)

				tpqw = {'PSRF': np.flip(pres3hr,axis=1), \
						'TBOT': np.flip(temp3hr,axis=1), \
						'WIND': np.flip(wind3hr,axis=1), \
						'QBOT': np.flip(huss3hr,axis=1)}
				create_datm2d('../data/datm/'+climate_forcing + '/' + climate_scenario + '/' + dtpqw,tpqw,t3hr,latixy,longxy,datetag+'-01',True)

	ncprec.close()
	ncsolr.close()
	nctemp.close()
	nctmax.close()
	nctmin.close()
	ncpres.close()
	nchuss.close()
	ncwind.close()



