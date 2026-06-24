''' Script to test contrast detection on the open_ms_data (https://github.com/muschellij2/open_ms_data)
    Download the dataset using:
    git clone https://github.com/muschellij2/open_ms_data.git
'''

#  %%
import os
import nibabel as nib
import pandas as pd
from clinmriqc.contrast import detect_contrast_enhancement
 

#%% 
# initialise path to open_ms_data
folder = '/Users/mathilderipart/Documents/work/260624_BMEIS_hackathon/open_ms_data/cross_sectional/coregistered'

# find subjects to run on. Here we look at all patients in the coregistered folder
subjects = os.listdir(folder)
subjects = [subject for subject in subjects if 'patient' in subject]

# %%
# for each patient, find the T1w image with contrast (T1WKS.nii.gz) and without (T1W.nii.gz) and the brain mask (brainmask.nii.gz)
# apply the function to assess if contrast is present
# TODO: get the brain mask from the image given

df = pd.DataFrame()
for subject in subjects:
    for contrast in [False, True]:
        if contrast:
            image = os.path.join(folder, subject, 'T1WKS.nii.gz')
        else:
            image = os.path.join(folder, subject, 'T1W.nii.gz')
        brain_mask = os.path.join(folder, subject, 'brainmask.nii.gz')
        
        # load nifti file
        image_arr = nib.load(image).get_fdata()
        mask_arr = nib.load(brain_mask).get_fdata().astype(bool)

        # detect contrast
        results = detect_contrast_enhancement(image_arr, 
                                                mask_arr, 
                                                vessel_ratio_threshold = 1.6, 
                                                bright_fraction_threshold = 0.002)

        # write results in dataframe
        results['id'] = subject
        results['path'] = image
        results['contrast'] = contrast

        df = pd.concat([df, pd.DataFrame([results])])

# analyse results
df_group = df.groupby(['contrast', 'enhanced'])

out = pd.DataFrame({
'count': df_group['id'].count(),
'vessel_ratio_mean': df_group['vessel_ratio'].mean(),
'vessel_ratio_min': df_group['vessel_ratio'].min(),
'vessel_ratio_max': df_group['vessel_ratio'].max(),
'bright_voxel_fraction_mean': df_group['bright_voxel_fraction'].mean(),
'bright_voxel_fraction_min': df_group['bright_voxel_fraction'].min(),
'bright_voxel_fraction_max': df_group['bright_voxel_fraction'].max(),
})

# %%
