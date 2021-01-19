#!/bin/bash
# Set up the legacypipe environment
# and launch mpi_main_runbricks.py (default) or mpi_script_runbricks.py (option -s).

# add here obiwan to python path if necessary
#export PYTHONPATH=$HOME/obiwan/py:$PYTHONPATH

# set number of OpenMP threads here
export OMP_NUM_THREADS=4
source ./legacypipe-env.sh
#chmod u+x ./runbrick.sh

python mpi_main_runbricks.py "$@"
python mpi_main_legacypipe.py "$@"
