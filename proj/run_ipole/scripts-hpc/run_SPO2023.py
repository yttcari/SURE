import subprocess
import numpy as np
from multiprocessing import Pool
import sys
import os
import h5py
import csv

NGC = ["NGC4594", "NGC3998", "NGC4261"]
log_MBH = [8.8, 8.9, 9.2]
dsource = [9.9, 14, 31]
mm_Flux = [0.2, 0.13, 0.2]

spin = ["+0.94", "+0.5", "0", "-0.5", "-0.94"]
freqcgs = ["86.e9", "230.e9", "345.e9"]
inclination = ["50", "160"]#, "60", "90"]

nR = ["1.9998", "1.9334", "1.8425", "1.8594", "1.8587"]
qshear = ["1.7265", "1.6539", "1.6332", "1.6548", "1.7477"]

dump_dir = "/xdisk/rtilanus/proj/eht/GRMHD_kharma-v3/Sa"

ipole_exe_dir = '../../../bin/ipole'

def plot_avg_ipole(a, i, v, M_unit, n):
    FOV = str(50)
    resolution = str(200)
    
    imgdump_dir = "/xdisk/rtilanus/home/yitungtsang/" + "_".join([NGC[n], spin[a], freqcgs[v], inclination[i]]) 
 
    # Make direectory if neccessary,
    # Pass if the directory is exist 
    try:
        os.mkdir(imgdump_dir)
    except:
        pass

    for fno in range(1000):
        par = [ipole_exe_dir ,'-par', '../../../par/SgrA.par', '--M_unit', str(M_unit),
               '--dsource', str(dsource[n])+"e6", '--MBH', str(round(10**log_MBH[n], 4)),
               '--freqcgs', freqcgs[v], '--thetacam', str(inclination[i]),
               '--dump', dump_dir + spin[a] + "_w5/torus.out0.05" + f"{fno:03}.h5",
               '--outfile', imgdump_dir + "/5" + f"{fno:03}.h5", 
               '--qshear', qshear[a], '--nR', nR[a],
               '--fovx_dsource', FOV, '--fovy_dsource', FOV,'--nx', resolution, '--ny', resolution]
        print(par)
        subprocess.run(par)

with open('../../../par/SPO_SANE_M_unit.csv', 'r', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

    for row in data:
        if ((sys.argv[1] == str(NGC.index(row[4]))) and (row[0] == '0')):
            #for v in range(len(freqcgs)):
            v = 0
            plot_avg_ipole(spin.index(row[0]), inclination.index(row[1]), v, row[3], NGC.index(row[4]))      
