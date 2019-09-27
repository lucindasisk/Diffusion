#!/usr/bin/env python
# coding: utf-8

# In[2]:


from nipype.interfaces.io import DataSink, SelectFiles, DataGrabber 
from nipype.interfaces.utility import IdentityInterface, Function    
from nipype.pipeline.engine import Node, Workflow, JoinNode, MapNode
from nipype.interfaces import fsl
from nipype import config, logging
from datetime import date
from pandas import Series, read_csv, to_numeric
from os import getcwd
from os.path import join, expanduser


# In[53]:


# Set variables
user = expanduser('~')

#Set user for laptop
if user == '/Users/lucindasisk':
    base = '/Users/lucindasisk/Desktop/Milgram/candlab'
    home = join(base,'analyses/shapes/dwi')
    data_dir = join(base, 'analyses/shapes/dwi/eddyCUDA_data')
    workflow_dir = join(base, 'analyses/shapes/dwi/eddyCUDA_workflow')
    raw_dir = join(base, 'data/mri/bids_recon/shapes')

#Set user for Grace
if user == '/home/fas/gee_dylan/lms233':
    home = getcwd() + '/..'
    data_dir = join(home, 'eddyCUDA_data')
    workflow_dir = join(home, 'eddyCUDA_workflow')

#Set user for Milgram
if user == '/home/lms233':
    home = '/gpfs/milgram/project/gee_dylan/candlab'
    data_dir = 'analyses/shapes/dwi/data'
    workflow_dir = join(home, 'analyses/shapes/dwi/workflows')
    raw_dir = join(home, 'data/mri/bids_recon/shapes')
    
# Manual subject list
subject_list = ['sub-A200', 'sub-A201'] #, 'sub-A687', 'sub-A694', 'sub-A695', 'sub-A698']  # , 'sub-A201']
    
# Read in subject subject_list
# subject_csv = read_csv(home + '/scripts/shapes/mri/dwi/shapes_dwi_subjList_08.07.2019.txt', sep=' ', header=None)
# subject_list = subject_csv[0].values.tolist()


# In[54]:


# Setup Datasink, Infosource, Selectfiles

datasink = Node(DataSink(base_directory=data_dir,
                         substitutions=[('_subject_id_', '')]),
                name='datasink')

# Set infosource iterables
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

# SelectFiles
template = dict(mask=join(home, 'analyses/shapes/dwi/data/2_Preprocessed/{subject_id}/out_file.nii.gz'),
                dti=join(
                    home, 'analyses/shapes/dwi/data/2_Preprocessed/{subject_id}/preprocessed_dwi.nii.gz'),
                bval=join(
                    raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.bval'),
                bvec=join(
                    raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.bvec'),
                aps=join(home, 'analyses/shapes/dwi/shapes_acqparams.txt'),
                index=join(home, 'analyses/shapes/dwi/shapes_index.txt')    
                )


sf = Node(SelectFiles(template,
                      base_directory=home),
          name='sf')


# In[38]:


#Eddy_CUDA Node
# FSL Eddy correction to remove eddy current distortion

eddy = Node(fsl.Eddy(is_shelled=True,
                     interp='trilinear',
                     method='jac',
                     output_type='NIFTI_GZ',
                     residuals=True,
                     use_cuda=True,
                     cnr_maps=True,
                     repol=True),
            name='eddy')


# In[39]:


eddy_flow = Workflow(name='eddy_flow')
eddy_flow.connect([(infosource, sf, [('subject_id', 'subject_id')]),
                   (sf, eddy, [('dti', 'in_file'),
                               ('bval', 'in_bval'),
                               ('bvec', 'in_bvec'),
                               ('index', 'in_index'),
                               ('aps', 'in_acqp'),
                               ('mask', 'in_mask')]),
                   (eddy, datasink, [('out_corrected', '2_Preprocessed'),
                                     ('out_rotated_bvecs', '2_Preprocessed.@par'),
                                     ('out_movement_rms',
                                      '2_Preprocessed.@par.@par'),
                                     ('out_parameter',
                                      '2_Preprocessed.@par.@par.@par'),
                                     ('out_restricted_movement_rms',
                                      '2_Preprocessed.@par.@par.@par.@par'),
                                     ('out_shell_alignment_parameters',
                                      '2_Preprocessed.@par.@par.@par.@par.@par'),
                                     ('out_cnr_maps',
                                      '2_Preprocessed.@par.@par.@par.@par.@par.@par'),
                                     ('out_residuals',
                                      '2_Preprocessed.@par.@par.@par.@par.@par.@par.@par'),
                                     ('out_outlier_report',
                                      '2_Preprocessed.@par.@par.@par.@par.@par.@par.@par.@par')])
                   ])
eddy_flow.base_dir = workflow_dir
eddy_flow.write_graph(graph2use='flat')
eddy = eddy_flow.run('MultiProc', plugin_args={'n_procs': 4})


# In[55]:


#eddyqc nodes

# eddyquad = Node(fsl.EddyQuad(),     
#                name='eddyquad')


# In[56]:


# Workflow

# eddyqc_flow = Workflow(name='eddyqc_flow')
# eddyqc_flow.connect([(infosource, sf, [('subject_id', 'subject_id')]),
#                      (sf, eddyquad, [('eddy_base','base_name'),
#                                      ('index', 'idx_file'),
#                                      ('aps', 'param_file'),
#                                      ('mask', 'mask_file'),
#                                      ('bval', 'bval_file'),
#                                      ('bvec','bvec_file')])
#                    ])
# eddyqc_flow.base_dir = workflow_dir
# eddyqc_flow.write_graph(graph2use='flat')
# eddyqc = eddyqc_flow.run('MultiProc', plugin_args={'n_procs': 4})


# In[ ]:




