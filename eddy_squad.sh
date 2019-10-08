#! /bin/bash

#Usage: ./eddy_qc <name_of_subject_list.txt

#SBATCH --job-name=shapes_eddycuda
#SBATCH --partition=gpu
#SBATCH --gres=gpu:2
#SBATCH --mem-per-cpu=10G
#SBATCH --time=3:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu
#SBATCH --gres=gpu:1

ml load StdEnv
ml load FSL/6.0.1-centos7_64

home='/gpfs/milgram/project/gee_dylan/candlab'
quad=$home'/analyses/shapes/dwi/data/4_Eddy_QC_Data'
cd $quad
#quad_fldrs=$(ls)
#echo $quad_fldrs > 'eddyquad_folders.txt'
fldrlist='eddyquad_folders.txt'

eddy_squad $fldrlist
