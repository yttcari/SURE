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

dump_dir = "/xdisk/rtilanus/proj/eht/GRMHD_kharma-v3/Sa"
#dump_dir = "/xdisk/chanc/proj/eht/GRMHD_dt5M/Ma"

ipole_exe_dir = '../../../bin/ipole'

"""
SHOULD NOT TOUCH AFTER THIS LINE
OTHER THAN CHANGING DIRECTORY
"""

def plot_avg_ipole(a, i, v, M_unit, n):
    FOV = str(50)
    resolution = str(200)
    print(qshear[a] + "_" + nR[a])
    print(a, i, v, M_unit, NGC[n])
    
    imgdump_dir = "../img_dump/" + "_".join([NGC[n], spin[a], freqcgs[v], inclination[i], M_unit]) 
    output_dir = "../img/"
 
    # Make direectory if neccessary,
    # Pass if the directory is exist 
    try:
        os.mkdir(imgdump_dir)
    except:
        pass

    avg = 0
 
    for fno in range(10): #REMEMBER to change to 10 when doing AVERAGE
        par = [ipole_exe_dir ,'-par', '../../../par/SgrA.par', '--M_unit', str(M_unit),
               '--dsource', str(dsource[n])+"e6", '--MBH', str(round(10**log_MBH[n], 4)),
               '--freqcgs', freqcgs[v], '--thetacam', str(inclination[i]),
               '--dump', dump_dir + spin[a] + "_w5/torus.out0.05" + str(fno) + "00.h5",
               '--outfile', imgdump_dir + "/5" + str(fno) + "00.h5", '-unpol', 
               '--qshear', qshear[a], '--nR', nR[a], '--trat_large', "40",
               '--fovx_dsource', FOV, '--fovy_dsource', FOV,'--nx', resolution, '--ny', resolution]
        print(par)
        subprocess.run(par)

        hfp = h5py.File(imgdump_dir + "/5" + str(fno) + "00.h5" , 'r')
        unpol = np.copy(hfp['unpol']).transpose((1,0))
        scale = hfp['header']['scale'][()]
        avg += unpol.sum()*scale

    avg /= 10
    with open("../doc/avg_unpol.csv", 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([NGC[n], spin[a], freqcgs[v], inclination[i], M_unit, str(log_MBH[n]), qshear[a], nR[a], str(dsource[n]), str(mm_Flux[n]), str(avg)]) 


with open('../../../par/SPO_SANE_M_unit.csv', 'r', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

    for row in data:
        if str(NGC.index(row[4])) == sys.argv[1]:    
            plot_avg_ipole(spin.index(row[0]), inclination.index(row[1]), freqcgs.index(row[2]), row[3], NGC.index(row[4]))      
