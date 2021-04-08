#! /bin/bash

ml load FSLeyes/0.32.3

data='/gpfs/milgram/project/gee_dylan/candlab/analyses/shapes/dwi'

# for sub in sub-A258 sub-A238 sub-A738 sub-A273 sub-A218 sub-A718 sub-A694 sub-A253 sub-A200 sub-A621 sub-A286 sub-A233 sub-A733 sub-A237 sub-A217 sub-A996 sub-A717 sub-A620 sub-A285 sub-A232 sub-A653 sub-A212 sub-A236 sub-A216 sub-A995 sub-A554 sub-A251 sub-A637 sub-A749 sub-A231 sub-A593 sub-A288 sub-A656 sub-A268 sub-A215 sub-A994 sub-A715 sub-A553 sub-A250 sub-A689 sub-A248 sub-A283 sub-A230 sub-A557 sub-A592 sub-A651 sub-A214 sub-A993 sub-A611 sub-A688 sub-A556 sub-A650 sub-A262 sub-A619 sub-A242 sub-A742 sub-A266 sub-A213 sub-A992 sub-A663 sub-A687 sub-A246 sub-A746 sub-A281 sub-A555 sub-A279 sub-A726 sub-A682 sub-A294 sub-A686 sub-A280 sub-A666 sub-A225 sub-A260 sub-A646 sub-A229 sub-A293 sub-A240 sub-A729 sub-A661 sub-A720 sub-A744 sub-A665 sub-A724 sub-A698 sub-A257 sub-A704 sub-A228 sub-A680 sub-A208 sub-A660 sub-A272 sub-A708 sub-A743 sub-A664 sub-A276 sub-A223 sub-A723 sub-A609 sub-A256 sub-A291 sub-A271 sub-A707 sub-A692 sub-A222 sub-A696 sub-A643 sub-A255 sub-A206 sub-A739 sub-A548 sub-A721 sub-A695 sub-A201 sub-A622 sub-A234 ; do 

for sub in sub-A749 ; do
    
    fsleyes ${data}/workflows/preproc_flow/_subject_id_${sub}/register1/${sub}_ses-shapesV1_T1w_brain_flirt.nii.gz ${data}/workflows/preproc_flow/_subject_id_${sub}/resample/preprocessed_dwi_flirt_resample.nii.gz ${data}/workflows/preproc_flow/_subject_id_${sub}/resample2/dwi_brain_mask_resample.nii.gz

done
