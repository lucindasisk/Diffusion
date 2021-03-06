#!/usr/bin/env python
# coding: utf-8

# In[2]:


from nipype.interfaces.io import DataSink, SelectFiles, DataGrabber
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.pipeline.engine import Node, Workflow, JoinNode, MapNode
from nipype.interfaces import fsl
from nipype.interfaces import ants
import nipype.interfaces.mrtrix3 as mtx
import nipype.interfaces.freesurfer as fsr
import nipype.interfaces.freesurfer.model as fsrm
from pandas import Series, read_csv, to_numeric
from glob import glob
from os.path import abspath, expanduser, join
from os import chdir, remove, getcwd, makedirs
from shutil import copyfile
from nipype import config, logging
from datetime import date
import sys

var1 = str(sys.argv[1])
today = str(date.today())
config.enable_debug_mode()


# In[ ]:


# Set variables
user = expanduser('~')
if user == '/Users/lucindasisk':
    home = join(user, 'Desktop/Milgram/candlab')
    raw_dir = join(home, 'data/mri/bids_recon/shapes')
    workflow_dir = join(home, 'analyses/shapes/dwi/workflows')
    data_dir = join(home, 'analyses/shapes/dwi/data')
else:
    home = '/gpfs/milgram/project/gee_dylan/candlab'
    raw_dir = join(home, 'data/mri/bids_recon/shapes')
    workflow_dir = join(home, 'analyses/shapes/dwi/workflows')
    data_dir = join(home, 'analyses/shapes/dwi/data')
    
# Read in subject subject_list
# subject_csv = read_csv(home + '/analyses/shapes/dwi/DTI_RI_SubjectList.csv', header=0)
# sublist = 'sub-' + Series(subject_csv['subid'])
# subject_list = sublist.values.tolist()
subject_list = [var1]


# In[8]:


# 9/22/19: change so that T1 is registered to B0 per https://mrtrix.readthedocs.io/en/latest/quantitative_structural_connectivity/act.html


# In[9]:


# Create preprocessing Workflow

# set default FreeSurfer subjects dir
fsr.FSCommand.set_default_subjects_dir(raw_dir)

# Setup Datasink, Infosource, Selectfiles

datasink = Node(DataSink(base_directory=data_dir,
                         substitutions=[('_subject_id_', '')]),
                name='datasink')

# Set infosource iterables
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

