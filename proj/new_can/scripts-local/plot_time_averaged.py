import subprocess
import numpy as np
from multiprocessing import Pool
import sys
import os
import h5py
import csv

EPSILON = 0.005

NGC = ["NGC4594", "NGC3998", "NGC4261"]
log_MBH = [8.8, 8.9, 9.2]
dsource = [9.9, 14, 31]
mm_Flux = [0.2, 0.13, 0.2]

spin = ["+0.94", "+0.5", "0", "-0.5", "-0.94"]
freqcgs = ["2.30e11"]#, "230e9", "345e9"]
inclination = ["50", "160"]#, "60", "90"]

nR = ["1.9998", "1.9334", "1.8425", "1.8594", "1.8587"]
qshear = ["1.7265", "1.6539", "1.6332", "1.6548", "1.7477"]

dump_dir = "../../../dump/SANE/Sa" 

par_dir = "../../../par/SgrA.par"
ipole_exe_dir = '../../../bin/beta-ipole'

"""
SHOULD NOT TOUCH AFTER THIS LINE
OTHER THAN CHANGING DIRECTORY
"""

def plot_avg_ipole(a, i, v, M_unit, n):
    FOV = str(50)
    resolution = str(200)
    print(qshear[a] + "_" + nR[a])
    print(a, i, v, M_unit, NGC[n])
    
    img_dir = "img/S_Beta/" 
    for fno in range(1): #REMEMBER to change to 10 when doing AVERAGE
        imgdump_dir = "../img_dump/S_Beta/" + "_".join([NGC[n], spin[a], freqcgs[v], inclination[i], "0000.h5"])
        par = [ipole_exe_dir ,'-par', par_dir, '--M_unit', str(M_unit),
               '--dsource', str(dsource[n])+"e6", '--MBH', str(round(10**log_MBH[n], 4)),
               '--freqcgs', freqcgs[v], '--thetacam', str(inclination[i]),
               '--dump', dump_dir + spin[a] + "_0000.h5",
               '--outfile', imgdump_dir,
               '--qshear', qshear[a], '--nR', nR[a], '--trat_large', "40",
               '--fovx_dsource', FOV, '--fovy_dsource', FOV,'--nx', resolution, '--ny', resolution]
        print(par)
        subprocess.run(par)
        # For plot.py to work, first argument is the absolute path under 2024SURE/
        # Parameters after the first parameter is(are) the path(s) of the img dump
        subprocess.call(['python3', 'plot_fullscreen.py', img_dir + 'fullscreen_', imgdump_dir])
        subprocess.call(['python3', 'plot.py', img_dir, imgdump_dir])


v = 0
with open('../SPO_SANE_M_unit.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

    for row in data:
        #print(row)
        plot_avg_ipole(spin.index(row[0]), inclination.index(row[1]), freqcgs.index(row[2]), row[3], NGC.index(row[4]))
       
