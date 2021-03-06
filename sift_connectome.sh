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

home='/gpfs/milgram/project/gee_dylan/candlab'
fbin='/gpfs/milgram/project/gee_dylan/lms233/fsr_bin'
dwi=$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/msCSD_brain_tracktography.tck'
wmfod=$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/wm.mif'
rawt1=$home'/data/mri/bids_recon/shapes/'$sub'/ses-shapesV1/anat/'${sub}'_ses-shapesV1_T1w.nii.gz'
t1=$home'/data/mri/shapes_freesurfer/'$sub'/mri/brain.mgz'
echo 'Starting '$sub'!'


#Making directory for connectome data
if [ -d $home'/analyses/shapes/dwi/data/7_Connectome_Data' ] ; then
  :
else
  mkdir $home'/analyses/shapes/dwi/data/7_Connectome_Data'
fi

#Perform 5tt segmentation (FAST FSL algorithm)
5ttgen fsl -force $rawt1 $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/T1s_5tt_segmented.nii.gz'

#Set ACTfile for easy calling
actfile=$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/T1s_5tt_segmented.nii.gz'

#Rename FreeSurfer LUT nodes
labelconvert -force $home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc+aseg.mgz' \
$fbin'/FreeSurferColorLUT.txt' $fbin'/fs_default.txt' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/'$sub'_parcellation_LUT.mif'

#Perform SIFT for tract data
if [ -e $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck' ] ; then
  echo 'SIFT output already exists for '$subs
else
  echo 'Running SIFT for '$sub
  tcksift -act $actfile $dwi $wmfod \
  $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck'
fi

echo 'Generating connectome for '$sub
tck2connectome -force -zero_diagonal -out_assignments \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/mrtrix_out/out_connectome_assignment.txt' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/'$sub'_parcellation_LUT.mif' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/'$sub'_wholeseg_SIFT_msCSD_connectome.csv'

connectome2tck -nodes 40,41,48,47,75,26 -force \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/mrtrix_out/out_connectome_assignment.txt' \
$home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/mrtrix_out/out_amygdala_connectome'



################################ OLD ##########################

# # Convert .mgz brain to .nii
# mri_convert $home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc.a2009s+aseg.mgz' \
# $home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc.a2009s+aseg.nii.gz'


# Extract ROIs of interest
# echo 'Extracting bilateral amygdala and frontal cortex for '$sub
# fslmaths $fsraseg -thr 17.5 -uthr 18.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_amyg.nii.gz'
# fslmaths $fsraseg -thr 53.5 -uthr 54.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_amyg.nii.gz'
# fslmaths $fsraseg -thr 11100.5 -uthr 11101.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_cortex.nii.gz'
# fslmaths $fsraseg -thr 12100.5 -uthr 12101.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_cortex.nii.gz'
# fslmaths $fsraseg -thr 46.5 -uthr 48.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_cerebellum.nii.gz'
# fslmaths $fsraseg -thr 7.5 -uthr 8.5 -bin $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_cerebellum.nii.gz'
#
#
# # Combine binarized ROIs into one file for connectome analysis
# echo 'Creating combined mask of all 4 ROIs for '$sub
# fslmaths $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_amyg.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_amyg.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_cortex.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_cortex.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/left_cerebellum.nii.gz' \
#  -add $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/right_cerebellum.nii.gz' \
# $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/combined_connectome_rois.nii.gz'


#-files per_node
# echo 'Generating shortened connectome for '$sub
# tck2connectome -force -zero_diagonal \
# $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/SIFT_msCSD_brain_tracktography.tck' \
# $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/combined_connectome_rois.nii.gz' \
# $home'/analyses/shapes/dwi/data/5_Tract_Reconstruction/'$sub'/'$sub'_ROI_SIFT_msCSD_connectome.csv'
