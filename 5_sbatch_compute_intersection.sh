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
MRtrix3/3.0_RC3-foss-2018a
ml load Python/3.6.4-foss-2018a

conda activate /gpfs/milgram/pi/gee_dylan/lms233/conda_envs/shapes-dwi3.7

in_template='/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_FOD_StudyTemplate.mif'
warped_masks='/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_warped_masks/*'

mrmath -force $warped_masks min '/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_FOD_Mask_Intersection.mif'

fod2fixel -force $in_template '/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_fixel_dir' -mask '/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_FOD_Mask_Intersection.mif' -peak 'CSD_MSMT_TemplatePeaksImage.mif'

echo 'Done'