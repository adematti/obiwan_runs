import os

survey_dir = os.getenv('LEGACY_SURVEY_DIR')
run = 'north'
output_dir = os.path.join(os.getenv('CSCRATCH'),'Obiwan','dr9','ebv1000shaper',run)

randoms_input_fn = '/global/cfs/cdirs/desi/target/catalogs/dr9m/0.44.0/randoms/resolve/randoms-1-0.fits'
truth_fn = '/project/projectdirs/desi/users/ajross/MCdata/seed.fits'
randoms_fn = os.path.join(output_dir,'randoms','randoms.fits')
bricklist_fn = 'bricklist_400N-EBV.txt'
runlist_fn = 'runlist_400N-EBV.txt'

def get_bricknames():
    return [brickname[:-len('\n')] for brickname in open(bricklist_fn,'r')]

fileid = 0
rowstart = 0
skipid = 0
legacypipe_output_dir = os.path.join(os.getenv('LEGACYPIPE_SURVEY_DIR'),run)
