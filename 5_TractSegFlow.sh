#! /bin/bash

home='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows'
datpath='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/data'

sub=$1
mkdir ${datpath}/tract_output
mkdir ${datpath}/tract_output/${sub}

conda activate shapes-dwi3.7

bval_path='/gpfs/milgram/pi/gee_dylan/candlab/data/mri/bids_recon/shapes/'${sub}'/ses-shapesV1/dwi/'${sub}'_ses-shapesV1_dwi.bval'
bvec_path=${datpath}'/1_Preprocessed_Data/'${sub}'/eddy_corrected.eddy_rotated_bvecs'

mrconvert -force ${datpath}'/3_Tensor_Data/'${sub}'/FA.mif' ${datpath}'/3_Tensor_Data/'${sub}'/FA.nii.gz'

# # Convert mask to .mif
# mrconvert -force ${datpath}'/1_Preprocessed_Data/'${sub}'/dwi_brain_mask_resample.nii.gz' ${datpath}'/1_Preprocessed_Data/'${sub}'/dwi_brain_mask_resample.mif'

# #Normalise peaks per this recommendation: https://github.com/MIC-DKFZ/TractSeg/issues/42
# echo "Normalising FOD DATA" 
# mtnormalise ${datpath}'/2_Deconvolved_Data/'${sub}'/wm.mif' ${datpath}'/2_Deconvolved_Data/'${sub}'/wm_normalized.mif' ${datpath}'/2_Deconvolved_Data/'${sub}'/gm.mif' ${datpath}'/2_Deconvolved_Data/'${sub}'/gm_normalized.mif' ${datpath}'/2_Deconvolved_Data/'${sub}'/csf.mif' ${datpath}'/2_Deconvolved_Data/'${sub}'/csf_normalized.mif' -mask ${datpath}'/1_Preprocessed_Data/'${sub}'/dwi_brain_mask_resample.mif'

# # if [ -e ${datpath}'/2_Deconvolved_Data/'${sub}'/wm_peaks.nii.gz' ] ; then
# #     :
# # else
# sh2peaks -force ${datpath}'/2_Deconvolved_Data/'${sub}'/wm_normalized.mif' ${datpath}'/2_Deconvolved_Data/'${sub}'/wm_peaks_normalized.mif'

# mrconvert -force ${datpath}'/2_Deconvolved_Data/'${sub}'/wm_peaks_normalized.mif' ${datpath}'/2_Deconvolved_Data/'${sub}'/wm_peaks_normalized.nii.gz'
# # fi

infile=${datpath}'/2_Deconvolved_Data/'${sub}'/wm_peaks_normalized.nii.gz'

# echo 'Starting TractSeg for '${sub}

# # # Run full TractSeg
# /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/TractSeg -i $infile -o ${datpath}/tract_output/${sub}/ --output_type endings_segmentation 

# /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/TractSeg -i $infile -o ${datpath}/tract_output/${sub}/ --output_type tract_segmentation 

# /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/TractSeg -i $infile -o ${datpath}/tract_output/${sub}/ --output_type TOM

# /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/Tracking -i $infile -o ${datpath}/tract_output/${sub}/ --nr_fibers 5000

echo 'Extracting peak length tractometry for '${sub}

/gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/Tractometry -i ${datpath}/tract_output/${sub}/TOM_trackings -o ${datpath}/tract_output/${sub}/Tractometry_PeakLength_${sub}.csv -e ${datpath}/tract_output/${sub}/endings_segmentations/ -s $infile --TOM ${datpath}/tract_output/${sub}/TOM --peak_length

echo 'Extracting FA tractometry for '${sub}

/gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes-dwi3.7/bin/Tractometry -i ${datpath}/tract_output/${sub}/TOM_trackings -o ${datpath}/tract_output/${sub}/Tractometry_TensorMetrics_${sub}.csv -e ${datpath}/tract_output/${sub}/endings_segmentations -s ${datpath}'/3_Tensor_Data/'${sub}'/FA.nii.gz'

echo '* Done *'
