#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from nipype.interfaces.io import DataSink, SelectFiles, DataGrabber
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.pipeline.engine import Node, Workflow, JoinNode, MapNode
from nipype.interfaces import fsl
import nipype.interfaces.mrtrix3 as mtx
import nipype.interfaces.freesurfer as fsr
from pandas import Series, read_csv, to_numeric
from glob import glob
from os.path import abspath, expanduser, join
from os import chdir, remove, getcwd, makedirs
from shutil import copyfile
from nipype import config, logging
from datetime import date
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
# subject_csv = read_csv(
#     home + '/scripts/shapes/mri/dwi/shapes_dwi_subjList_08.07.2019.txt', sep=' ', header=None)
# subject_list = subject_csv[0].values.tolist()

# Manual subject list
subject_list = ['sub-A686']


# In[ ]:


# 9/22/19: change so that T1 is registered to B0 per https://mrtrix.readthedocs.io/en/latest/quantitative_structural_connectivity/act.html


# In[ ]:


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
                mni=join(home, 'atlases/MNI152_T1_2mm_brain.nii.gz')
                )

sf = Node(SelectFiles(template,
                      base_directory=home),
          name='sf')


# In[ ]:


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


# In[ ]:


# Drop bottom slice (S/I) to create even # of slices
drop = Node(fsl.ExtractROI(x_min=0, x_size=140,
                           y_min=0, y_size=140,
                           z_min=1, z_size=80, output_type='NIFTI_GZ'),
            name='drop')

# drop bottom slice of DTI file
drop2 = drop.clone(name='drop2')

# Denoise DWI data susing local PCA correction - mrTrix3
denoise = Node(mtx.DWIDenoise(out_file='denoised.nii.gz'),
               name='denoise')

# Steps added 7/17 per Jiook's reccomendations
# Gibbs ringing removal
gibbs = Node(mtx.MRDeGibbs(out_file='denoised_gibbs.nii.gz'),
             name='gibbs')

# DWI bias file correction using ANTS N4
bias = Node(mtx.DWIBiasCorrect(use_ants=True,
                               out_file='denoised_gibbs_bias.nii.gz'),
            name='bias')

###########################

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
                           rigid2D=True,
                           output_type='NIFTI_GZ'),
                 name='register1')

# apply topup from merged file to rest of pe0 scan
apptop = Node(fsl.ApplyTOPUP(method='jac',
                             in_index=[2],
                             output_type='NIFTI_GZ',
                             out_corrected='preprocessed_dwi.nii.gz'),
              name='apptop')

# Skullstrip the T1w image
stripT1 = Node(fsl.BET(mask=True, output_type='NIFTI_GZ'),
               name='stripT1')

# Eddy_CUDA Node
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


# In[ ]:


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
                      (topup, datasink, [
                       ('out_corrected', '1_Check_Unwarped.@par'),
                       ('out_fieldcoef', '1_Check_Unwarped.@par.@par')]),
                      # Extract b0 image from nifti with topup applied
                      (topup, fslroi, [('out_corrected', 'in_file')]),
                      # Register T1 to b0 brain
                      (sf, register1, [('t1', 'in_file')]),
                      (fslroi, register1, [('roi_file', 'reference')]),
                      # skullstrip T1
                      (register1, stripT1, [('out_file', 'in_file')]),
                      # Save stripped anat and mask
                      (stripT1, datasink, [('mask_file', '1_Check_Unwarped.@par.@par.@par'),
                                           ('mask_file', '2_Preprocessed.@par.@par')]),
                      (stripT1, datasink, [('out_file', '1_Check_Unwarped.@par.@par.@par.@par'),
                                           ('out_file', '2_Preprocessed.@par.@par.@par')]),
                      # Drop bottom slice from DTI nifti
                      (sf, drop2, [('dti', 'in_file')]),
                      # Local PCA to denoise DTI data
                      (drop2, denoise, [('roi_file', 'in_file')]),
                      (denoise, datasink, [
                       ('out_file', '1_Check_Unwarped.@par.@par.@par.@par.@par')]),
                      # Gibbs ringing removal
                      (drop2, gibbs, [('roi_file', 'in_file')]),
                      # Perform DWI bias field correction
                      (gibbs, bias, [('out_file', 'in_file')]),
                      (sf, bias, [('bvec', 'in_bvec')]),
                      (sf, bias, [('bval', 'in_bval')]),
                      # Apply topup to bias corrected DTI data
                      (topup, apptop, [('out_fieldcoef', 'in_topup_fieldcoef'),
                                       ('out_movpar', 'in_topup_movpar')]),
                      (bias, apptop, [('out_file', 'in_files')]),
                      (sf, apptop, [('aps', 'encoding_file')]),
                      (apptop, datasink, [
                          ('out_corrected',
                           '1_Check_Unwarped.@par.@par.@par.@par.@par.@par'),
                          ('out_corrected', '2_Preprocessed.@par.@par.@par.@par')])
                      ])
preproc_flow.base_dir = workflow_dir
preproc_flow.write_graph(graph2use='flat')
preproc = preproc_flow.run('MultiProc', plugin_args={'n_procs': 4})


# In[ ]:


# In[ ]:


# In[ ]:
