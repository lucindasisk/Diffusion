#! /bin/bash

home='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/workflows/csd_flow/'
cd $home
subs=$(ls)
dir='bias'

for sub in $subs ; do
  echo 'removing '$dir' directory for '$sub
  cd $home
  rm -R $sub'/'$dir
done
