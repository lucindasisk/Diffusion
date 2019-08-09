#!/usr/bin/env python
# coding: utf-8

# In[1]:


from nipype.interfaces.io import DataSink, SelectFiles, DataGrabber
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.pipeline.engine import Node, Workflow, JoinNode, MapNode
from nipype.interfaces import fsl
from nipype import config, logging
from datetime import date
from os import getcwd
from os.path import join


# In[2]:


# Set variables
subject_list = ['sub-A200']  # , 'sub-A201']

home = getcwd()
data_dir = join(home, 'eddyCUDA_data')
workflow_dir = join(home, 'eddyCUDA_workflow')
home


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
template = dict(mask=join(home, '2_Transfer/{subject_id}/{subject_id}_ses-shapesV1_T1w_resample_brain_mask.nii.gz'),
                dti=join(
                    home, '2_Transfer/{subject_id}/resampled_dropped_denoised_gibbs_biascorr_corrected_reoriented_flirt.nii.gz'),
                bval=join(
                    home, '2_Transfer/{subject_id}/{subject_id}_ses-shapesV1_dwi.bval'),
                bvec=join(
                    home, '2_Transfer/{subject_id}/{subject_id}_ses-shapesV1_dwi.bvec'),
                aps=join(home, 'shapes_acqparams.txt'),
                index=join(home, 'shapes_index.txt')
                )

sf = Node(SelectFiles(template,
                      base_directory=home),
          name='sf')


# In[4]:


# Eddy_CUDA Node
# FSL Eddy correction to remove eddy current distortion

eddy = Node(fsl.Eddy(is_shelled=True,
                     interp='linear',
                     method='jac',
                     output_type='NIFTI_GZ',
                     residuals=True,
                     use_cuda=True,
                     cnr_maps=True,
                     repol=True),
            name='eddy')


# In[ ]:


# Workflow

eddy_flow = Workflow(name='eddy_flow')
eddy_flow.connect([(infosource, sf, [('subject_id', 'subject_id')]),
                   (sf, eddy, [('dti', 'in_file'),
                               ('bval', 'in_bval'),
                               ('bvec', 'in_bvec'),
                               ('index', 'in_index'),
                               ('aps', 'in_acqp'),
                               ('mask', 'in_mask')]),
                   (eddy, datasink, [('out_corrected', '3_Eddy_Corrected'),
                                     ('out_rotated_bvecs', '3_Eddy_Corrected.@par'),
                                     ('out_movement_rms',
                                      '3_Eddy_Corrected.@par.@par'),
                                     ('out_parameter',
                                      '3_Eddy_Corrected.@par.@par.@par'),
                                     ('out_restricted_movement_rms',
                                      '3_Eddy_Corrected.@par.@par.@par.@par'),
                                     ('out_shell_alignment_parameters',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par'),
                                     ('out_cnr_maps',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par.@par'),
                                     ('out_residuals',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par.@par.@par'),
                                     ('out_outlier_report',
                                      '3_Eddy_Corrected.@par.@par.@par.@par.@par.@par.@par')])
                   ])
eddy_flow.base_dir = workflow_dir
eddy_flow.write_graph(graph2use='flat')
eddy = eddy_flow.run('MultiProc', plugin_args={'n_procs': 4})
