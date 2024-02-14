import numpy as np
import os
from urllib.request import urlretrieve
import netCDF4

scenarios = ['1901soc','2015soc','histsoc']
datasets  = ['15crops','urbanareas']

if not os.path.exists('../data'):
	os.mkdir('../data')
if not os.path.exists('../data/isimip3a'):
	os.mkdir('../data/isimip3a')
if not os.path.exists('../data/isimip3a/landuse_and_irrigation'):
	os.mkdir('../data/isimip3a/landuse_and_irrigation')
	
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