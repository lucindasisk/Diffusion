#!/bin/bash

#SBATCH --job-name=shapes_preprocessing
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=10G
#SBATCH --time=12:00:00
#SBATCH --partition=long
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu
source ~/.bashrc

ml load StdEnv
ml load Python/3.6.4-foss-2018a

conda activate /gpfs/milgram/pi/gee_dylan/lms233/conda_envs/shapes-dwi3.7

home='/home/lms233/Github/Diffusion'

in_fod='/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/4_Deconvolution/'$1'/wm.mif'
in_mask='/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/3_Eddy_Corrected/'$1'/b0_img_brain_mask_thresh_resample_flirt.nii.gz'
out_fldr='/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/4_Deconvolution/'$1
in_template='/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_FOD_StudyTemplate.mif'
path='/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_fixel_dir'

echo 'Computing tractography'
tckgen -angle 22.5 -maxlen 250 -minlen 10 -power 1.0 $in_template -seed_image ${path}'/CSD_MSMT_FOD_StudyTemplate_ThresholdedMask_VoxelMask.mif' -mask ${path}'/CSD_MSMT_FOD_StudyTemplate_ThresholdedMask_VoxelMask.mif' -number 20000000 ${path}'/CSD_MSMT_FOD_StudyTemplate_WholeBrainTemplate_Tractogram.mif'

echo 'Filtering using SIFT'
tcksift ${path}'/CSD_MSMT_FOD_StudyTemplate_WholeBrainTemplate_Tractogram.mif' $in_template ${path}'/CSD_MSMT_FOD_StudyTemplate_WholeBrainTemplate_Tracts2million.tck' -term_number 2000000

# fixellog -force ''$out_fldr'/subject_to_template_image_warped.mif' ''$out_fldr'/wm_FOD_warped_fd_segmented_reoriented_fixelsAssigned_FC.mif'

echo '* Done *'
