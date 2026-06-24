# %%
import os
import json
import argparse
import nibabel as nib
import pandas as pd
from clinmriqc.contrast import detect_contrast_enhancement

# %%
def main():
    # %%
    parser = argparse.ArgumentParser(description="ClinMRI-QC: run full QC pipeline")
    parser.add_argument("--image", required=True, help="Path to image")
    parser.add_argument("--brain_mask", required=True, help="Path to brain mask NIfTI image")
    parser.add_argument("--outfile", default=None, help="Optional path to save JSON results")
    args = parser.parse_args()

    image = args.image
    brain_mask = args.brain_mask
    outfile = args.outfile
    

    # %% TEST
    folder = '/Users/mathilderipart/Documents/work/260624_BMEIS_hackathon/open_ms_data/cross_sectional/coregistered'
    subjects = os.listdir(folder)
    subjects = [subject for subject in subjects if 'patient' in subject]
    # %%
    
    df = pd.DataFrame()
    for subject in subjects:
        for contrast in [False, True]:
            if contrast:
                image = os.path.join(folder, subject, 'T1WKS.nii.gz')
            else:
                image = os.path.join(folder, subject, 'T1W.nii.gz')
            brain_mask = os.path.join(folder, subject, 'brainmask.nii.gz')
            outfile = None
            
            image_arr = nib.load(image).get_fdata()
            mask_arr = nib.load(brain_mask).get_fdata().astype(bool)

            results = detect_contrast_enhancement(image_arr, 
                                                  mask_arr, 
                                                  vessel_ratio_threshold = 1.6, 
                                                  bright_fraction_threshold = 0.002)

            # results
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
    out

# %%
