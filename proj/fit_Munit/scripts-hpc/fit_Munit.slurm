#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mail-user=1155194496@link.cuhk.edu.hk
#SBATCH --mail-type=ALL
#SBATCH --array=0-2

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

module load gnu8 gsl hdf5 python
source ../../../python_venv/bin/activate

python fitMunit.py ${SLURM_ARRAY_TASK_ID}
