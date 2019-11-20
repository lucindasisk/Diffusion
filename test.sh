#!/bin/bash

#SBATCH --job-name=test
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=5G
#SBATCH --time=1:00:00
#SBATCH --partition=long
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu

ml miniconda

source activate /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes_dwi

module list

which python

