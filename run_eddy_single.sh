#!/bin/bash

#SBATCH --job-name=shapes_eddycuda
#SBATCH --ntasks=1 --nodes=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=6:00:00
#SBATCH --mail-type=ALL
#SBATCH --cpus-per-task=5
#SBATCH --mail-user=lucinda.sisk@yale.edu
#SBATCH --gres=gpu:1


 ml load StdEnv
# ml load CUDA/7.5.18
 ml load FreeSurfer/6.0.0
 ml load FSL/6.0.1-centos7_64
 ml load Python/miniconda

source activate /gpfs/milgram/project/gee_dylan/lms233/conda_envs/shapes_dwi

sub=$1


eddy_cuda --cnr_maps --ff=10.0 --acqp=/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/shapes_acqparams.txt --bvals=/gpfs/milgram/project/gee_dylan/candlab/data/mri/bids_recon/shapes/${sub}/ses-shapesV1/dwi/${sub}_ses-shapesV1_dwi.bval --bvecs=/gpfs/milgram/project/gee_dylan/candlab/data/mri/bids_recon/shapes/${sub}/ses-shapesV1/dwi/${sub}_ses-shapesV1_dwi.bvec --imain=/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows/eddy_flow/_subject_id_${sub}/resamp_2/preprocessed_dwi_resample.nii.gz --index=/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/shapes_index.txt --mask=/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows/eddy_flow/_subject_id_${sub}/resamp_1/b0_img_brain_mask_roi_resample.nii.gz --interp=trilinear --data_is_shelled --resamp=jac --niter=5 --nvoxhp=1000 --out=/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows/eddy_flow/_subject_id_${sub}/eddy/eddy_corrected --repol --residuals
