#!/bin/bash

#SBATCH --job-name=shapes_eddycuda
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=6:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu
#SBATCH --gres=gpu:1


 ml load StdEnv
 ml load CUDA/7.5.18
 ml load FSL/6.0.0
 ml load Python/miniconda

source activate /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes_dwi

home='/gpfs/milgram/project/gee_dylan/candlab/scripts/shapes/mri/dwi/Diffusion'
python $home/2_EDDY_CUDA.py
