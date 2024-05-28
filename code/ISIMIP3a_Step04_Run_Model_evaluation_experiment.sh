#!/bin/sh

RES=ELMMOS_USRDAT
COMPSET=IELM
MACH=compy
COMPILER=intel
PROJECT=esmd

SCENARIO=$1  # obsclim, spinclim
tag=$2       # date tag for datm forcing
FORCING=GSWP3-W5E5

if [ $SCENARIO=='obsclim' ]
then
   yr_start=$((1901)) # 1901,    1801
   yr_end=$((2019))   # 2019,    1900
elif [ $SCENARIO=='spinclim' ]
then
   yr_start=$((1801)) # 1901,    1801
   yr_end=$((1900))   # 2019,    1900
fi

SRC_DIR=/qfs/people/xudo627/e3sm-master
CASE_DIR=${SRC_DIR}/cime/scripts

cd ..
wkdir=${PWD}
datmdir=${wkdir}/data/datm/${FORCING}/${SCENARIO}

cd ${SRC_DIR}

GIT_HASH=`git log -n 1 --format=%h`
CASE_NAME=ISIMIP3a_${FORCING}_${SCENARIO}_${GIT_HASH}.`date "+%Y-%m-%d-%H%M%S"`

cd ${SRC_DIR}/cime/scripts

./create_newcase \
-case ${CASE_NAME} \
-res ${RES} \
-mach ${MACH} \
-compiler ${COMPILER} \
-compset ${COMPSET} --project ${PROJECT}


cd ${CASE_DIR}/${CASE_NAME}

./xmlchange -file env_run.xml -id DOUT_S             -val FALSE
./xmlchange -file env_run.xml -id INFO_DBUG          -val 2

./xmlchange DATM_MODE=CLMGSWP3v1
./xmlchange CLM_USRDAT_NAME=test_r05_r05
./xmlchange LND_DOMAIN_FILE=domain.lnd.r05_isimip3a.nc
./xmlchange ATM_DOMAIN_FILE=domain.lnd.r05_isimip3a.nc
./xmlchange LND_DOMAIN_PATH=/compyfs/xudo627/projects/isimip-mosart/inputdata
./xmlchange ATM_DOMAIN_PATH=/compyfs/xudo627/projects/isimip-mosart/inputdata
./xmlchange CIME_OUTPUT_ROOT=${wkdir}/outputs

./xmlchange DATM_CLMNCEP_YR_END=${yr_end}
./xmlchange DATM_CLMNCEP_YR_START=${yr_start}
./xmlchange DATM_CLMNCEP_YR_ALIGN=1

./xmlchange DATM_CO2_TSERIES='20tr'
./xmlchange ELM_CO2_TYPE='diagnostic',CCSM_BGC='CO2A'
./xmlchange RUN_STARTDATE=${yr_start}-01-01

./xmlchange PIO_BUFFER_SIZE_LIMIT=67108864
./xmlchange STOP_N=$(((yr_end-yr_start+1)/2))
./xmlchange STOP_OPTION=nyears
./xmlchange JOB_QUEUE=slurm
./xmlchange RESUBMIT=1
./xmlchange NTASKS=400
./xmlchange JOB_WALLCLOCK_TIME=48:00:00

./preview_namelists

if [ "$SCENARIO" = "spinclim" ]; then

cat >> user_nl_mosart << EOF
frivinp_rtm = '/compyfs/xudo627/projects/isimip-mosart/inputdata/MOSART_global_half_20180721b.nc'
frivinp_mesh = 'UNDEFINED'
rtmhist_fincl1='RIVER_DISCHARGE_OVER_LAND_LIQ','RIVER_DISCHARGE_TO_OCEAN_LIQ','FLOODED_FRACTION','FLOODPLAIN_FRACTION'
inundflag = .true.
opt_elevprof = 1
EOF

cat >> user_nl_elm << EOF
fsurdat = '/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr1850_c211019.nc'
EOF

elif [ "$SCENARIO" = "obsclim" ]; then

