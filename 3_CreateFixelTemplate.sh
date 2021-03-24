#! /bin/bash

#SBATCH --job-name=create_fixeltemplate
#SBATCH --partition=verylong
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=10G
#SBATCH --time=160:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lucinda.sisk@yale.edu
source ~/.bashrc

conda activate shapes-dwi3.7

out_file='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_FOD_StudyTemplate.mif'
in_fldr='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_FOD_TemplateImages'
mask_fldr='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/data/CSD_MSMT_FOD_TemplateMasks'

cd $mask_flder
subs=$(ls)

for sub in ${subs}; do
    mrconvert ${sub}_dwi_mask.nii.gz ${sub}_dwi_mask.mif
    rm mrconvert ${sub}_dwi_mask.nii.gz
done
    
population_template -force $in_fldr -mask_dir $mask_fldr $out_file

