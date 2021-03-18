#!/usr/bin/env python
# coding: utf-8

# In[2]:


from nipype.interfaces.io import DataSink, SelectFiles, DataGrabber
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.pipeline.engine import Node, Workflow, JoinNode, MapNode
import nipype.interfaces.mrtrix3 as mtx
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
today = str(date.today())
config.enable_debug_mode()


# In[ ]:


# Resources for MRTRIX:
# https://community.mrtrix.org/t/the-output-of-tck2connectome/345/25


# In[3]:


# Set user and path variables
local = 'False'
user = expanduser('~')
if user == '/Users/lucindasisk':
    if local == 'True':
        laptop = '/Users/lucindasisk/Desktop/DATA'
        home = join(user, 'Desktop/Milgram/candlab')
        raw_dir = join(home, 'data/mri/bids_recon/shapes')
        proc_dir = join(home, 'analyses/shapes/dwi')
        workflow_dir = join(laptop, 'workflows_ls')
        data_dir = join(laptop, 'data_ls')
    else:
        home = join(user, 'Desktop/Milgram/candlab')
        raw_dir = join(home, 'data/mri/bids_recon/shapes')
        proc_dir = join(home, 'analyses/shapes/dwi/data')
        workflow_dir = join(home, 'analyses/shapes/dwi/workflows')
        data_dir = join(home, 'analyses/shapes/dwi/data')
else:
    home = '/gpfs/milgram/project/gee_dylan/candlab'
    raw_dir = join(home, 'data/mri/bids_recon/shapes')
    proc_dir = join(home, 'analyses/shapes/dwi/data')
    workflow_dir = join(home, 'analyses/shapes/dwi/workflows')
    data_dir = join(home, 'analyses/shapes/dwi/data')

# Read in subject subject_list
subject_info = read_csv(
    home + '/scripts/shapes/mri/dwi/shapes_dwi_subjList_08.07.2019.txt', sep=' ', header=None)
subject_list = subject_info[0].tolist()

# Manual subject list
# subject_list = ['sub-A208', 'sub-A207']


# In[4]:


# Setup Datasink, Infosource, Selectfiles

datasink = Node(DataSink(base_directory=data_dir,
                         substitutions=[('_subject_id_', '')]),
                name='datasink')

# Set infosource iterables
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

# SelectFiles
template = dict(dti=join(proc_dir, '3_Eddy_Corrected/{subject_id}/eddy_corrected_resample.nii.gz'),
                bval=join(
                    raw_dir, '{subject_id}/ses-shapesV1/dwi/{subject_id}_ses-shapesV1_dwi.bval'),
                bvec=join(
                    proc_dir, '3_Eddy_Corrected/{subject_id}/eddy_corrected.eddy_rotated_bvecs'),
                t1=join(
                    proc_dir, '2_Preprocessed/{subject_id}/{subject_id}_ses-shapesV1_T1w_flirt_brain.nii.gz'),
                mni=join(home, 'atlases/MNI152_T1_2mm_brain.nii.gz')
                )

sf = Node(SelectFiles(template,
                      base_directory=home),
          name='sf')


# ### Nodes for Diffusion workflow

# In[6]:


# Generate binary mask
bet = Node(fsl.BET(frac=0.2,
                   mask=True),
           name='bet')

# Convert bvals and bvecs to fslgrad
gradconv = Node(mtx.MRConvert(),
                name='gradconv')

# Generate 5 tissue type (5tt) segmentation using FAST algorithm
# seg5tt = Node(mtx.Generate5tt(algorithm='fsl',
#                               out_file='T1s_5tt_segmented.nii.gz'),
#               name='seg5tt')

# Estimate response functions for spherical deconvolution using the specified algorithm (Dhollander)
# https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.mrtrix3/preprocess.html#responsesd
# https://mrtrix.readthedocs.io/en/latest/constrained_spherical_deconvolution/response_function_estimation.html#response-function-estimation
# Max_sh (lmax variable) determined in shell order from here: https://mrtrix.readthedocs.io/en/3.0_rc2/constrained_spherical_deconvolution/lmax.html
# DWI has 5 shells: 7 b0 volumes, 6 b500 vols, 15 b1000 vols, 15 b2000 bols, 60 b3000 vols
dwiresp = Node(mtx.ResponseSD(algorithm='dhollander',
                              max_sh=[0, 2, 4, 4, 8],
                              wm_file='wm_response.txt',
                              gm_file='gm_response.txt',
                              csf_file='csf_response.txt'),
               name='dwiresp')

# Estimate fiber orientation distributions from diffusion data sing spherical deconvolution
# https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.mrtrix3/reconst.html
# https://mrtrix.readthedocs.io/en/latest/constrained_spherical_deconvolution/multi_shell_multi_tissue_csd.html
# Max SH here determined by tissue type - chose 8,8,8 per forum recommendations
mscsd = Node(mtx.EstimateFOD(algorithm='msmt_csd',
                             bval_scale='yes',
                             max_sh=[8, 8, 8]),
             name='mscsd')

