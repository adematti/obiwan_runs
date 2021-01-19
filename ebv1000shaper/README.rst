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

Pull Docker image::

  shifterimg -v pull adematti/obiwan:DR9

Set up randoms::

  source legacypipe-env.sh
  shifter --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9 python preprocess.py --do randoms --run north

and similarly (``--run south``) for south. Then create run lists::

  shifter --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9 python /src/obiwan/py/obiwan/scripts/runlist.py --outdir /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/north --brick bricklist_400N-EBV.txt --write-list runlist_400N-EBV.txt --modules legacypipe
  shifter --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9 python /src/obiwan/py/obiwan/scripts/runlist.py --outdir /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/south --brick bricklist_600S-EBV.txt --write-list runlist_600S-EBV.txt --modules legacypipe

Run::

  chmod u+x ./mpi_runbricks.sh
  salloc -N 20 -C haswell -t 03:00:00 --qos interactive -L SCRATCH,project
  srun -n 101 shifter --module=mpich-cle6 --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9 ./mpi_runbricks.sh --run north

and similarly for south::

  salloc -N 30 -C haswell -t 03:00:00 --qos interactive -L SCRATCH,project
  srun -n 151 shifter --module=mpich-cle6 --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9 ./mpi_runbricks.sh --run south

.. note::

  With 101 tasks ``srun -n 101``, there will be 1 root and 100 workers, hence 100 bricks run in parallel.

Check everything ran and match::

  shifter --volume ${HOME}:/homedir/ --image=adematti/obiwan:DR9 /bin/bash
  python /src/obiwan/py/obiwan/scripts/check.py --outdir $CSCRATCH/Obiwan/dr9/ebv1000shaper/north --brick bricklist_400N-EBV.txt
  python /src/obiwan/py/obiwan/scripts/match.py --cat-dir $CSCRATCH/Obiwan/dr9/ebv1000shaper/north/merged --outdir $CSCRATCH/Obiwan/dr9/ebv1000shaper/north --plot-hist plots/hist_N.png
  exit

and similarly for south. Other commands::

  python /src/obiwan/py/obiwan/scripts/cutout.py --outdir $CSCRATCH/Obiwan/dr9/ebv1000shaper/north --plot-fn "plots/cutout_N-%(brickname)s-%(icut)d.png" --ncuts 2
  python /src/obiwan/py/obiwan/scripts/merge.py --filetype randoms tractor --cat-dir $CSCRATCH/Obiwan/dr9/ebv1000shaper/north/merged --outdir $CSCRATCH/Obiwan/dr9/ebv1000shaper/north
  python /src/obiwan/py/obiwan/scripts/match.py --tractor-legacypipe /global/cfs/cdirs/cosmo/work/legacysurvey/dr9m/north/ --outdir $CSCRATCH/Obiwan/dr9/ebv1000shaper/north --cat-fn $CSCRATCH/Obiwan/dr9/ebv1000shaper/north/merged/matched_legacypipe_input.fits
  python /src/obiwan/py/obiwan/scripts/resources.py --outdir $CSCRATCH/Obiwan/dr9/ebv1000shaper/north --plot-fn plots/resources-summary_N.png
