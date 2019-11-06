#! /bin/bash

#home='/Users/lucindasisk/Desktop/Milgram/candlab/analyses/shapes/dwi'
base='/Users/lucindasisk/Desktop/Milgram/candlab'

subs='sub-A201'

for sub in $subs; do

  home=$base'/tractography_data/5_tract_Reconstruction/'$sub
  dwi=$home'//analyses/shapes/dwi/data/5_tract_Reconstruction/'$sub'/whole_brain_trcktography.tck'
  actfile=$home'/T1s_5tt_segmented.nii.gz'
  wmfod=$home'/wm.mif'
  fsraseg=$home'/data/mri/shapes_freesurfer/'$sub'/mri/aparc.a2009s+aseg.nii.gz'
  t1=$home'/sub-A201_ses-shapesV1_T1w_resample_brain_brain.nii.gz'
 candlab/data/mri/shapes_freesurfer/sub-A698/mri
  echo 'Starting '$sub'!'

  #Registering Freesurfer parcellation to T1 image
  echo 'Registering parcellation to T1'
  if [ -e $home'/registered_aparc.a2009s+aseg.nii.gz' ] ; then
    echo 'Registered parcellation already exists for '$sub
  else
    flirt -noresampblur -in $fsraseg -ref $t1 -out $home'/registered_aparc.a2009s+aseg.nii.gz'
  fi

  #Extract ROIs of interest
  echo 'Extracting bilateral amygdala and frontal cortex for '$sub
  fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 17.5 -uthr 18.5 -bin $home/'left_amyg.nii.gz'
  fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 53.5 -uthr 54.5 -bin $home/'right_amyg.nii.gz'
  fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 11100.5 -uthr 11101.5 -bin $home/'left_cortex.nii.gz'
  fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 12100.5 -uthr 12101.5 -bin $home/'right_cortex.nii.gz'
  fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 46.5 -uthr 48.5 -bin $home/'left_cerebellum.nii.gz'
  fslmaths $home'/registered_aparc.a2009s+aseg.nii.gz' -thr 7.5 -uthr 8.5 -bin $home/'right_cerebellum.nii.gz'

  #Combine binarized ROIs into one file for connectome analysis
  echo 'Creating combined mask of all 4 ROIs for '$sub
  fslmaths $home/'left_amyg.nii.gz' -add $home/'right_amyg.nii.gz' -add $home/'left_cortex.nii.gz' \
  -add $home/'right_cortex.nii.gz' -add $home/'left_cerebellum.nii.gz' -add $home/'right_cerebellum.nii.gz' \
  $home'/combined_connectome_rois.nii.gz'

  #Perform SIFT for tract data
  if [ -e $home'/out_tracks.tck' ] ; then
    echo 'SIFT output already exists for '$subs
  else
    echo 'Running SIFT for '$sub
    tcksift -act -force $actfile $dwi $wmfod $home'/out_tracks.tck'
  fi
  echo 'Generating connectome for '$sub
  tck2connectome -force -assignment_end_voxels $home'/out_tracks.tck' $home'/registered_aparc.a2009s+aseg.nii.gz' $home'/out_connectome.csv'

done
