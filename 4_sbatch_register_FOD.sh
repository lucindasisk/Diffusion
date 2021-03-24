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

# if [ -e ''$out_fldr'/subject_to_template_image_warped_b0_mask.mif' ] ; then
#     echo 'Already run for '$1
# else
## MRConvert nii.gz to mif
mrconvert -force $in_mask '/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/3_Eddy_Corrected/'$1'/b0_img_brain_mask_thresh_resample_flirt.mif'
in_mif='/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/3_Eddy_Corrected/'$1'/b0_img_brain_mask_thresh_resample_flirt.mif'

## Register all subject FOD images to the FOD template
mrregister -force $in_fod -mask1 $in_mif $in_template -nl_warp ''$out_fldr'/subject_to_template_image_warped.mif' ''$out_fldr'/template_to_subject_warpImage.mif'

## Compute the intersection of all subject masks in template space
mrtransform -force $in_mask -warp ''$out_fldr'/subject_to_template_image_warped.mif' -interp nearest ''$out_fldr'/subject_to_template_image_warped_b0_mask.mif'

# fi

# mkdir '/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_warped_masks'
cp ''$out_fldr'/subject_to_template_image_warped_b0_mask.mif' '/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_warped_masks/'$1'_subject_to_template_image_warped_b0_mask.mif'
    
echo '* Done *'