# SelectFiles
template = dict(t1=join(raw_dir, '{subject_id}/ses-shapesV1/anat/{subject_id}_ses-shapesV1_T1w.nii.gz'),
                dti=join(
                    raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.nii.gz'),
                bval=join(
                    raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.bval'),
                bvec=join(
                    raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.bvec'),
                fmappa=join(
                    raw_dir, '{subject_id}/ses-shapesV1/fmap/{subject_id}_ses-shapesV1_acq-dwi_dir-PA_epi.nii.gz'),
                fmapap=join(
                    raw_dir, '{subject_id}/ses-shapesV1/fmap/{subject_id}_ses-shapesV1_acq-dwi_dir-AP_epi.nii.gz'),
                aps=join(raw_dir, 'shapes_acqparams.txt'),
                index=join(raw_dir, 'shapes_index.txt'),
                mni=join(home, 'atlases/MNI152_T1_2mm_brain.nii.gz'),
                mni_mask=join(home, 'atlases/MNI152_T1_2mm_brain_mask.nii.gz')
                )

sf = Node(SelectFiles(template,
                      base_directory=home),
          name='sf')


# In[10]:


# Merge AP/PA encoding direction fieldmaps
def create_merged_files(ap, pa):
    from nipype.interfaces import fsl
    from os.path import abspath
    merge = fsl.Merge(in_files=[ap, pa],
                      dimension='t', output_type='NIFTI_GZ', merged_file='AP_PA_merged.nii.gz').run()
    merged_file = abspath('AP_PA_merged.nii.gz')
    return merged_file


create_merge = Node(Function(input_names=['ap', 'pa'],
                             output_names=['merged_file'],
                             function=create_merged_files),
                    name='create_merge')


# In[11]:


########################### MRTrix Commands ###########################

# Drop bottom slice (S/I) to create even # of slices
drop = Node(fsl.ExtractROI(x_min=0, x_size=140,
                           y_min=0, y_size=140,
                           z_min=1, z_size=80, output_type='NIFTI_GZ'),
            name='drop')

# drop bottom slice of DTI file
drop2 = drop.clone(name='drop2')

# Denoise DWI data susing local PCA correction - mrTrix3
denoise = Node(mtx.DWIDenoise(),
               name='denoise')

# Steps added 7/17 per Jiook's reccomendations
# Gibbs ringing removal
gibbs = Node(mtx.MRDeGibbs(),
             name='gibbs')

# DWI bias file correction using ANTS N4
bias = Node(mtx.DWIBiasCorrect(use_ants=True,
                              bval_scale = 'yes'),
            name='bias')

# Extract mask from DWI data
dwimask = Node(mtx.BrainMask(bval_scale = 'yes',
                            out_file = 'dwi_brain_mask.nii.gz'),
              name = 'dwimask')

mrconvert1 = Node(mtx.MRConvert(),
                 name = 'mrconvert1')

mrconvert2 = Node(mtx.MRConvert(),
                 name = 'mrconvert2')

########################### Standard/Other nodes ###########################

# Run topup on merged files from pe1 and pe0
topup = Node(fsl.TOPUP(config='b02b0.cnf',
                       out_corrected='ap_pa_topup.nii.gz', output_type='NIFTI_GZ'),
             name='topup')

# Select b0 image for registration
fslroi = Node(fsl.ExtractROI(t_min=0,
                             t_size=1,
                             roi_file='b0_img.nii.gz', output_type='NIFTI_GZ'),
              name='fslroi')

# Reorient topup b0 image to std
reorient1 = Node(fsl.Reorient2Std(output_type='NIFTI_GZ'),
                 name='reorient1')

# Register T1 to b0 - rigid 2D transformation
register1 = Node(fsl.FLIRT(out_matrix_file='b0toT1_reorient_reg.mat',
                           output_type='NIFTI_GZ'),
                 name='register1')

# apply topup from merged file to rest of pe0 scan
apptop = Node(fsl.ApplyTOPUP(method='jac',
                             in_index=[2], 
                             output_type='NIFTI_GZ',
                            out_corrected = 'preprocessed_dwi.nii.gz'),
              name='apptop')

# Skullstrip the T1w image
stripT1 = Node(fsl.BET(mask=True, output_type='NIFTI_GZ'),
               name='stripT1')

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
                     repol=True),
            name='eddy')

#Upsample dti to isotropic 1x1x1
resample = Node(fsr.Resample(voxel_size=(1, 1, 1)),
               name = "resample")

#Upsample dti to isotropic 1x1x1
resample2 = Node(fsr.Resample(voxel_size=(1, 1, 1)),
               name = "resample2")

#Register DTI to MNI brain
registermni = Node(fsl.FLIRT(out_matrix_file='b0toMNI_registered.mat',
                           output_type='NIFTI_GZ'),
                 name='registermni')

applyreg_mni = Node(fsl.FLIRT(out_matrix_file='b0toMNI_registered.mat',
                             output_type='NIFTI_GZ',
                             apply_xfm = True),
                 name='applyreg_mni')


# In[14]:


preproc_flow = Workflow(name='preproc_flow')
preproc_flow.connect([(infosource, sf, [('subject_id', 'subject_id')]),
                      
                      # Select AP and PA encoded fieldmaps; merge niftis
                      (sf, create_merge, [('fmapap', 'ap'),
                                          ('fmappa', 'pa')]),
                      
                      # Drop bottom slice of nifi (had odd # slices)
                      (create_merge, drop, [('merged_file', 'in_file')]),
                      
                      # Run topop across merged niftis
                      (drop, topup, [('roi_file', 'in_file')]),
                      (sf, topup, [('aps', 'encoding_file')]),
                      
                      #Select data, drop bottom slice (odd # slices)
                      (sf, drop2, [('dti', 'in_file')]),
                      
                      # denoise
                      (drop2, denoise, [('roi_file', 'in_file')]),
                      
                      # Gibbs ringing removal (in this order per https://mrtrix.readthedocs.io/en/latest/reference/commands/mrdegibbs.html)
                      (denoise, gibbs, [('out_file', 'in_file')]),
                      
                      # Apply topup to bias/Gibbs corrected DTI data
                      (topup, apptop, [('out_fieldcoef', 'in_topup_fieldcoef'),
                                      ('out_movpar','in_topup_movpar')]),
                      (gibbs, apptop, [('out_file', 'in_files')]),
                      (sf, apptop, [('aps', 'encoding_file')]),
                      
                       # Extract b0 image from nifti with topup applied
                      (apptop, fslroi, [('out_corrected', 'in_file')]),
                      
                      # Skullstrip b0
                      (fslroi, stripb0, [('roi_file', 'in_file')]),
                      
                      #Register b0 to MNI
                      (stripb0, registermni, [('out_file', 'in_file')]),
                      (sf, registermni, [('mni', 'reference')]),
                      
                      #Apply transform to dwi data
                      (registermni, applyreg_mni, [('out_matrix_file', 'in_matrix_file')]),
                      (sf, applyreg_mni, [('mni', 'reference')]),
                      (apptop, applyreg_mni, [('out_corrected', 'in_file')]),
                      (applyreg_mni, datasink, [('out_file', '1_Preprocessed_Data')]),
                      
                      # Register T1 to MNI-registered b0 ]
                      (sf, reorient1, [('t1', 'in_file')]),
                      (reorient1, register1, [('out_file', 'in_file')]),
                      (registermni, register1, [('out_file', 'reference')]),
                      (register1, datasink, [('out_file', '1_Preprocessed_Data.@par')]),
                      
                      #Convert image data to .mif for dwimask
                      (applyreg_mni, mrconvert1, [('out_file', 'in_file')]),
                      (sf, mrconvert1, [('bval', 'in_bval'),
                                     ('bvec', 'in_bvec')]),
               
                      # Create analysis mask for next steps
                      (mrconvert1, dwimask, [('out_file', 'in_file')]),
                      
                      #Resample DTI to uniform dimensions 1x1x1
                      (applyreg_mni, resample, [('out_file', 'in_file')]),
                      
                      #Resample mask file 1x1x1
                      (dwimask, resample2, [('out_file', 'in_file')]),
                      (resample2, datasink, [('resampled_file', '1_Preprocessed_Data.@par.@par')]),
                      
                      #Pass in resampled outputs to Eddy
                      (resample, eddy, [('resampled_file', 'in_file')]),
                      (sf, eddy,[('bval', 'in_bval'),
                                 ('bvec', 'in_bvec'),
                                 ('index', 'in_index'),
                                 ('aps', 'in_acqp')]),
                      (resample2, eddy, [('resampled_file', 'in_mask')]),
                      
                      #Save Eddy outputs
                      (eddy, datasink, [('out_corrected', '1_Preprocessed_Data.@par.@par.@par'),
                                        ('out_rotated_bvecs', '1_Preprocessed_Data.@par.@par.@par.@par'),
                                        ('out_movement_rms',
                                         '1_Preprocessed_Data.@par.@par.@par.@par.@par'),
                                        ('out_parameter',
                                         '1_Preprocessed_Data.@par.@par.@par.@par.@par.@par'),
                                        ('out_restricted_movement_rms',
                                         '1_Preprocessed_Data.@par.@par.@par.@par.@par.@par.@par'),
                                        ('out_shell_alignment_parameters',
                                         '1_Preprocessed_Data.@par.@par.@par.@par.@par.@par.@par.@par'),
                                        ('out_cnr_maps',
                                         '1_Preprocessed_Data.@par.@par.@par.@par.@par.@par.@par.@par.@par'),
                                        ('out_residuals',
                                         '1_Preprocessed_Data.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par'),
                                        ('out_outlier_report',
                                         '1_Preprocessed_Data.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par')]),
                     ])

preproc_flow.base_dir = workflow_dir
preproc_flow.write_graph(graph2use='flat')
preproc = preproc_flow.run('MultiProc', plugin_args={'n_procs': 2})


# In[ ]:





# In[ ]:





# In[ ]:




