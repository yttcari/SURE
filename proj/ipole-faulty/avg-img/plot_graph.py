import matplotlib.pyplot as plt
import numpy as np
import h5py
import sys
import pandas as pd
import os

for arg in sys.argv[1:]:
  home_dir = arg
  file_dir = os.listdir(home_dir)

  unpol_list = []
  snapshot_t = []

  for fname in file_dir:

    if fname[-3:] != ".h5": continue
    print("plotting {0:s}".format(fname))

    do_fullscreen_unpol = False
    if '--fullscreen' in sys.argv:
      do_fullscreen_unpol = True

    # load  
    hfp = h5py.File(home_dir+fname,'r')    
    scale = hfp['header']['scale'][()]
    evpa_0 = 'W'
    if 'evpa_0' in hfp['header']:
      evpa_0 = hfp['header']['evpa_0'][()]
    unpol = np.copy(hfp['unpol']).transpose((1,0))
    if 'pol' in hfp:
      no_pol = False
      do_fullscreen_unpol = False
      imagep = np.copy(hfp['pol']).transpose((1,0,2))
      I = imagep[:,:,0]
      Q = imagep[:,:,1]
      U = imagep[:,:,2]
      V = imagep[:,:,3]
    else:
      no_pol = True
      I = unpol
      unpol_list.append(unpol.sum()*scale)
      snapshot_t.append(int(fname.replace("img_", "").replace(".h5", "")))
    hfp.close()
  df = pd.DataFrame({'fname': snapshot_t, 'unpol': unpol_list})
  df = df.sort_values('fname')
  trim_from = 0
  trim_to = 1000
  print("average: {}, max: {}, min: {}, sd: {}".format(np.mean(df['unpol'][trim_from:trim_to]), np.max(df['unpol'][trim_from:trim_to]), np.min(df['unpol'][trim_from:trim_to]), np.std(df['unpol'][trim_from:trim_to])))
  plt.plot(df['fname'][trim_from:trim_to], df['unpol'][trim_from:trim_to], label=arg)
plt.xlabel('snapshot')
plt.ylabel('I (Jy)')
plt.legend()
plt.savefig("Snaposhot_I.pdf",format='pdf')
