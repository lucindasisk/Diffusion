#! /bin/bash

home='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows/tract_flow/'
cd $home
subs=$(ls)

for sub in $subs ; do
  cd $home
  rm -R $sub'/trkconvert'
done
