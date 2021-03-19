#!/bin/bash

#SBATCH --job-name=shapes_eddycuda
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:2
#SBATCH --mem-per-cpu=10G
#SBATCH --time=12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu
source ~/.bashrc

ml load StdEnv
ml load FreeSurfer/6.0.0
ml load FSL/6.0.3-centos7_64
ml load MRtrix3/3.0_RC3-foss-2018a
ml load Python/3.6.4-foss-2018a
ml load FreeSurfer/7.1.0-centos7_x86_64

conda activate /gpfs/milgram/pi/gee_dylan/lms233/conda_envs/shapes-dwi3.7

home='/home/lms233/Github/Diffusion'
python $home/1_DTI_Preprocessing-SHAPES.py $1
