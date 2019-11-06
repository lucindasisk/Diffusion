#! /bin/bash

#SBATCH --job-name=SIFT_connectome
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=10G
#SBATCH --time=1:00:00
#SBATCH --partition=long
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu

sub=$1

home='/gpfs/milgram/project/gee_dylan/candlab'
dwi=$home'/analyses/shapes/dwi/data/5_tract_Reconstruction/'$sub'/msCSD_brain_tracktography.tck'
actfile=$home'/analyses/shapes/dwi/data/5_tract_Reconstruction/'$sub'/T1s_5tt_segmented.nii.gz'
wmfod=$home'/analyses/shapes/dwi/data/5_tract_Reconstruction/'$sub'/wm.mif'
fsraseg=$home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc.a2009s+aseg.mgz'
t1=$home'/data/mri/shapes_freesurfer/'$sub'/mri/brain.mgz'
echo 'Starting '$sub'!'

# #Registering Freesurfer parcellation to T1 image
# echo 'Registering parcellation to T1'
# if [ -e $home'/registered_aparc.a2009s+aseg.nii.gz' ] ; then
#   echo 'Registered parcellation already exists for '$sub
# else
#   flirt -noresampblur -in $fsraseg -ref $t1 -out $home'/registered_aparc.a2009s+aseg.nii.gz'
# fi

#Extract ROIs of interest
# echo 'Extracting bilateral amygdala and frontal cortex for '$sub
# fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 17.5 -uthr 18.5 -bin $home/'left_amyg.nii.gz'
# fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 53.5 -uthr 54.5 -bin $home/'right_amyg.nii.gz'
# fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 11100.5 -uthr 11101.5 -bin $home/'left_cortex.nii.gz'
# fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 12100.5 -uthr 12101.5 -bin $home/'right_cortex.nii.gz'
# fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 46.5 -uthr 48.5 -bin $home/'left_cerebellum.nii.gz'
# fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 7.5 -uthr 8.5 -bin $home/'right_cerebellum.nii.gz'

# Convert .mgz brain to .nii
mri_convert $fsraseg $home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc.a2009s+aseg.nii.gz'

#Combine binarized ROIs into one file for connectome analysis
# echo 'Creating combined mask of all 4 ROIs for '$sub
# fslmaths $home/'left_amyg.nii.gz' -add $home/'right_amyg.nii.gz' -add $home/'left_cortex.nii.gz' \
# -add $home/'right_cortex.nii.gz' -add $home/'left_cerebellum.nii.gz' -add $home/'right_cerebellum.nii.gz' \
# $home'/combined_connectome_rois.nii.gz'

#Perform SIFT for tract data
if [ -e $home'/analyses/shapes/dwi/data/5_tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck' ] ; then
  echo 'SIFT output already exists for '$subs
else
  echo 'Running SIFT for '$sub
  tcksift -act $actfile $dwi $wmfod \
  $home'/analyses/shapes/dwi/data/5_tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck'
fi
echo 'Generating connectome for '$sub
tck2connectome -force -assignment_end_voxels \
$home'/analyses/shapes/dwi/data/5_tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck' \
$home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc.a2009s+aseg.nii.gz' \
$home'/analyses/shapes/dwi/data/5_tract_Reconstruction/'$sub'/'$sub'_SIFT_msCSD_connectome.csv'
