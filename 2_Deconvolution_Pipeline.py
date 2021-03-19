#!/usr/bin/env python
# coding: utf-8

# In[2]:


from nipype.interfaces.io import DataSink, SelectFiles, DataGrabber 
from nipype.interfaces.utility import IdentityInterface, Function    
from nipype.pipeline.engine import Node, Workflow, JoinNode, MapNode
import nipype.interfaces.mrtrix3 as mtx
import nipype.interfaces.mrtrix3.utils as mtxu
import nipype.interfaces.mrtrix.convert as mtxc
import nipype.interfaces.mrtrix.preprocess as mtxp
import nipype.interfaces.fsl as fsl
from pandas import Series, read_csv, to_numeric
from glob import glob
from os.path import abspath, expanduser, join
from os import chdir, remove, getcwd, makedirs
from shutil import copyfile
from nipype import config, logging
from datetime import date
import sys

sub = sys.argv[1]

today = str(date.today())
config.enable_debug_mode()


# In[3]:


# Resources for MRTRIX:
# https://community.mrtrix.org/t/the-output-of-tck2connectome/345/25

## Error: FSLDIR not set
# Set module load and sourcing scripts within the activate.d folder file


# In[4]:


#Set user and path variables
local='False'

home = '/gpfs/milgram/project/gee_dylan/candlab'
raw_dir = join(home, 'data/mri/bids_recon/shapes')
proc_dir = join(home, 'analyses/shapes/dwi/data')
workflow_dir = join(home, 'analyses/shapes/dwi/workflows')
data_dir = join(home, 'analyses/shapes/dwi/data')
    
# Read in subject subject_list
# subject_info = read_csv(
#     home + '/scripts/shapes/mri/dwi/shapes_dwi_subjList_08.07.2019.txt', sep=' ', header=None)
# subjects = subject_info[0].tolist()
subject_list = [sub]

#Setup Datasink, Infosource, Selectfiles

datasink = Node(DataSink(base_directory = data_dir,
                        substitutions = [('_subject_id_', '')]),
                   name='datasink')

#Set infosource iterables
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

#SelectFiles
template = dict(dti = join(proc_dir,'3_Eddy_Corrected/{subject_id}/eddy_corrected_flirt.nii.gz'),
                bval = join(raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.bval'),
                bvec = join(proc_dir, '3_Eddy_Corrected/{subject_id}/eddy_corrected.eddy_rotated_bvecs'),
                t1 = join(raw_dir, '{subject_id}/ses-shapesV1/anat/{subject_id}_ses-shapesV1_T1w.nii.gz'),
                mni=join(home, 'atlases/MNI152_T1_2mm_brain.nii.gz'),
                b0_mask = join(proc_dir, '3_Eddy_Corrected/{subject_id}/b0_img_brain_mask_thresh_resample_flirt.nii.gz')
               )

sf = Node(SelectFiles(template, 
                      base_directory = home),
          name = 'sf')
                


# ### Nodes for Diffusion workflow

# In[5]:


# #Generate binary mask
# bet=Node(fsl.BET(frac=0.2,
#                 mask=True),
#         name='bet')

#Convert bvals and bvecs to fslgrad
gradconv = Node(mtx.MRConvert(),
               name = 'gradconv')

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

#Perform Tractography - iFOD2 (https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.mrtrix3/tracking.html) 
tract = Node(mtx.Tractography(algorithm='iFOD2',
                              select=100000, #Jiook has done 100 million streamlines
                              n_trials=10000, 
                              out_file='msCSD_brain_tracktography.tck'),
            name='tract')


# In[ ]:


csd_flow = Workflow(name = 'csd_flow')
csd_flow.connect([(infosource, sf, [('subject_id','subject_id')]),
                    #Segment T1 image with FSL 5tt algorithm
                    (sf, seg5tt, [('t1', 'in_file')]),
                    (seg5tt, datasink, [('out_file', '4_Deconvolution')]),
                   
                    #Convert bval/bvec to gradient tables
                    (sf, gradconv, [('dti', 'in_file'),
                                   ('bval','in_bval'),
                                   ('bvec', 'in_bvec')]),
                    #Compute FOD response functions
                    (sf, dwiresp, [('b0_mask', 'in_mask')]),
                    (gradconv, dwiresp, [('out_file', 'in_file')]),
                    (dwiresp, datasink, [('wm_file', '4_Deconvolution.@par.@par'),
                                        ('gm_file', '4_Deconvolution.@par.@par.@par'),
                                        ('csf_file', '4_Deconvolution.@par.@par.@par.@par')]),
                    (gradconv, mscsd, [('out_file', 'in_file')]),
                    #Perform multi-shell constrained spherical deconvolution
                    (dwiresp, mscsd, [('wm_file', 'wm_txt'),
                                      ('gm_file', 'gm_txt'),
                                      ('csf_file', 'csf_txt')]),
                    (sf, mscsd, [('b0_mask', 'mask_file')]),
#                     (mscsd, tract, [('wm_odf', 'in_file')]),
                    (mscsd, datasink, [('wm_odf', '4_Deconvolution.@par.@par.@par.@par.@par'),
                                       ('gm_odf', '4_Deconvolution.@par.@par.@par.@par.@par.@par'),
                                       ('csf_odf','4_Deconvolution.@par.@par.@par.@par.@par.@par.@par')]),
                    (gradconv, datasink, [('out_file', '4_Deconvolution.@par.@par.@par.@par.@par.@par.@par.@par')])
                   ])
csd_flow.base_dir = workflow_dir
csd_flow.write_graph(graph2use = 'flat')
dwi = csd_flow.run('MultiProc', plugin_args={'n_procs': 4})
