#!/bin/bash

#SBATCH --job-name=shapes_preproc
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=6:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu

 ml load StdEnv
 ml load FreeSurfer/6.0.0
 ml load FSL/6.0.0
 ml load MRtrix3/3.0_RC3-foss-2018a
 ml load Python/miniconda
 ml load ANTs/2.3.1-foss-2018a

source activate /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes_dwi

home='/gpfs/milgram/project/gee_dylan/candlab/scripts/shapes/mri/dwi/Diffusion'
python $home/1_DTI_Preprocessing-SHAPES.py