# Perform Tractography - iFOD2 (https://nipype.readthedocs.io/en/latest/interfaces/generated/interfaces.mrtrix3/tracking.html)
tract = Node(mtx.Tractography(algorithm='iFOD2',
                              select=100000,  # Jiook has done 100 million streamlines
                              n_trials=10000,
                              out_file='msCSD_brain_tracktography.tck'),
             name='tract')

# Perform probabilistic tractography (Tensor_Prob)
tract_prob = Node(mtx.Tractography(algorithm='Tensor_Prob',
                                   select=100000,  # Jiook has done 100 million streamlines
                                   n_trials=10000,
                                   out_file='tensorProb_brain_tracktography.tck'),
                  name='tract_prob')

# Convert whole-brain tractography from MrTrix format to TrackVis
trkconvert = Node(mtxc.MRTrix2TrackVis(out_filename='msCSD_tractography_converted.trk'),
                  name='trkconvert')

trkconvert2 = Node(mtxc.MRTrix2TrackVis(out_filename='tensorProb_tractography_converted.trk'),
                   name='trkconvert2')

# convert eddy-corrected raw DTI to tensor format
dwi2tensor = Node(mtx.FitTensor(out_file='whole_brain_tensorfile.mif',
                                bval_scale='yes'),
                  name='dwi2tensor')

# Compute FA from tensor files
tensor2fa = Node(mtx.TensorMetrics(out_fa='whole_brain_FA.mif'),
                 name='tensor2fa')


# In[7]:


tract_flow = Workflow(name='tract_flow')
tract_flow.connect([(infosource, sf, [('subject_id', 'subject_id')]),
                    # Skullstrip T1
                    (sf, bet, [('t1', 'in_file')]),
                    # Convert bval/bvec to gradient tables
                    (sf, gradconv, [('dti', 'in_file'),
                                    ('bval', 'in_bval'),
                                    ('bvec', 'in_bvec')]),
                    # Compute FOD response functions
                    (gradconv, dwiresp, [('out_file', 'in_file')]),
                    (dwiresp, datasink, [('wm_file', '5_Tract_Reconstruction.@par'),
                                         ('gm_file', '5_Tract_Reconstruction.@par.@par'),
                                         ('csf_file', '5_Tract_Reconstruction.@par.@par.@par')]),
                    (gradconv, mscsd, [('out_file', 'in_file')]),
                    # Perform multi-shell constrained spherical deconvolution
                    (dwiresp, mscsd, [('wm_file', 'wm_txt'),
                                      ('gm_file', 'gm_txt'),
                                      ('csf_file', 'csf_txt')]),
                    (mscsd, tract, [('wm_odf', 'in_file')]),
                    (mscsd, datasink, [('wm_odf', '5_Tract_Reconstruction.@par.@par.@par.@par'),
                                       ('gm_odf', '5_Tract_Reconstruction.@par.@par.@par.@par.@par'),
                                       ('csf_odf', '5_Tract_Reconstruction.@par.@par.@par.@par.@par.@par')]),
                    (sf, tract, [('bval', 'in_bval'),
                                 ('bvec', 'in_bvec')]),
                    (bet, tract, [('mask_file', 'seed_image')]),
                    # Convert ms-csd files to global tractography
                    (tract, trkconvert, [('out_file', 'in_file')]),
                    (sf, trkconvert, [('t1', 'image_file')]),
                    (sf, trkconvert, [('t1', 'registration_image_file')]),
                    (trkconvert, datasink, [
                     ('out_file', '5_Tract_Reconstruction.@par.@par.@par.@par.@par.@par.@par')]),
                    (tract, datasink, [
                     ('out_file', '5_Tract_Reconstruction.@par.@par.@par.@par.@par.@par.@par.@par')]),
                    (bet, datasink, [
                     ('mask_file', '5_Tract_Reconstruction.@par.@par.@par.@par.@par.@par.@par.@par.@par')]),
                    (bet, datasink, [
                     ('out_file', '5_Tract_Reconstruction.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par')]),
                    (gradconv, tract_prob, [('out_file', 'in_file')]),
                    (bet, tract_prob, [('mask_file', 'seed_image')]),
                    (tract_prob, datasink, [
                     ('out_file', '5_Tract_Reconstruction.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par')]),
                    (tract_prob, trkconvert2, [('out_file', 'in_file')]),
                    (sf, trkconvert2, [('t1', 'image_file')]),
                    (sf, trkconvert2, [('t1', 'registration_image_file')]),
                    (trkconvert2, datasink, [
                     ('out_file', '5_Tract_Reconstruction.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par.@par')]),
                    # Nodes to create tensor FA files
                    (gradconv, dwi2tensor, [('out_file', 'in_file')]),
                    (dwi2tensor, datasink, [('out_file', '6_Tensor_Data')]),
                    (dwi2tensor, tensor2fa, [('out_file', 'in_file')]),
                    (tensor2fa, datasink, [('out_fa', '6_Tensor_Data.@par')]),
                    ])
tract_flow.base_dir = workflow_dir
tract_flow.write_graph(graph2use='flat')
dwi = tract_flow.run('MultiProc', plugin_args={'n_procs': 10})


# In[ ]:
