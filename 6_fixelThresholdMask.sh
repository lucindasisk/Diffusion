#! /bin/bash

#SBATCH --job-name=shapes_preprocessing
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=10G
#SBATCH --time=12:00:00
#SBATCH --partition=long
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu
source ~/.bashrc

ml load StdEnv
ml load MRtrix3/3.0_RC3-foss-2018a

conda activate /gpfs/milgram/pi/gee_dylan/lms233/conda_envs/shapes-dwi3.7

path='/gpfs/milgram/pi/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_fixel_dir'
in_template=${path}'/CSD_MSMT_TemplatePeaksImage.mif'

echo 'Threholding peaks'
#Threshold the peaks fixel image:
mrthreshold -force ${in_template} -abs 0.15 ${path}'/CSD_MSMT_FOD_StudyTemplate_ThresholdedMask.mif'

#Generate an analysis voxel mask from the fixel mask.
fixel2voxel -force ${path}'/CSD_MSMT_FOD_StudyTemplate_ThresholdedMask.mif' count - | mrthreshold - - -abs 0.5 -force | mrfilter - median -force ${path}'/CSD_MSMT_FOD_StudyTemplate_ThresholdedMask_VoxelMask.mif'

#Recompute the fixel mask using the analysis voxel mask.
mkdir ${path}'/recomputed_fixel_dir'
rm ${path}'/recomputed_fixel_dir/*'

fod2fixel -force -mask ${path}'/CSD_MSMT_FOD_StudyTemplate_ThresholdedMask_VoxelMask.mif' ${path}'/../CSD_MSMT_FOD_StudyTemplate.mif' $path'/recomputed_fixel_dir' -peak '/temp.mif'

mrthreshold -force ${path}'/recomputed_fixel_dir/temp.mif' -abs 0.2 ${path}'/CSD_MSMT_FOD_StudyTemplate_Thresholded_FixelMaskFinal.mif' -force

rm ${path}'/CSD_MSMT_fixel_dir/temp.mif'

echo 'Done'
