"""Run directly obiwan.runbrick.main."""

import os
import argparse
import time
from obiwan import runbrick,RunCatalog,get_randoms_id,setup_logging
from obiwan.batch import TaskManager

ntasks = int(os.getenv('SLURM_NTASKS','1'))
threads = int(os.getenv('OMP_NUM_THREADS','1'))

parser = argparse.ArgumentParser(description='Obiwan main runbrick')
parser.add_argument('-r','--run',type=str,choices=['north','south'],required=True,help='Run?')
opt = parser.parse_args()

if opt.run == 'north':
    import settings_north as settings
else:
    import settings_south as settings

runcat = RunCatalog.from_input_cmdline(dict(brick=settings.get_bricknames(),
                                        fileid=settings.fileid,rowstart=settings.rowstart,skipid=settings.skipid))
runcat.seed = runcat.index()*42


brick = [brickname.split()[0] for brickname in open('missing_%s.txt' % opt.run,'r')]
torerun = RunCatalog.from_input_cmdline(dict(brick=brick,
                                        fileid=settings.fileid,rowstart=settings.rowstart,skipid=settings.skipid))
#torerun = RunCatalog.from_list('missing_%s.txt' % opt.run)
mask = runcat.in1d(torerun)
runcat = runcat[mask]

with TaskManager(ntasks=ntasks) as tm:

    for run in tm.iterate(runcat):

        log_fn = os.path.join(settings.output_dir,'logs',run.brickname[:3],run.brickname,
                        get_randoms_id(fileid=run.fileid,rowstart=run.rowstart,skipid=run.skipid),'%s.log' % run.brickname)

        command = ['--brick',run.brickname,'--threads',threads,'--outdir',settings.output_dir,'--run',settings.run,
                    '--ran-fn',settings.randoms_fn,'--fileid',run.fileid,'--rowstart',run.rowstart,'--skipid',run.skipid,
                    '--sim-blobs','--stage','writecat','--no-wise','--force-all','--no-write','--seed',run.seed,
                    '--add-sim-noise','poisson',
                    '--log-fn',log_fn,'--ps','--ps-t0',int(time.time())]
                    #'--ps',ps_fn,'--ps-t0',int(time.time())]

        print('Launching ' + ' '.join(map(str,command)))

        runbrick.main(command)
