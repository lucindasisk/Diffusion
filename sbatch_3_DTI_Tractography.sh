#!/bin/bash

#SBATCH --job-name=shapes_tractography
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=10G
#SBATCH --time=12:00:00
#SBATCH --partition=long
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu

 ml load StdEnv
 ml load FreeSurfer/6.0.0
 ml load FSL/6.0.1-centos7_64
 ml load MRtrix3/3.0_RC3-foss-2018a
 ml load Python/miniconda
 ml load ANTs/2.3.1-foss-2018a

source activate /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes_dwi

home='/gpfs/milgram/project/gee_dylan/candlab/scripts/shapes/mri/dwi/Diffusion'
python $home/3_Tractography_Pipeline.py
