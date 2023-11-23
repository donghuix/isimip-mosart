import sys, getopt
import numpy as np
from matplotlib import pyplot as plt
import netCDF4
import csv
import glob 

def main(argv):

    # Default options
    yr1   = 1979
    yr2   = 2008
    model = 'H08'
    debug = False

    opts, args = getopt.getopt(argv,"hm:d:s:e:",["ifile=","ofile="])
    for opt, arg in opts:
        if opt == '-h':
            print ('Step04_validate_MOSART.py -m <model name> -d <debug option> -s <start year> -e <end year>')
            sys.exit()
        elif opt in ("-m", "--model"):
            model = arg
        elif opt in ("-d", "--debug"):
            if arg == 'True':
                debug = True
            elif arg == 'False':
                debug = False
            else:
                raise Exception(arg + ' is not available for -d')
        elif opt in ("-s", "--start"):
            yr1 = int(arg)
        elif opt in ("-e", "--end"):
            yr2 = int(arg)

    rundir = '/compyfs/xudo627/e3sm_scratch/Global_DLND_MOSART_GRFR_7b57911.2023-11-14-210958/run/'

    gsim_no, row, col = read_gsim_index()
    
    q_sim,  yrs_sim,  mos_sim  = read_mosart_outputs(rundir, yr1, yr2, row, col)

    ns = len(row) # Number of gauges for evaluation
    for i in range(ns):

        q_gsim, yrs_gsim, mos_gsim = read_gsim_mon(gsim_no[i])
        ind_sim, ind_gsim, no_overlap  = match_time_series(yrs_sim,mos_sim,yrs_gsim,mos_gsim)

        # compute evaluation metric
        if no_overlap:
        else:
            obs = q_gsim[ind_gsim]
            sim = q_sim[ind_sim,i]
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Functions
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def read_gsim_index():
    with open('gsim_index.csv', mode ='r') as file:
        csvFile = csv.reader(file)
        num_of_stations = sum(1 for lines in csvFile)
        gsim_no = [''] * num_of_stations
        row = np.empty((num_of_stations, ),dtype=int)
        col = np.empty((num_of_stations, ),dtype=int)

    with open('gsim_index.csv', mode ='r') as file:
        csvFile = csv.reader(file)
        k = 0
        for lines in csvFile:
            row[k] = lines[4]
            col[k] = lines[5]
            gsim_no[k] = lines[0]
            k = k + 1

    return gsim_no, row, col

def read_mosart_outputs(rundir, yr1, yr2, row, col):

    num_of_stations = len(row)

    qlnd = np.empty(((yr2-yr1+1)*12,360,720)) # discharge over land
    qocn = np.empty(((yr2-yr1+1)*12,360,720)) # discharge to ocean

    assert(len(glob.glob(rundir + '*.mosart.h0.*.nc')) == (yr2 - yr1 + 1)*12)

    k = 0
    for files in sorted(glob.glob(rundir + '*.mosart.h0.*.nc')):
        print(files)
        ncio = netCDF4.Dataset(files)
        qlnd[k,:,:] = ncio.variables['RIVER_DISCHARGE_OVER_LAND_LIQ'][:] # UNIT: [m^{3}/s]
        qocn[k,:,:] = ncio.variables['RIVER_DISCHARGE_TO_OCEAN_LIQ'][:] # UNIT: [m^{3}/s]
        k = k + 1

    qsim = np.empty(((yr2-yr1+1)*12,num_of_stations)) # simulated discharge [m^{3}/s]
    for i in range(num_of_stations):
        if qlnd[0,col[i],row[i]] > 1e10:
            qsim[:,i] = qocn[:,col[i],row[i]]
        elif qocn[0,col[i],row[i]] > 1e10:
            qsim[:,i] = qlnd[:,col[i],row[i]]

    yrs_sim = np.empty(((yr2-yr1+1)*12, ),dtype=int)
    mos_sim = np.empty(((yr2-yr1+1)*12, ),dtype=int)
    k = 0
    for yr in np.arange(yr1,yr2+1,1):
        for mo in np.arange(1,13,1):
            yrs_sim[k] = yr
            mos_sim[k] = mo
            k = k + 1

    return qsim, yrs_sim, mos_sim, qlnd, qocn

def read_gsim_mon(station):
    # read monthly GSIM streamflow indices
    fname = '../data/GSIM_indices/TIMESERIES/monthly/' + station + '.mon'
    nlines = -1
    for line in open(fname):
        li=line.strip()
        if not li.startswith("#"):
            nlines = nlines + 1

    yrs   = np.empty((nlines, ),dtype=int)
    mos   = np.empty((nlines, ),dtype=int)
    qgsim = np.empty((nlines, ))

    k = 0
    for line in open(fname):
        li=line.strip()
        if not li.startswith("#"):
            if k > 0:
                yrs[k-1]   = int(line.split(',\t')[0][:4])
                mos[k-1]   = int(line.split(',\t')[0][5:7])
                if line.split(',\t')[1] == 'NA':
                    qgsim[k-1] = np.nan
                else:
                    qgsim[k-1] = float(line.split(',\t')[1])
                print(qgsim[k-1])
            k = k + 1

    return qgsim, yrs, mos, 

def match_time_series(yrs1,mos1,yrs2,mos2):
    # find the index for two time series to match
    no_overlap = False
    if np.max(yrs1) < np.min(yrs2) or np.max(yrs2) < np.min(yrs1):
        no_overlap = True
    else:
        ind1 = []
        ind2  = []
        if np.min(yrs1) >= np.min(yrs2):
            for i in range(len(yrs1)):
                ind = np.where(np.logical_and(yrs2 == yrs1[i], mos2 == mos1[i]))[0]
                if len(ind) > 0:
                    ind2.append(ind[0])
                    ind1.append(i)

        elif np.min(yrs1) < np.min(yrs2):
            for i in range(len(yrs2)):
                ind = np.where(np.logical_and(yrs1 == yrs2[i], mos1 == mos2[i]))[0]
                if len(ind) > 0:
                    ind1.append(ind[0])
                    ind2.append(i)
    
    return ind1, ind2, no_overlap

if __name__ == '__main__':
    main(sys.argv[1:])