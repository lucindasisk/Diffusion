#!/usr/bin/env python
# coding: utf-8

# In[33]:


from nipype.interfaces.io import DataSink, SelectFiles, DataGrabber
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.pipeline.engine import Node, Workflow, JoinNode, MapNode
import nipype.interfaces.mrtrix3 as mtx
import nipype.interfaces.fsl as fsl
from nipype.workflows.dmri.mrtrix.diffusion import create_mrtrix_dti_pipeline
from pandas import Series, read_csv, to_numeric
from glob import glob
from os.path import abspath, expanduser, join
from os import chdir, remove, getcwd, makedirs
from shutil import copyfile
from nipype import config, logging
from datetime import date
today = str(date.today())
config.enable_debug_mode()


# In[34]:


# Set user and path variables

user = expanduser('~')
if user == '/Users/lucindasisk':
    home = join(user, 'Desktop/Milgram/candlab')
    raw_dir = join(home, 'data/mri/bids_recon/shapes')
    proc_dir = join(home, 'analyses/dwi')
    workflow_dir = join(home, 'analyses/dwi/tractography_workflow')
    data_dir = join(home, 'analyses/dwi/tractography_data')
else:
    home = '/gpfs/milgram/project/gee_dylan/candlab'
    raw_dir = join(home, 'data/mri/bids_recon/shapes')
    proc_dir = join(home, 'analyses/dwi')
    workflow_dir = join(home, 'analyses/dwi/tractography_workflow')
    data_dir = join(home, 'analyses/dwi/tractography_data')

# Read in subject subject_list
# subject_info = read_csv(
#     home + '/scripts/shapes/mri/dwi/shapes_dwi_subjList_08.07.2019.txt', sep=' ', header=None)
# subject_list = subject_info[0].tolist()

# Manual subject list
subject_list = ['sub-A200']  # , 'sub-A201']


# In[35]:


# Setup Datasink, Infosource, Selectfiles

datasink = Node(DataSink(base_directory=data_dir,
                         substitutions=[('_subject_id_', '')]),
                name='datasink')

# Set infosource iterables
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

# SelectFiles
template = dict(dti=join(proc_dir, '3_Eddy_CUDA_Corrected/{subject_id}/eddy_corrected.nii.gz'),
                bval=join(
                    proc_dir, '3_Eddy_CUDA_Corrected/{subject_id}/{subject_id}_ses-shapesV1_dwi.bval'),
                bvec=join(
                    proc_dir, '3_Eddy_CUDA_Corrected/{subject_id}/eddy_corrected.eddy_rotated_bvecs'),
                t1=join(
                    raw_dir, '{subject_id}/ses-shapesV1/anat/{subject_id}_ses-shapesV1_T1w.nii.gz')
                )

sf = Node(SelectFiles(template,
                      base_directory=home),
          name='sf')


# In[36]:


# Generate 5 tissue type (5tt) segmentation using FAST algorithm
seg5tt = Node(mtx.Generate5tt(algorithm='fsl',
                              out_file='T1s_5tt_segmented.nii.gz'),
              name='seg5tt')

# Perform Tractography - ACT using iFOD2 (https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.mrtrix3/tracking.html)
tract = Node(mtx.Tractography(algorithm='iFOD2',
                              n_trials=10000),
             name='tract')


# In[ ]:


tract_flow = Workflow(name='tract_flow')
tract_flow.connect([(infosource, sf, [('subject_id', 'subject_id')]),
                    (sf, seg5tt, [('dti', 'in_file')]),
                    (seg5tt, datasink, [
                     ('out_file', '4_tract_Reconstruction')]),
                    (seg5tt, tract, [('out_file', 'act_file')]),
                    (sf, tract, [('dti', 'in_file')]),
                    (tract, datasink, [('out_file', '4_tract_Reconstruction.@par'),
                                       ('out_seeds', '4_tract_Reconstruction.@par.@par')])
                    ])
tract_flow.base_dir = workflow_dir
tract_flow.write_graph(graph2use='flat')
dwi = tract_flow.run('MultiProc', plugin_args={'n_procs': 4})


# In[ ]:


# In[ ]:


# In[ ]:


# dwi_flow = Workflow(name = 'dwi_flow')
# dwi_flow.connect([(infosource, sf, [('subject_id','subject_id')]),
#                   (sf, mrconv, [('dti', 'in_file')]),
#                   (mrconv, dwi_res, [('out_file', 'in_file')]),
#                   (sf, dwi_res, [('bval', 'in_bval'),
#                                  ('bvec', 'in_bvec')]),
#                   (dwi_res, datasink, [('csf_file', '4_DWI_Reconstruction.@par'),
#                                       ('wm_file', '4_DWI_Reconstruction.@par.@par'),
#                                       ('gm_file', '4_DWI_Reconstruction.@par.@par.@par')]),
#                   (sf, ms_csd, [('dti','in_file'),
#                                ('bval','in_bval'),
#                                ('bvec','in_bvec'),
#                                ('mask', 'mask_file')]),
#                   (dwi_res, ms_csd, [('wm_file', 'wm_txt'),
#                                      ('gm_file', 'gm_txt'),
#                                      ('csf_file', 'csf_txt')]),
#                   (ms_csd, datasink, [('wm_odf', '4_DWI_Reconstruction.@par.@par.@par.@par'),
#                                      ('gm_odf','4_DWI_Reconstruction.@par.@par.@par.@par.@par'),
#                                      ('csf_odf', '4_DWI_Reconstruction.@par.@par.@par.@par.@par.@par')])
#                  ])
# dwi_flow.base_dir = workflow_dir
# dwi_flow.write_graph(graph2use = 'flat')
# dwi = dwi_flow.run('MultiProc', plugin_args={'n_procs': 4})


# In[ ]:


# In[ ]:


# In[ ]:
