#! /bin/bash

home='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi/data'

# subs=(sub-A686 sub-A621 sub-A291 sub-A653 sub-A215 sub-A687 sub-A720 sub-A294 sub-A232 sub-A739 sub-A201 sub-A689 sub-A222 sub-A280 sub-A661 sub-A293 sub-A707 sub-A646 sub-A637 sub-A743 sub-A216 sub-A217 sub-A233 sub-A650 sub-A229 sub-A682 sub-A663 sub-A234 sub-A680 sub-A993 sub-A717 sub-A665 sub-A733 sub-A726 sub-A992 sub-A996 sub-A651 sub-A656 sub-A213 sub-A256)
 
 for sub in sub-A686 sub-A621 sub-A291 sub-A653 sub-A215 sub-A687 sub-A720 sub-A294 sub-A232 sub-A739 sub-A201 sub-A689 sub-A222 sub-A280 sub-A661 sub-A293 sub-A707 sub-A646 sub-A637 sub-A743 sub-A216 sub-A217 sub-A233 sub-A650 sub-A229 sub-A682 sub-A663 sub-A234 sub-A680 sub-A993 sub-A717 sub-A665 sub-A733 sub-A726 sub-A992 sub-A996 sub-A651 sub-A656 sub-A213 sub-A256; do 
     fsleyes ${home}/3_Eddy_Corrected/${sub}/eddy_corrected_flirt.nii.gz ${home}/3_Eddy_Corrected/${sub}/b0_img_brain_mask_resample_flirt.nii.gz
 done