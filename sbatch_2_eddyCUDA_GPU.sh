#!/bin/bash

#SBATCH --job-name=shapes_eddycuda
#SBATCH --partition=gpu
#SBATCH --gres=gpu:2
#SBATCH --mem-per-cpu=10G
#SBATCH --time=12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu


 ml load StdEnv
 ml load FreeSurfer/6.0.0
 ml load FSL/6.0.1-centos7_64
 ml load Python/miniconda

source activate /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes_dwi

home='/gpfs/milgram/project/gee_dylan/candlab/scripts/shapes/mri/dwi/Diffusion'
python $home/2_EDDY_CUDA.py
