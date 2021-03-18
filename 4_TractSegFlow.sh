#! /bin/bash

home='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows'
datpath='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/data'

sub=$1
mkdir ${datpath}/tract_output
mkdir ${datpath}/tract_output/${sub}

bval_path='/gpfs/milgram/pi/gee_dylan/candlab/data/mri/bids_recon/shapes/'${sub}'/ses-shapesV1/dwi/'${sub}'_ses-shapesV1_dwi.bval'
bvec_path=${datpath}'3_Eddy_Corrected/'${sub}'/eddy_corrected.eddy_rotated_bvecs'
infile=${datpath}'/3_Eddy_Corrected/'${sub}'/eddy_corrected.nii.gz'
mnifile='/gpfs/milgram/pi/gee_dylan/candlab/atlases/MNI152_T1_2mm_brain.nii.gz'
mnimask='/gpfs/milgram/pi/gee_dylan/candlab/atlases/MNI152_T1_2mm_brain_mask.nii.gz'

epi_reg --epi

TractSeg --csd_type csd_msmt_5tt -i $infile --bvals $bval_path --bvecs $bvec_path -o ${datpath}/tract_output/${sub} --raw_diffusion_input