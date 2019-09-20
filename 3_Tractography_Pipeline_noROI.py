#!/usr/bin/env python
# coding: utf-8

# In[1]:


from nipype.interfaces.io import DataSink, SelectFiles, DataGrabber 
from nipype.interfaces.utility import IdentityInterface, Function    
from nipype.pipeline.engine import Node, Workflow, JoinNode, MapNode
import nipype.interfaces.mrtrix3 as mtx
import nipype.interfaces.mrtrix.convert as mtxc
import nipype.interfaces.fsl as fsl
from nipype.workflows.dmri.mrtrix.diffusion import create_mrtrix_dti_pipeline
from pandas import Series, read_csv, to_numeric
from glob import glob
from os.path import abspath, expanduser, join
from os import chdir, remove, getcwd, makedirs
from shutil import copyfile
from nipype import config, logging
from datetime import date
import AFQ
today = str(date.today())
config.enable_debug_mode()


# In[2]:


#Set user and path variables

user = expanduser('~')
if user == '/Users/lucindasisk':
    home = join(user, 'Desktop/Milgram/candlab')
    raw_dir = join(home, 'data/mri/bids_recon/shapes')
    proc_dir = join(home, 'analyses/shapes/dwi')
    workflow_dir = join(home, 'analyses/shapes/dwi/tractography_workflow')
    data_dir = join(home, 'analyses/shapes/dwi/tractography_data')
else:
    home = '/gpfs/milgram/project/gee_dylan/candlab'
    raw_dir = join(home, 'data/mri/bids_recon/shapes')
    proc_dir = join(home, 'analyses/shapes/dwi/eddyCUDA_data')
    workflow_dir = join(home, 'analyses/shapes/dwi/tractography_workflow')
    data_dir = join(home, 'analyses/shapes/dwi/tractography_data')
    
# Read in subject subject_list
# subject_info = read_csv(
#     home + '/scripts/shapes/mri/dwi/shapes_dwi_subjList_08.07.2019.txt', sep=' ', header=None)
# subject_list = subject_info[0].tolist()

# Manual subject list
subject_list = ['sub-A200', 'sub-A201']


# In[3]:


#Setup Datasink, Infosource, Selectfiles

datasink = Node(DataSink(base_directory = data_dir,
                        substitutions = [('_subject_id_', '')]),
                   name='datasink')

#Set infosource iterables
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