cat >> user_nl_mosart << EOF
frivinp_rtm = '/compyfs/xudo627/projects/isimip-mosart/inputdata/MOSART_global_half_20180721b.nc'
frivinp_mesh = 'UNDEFINED'
finidat_rtm = '/compyfs/xudo627/projects/isimip-mosart/outputs/ISIMIP3a_GSWP3-W5E5_spinclim_5886da6.2024-02-12-220220/run/ISIMIP3a_GSWP3-W5E5_spinclim_5886da6.2024-02-12-220220.mosart.r.0101-01-01-00000.nc'
rtmhist_fincl1='RIVER_DISCHARGE_OVER_LAND_LIQ','RIVER_DISCHARGE_TO_OCEAN_LIQ','FLOODED_FRACTION','FLOODPLAIN_FRACTION'
inundflag = .true.
opt_elevprof = 1
EOF

cat >> user_nl_elm << EOF
fsurdat = '/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr1850_c211019.nc'
finidat = '/compyfs/xudo627/projects/isimip-mosart/outputs/ISIMIP3a_GSWP3-W5E5_spinclim_5886da6.2024-02-12-220220/run/ISIMIP3a_GSWP3-W5E5_spinclim_5886da6.2024-02-12-220220.elm.r.0101-01-01-00000.nc'
create_crop_landunit = .true.
flanduse_timeseries = '/compyfs/xudo627/projects/isimip-mosart/inputdata/landuse.timeseries_isimip3a_histsoc_simyr1850_2015'
check_dynpft_consistency = .false.
do_transient_pfts = .true.
EOF

fi

cat >> user_nl_datm << EOF
tintalgo = 'coszen', 'nearest', 'linear', 'linear', 'lower'
dtlimit=2.0e0,2.0e0,2.0e0,2.0e0,2.0e0
EOF

./case.setup
# ---------------------------------------------------------------------------- #
# **************************************************************************** #
# ---------------------------------------------------------------------------- #
files1=""
for i in $( eval echo {$yr_start..$yr_end} )
do
   for j in {1..12}
   do
      if [ $j -lt 10 ]
      then
         files1="${files1}clmforc.${FORCING,,}.${SCENARIO}.${tag}.0.5x0.5.Prec.$i-0$j.nc\n"
      else
         if [ $i == $yr_end ] && [ $j == 12 ]
         then
             files1="${files1}clmforc.${FORCING,,}.${SCENARIO}.${tag}.0.5x0.5.Prec.$i-$j.nc"
         else
             files1="${files1}clmforc.${FORCING,,}.${SCENARIO}.${tag}.0.5x0.5.Prec.$i-$j.nc\n"
         fi
      fi
   done
done

var=$((30+(yr_end-yr_start+1)*12-2))
echo $var
cp ${CASE_DIR}/${CASE_NAME}/CaseDocs/datm.streams.txt.CLMGSWP3v1.Precip ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip2
chmod +rw ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip2
sed "30,${var}d" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip2 > ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip
rm ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip2
chmod +rw ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip

perl -w -i -p -e "s@/compyfs/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v1.c170516/Precip@${datmdir}@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip
perl -w -i -p -e "s@/compyfs/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v1.c170516@/compyfs/xudo627/inputdata@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip
perl -w -i -p -e "s@domain.lnd.360x720_gswp3.0v1.c170606.nc@domain.lnd.360x720_isimip.3b.c211109.nc@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip
perl -w -i -p -e "s@clmforc.GSWP3.c2011.0.5x0.5.Prec.${yr_start}-01.nc@${files1}@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip
sed -i '/ZBOT/d' ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Precip
# ---------------------------------------------------------------------------- #
# **************************************************************************** #
# ---------------------------------------------------------------------------- #
files2=""
for i in $( eval echo {$yr_start..$yr_end} )
do
   for j in {1..12}
   do
      if [ $j -lt 10 ]
      then
         files2="${files2}clmforc.${FORCING,,}.${SCENARIO}.${tag}.0.5x0.5.Solr.$i-0$j.nc\n"
      else
         if [ $i == $yr_end ] && [ $j == 12 ]
         then
             files2="${files2}clmforc.${FORCING,,}.${SCENARIO}.${tag}.0.5x0.5.Solr.$i-$j.nc"
         else
             files2="${files2}clmforc.${FORCING,,}.${SCENARIO}.${tag}.0.5x0.5.Solr.$i-$j.nc\n"
         fi
      fi
   done
