#! /bin/bash

#Usage: ./eddy_qc <name_of_subject_list.txt

#SBATCH --job-name=shapes_eddycuda
#SBATCH --partition=gpu
#SBATCH --gres=gpu:2
#SBATCH --mem-per-cpu=10G
#SBATCH --time=3:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu
#SBATCH --gres=gpu:1

ml load StdEnv
ml load FSL/6.0.1-centos7_64

home='/gpfs/milgram/project/gee_dylan/candlab'
dwi='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi'
subs=`cat $home'/scripts/shapes/mri/dwi/shapes_dwi_subjList_08.07.2019.txt'`

if [ -d $home'/analyses/shapes/dwi/data/4_Eddy_QC_Data' ] ; then
  :
else
  mkdir $home'/analyses/shapes/dwi/data/4_Eddy_QC_Data'
fi

for sub in $subs ; do
  fldr=$home'/analyses/shapes/dwi/data/4_Eddy_QC_Data'
  if [ -d $fldr'/'$sub ] ; then
    :
  else
    eddy_quad $dwi'/data/3_EddyCorrected/'$sub'/eddy_corrected' \
    -idx $dwi'/shapes_index.txt' \
    -par $dwi'/shapes_acqparams.txt' \
    -m $dwi'/data/3_EddyCorrected/'$sub'/b0_img_brain_mask.nii.gz' \
    -b $home'/data/mri/bids_recon/shapes/'$sub'/ses-shapesV1/dwi/'$sub'_ses-shapesV1_dwi.bval' \
    -g $dwi'/data/3_EddyCorrected/'$sub'/eddy_corrected.eddy_rotated_bvecs' \
    -o $fldr'/'$sub
  fi
done
