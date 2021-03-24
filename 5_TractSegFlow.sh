#! /bin/bash

home='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows'
datpath='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/data'

sub=$1
mkdir ${datpath}/tract_output
mkdir ${datpath}/tract_output/${sub}

conda activate shapes-dwi3.7

bval_path='/gpfs/milgram/pi/gee_dylan/candlab/data/mri/bids_recon/shapes/'${sub}'/ses-shapesV1/dwi/'${sub}'_ses-shapesV1_dwi.bval'
bvec_path=${datpath}'/3_Eddy_Corrected/'${sub}'/eddy_corrected.eddy_rotated_bvecs'

mrconvert ${datpath}'/4_Deconvolution/'${sub}'/wm.mif' ${datpath}'/4_Deconvolution/'${sub}'/wm_FOD.nii.gz'
infile=${datpath}'/4_Deconvolution/'${sub}'/wm_FOD.nii.gz'

/gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/TractSeg -i $infile --bvals ${datpath}'/tract_output/'${sub}'/raw_bvals.bval' --bvecs ${datpath}'/tract_output/'${sub}'/eddy_corrected_bvecs.bvec' -o ${datpath}/tract_output/${sub} 