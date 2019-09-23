#!/bin/bash

#SBATCH --job-name=shapes_preproc
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=8G
#SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu

 ml load StdEnv
 ml load FreeSurfer/6.0.0
 ml load FSL/6.0.0
 ml load MRtrix3/3.0_RC3-foss-2018a
 ml load Python/miniconda
 ml load ANTs/2.3.1-foss-2018a

home='/Users/lucindasisk/Dropbox/Github/Diffusion'
python $home/3_Tractography_Pipeline.py
