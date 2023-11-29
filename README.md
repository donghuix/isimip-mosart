# isimip-mosart
* Download ISIMIP3a daily runoff and convert it to DLND format to drive MOSART.
* Available ISIMIP3a impact models: CLASSIC, CWatM, H08, HydroPy, JULES-W2, JULES-W2-DDM30, MIROC-INTEG-LAND
* Climate forcing: GSWP3-W5E5
* Climate scenario
  * counterclim: counterfactual climate
  * obsclim: factual climate

Required packages
* Python
* numpy, os, urllib

Download GSIM dataset
```
wget https://store.pangaea.de/Publications/DoH-etal_2018/GSIM_metadata.zip
wget https://store.pangaea.de/Publications/GudmundssonL-etal_2018/GSIM_indices.zip
```

On compy
* ``module load python/3.7.3``

# Workflow
1. ```python3 Step01_Download_ISIMIP3a.py``` Download ISIMIP3a runoff forcings
2. ```python3 Step02_Generate_DLND.py``` Process the ISIMIP3a runoff forcings to DLND format
3. ```sh Step03_Run_MOSART.sh``` setup, build, and submit DLND-MOSART simulation. Need to mannually ``MODEL`` and MOSART input file.
4. TODO. Validate simulation against GSIM streamflow observation.