"""Run :mod:`legacypipe.runbrick`."""

import os
import argparse
import time
from obiwan import RunCatalog,get_randoms_id
from obiwan.batch import TaskManager,EnvironmentManager
from legacypipe import runbrick

ntasks = int(os.getenv('SLURM_NTASKS','1'))
threads = int(os.getenv('OMP_NUM_THREADS','1'))

parser = argparse.ArgumentParser(description='Legacypipe main runbrick')
parser.add_argument('-r','--run',type=str,choices=['north','south'],required=True,help='Run?')
opt = parser.parse_args()

if opt.run == 'north':
    import settings_north as settings
else:
    import settings_south as settings

runcat = RunCatalog.from_input_cmdline(dict(brick=settings.get_bricknames(),
                                        fileid=settings.fileid,rowstart=settings.rowstart,skipid=settings.skipid))
runcat.seed = runcat.index()*42
runcat.id = runcat.index()

if opt.run == 'north':
    import settings_north as settings
else:
    import settings_south as settings

#runcat = RunCatalog.from_input_cmdline(dict(brick=settings.get_bricknames(),fileid=settings.fileid,rowstart=settings.rowstart,skipid=settings.skipid))
runcat = RunCatalog.from_list(settings.runlist_fn)
runcat.seed = runcat.index()*42

with TaskManager(ntasks=ntasks) as tm:

    for run in tm.iterate(runcat):

        legacypipe_fn = find_file(base_dir=settings.legacypipe_output_dir,filetype='tractor',source='legacypipe',brickname=run.brickname)

        command = []
        for stage,versions in run.stages.items():
            environment = EnvironmentManager(fn=legacypipe_fn)
            environ = ['%s=%s' % (key,val) for key,val in environment.environ.items()]
            environ += ['PYTHONPATH=%s' % get_pythonpath(module_dir='/src/',versions=versions,full=True,as_string=True)]
            command += [' '.join(environ)]
            command += ['python',runbrick.__file__]
            command += ['--brick',run.brickname,'--threads',threads,'--outdir',settings.output_dir,'--run',settings.run,
                        '--no-wise','--no-write','--stage',stage]
        print(command)
