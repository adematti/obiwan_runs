import argparse
import logging
import numpy as np
from obiwan import SimCatalog,BrickCatalog,utils,setup_logging

logger = logging.getLogger('preprocessing')

def isELG_colors(gflux=None, rflux=None, zflux=None, south=True, gmarg=0., grmarg=0., rzmarg=0., primary=None):
    """
    Apply ELG selection with box enlarged by ``gmarg``, ``grmarg``, ``rzmarg``.

    Base selection from https://github.com/desihub/desitarget/blob/master/py/desitarget/cuts.py.
    """
    if primary is None:
        primary = np.ones_like(rflux, dtype='?')
    elg = primary.copy()

    # ADM work in magnitudes instead of fluxes. NOTE THIS IS ONLY OK AS
    # ADM the snr masking in ALL OF g, r AND z ENSURES positive fluxes.
    g = 22.5 - 2.5*np.log10(gflux.clip(1e-16))
    r = 22.5 - 2.5*np.log10(rflux.clip(1e-16))
    z = 22.5 - 2.5*np.log10(zflux.clip(1e-16))

    # ADM cuts shared by the northern and southern selections.
    elg &= g > 20 - gmarg                          # bright cut.
    elg &= r - z > 0.3 - rzmarg                    # blue cut.
    elg &= r - z < 1.6 + rzmarg                    # red cut.
    elg &= g - r < -1.2*(r - z) + 1.6 + grmarg     # OII flux cut.

    # ADM cuts that are unique to the north or south.
    if south:
        elg &= g < 23.4 + gmarg # faint cut.
        # ADM south has the FDR cut to remove stars and low-z galaxies.
        elg &= g - r < 1.15*(r - z) - 0.15 + grmarg
    else:
        elg &= g < 23.5 + gmarg # faint cut.
        elg &= g - r < 1.15*(r - z) - 0.20 + grmarg # remove stars and low-z galaxies.

    return elg

def get_truth(truth_fn, south=True):
    """Build truth table."""
    truth = SimCatalog(truth_fn)
    mask = isELG_colors(south=south,gmarg=0.5,grmarg=0.5,rzmarg=0.5,**{'%sflux' % b:utils.mag2nano(truth.get(b)) for b in ['g','r','z']})
    for b in ['g','r','z']:
        mask &= (~np.isnan(truth.get(b))) & (~np.isinf(truth.get(b)))
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
        transmission = 10**(-0.4*randoms.get_extinction(b,camera='DES'))
        randoms.set('mw_transmission_%s' % b,transmission)
        flux = utils.mag2nano(randoms.get(b))*transmission
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
    #randoms.keep_columns('id','ra','dec','maskbits','photsys','brickname')

    for photsys in ['N','S']:
        truth = get_truth(truth_fn,south=photsys=='S')
        mask = randoms.photsys == photsys
        logger.info('Found %d randoms in %s.' % (mask.sum(),photsys))
        if mask.any():
            randoms.fill(sample_from_truth(randoms[mask],truth,seed=seed),index_self=mask,index_other=None)

    randoms.writeto(randoms_fn)

if __name__ == '__main__':

    setup_logging()

    parser = argparse.ArgumentParser(description='Obiwan preprocessing')
    parser.add_argument('-d','--do',nargs='*',type=str,choices=['bricklist','randoms'],default=[],required=False,help='What should I do?')
    parser.add_argument('-r','--run',type=str,choices=['north','south'],required=True,help='Run?')
    opt = parser.parse_args()

    if opt.run == 'north':
        import settings_north as settings
    else:
        import settings_south as settings

    if 'bricklist' in opt.do:
        write_bricklist(settings.randoms_input_fn,settings.bricklist_fn,south=settings.run=='south')

    if 'randoms' in opt.do:
        write_legacysurvey_randoms(settings.randoms_input_fn,settings.truth_fn,settings.randoms_fn,bricknames=settings.get_bricknames(),seed=42)
