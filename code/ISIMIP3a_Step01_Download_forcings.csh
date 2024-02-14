#!/bin/csh

#SBATCH --job-name=isimp3a              ## job_name
#SBATCH --partition=slurm
#SBATCH --account=esmd                  ## project_name
#SBATCH --time=40:00:00                 ## time_limit
#SBATCH --nodes=1                       ## number_of_nodes
#SBATCH --ntasks-per-node=10            ## number_of_cores
#SBATCH --output=mat.stdout1            ## job_output_filename
#SBATCH --error=mat.stderr1             ## job_errors_filename

ulimit -s unlimited

module load python/3.7.3 

mpiexec -n 10 python3 -m mpi4py ISIMIP3a_Step01_Download_forcings.py --mca btl_openib_allow_ib 1 > ISIMIP3a_Step01_Download_forcings.log
