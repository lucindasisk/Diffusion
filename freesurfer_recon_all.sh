#! /bin/bash

#SBATCH --job-name=freesurfer_reconall
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=12:00:00
#SBATCH --partition=long
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu

ml load FreeSurfer/6.0.0
export SUBJECTS_DIR='/gpfs/milgram/project/gee_dylan/candlab/data/mri/shapes_freesurfer'

sub=$1
base='/gpfs/milgram/project/gee_dylan/candlab'
raw=$base'/data/mri/bids_recon/shapes/'$sub'/ses-shapesV1/anat/'$sub'_ses-shapesV1_T1w.nii.gz'

recon-all -i $raw -s $1 -all
