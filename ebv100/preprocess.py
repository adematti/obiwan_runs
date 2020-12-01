import argparse
import logging
import numpy as np
from obiwan import SimCatalog,BrickCatalog,utils,setup_logging
import settings

logger = logging.getLogger('preprocessing')

def write_bricklist(ran_fn, bricklist_fn, south=False, nbricks=100, range_ebv=(0.002,0.15)):
    """Return brick list for ebv run."""
    bands = ['g','r','z']
    randoms = SimCatalog(ran_fn,columns=['photsys','brickname','ebv'] + ['nobs_%s' % b for b in bands])
    mask = randoms.photsys == ('S' if south else 'N')
    for b in bands: mask &= randoms.get('nobs_%s' % b)>0
    #mask &= randoms.maskbits == 0
    randoms = randoms[mask]
    step_ebv = (range_ebv[-1]-range_ebv[0])/nbricks
    with open(bricklist_fn,'w') as file:
        for ibrick in range(nbricks):
            min_ebv,max_ebv = ibrick*step_ebv + range_ebv[0],(ibrick+1)*step_ebv + range_ebv[0]
            mask = (randoms.ebv > min_ebv) & (randoms.ebv < max_ebv)
            if mask.any():
                file.write('%s\n' % randoms.brickname[mask][0])
            else:
                logger.info('No brick found in EBV interval %.3f - %.3f.' % (min_ebv,max_ebv))

def get_truth(truth_fn, south=True):
    """Build truth table."""
    truth = SimCatalog(truth_fn)
    mask = (truth.g >= 22.) & (truth.g <= 24.)
    logger.info('Target selection: %d/%d objects' % (mask.sum(),mask.size))
    truth = truth[mask]
    truth.rename('objid','id_truth')
    truth.rename('rhalf','shape_r')
    #truth.shape_r = 1e-5*truth.ones()
    truth.rename('hsc_mizuki_photoz_best','redshift')
    truth.sersic = truth.ones(dtype=int)
    truth.sersic[truth.type=='DEV'] = 4
    return truth

def sample_from_truth(randoms, truth, rng=None, seed=None):
    """Sample random photometry from truth table."""
    if rng is None:
        rng = np.random.RandomState(seed=seed)

    ind = rng.randint(low=0,high=truth.size,size=randoms.size)

    for field in ['id_truth','g','r','z','shape_r','sersic','redshift']:
        randoms.set(field,truth.get(field)[ind])

    for b in ['g','r','z']:
        transmission = randoms.get_extinction(b,camera='DES')
        flux = utils.mag2nano(randoms.get(b))*10**(-0.4*transmission)
        randoms.set('flux_%s' % b,flux)

    ba = rng.uniform(0.2,1.,size=randoms.size)
    phi = rng.uniform(0,np.pi,size=randoms.size)
    randoms.shape_e1,randoms.shape_e2 = utils.get_shape_e1_e2(ba,phi)

    return randoms

def write_legacysurvey_randoms(input_fn, truth_fn, randoms_fn, bricknames=[], seed=None):
    """Build Obiwan randoms from legacysurvey randoms and truth table."""
    randoms = SimCatalog(input_fn)
    logger.info('Selecting randoms in %s' % bricknames)
    mask = np.in1d(randoms.brickname,bricknames)
    randoms = randoms[mask]
    randoms.rename('targetid','id')
    logger.info('Selected random catalog of size = %d.' % randoms.size)
    randoms.keep_columns('id','ra','dec','maskbits','photsys','brickname')

    for photsys in ['N','S']:
        truth = get_truth(truth_fn,south=photsys=='S')
        mask = randoms.photsys == photsys
        if mask.any():
            randoms.fill(sample_from_truth(randoms[mask],truth,seed=seed),index_self=mask,index_other=None)

    randoms.writeto(randoms_fn)

if __name__ == '__main__':

    setup_logging()

    parser = argparse.ArgumentParser(description='Obiwan preprocessing')
    parser.add_argument('-d','--do',nargs='*',type=str,choices=['bricklist','randoms'],default=[],required=False,help='What should I do')
    opt = parser.parse_args()

    if 'bricklist' in opt.do:
        write_bricklist(settings.randoms_input_fn,settings.bricklist_fn,south=settings.run=='south')

    if 'randoms' in opt.do:
        write_legacysurvey_randoms(settings.randoms_input_fn,settings.truth_fn,settings.randoms_fn,bricknames=settings.get_bricknames(),seed=42)
