#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --array=0-9
#SBATCH --mail-user=1155194496@link.cuhk.edu.hk
#SBATCH --mail-type=ALL

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

module load gnu8
module load gsl
module load hdf5

mass_unit=4.5225e17

hundred_dit=0

while [ $hundred_dit -le 9 ]
do
  ten_digit=0
  while [ $ten_digit -le 9 ]
  do
   ./SPO2023_ipole -par SgrA*-example.par --dump /xdisk/chanc/proj/eht/GRMHD_dt5M/Ma+0.94_w5/torus.out0.05${hundred_dit}${ten_digit}${SLURM_ARRAY_TASK_ID}.h5  --M_unit ${mass_unit} --outfile ./avg-img/light_curve_SPO2023/img_5${hundred_dit}${ten_digit}${SLURM_ARRAY_TASK_ID}.h5 -unpol
    ((ten_digit++))
  done
  ((hundred_dit++))
done
