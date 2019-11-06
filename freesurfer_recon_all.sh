#! /bin/bash

export SUBJECTS_DIR='/gpfs/milgram/project/gee_dylan/candlab/data/mri/shapes_freesurfer'

sub=$1
base='/gpfs/milgram/project/gee_dylan/candlab'
raw=$base'/data/mri/bids_recon/shapes/'$sub'/ses-shapesV1/anat/'$sub'_ses-shapesV1_T1w.nii.gz'

recon-all -i $raw -s $1 -all
