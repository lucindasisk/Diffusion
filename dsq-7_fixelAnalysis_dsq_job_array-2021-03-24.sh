#!/bin/bash
#SBATCH --output dsq-7_fixelAnalysis_dsq_job_array-%A_%3a-%N.out
#SBATCH --array 0-116
#SBATCH --job-name dsq-7_fixelAnalysis_dsq_job_array
#SBATCH --mem-per-cpu 10g -t 2:00:00 --mail-type ALL --partition verylong

# DO NOT EDIT LINE BELOW
/gpfs/milgram/apps/hpc.rhel7/software/dSQ/1.05/dSQBatch.py --job-file /gpfs/milgram/home/lms233/Github/Diffusion/7_fixelAnalysis_dsq_job_array.txt --status-dir /gpfs/milgram/home/lms233/Github/Diffusion

