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