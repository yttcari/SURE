import numpy as np
import h5py
import os
import sys

avg_unpol = 0

file_dir = os.listdir("/home/u22/yitungtsang/ipole/avg-img/img_" + sys.argv[-1]+'/')

# load
for fname in file_dir:

    if fname[-3:] != ".h5": continue

    # load
    hfp = h5py.File('/home/u22/yitungtsang/ipole/avg-img/img_'+sys.argv[-1]+"/"+fname,'r')    
    unpol = np.copy(hfp['unpol']).transpose((1,0))
    scale = hfp['header']['scale'][()]
    hfp.close()

    avg_unpol += unpol.sum()*scale
    print("fname: {} unpol: {}".format(fname, unpol.sum()*scale))
#print(file_dir)
file_count = len(file_dir)
print("Total file input: {}".format(file_count))
avg_unpol /= file_count

print("avg_unpol: {}".format(avg_unpol))
