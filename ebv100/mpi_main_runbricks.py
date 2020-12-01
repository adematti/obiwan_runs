"""Run directly obiwan.runbrick.main."""

import os
import time
from obiwan import runbrick,get_randoms_id,setup_logging
from obiwan.batch import TaskManager
import settings

ntasks = os.getenv('SLURM_NTASKS',1)
threads = os.getenv('OMP_NUM_THREADS',1)

with TaskManager(ntasks=ntasks) as tm:

    for ibrick,brick in tm.iterate(list(enumerate(settings.get_bricknames()))):

        log_fn = os.path.join(settings.output_dir,'logs',brick[:3],brick,
                        get_randoms_id(fileid=settings.fileid,rowstart=settings.rowstart,skipid=settings.skipid),'%s.log' % brick)
        ps_fn = os.path.join(settings.output_dir,'metrics',brick[:3],brick,
                        get_randoms_id(fileid=settings.fileid,rowstart=settings.rowstart,skipid=settings.skipid),'ps-%s.fits' % brick)

        command = ['--brick',brick,'--threads',threads,'--outdir',settings.output_dir,'--run',settings.run,
                    '--ran-fn',settings.randoms_fn,'--fileid',settings.fileid,'--rowstart',settings.rowstart,'--skipid',settings.skipid,
                    '--sim-blobs','--stage','writecat','--no-wise','--force-all','--no-write','--seed',ibrick*42,
                    '--add-sim-noise','gaussian',
                    '--log-fn',log_fn,'--ps',ps_fn,'--ps-t0',int(time.time())]
                    #'--ps',ps_fn,'--ps-t0',int(time.time())]

        print('Launching ' + ' '.join(map(str,command)))

        runbrick.main(command)
