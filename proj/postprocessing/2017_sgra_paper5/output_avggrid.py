from common import dalt
from common import hallmark as hm
from common import viz
from common import io_ipole as io
from common import mockservation as ms
import numpy as np
from matplotlib import pyplot as plt, cm
import os
import h5py

#pf = hm.ParaFrame('/Users/caritsang/desktop/project/2024SURE/dump/{NGC}_{aspin:g}_{freq}_{inc:g}/')
pf = hm.ParaFrame('cache/SPO2023/avg/{NGC}_a{aspin:g}_i{inc:g}_f{freq}.h5')

for k in set(pf.keys()) - {'path'}:
    globals()[k] = np.unique(pf[k])
    print(k, globals()[k][:16])

def readimg(f):
    with h5py.File(f) as h:
        m    = h['meta']
        meta = dalt.ImageMeta(**{k:m[k][()] for k in m.keys()})
        data = h['data'][:]
    return dalt.Image(data, meta=meta)

def grid(pf, n, i, ylabel=None, title=None, xtitle=None, xlabel=None, **kwargs):
    pf = pf.sort_values('aspin')
    keys   = list(kwargs.keys())
    colkey = keys[0]
    cols   = kwargs.pop(keys[0])
    rowkey = keys[1]
    rows   = kwargs.pop(keys[1])

    fig, axes = plt.subplots(ncols=len(cols), nrows=len(rows), figsize=(11,11), sharex=True, sharey=True, squeeze=False)
    plt.subplots_adjust(wspace=0, hspace=0)

    for i, x in enumerate(rows):
        for j, y in enumerate(cols):
            print(i, j)
            ax = axes[i][j]
            print(x, y)
            pf = pf(freq=y)(aspin=x)
            print(pf['path'].iloc[0])
            #img_avg  = io.load_mov([pf(**{colkey:x})(**{rowkey:y})['path'].iloc[0] + f'/5{i:03}.h5' for i in range(1000)], mean=True)
            img_avg = readimg(pf['path'].iloc[0])
            print(pf(freq=x)(aspin=y)['path'].iloc[0])
            vmax = (np.max(img_avg).value.astype(float))
            print(vmax)
            viz.show(img_avg, ax=ax, cmap='afmhot', vmin=0, vmax=vmax,interpolation='none')

            print(np.max(img_avg))
            
            ax.set_title(title.format(y, x))

            if j == len(rows)-1:
                ax.set_xlabel(xlabel)
            else:
                ax.set_xticklabels([])

    fig.tight_layout()
    fig.savefig('output/plot/avg_plot/{}_{}.pdf'.format(OBJ, INC), bbox_inches='tight')
    
for OBJ in NGC:
    for INC in inc:
        col = np.sort(pf(NGC=OBJ)(inc=INC)['freq'].unique())
        row = np.sort(pf(NGC=OBJ)(inc=INC)['aspin'].unique())
        grid(pf(NGC=OBJ)(inc=INC), OBJ, INC, freq=col, aspin=row, 
                title=r'a={}, f={}',
                xlabel=r'$x$ [$\mu$as]', ylabel=r'$y$ [$\mu$as]')
