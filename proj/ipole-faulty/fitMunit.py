import subprocess
import numpy as np
from multiprocessing import Pool
import sys
import os
import h5py
import csv

EPSILON = 0.005

NGC = ["NGC4594", "NGC4261", "NGC2663"]
log_MBH = [8.8, 8.9, 9.2]
dsource = [9.9, 14, 31]
mm_Flux = [0.2, 0.13, 0.2]

spin = ["+0.94"]#, "+0.5", "0", "-0.5", "-0.94"]
freqcgs = ["230.e9"]#, "230e9", "345e9"]
inclination = ["30"]#, "60", "90"]

nR = ["1.9998", "1.9334", "1.8425", "1.8594", "1.8587"]
qshear = ["1.7265", "1.6539", "1.6332", "1.6548", "1.7477"]

dump_dir = "/xdisk/rtilanus/proj/eht/GRMHD_kharma-v3/Sa"

def run_ipole(a, i, v, M_unit):
    
    avg_unpol = 0

    output_parent_dir = "./output/SPO2023/"
    try:
        os.mkdir(output_parent_dir)
    except OSError as error:
        pass
    try:
        os.mkdir(output_parent_dir + "M_" + str(M_unit))
    except OSError as error:
        pass
    output_dir = output_parent_dir + "M_" + str(M_unit) +"/"
    for fno in range(10):
        par = ['./ipole' ,'-par', './SgrA-example.par', '--M_unit', str(M_unit) + "e17",
               '--dump', dump_dir + spin[a] + "_w5/torus.out0.05" + str(fno) + "00.h5",
               '--outfile', output_dir + str(fno) + "000.h5",
               '--qshear', qshear[a], '--nR', nR[a], '-unpol']
        subprocess.run(par)
        hfp = h5py.File(output_dir + str(fno) + "000.h5")
        scale = hfp['header']['scale'][()]
        unpol = np.copy(hfp['unpol']).transpose((1, 0)).sum()*scale
        with open(output_dir + "log.csv", 'a') as log:
                write = csv.writer(log)
                write.writerow([str(fno), str(unpol)])

        avg_unpol += unpol
    avg_unpol /= 10

    return avg_unpol

def bisection(a, i, v, init_M_unit):
    left = 1
    right = 1e4
    Munit = init_M_unit

    calc_flux = run_ipole(a, i, v, init_M_unit)

    while abs(calc_flux - 2.4) > EPSILON:
        if calc_flux < 2.4:
            left = Munit
        else:
            right = Munit
        Munit = (left + right)/2
        calc_flux = run_ipole(a, i, v, Munit)
    return Munit

def iter(param):
    a, i, v = param

    initMunit = 100

    newMunit = bisection(a, i, v, initMunit)
    print(newMunit)
    return (spin[a], inclination[i], freqcgs[v], newMunit, NGC[n])

if __name__ == "__main__":
    param = [(a, i, v) for a in range(len(spin))
                       for i in range(len(inclination))
                       for v in range(len(freqcgs))]
    with Pool() as pool:
        row = pool.map(iter, param)
    import csv
    with open("M_unit.csv", 'a') as f:
        write = csv.writer(f)
        write.writerows(row)

    

