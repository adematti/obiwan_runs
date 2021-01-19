EBV 1000
========

Run 1000 bricks covering a large EBV range in north and south.

On NERSC
--------

Set up data::

  mkdir -p ${CSCRATCH}/Obiwan/dr9/data/
  cp /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/ccds-annotated-* ${CSCRATCH}/Obiwan/dr9/data/
  cp /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/survey-* ${CSCRATCH}/Obiwan/dr9/data/
  ln -s /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/calib/ ${CSCRATCH}/Obiwan/dr9/data/
  ln -s /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/images/ ${CSCRATCH}/Obiwan/dr9/data/

Pull **Docker** image::

  shifterimg -v pull adematti/obiwan:DR9.6.7.ebv1000

Run::

  chmod u+x ./mpi_runbricks.sh
  salloc -N 1 -C haswell -t 02:00:00 --qos interactive -L SCRATCH,project
  srun -n 5 shifter --module=mpich-cle6 --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9.6.7.ebv1000 ./mpi_runbricks.sh --run north

and similarly for south.

.. note::

  With 21 tasks ``srun -n 21``, there will be 1 root and 20 workers, hence 20 bricks run in parallel.
