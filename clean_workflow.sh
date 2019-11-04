#! /bin/bash

home='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows/tract_flow/'

subs=$(ls)

for sub in $subs ; do
  rm -R $sub'/trkconvert'
done
