#!/bin/bash
#SBATCH --array 0-140
#SBATCH --output dsq-3_csd_dsq_job_array-%A_%3a-%N.out
#SBATCH --job-name dsq-3_csd_dsq_job_array
#SBATCH --mem-per-cpu 10g -t 50:00:00 --mail-type ALL --partition verylong

# DO NOT EDIT LINE BELOW
/gpfs/milgram/apps/hpc.rhel7/software/dSQ/1.05/dSQBatch.py --job-file /gpfs/milgram/home/lms233/Github/Diffusion/3_csd_dsq_job_array.txt --status-dir /gpfs/milgram/home/lms233/Github/Diffusion

