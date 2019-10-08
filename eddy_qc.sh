#! /bin/bash

#Usage: ./eddy_qc <name_of_subject_list.txt

ml load StdEnv
ml load FSL/6.0.1-centos7_64

home='/gpfs/milgram/project/gee_dylan/candlab/'
dwi='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi'
subs=`cat $home'/scripts/shapes/mri/dwi/Diffusion/'$1`

if [ -d $home'/analyses/shapes/dwi/data/4_Eddy_QC_Data' ] ; then
  pass
else
  mkdir $home'/analyses/shapes/dwi/data/4_Eddy_QC_Data'
fi

for sub in $subs; do
  fldr=$home'/analyses/shapes/dwi/data/4_Eddy_QC_Data'
  mkdir $fldr'/sub'

  eddy_quad $home'/data/3_EddyCorrected/'$sub'/eddy_corrected' \
  -idx $dwi'/shapes_index.txt' \
  -par $dwi'/shapes_acqparams.txt' \
  -m $home'/data/3_EddyCorrected/'$sub'/b0_img_brain_mask.nii.gz' \
  -b $home'/data/mri/bids_recon/shapes/'$sub'/ses-shapesV1/dwi/sub-A201_ses-shapesV1_dwi.bval' \
  -o $fldr'/sub'
done