#SelectFiles
template = dict(dti = join(proc_dir,'eddyCUDA_data/3_Eddy_Corrected/{subject_id}/eddy_corrected.nii.gz'),
                bval = join(raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.bval'),
                bvec = join(proc_dir,'eddyCUDA_data/3_Eddy_Corrected/{subject_id}/eddy_corrected.eddy_rotated_bvecs'),
                t1 = join(proc_dir, 'preproc_data/2_Transfer/{subject_id}/{subject_id}_ses-shapesV1_T1w_resample_brain.nii.gz'),
                aseg = join(home, 'data/mri/hcp_pipeline_preproc/shapes/{subject_id}/MNINonLinear/aparc.a2009s+aseg.nii.gz')
               )

sf = Node(SelectFiles(template, 
                      base_directory = home),
          name = 'sf')
                


# ### Pull aseg file and extract ROIs

# In[ ]:

#
## Reorient topup b0 image to std
#reorient1 = Node(fsl.Reorient2Std(output_type='NIFTI_GZ'),
#                 name='reorient1')
#
##Register aseg to T1
#register1 = Node(fsl.FLIRT(out_matrix_file='asegtoT1_reorient_reg.mat',
#                           rigid2D=True,
#                           output_type='NIFTI_GZ'),
#                 name='register1')
#
##Threshold left hippocampus and amygdala (hippocampus = 17, amygdala = 18)
#thresh1 = Node(fsl.Threshold(thresh = 17,
#                           direction = 'below'),
#              name='thresh1')
#thresh2 = Node(fsl.Threshold(thresh = 19,
#                             direction = 'above',
#                             out_file='Left_Hipp_Amyg_ROI.nii.gz'),
#              name='thresh2')
#
##Threshold right hippocampus and amygdala (hippocampus =53, amygdala = 54)
#thresh3 = Node(fsl.Threshold(thresh = 52,
#                           direction = 'below'),
#              name='thresh3')
#thresh4 = Node(fsl.Threshold(thresh = 54,
#                             direction = 'above',
#                             out_file='Right_Hipp_Amyg_ROI.nii.gz'),
#              name='thresh4')
#
##Threshold left OFC (Lh G Orbital Cortex = 11124)
#thresh5 = Node(fsl.Threshold(thresh = 11123,
#                             direction = 'below'),
#              name='thresh5')
#thresh6 = Node(fsl.Threshold(thresh = 11124,
#                             direction = 'above',
#                             out_file='Left_OFC_ROI.nii.gz'),
#              name='thresh6')
#
##Threshold right OFC (Rh G Orbital Cortex = 11124)
#thresh7 = Node(fsl.Threshold(thresh = 12123,
#                             direction = 'below'),
#              name='thresh7')
#thresh8 = Node(fsl.Threshold(thresh = 12124,
#                             direction = 'above',
#                             out_file='Right_OFC_ROI.nii.gz'),
#              name='thresh8')
#
#
## In[ ]:
#
#
#roi_flow = Workflow(name = 'roi_flow')
#roi_flow.connect([(infosource, sf, [('subject_id','subject_id')]),
#                  (sf, reorient1, [('aseg', 'in_file')]),
#                  (reorient1, register1, [('out_file', 'in_file')]),
#                  (sf, register1, [('t1', 'reference')]),
#                  (register1, datasink, [('out_file', '4_ROIs')]),
#                  (register1, thresh1, [('out_file', 'in_file')]),
#                  (thresh1, thresh2, [('out_file', 'in_file')]),
#                  (register1, thresh3, [('out_file', 'in_file')]),
#                  (thresh3, thresh4, [('out_file', 'in_file')]),
#                  (thresh2, datasink, [('out_file', '4_ROIs.@par')]),
#                  (thresh4, datasink, [('out_file', '4_ROIs.@par.@par')]),
#                  (register1, thresh5, [('out_file', 'in_file')]),
#                  (thresh5, thresh6, [('out_file', 'in_file')]),
#                  (thresh6, datasink, [('out_file', '4_ROIs.@par.@par.@par')]),
#                  (register1, thresh7, [('out_file', 'in_file')]),
#                  (thresh7, thresh8, [('out_file', 'in_file')]),
#                  (thresh8, datasink, [('out_file', '4_ROIs.@par.@par.@par.@par')])
#                 ])
#                  
#roi_flow.base_dir = workflow_dir
#roi_flow.write_graph(graph2use = 'flat')
#dwi = roi_flow.run('MultiProc', plugin_args={'n_procs': 4})


# ### Nodes for Diffusion workflow

# In[4]:


#Generate binary mask
bet=Node(fsl.BET(frac=0.2,
                mask=True),
        name='bet')

#Generate 5 tissue type (5tt) segmentation using FAST algorithm
seg5tt = Node(mtx.Generate5tt(algorithm = 'fsl',
                             out_file = 'T1s_5tt_segmented.nii.gz'),
             name='seg5tt')

#Estimate response functions for spherical deconvolution using the specified algorithm (Dhollander)
#https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.mrtrix3/preprocess.html#responsesd
#https://mrtrix.readthedocs.io/en/latest/constrained_spherical_deconvolution/response_function_estimation.html#response-function-estimation
#Max_sh (lmax variable) determined in shell order from here: https://mrtrix.readthedocs.io/en/3.0_rc2/constrained_spherical_deconvolution/lmax.html
#DWI has 5 shells: 7 b0 volumes, 6 b500 vols, 15 b1000 vols, 15 b2000 bols, 60 b3000 vols
dwiresp = Node(mtx.ResponseSD(algorithm = 'dhollander',
                              max_sh=[0,2,4,4,8],
                              wm_file = 'wm_response.txt',
                              gm_file = 'gm_response.txt',
                              csf_file = 'csf_response.txt'),
              name='dwiresp')

#Estimate fiber orientation distributions from diffusion data sing spherical deconvolution
#https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.mrtrix3/reconst.html
#https://mrtrix.readthedocs.io/en/latest/constrained_spherical_deconvolution/multi_shell_multi_tissue_csd.html
#Max SH here determined by tissue type - chose 8,8,8 per forum recommendations
mscsd = Node(mtx.EstimateFOD(algorithm = 'msmt_csd',
                             bval_scale = 'yes',
                            max_sh = [8,8,8]),
            name='mscsd')

#Perform Tractography - ACT using iFOD2 (https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.mrtrix3/tracking.html) 
tract = Node(mtx.Tractography(algorithm='iFOD2',
                             n_trials=10000,
                             out_file='whole_brain_trcktography.tck'),
            name='tract')

trkconvert = Node(mtxc.MRTrix2TrackVis(out_filename = 'whole_brain_tractography_converted.trk'),
                 name='trkconvert')


# In[ ]:


tract_flow = Workflow(name = 'tract_flow')
tract_flow.connect([(infosource, sf, [('subject_id','subject_id')]),
                    (sf, bet, [('t1', 'in_file')]),
                    (sf, seg5tt, [('t1', 'in_file')]),
                    (seg5tt, datasink, [('out_file', '4_tract_Reconstruction')]),
                    (sf, dwiresp, [('dti', 'in_file'),
                                   ('bval','in_bval'),
                                   ('bvec', 'in_bvec')]),
#                     (dwiresp, datasink, [('wm_file', '4_tract_Reconstruction.@par'),
#                                         ('gm_file', '4_tract_Reconstruction.@par.@par'),
#                                         ('csf_file', '4_tract_Reconstruction.@par.@par.@par')]),
                    (sf, mscsd, [('dti', 'in_file'),
                                ('bval', 'in_bval'),
                                ('bvec', 'in_bvec')]),
                    (dwiresp, mscsd, [('wm_file', 'wm_txt'),
                                      ('gm_file', 'gm_txt'),
                                      ('csf_file', 'csf_txt')]),
                    (seg5tt, tract, [('out_file', 'act_file')]),
                    (mscsd, tract, [('wm_odf', 'in_file')]),
#                     (mscsd, datasink, [('wm_odf', '4_tract_Reconstruction.@par.@par.@par.@par'),
#                                        ('gm_odf', '4_tract_Reconstruction.@par.@par.@par.@par.@par'),
#                                        ('csf_odf','4_tract_Reconstruction.@par.@par.@par.@par.@par.@par')]),
                    (sf, tract, [('bval', 'in_bval'),
                                 ('bvec', 'in_bvec')]),
                    (bet, tract, [('mask_file', 'seed_image')]),
                    (tract, trkconvert, [('out_file', 'in_file')]),
                    (sf, trkconvert, [('t1','image_file')]),
                    (sf, trkconvert, [('t1','registration_image_file')]),
                    (trkconvert, datasink, [('out_file', '4_tract_Reconstruction.@par.@par.@par.@par.@par.@par.@par')]),
                    (tract, datasink, [('out_file', '4_tract_Reconstruction.@par.@par.@par.@par.@par.@par.@par.@par')]),      
                    (bet, datasink, [('mask_file','4_tract_Reconstruction.@par.@par.@par.@par.@par.@par.@par.@par.@par')])
                   ])
tract_flow.base_dir = workflow_dir
tract_flow.write_graph(graph2use = 'flat')
dwi = tract_flow.run('MultiProc', plugin_args={'n_procs': 4})


# In[18]:


#import os.path as op
#import matplotlib.pyplot as plt
#import numpy as np
#import nibabel as nib
#import dipy.data as dpd
#from dipy.data import fetcher
#import dipy.tracking.utils as dtu
#import dipy.tracking.streamline as dts
#from dipy.io.streamline import save_tractogram, load_tractogram
#from dipy.stats.analysis import afq_profile, gaussian_weights
#from dipy.io.stateful_tractogram import StatefulTractogram
#from dipy.io.stateful_tractogram import Space
#
#import AFQ.utils.streamlines as aus
#import AFQ.data as afd
#import AFQ.tractography as aft
#import AFQ.registration as reg
#import AFQ.dti as dti
#import AFQ.segmentation as seg
#from AFQ.utils.volume import patch_up_roi
#
#
## In[ ]:
#
#
## Create Nodes for AFQ Tractography Workflow
## Load processed data
#
#
## In[ ]:
#
#
#tg = load_tractogram('./dti_streamlines.trk', img)
#streamlines = tg.streamlines
#
## streamlines = dts.Streamlines(
##     dtu.transform_tracking_output(streamlines,
##                                   np.linalg.inv(img.affine)))
#
#templates = afd.read_templates()
#bundle_names = ["UF", "CST"]
#
#print("Segmenting fiber groups...")
#segmentation = seg.Segmentation()
#segmentation.segment(bundles,
#                     streamlines,
#                     fdata=hardi_fdata,
#                     fbval=hardi_fbval,
#                     fbvec=hardi_fbvec,
#                     mapping=mapping,
#                     reg_template=MNI_T2_img)
#
#
#fiber_groups = segmentation.fiber_groups
#
#print("Cleaning fiber groups...")
#for bundle in bundles:
#    fiber_groups[bundle] = seg.clean_fiber_group(fiber_groups[bundle])
#
#for kk in fiber_groups:
#    print(kk, len(fiber_groups[kk]))
#
#    sft = StatefulTractogram(
#        dtu.transform_tracking_output(fiber_groups[kk], img.affine),
#        img, Space.RASMM)
#
#    save_tractogram(sft, './%s_afq.trk'%kk,
#                    bbox_valid_check=False)
#
#print("Extracting tract profiles...")
#for bundle in bundles:
#    fig, ax = plt.subplots(1)
#    weights = gaussian_weights(fiber_groups[bundle])
#    profile = afq_profile(FA_data, fiber_groups[bundle],
#                          np.eye(4), weights=weights)
#    ax.plot(profile)
#    ax.set_title(bundle)
#
#plt.show()
#
#
## In[ ]:
#
#
#
#
#
## In[ ]:
#
#
#
#
#
## In[ ]:
#
#
## (mscsd, datasink, [('wm_odf', '4_tract_Reconstruction.@par.@par.@par.@par'),
##                                        ('gm_odf', '4_tract_Reconstruction.@par.@par.@par.@par.@par'),
##                                        ('csf_odf','4_tract_Reconstruction.@par.@par.@par.@par.@par.@par')]),
#
#
## dwi_flow = Workflow(name = 'dwi_flow')
## dwi_flow.connect([(infosource, sf, [('subject_id','subject_id')]),
##                   (sf, mrconv, [('dti', 'in_file')]),
##                   (mrconv, dwi_res, [('out_file', 'in_file')]),
##                   (sf, dwi_res, [('bval', 'in_bval'),
##                                  ('bvec', 'in_bvec')]),
##                   (dwi_res, datasink, [('csf_file', '4_DWI_Reconstruction.@par'),
##                                       ('wm_file', '4_DWI_Reconstruction.@par.@par'),
##                                       ('gm_file', '4_DWI_Reconstruction.@par.@par.@par')]),
##                   (sf, ms_csd, [('dti','in_file'),
##                                ('bval','in_bval'),
##                                ('bvec','in_bvec'),
##                                ('mask', 'mask_file')]),
##                   (dwi_res, ms_csd, [('wm_file', 'wm_txt'),
##                                      ('gm_file', 'gm_txt'),
##                                      ('csf_file', 'csf_txt')]),
##                   (ms_csd, datasink, [('wm_odf', '4_DWI_Reconstruction.@par.@par.@par.@par'),
##                                      ('gm_odf','4_DWI_Reconstruction.@par.@par.@par.@par.@par'),
##                                      ('csf_odf', '4_DWI_Reconstruction.@par.@par.@par.@par.@par.@par')])
##                  ])
## dwi_flow.base_dir = workflow_dir
## dwi_flow.write_graph(graph2use = 'flat')
## dwi = dwi_flow.run('MultiProc', plugin_args={'n_procs': 4})
#
