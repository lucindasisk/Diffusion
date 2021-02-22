#!/bin/bash

#SBATCH --job-name=shapes_eddycuda
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --mem-per-cpu=10G
#SBATCH --time=12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu

 ml load StdEnv
 ml load FreeSurfer/6.0.0
 ml load FSL/6.0.1-centos7_64
 ml load MRtrix3/3.0_RC3-foss-2018a
 ml load Python/miniconda

source activate /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes_dwi

home='/gpfs/milgram/project/gee_dylan/candlab/scripts/shapes/mri/dwi/Diffusion'

python $home/1_DTI_Preprocessing-SHAPES.py
