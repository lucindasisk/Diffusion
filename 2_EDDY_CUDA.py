#!/usr/bin/env python
# coding: utf-8

# In[1]:


from nipype.interfaces.io import DataSink, SelectFiles, DataGrabber 
from nipype.interfaces.utility import IdentityInterface, Function    
from nipype.pipeline.engine import Node, Workflow, JoinNode, MapNode
from nipype.interfaces import fsl
import nipype.interfaces.freesurfer as fsr
from nipype import config, logging
from datetime import date
from pandas import Series, read_csv, to_numeric
from os import getcwd
from os.path import join, expanduser


# In[2]:


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
    data_dir = join(home,'analyses/shapes/dwi/data')
    workflow_dir = join(home, 'analyses/shapes/dwi/workflows')
    raw_dir = join(home, 'data/mri/bids_recon/shapes')
    
## Manual subject list
#subject_list = ['sub-A200', 'sub-A202'] #, 'sub-A687', 'sub-A694', 'sub-A695', 'sub-A698']  # , 'sub-A201']
    
# Read in subject subject_list
subject_csv = read_csv(home + '/scripts/shapes/mri/dwi/shapes_dwi_subjList_08.07.2019.txt', sep=' ', header=None)
subject_list = subject_csv[0].values.tolist()


# In[3]:


# Setup Datasink, Infosource, Selectfiles

datasink = Node(DataSink(base_directory=data_dir,
                         substitutions=[('_subject_id_', '')]),
                name='datasink')

# Set infosource iterables
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

# SelectFiles
template = dict(mask=join(home, 'analyses/shapes/dwi/data/2_Preprocessed/{subject_id}/b0_img_brain_mask.nii.gz'),
                dti=join(
                    home, 'analyses/shapes/dwi/data/2_Preprocessed/{subject_id}/preprocessed_dwi.nii.gz'),
                bval=join(
                    raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.bval'),
                bvec=join(
                    raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.bvec'),
                aps=join(home, 'analyses/shapes/dwi/shapes_acqparams.txt'),
                index=join(home, 'analyses/shapes/dwi/shapes_index.txt'),
                mni=join(home, 'atlases/MNI152_T1_2mm_brain.nii.gz')
                )


sf = Node(SelectFiles(template,
                      base_directory=home),
          name='sf')


# #### Workflow Nodes

# In[4]:


# Select b0 image for registration
fslroi = Node(fsl.ExtractROI(t_min=0,
                             t_size=1,
                             roi_file='b0_img.nii.gz', output_type='NIFTI_GZ'),
              name='fslroi')

# Skullstrip the b0 image
stripb0 = Node(fsl.BET(mask=True, output_type='NIFTI_GZ'),
               name='stripb0')

#Eddy_CUDA Node
# FSL Eddy correction to remove eddy current distortion

eddy = Node(fsl.Eddy(is_shelled=True,
                     interp='trilinear',
                     method='jac',
                     output_type='NIFTI_GZ',
                     residuals=True,
                     use_cuda=True,
                     cnr_maps=True,
                     repol=True,
                     args="--ol_type='both', --ol_pos=true'"),
            name='eddy')

#Resample dti to isotropic 1.7x1.7x1.7
resample = Node(fsr.Resample(voxel_size=(1.7, 1.7, 1.7)),
               name = "resample")

## Take out these nodes per this "best practices" discussion: https://community.mrtrix.org/t/diffusion-in-mni-space/367

# #Reorient to standard
# reorient = Node(fsl.Reorient2Std(output_type='NIFTI_GZ'),
#                  name='reorient')

# #Register to MNI brain
# register = Node(fsl.FLIRT(no_resample=True,
#                           out_matrix_file='DwiToMNI_reorient_reg.mat',
#                           output_type='NIFTI_GZ',
#                           out_file='eddy_corrected_resample_mni.nii.gz'),
#                name='register')


# #### Workflow Nodes

# In[5]:


eddy_flow = Workflow(name='eddy_flow')
eddy_flow.connect([(infosource, sf, [('subject_id', 'subject_id')]),
                   #Resample DTI to uniform dimensions
                   (sf, fslroi, [('dti', 'in_file')]),
                   #Skullstrip b0 volume
                   (fslroi, stripb0, [('roi_file', 'in_file')]),
                   #Save b0 mask
                   (stripb0, datasink, [('mask_file', '3_Eddy_Corrected.@par')]),
                   #Run Eddy correction
                   (sf, eddy, [('dti', 'in_file'),
                               ('bval', 'in_bval'),
                               ('bvec', 'in_bvec'),
                               ('index', 'in_index'),
                               ('aps', 'in_acqp')]),
                   (stripb0, eddy, [('mask_file', 'in_mask')]),
                   #Save Eddy outputs
                   (eddy, datasink, [('out_corrected', '3_Eddy_Corrected.@par.@par'),
                                     ('out_rotated_bvecs', '3_Eddy_Corrected.@par.@par.@par'),
                                     ('out_movement_rms',
                                      '3_Eddy_Corrected.@par.@par.@par.@par'),
                                     ('out_parameter',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par'),
                                     ('out_restricted_movement_rms',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par.@par'),
                                     ('out_shell_alignment_parameters',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par.@par.@par'),
                                     ('out_cnr_maps',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par.@par.@par.@par'),
                                     ('out_residuals',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par.@par.@par.@par.@par'),
                                     ('out_outlier_report',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par')]),   
                   (eddy, resample, [('out_corrected', 'in_file')]),
                   (resample, datasink, [('resampled_file', '3_Eddy_Corrected.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par')])      
                   ])
eddy_flow.base_dir = workflow_dir
eddy_flow.write_graph(graph2use='flat')
eddy = eddy_flow.run('MultiProc', plugin_args={'n_procs': 4})


# In[ ]:


#eddyqc nodes

# eddyquad = Node(fsl.EddyQuad(),     
#                name='eddyquad')


# In[ ]:


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




