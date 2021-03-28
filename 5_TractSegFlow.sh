#! /bin/bash

home='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows'
datpath='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/data'

sub=$1
mkdir ${datpath}/tract_output
mkdir ${datpath}/tract_output/${sub}

conda activate shapes-dwi3.7

# bval_path='/gpfs/milgram/pi/gee_dylan/candlab/data/mri/bids_recon/shapes/'${sub}'/ses-shapesV1/dwi/'${sub}'_ses-shapesV1_dwi.bval'
# bvec_path=${datpath}'/3_Eddy_Corrected/'${sub}'/eddy_corrected.eddy_rotated_bvecs'

# #Normalise peaks per this recommendation: https://github.com/MIC-DKFZ/TractSeg/issues/42
# echo "Normalising FOD DATA" 
# mtnormalise ${datpath}'/4_Deconvolution/'${sub}'/wm.mif' ${datpath}'/4_Deconvolution/'${sub}'/wm_normalized.mif' ${datpath}'/4_Deconvolution/'${sub}'/gm.mif' ${datpath}'/4_Deconvolution/'${sub}'/gm_normalized.mif' ${datpath}'/4_Deconvolution/'${sub}'/csf.mif' ${datpath}'/4_Deconvolution/'${sub}'/csf_normalized.mif' -mask ${datpath}'/3_Eddy_Corrected/'${sub}'/b0_img_brain_mask_thresh_resample_flirt.mif'

# # if [ -e ${datpath}'/4_Deconvolution/'${sub}'/wm_peaks.nii.gz' ] ; then
# #     :
# # else
# sh2peaks -force ${datpath}'/4_Deconvolution/'${sub}'/wm_normalized.mif' ${datpath}'/4_Deconvolution/'${sub}'/wm_peaks_normalized.mif'

# mrconvert -force ${datpath}'/4_Deconvolution/'${sub}'/wm_peaks_normalized.mif' ${datpath}'/4_Deconvolution/'${sub}'/wm_peaks_normalized.nii.gz'
# # fi

infile=${datpath}'/4_Deconvolution/'${sub}'/wm_peaks_normalized.nii.gz'

# echo 'Starting TractSeg for '${sub}

# # # Run full TractSeg
# /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/TractSeg -i $infile -o ${datpath}/tract_output/${sub}/ --output_type endings_segmentation 

# /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/TractSeg -i $infile -o ${datpath}/tract_output/${sub}/ --output_type tract_segmentation 

# /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/TractSeg -i $infile -o ${datpath}/tract_output/${sub}/ --output_type TOM

# echo 'Extracting bundles for '${sub}

# # Extract tracts
# /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/Tracking -i $infile -o ${datpath}/tract_output/${sub}

# /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/Tractometry -i ${datpath}/tract_output/${sub}/TOM_trackings -o ${datpath}/tract_output/${sub}/Tractometry_${sub}.csv -e ${datpath}/tract_output/${sub}/endings_segmentations/ -s $infile --TOM ${datpath}/tract_output/${sub}/TOM --peak_length

echo 'Running tractography for '${sub}
/gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/Tracking -i $infile -o ${datpath}/tract_output/${sub}/ --nr_fibers 5000

/gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/Tractometry -i ${datpath}/tract_output/${sub}/TOM_trackings -o ${datpath}/tract_output/${sub}/Tractometry_TensorMetrics_${sub}.csv -e ${datpath}/tract_output/${sub}/endings_segmentations -s ${datpath}/tract_output/${sub}/FA.nii.gz

echo '* Done *'
