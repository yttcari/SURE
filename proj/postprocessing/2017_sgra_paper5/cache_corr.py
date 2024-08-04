from pathlib   import Path
from itertools import product
from importlib import import_module

import numpy  as np
import pandas as pd
import h5py

from astropy import units as u, constants as c
from tqdm    import tqdm
from yaml    import safe_load

from scipy.interpolate import interp2d

from common import hallmark as hm
from common import analyses as mm


def cache_corr(src_fmt, dst_fmt, params=None,
               cols = ['time', 'Mdot', 'Ftot', 'alpha0', 'beta0', 'major_FWHM', 'minor_FWHM', 'PA'],
               **kwargs):

    dlen = 0 # For pretty format in tqdm

    # Find input models using hallmark `ParaFrame`
    pf = hm.ParaFrame(src_fmt, **kwargs)
    if len(pf) == 0:

        print('No input found; please try different options')
        exit(1)

    # Automatically determine parameters if needed, turn `params` into
    # a dict of parameters and their unique values
    if params is None:
        params = list(pf.keys())
        print(params)
        params.remove('path')
    params = {p:np.unique(pf[p]) for p in params}

    # Main loop for generating multiple summary tables
    for values in product(*params.values()):

        criteria = {p:v for p, v in zip(params.keys(), values)}

         # Check output file
        dst = Path(dst_fmt.format(**criteria))
        if dst.is_file():
            print(f'  "{dst}" exists; SKIP')
            continue

        # Select models according to `criteria`
        sel = pf
        for p, v in criteria.items():
            sel = sel(**{p:v})
        if len(sel) == 0:
            print(f'  No input found for {criteria}; SKIP')
            continue

        # Pretty format in `tqdm`
        desc = f'* "{dst}"'
        desc = f'{desc:<{dlen}}'
        dlen = len(desc)

        # Actually creating the table
        df = pd.read_csv(sel.path.iloc[0], sep='\t')
        corr = df[cols].corr()

        # Only touch file system if everything works
        dst.parent.mkdir(parents=True, exist_ok=True)
        corr.to_csv(dst, sep='\t', index=True)


#==============================================================================
# Make cache_stat() callable as a script

import click

@click.command()
@click.argument('args', nargs=-1)
def cmd(args):

    confs  = []
    params = {}
    for arg in args:
        if '=' in arg:
            p = arg.split('=')
            params[p[0]] = p[1]
        else:
            confs.append(arg)

    for c in confs:
        with open(c) as f:
            cache_corr(**safe_load(f), **params)

if __name__ == '__main__':
    cmd()