done

cp ${CASE_DIR}/${CASE_NAME}/CaseDocs/datm.streams.txt.CLMGSWP3v1.Solar ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar2
chmod +rw ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar2
sed "30,${var}d" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar2 > ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar
rm ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar2
chmod +rw ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar

perl -w -i -p -e "s@/compyfs/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v1.c170516/Solar@${datmdir}@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar
perl -w -i -p -e "s@/compyfs/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v1.c170516@/compyfs/xudo627/inputdata@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar
perl -w -i -p -e "s@domain.lnd.360x720_gswp3.0v1.c170606.nc@domain.lnd.360x720_isimip.3b.c211109.nc@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar
perl -w -i -p -e "s@clmforc.GSWP3.c2011.0.5x0.5.Solr.${yr_start}-01.nc@${files2}@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar
sed -i '/ZBOT/d' ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.Solar
# ---------------------------------------------------------------------------- #
# **************************************************************************** #
# ---------------------------------------------------------------------------- #
files3=""
for i in $( eval echo {$yr_start..$yr_end} )
do
   for j in {1..12}
   do
      if [ $j -lt 10 ]
      then
         files3="${files3}clmforc.${FORCING,,}.${SCENARIO}.${tag}.0.5x0.5.TPQW.$i-0$j.nc\n"
      else
         if [ $i == $yr_end ] && [ $j == 12 ]
         then
             files3="${files3}clmforc.${FORCING,,}.${SCENARIO}.${tag}.0.5x0.5.TPQW.$i-$j.nc"
         else
             files3="${files3}clmforc.${FORCING,,}.${SCENARIO}.${tag}.0.5x0.5.TPQW.$i-$j.nc\n"
         fi
      fi
   done
done

var=$((33+(yr_end-yr_start+1)*12-2))
cp ${CASE_DIR}/${CASE_NAME}/CaseDocs/datm.streams.txt.CLMGSWP3v1.TPQW ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW2
chmod +rw ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW2
sed '27d' ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW2 > ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW3
rm ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW2
chmod +rw ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW3
sed "33,${var}d" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW3 > ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW
rm ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW3
chmod +rw ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW

perl -w -i -p -e "s@/compyfs/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v1.c170516/TPHWL@${datmdir}@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW
perl -w -i -p -e "s@/compyfs/inputdata/atm/datm7/atm_forcing.datm7.GSWP3.0.5d.v1.c170516@/compyfs/xudo627/inputdata@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW
perl -w -i -p -e "s@domain.lnd.360x720_gswp3.0v1.c170606.nc@domain.lnd.360x720_isimip.3b.c211109.nc@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW
perl -w -i -p -e "s@clmforc.GSWP3.c2011.0.5x0.5.TPQWL.${yr_start}-01.nc@${files3}@" ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW
sed -i '/ZBOT/d' ${CASE_DIR}/${CASE_NAME}/user_datm.streams.txt.CLMGSWP3v1.TPQW
# ---------------------------------------------------------------------------- #
# **************************************************************************** #
# ---------------------------------------------------------------------------- #

if [ $SCENARIO=='obsclim' ]
then
   cp ./CaseDocs/datm.streams.txt.co2tseries.20tr ./user_datm.streams.txt.co2tseries.20tr
   chmod +rw ./user_datm.streams.txt.co2tseries.20tr
   perl -w -i -p -e "s@/compyfs/inputdata/atm/datm7/CO2@/compyfs/xudo627/projects/isimip-mosart/inputdata@" ./user_datm.streams.txt.co2tseries.20tr
   perl -w -i -p -e "s@fco2_datm_1765-2007_c100614.nc@fco2_datm_1777-2021_obsclim.nc@" ./user_datm.streams.txt.co2tseries.20tr
   sed -i '/ZBOT/d' ./user_datm.streams.txt.co2tseries.20tr
fi

./case.setup

./case.build

./case.submit
