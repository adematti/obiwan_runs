EBV 100
=======

Run 100 bricks covering a large EBV range.

On NERSC
--------

Set up data::

  mkdir -p ${CSCRATCH}/Obiwan/dr9/data/
  cp /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/ccds-annotated-* ${CSCRATCH}/Obiwan/dr9/data/
  cp /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/survey-* ${CSCRATCH}/Obiwan/dr9/data/
  ln -s /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/calib/ ${CSCRATCH}/Obiwan/dr9/data/
  ln -s /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/images/ ${CSCRATCH}/Obiwan/dr9/data/

Pull **Docker** image::

  shifterimg -v pull adematti/obiwan:DR9.6.7.ebv100

Set up bricklist and randoms::

  shifter --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9.6.7.ebv100 python preprocess.py --do bricklist
  shifter --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9.6.7.ebv100 python preprocess.py --do randoms

Run::

  chmod u+x ./mpi_runbricks.sh
  salloc -N 2 -C haswell -t 02:00:00 --qos interactive -L SCRATCH,project
  srun -n 4 shifter --module=mpich-cle6 --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9.6.7.ebv100 ./mpi_runbricks.sh

.. note::

  With 4 tasks ``srun -n 4``, there will be 1 root and 3 workers, hence 3 bricks are run in parallel.

Match::

  shifter --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9.6.7.ebv100 python postprocess.py --do match
