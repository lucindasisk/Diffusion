#! /bin/bash

#SBATCH --job-name=SIFT_connectome
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=1:00:00
#SBATCH --partition=long
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu

ml load FreeSurfer/6.0.0
sub=$1
laptop='true'

if $laptop == 'true'; then
  home='/Users/lucindasisk/Desktop/Milgram/candlab'
else
  home='/gpfs/milgram/project/gee_dylan/candlab'
fi
dwi=$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/msCSD_brain_tracktography.tck'
actfile=$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/T1s_5tt_segmented.nii.gz'
wmfod=$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/wm.mif'
t1=$home'/data/mri/shapes_freesurfer/'$sub'/mri/brain.mgz'
echo 'Starting '$sub'!'

# Convert .mgz brain to .nii
mri_convert $home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc.a2009s+aseg.mgz' \
$home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc.a2009s+aseg.nii.gz'

#Set freesurfer variable
fsraseg=$home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc.a2009s+aseg.nii.gz'

# Extract ROIs of interest
echo 'Extracting bilateral amygdala and frontal cortex for '$sub
fslmaths $fsraseg -thr 17.5 -uthr 18.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_amyg.nii.gz'
fslmaths $fsraseg -thr 53.5 -uthr 54.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_amyg.nii.gz'
fslmaths $fsraseg -thr 11100.5 -uthr 11101.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_cortex.nii.gz'
fslmaths $fsraseg -thr 12100.5 -uthr 12101.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_cortex.nii.gz'
fslmaths $fsraseg -thr 46.5 -uthr 48.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_cerebellum.nii.gz'
fslmaths $fsraseg -thr 7.5 -uthr 8.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_cerebellum.nii.gz'


# Combine binarized ROIs into one file for connectome analysis

# echo 'Creating combined mask of all 4 ROIs for '$sub
# fslmaths $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_amyg.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_amyg.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_cortex.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_cortex.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_cerebellum.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_cerebellum.nii.gz' \
# $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/combined_connectome_rois.nii.gz'

fslmaths $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_amyg.nii.gz' \
 -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_cortex.nii.gz' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_amyg_cortex_connectome_rois.nii.gz'

fslmaths $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_amyg.nii.gz' \
 -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_cortex.nii.gz' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/rightt_amyg_cortex_connectome_rois.nii.gz'

#Perform SIFT for tract data
if [ -e $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck' ] ; then
  echo 'SIFT output already exists for '$subs
else
  echo 'Running SIFT for '$sub
  tcksift -act $actfile $dwi $wmfod \
  $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck'
fi

echo 'Generating connectome for '$sub
tckedit -force  \
-include $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_amyg_cortex_connectome_rois.nii.gz' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_SIFT_msCSD_ROI_connectivity.tck'

echo 'Generating connectome for '$sub
tckedit -force  \
-include $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_amyg_cortex_connectome_rois.nii.gz' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_SIFT_msCSD_ROI_connectivity.tck'
