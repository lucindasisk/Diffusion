#!/bin/bash

#SBATCH --job-name=shapes_preprocessing
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=10G
#SBATCH --time=12:00:00
#SBATCH --partition=long
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu
source ~/.bashrc

ml load StdEnv
ml load MRtrix3/3.0_RC3-foss-2018a
ml load Python/3.6.4-foss-2018a
ml load ANTs/2.3.1-foss-2018a

conda activate /gpfs/milgram/pi/gee_dylan/lms233/conda_envs/shapes-dwi3.7

home='/home/lms233/Github/Diffusion'
python $home/2_Deconvolution_Pipeline.py $1
