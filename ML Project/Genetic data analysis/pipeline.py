# -*- coding: utf-8 -*-

####################
# import libraries #
####################

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from natsort import natsorted

import os
import subprocess

# file_path = os.path.join('My Drive', 'liv', 'VIVA', 'viva_data')

"""# MOUNT THE GOOGLE DRIVE"""

# Commented out IPython magic to ensure Python compatibility.
from google.colab import drive
drive.mount('/gdrive')
# %cd /gdrive/My\ Drive/liv/VIVA/viva_data

"""# SET GLOBAL VARIABLES"""

diseases_dir = ['GSE108423', 'GSE125367', 'GSE74432', 'GSE97362', 'GSE55491', 'GSE133774']
pheno_format = 'pheno_beta_{}.tsv'

"""# MERGE SAMPLES"""

def read_and_merge_gse(diseases_dir):
    disease_df_columns = ['Chromosome', 'Start', 'End', 'ID']

    for disease in diseases_dir:
        if disease == 'GSE55491' or disease == 'GSE133774':
            file_path = 'BWS_SRS'
        else:
            file_path = '.'

        first = True
        disease_df = pd.DataFrame(columns=disease_df_columns)
        
        file_list = [ 
            f for f in os.listdir(os.path.join(file_path, disease)) \
            if os.path.isfile(os.path.join(file_path, disease, f)) \
            and f != pheno_format.format(disease) 
        ]
        
        pheno_df = pd.read_csv(os.path.join(file_path, disease, pheno_format.format(disease)), sep='\t')
        GSE_name_dict = pheno_df[ ['Sample_ID', 'GSEnumber_in_GEO_analysis'] ].set_index('Sample_ID').to_dict()['GSEnumber_in_GEO_analysis']
        # print(GSE_name_dict)

        print(f'Length of the {disease} [{len(file_list)}]')
        # print(file_list)
        for idx, sample_file in enumerate(file_list, 1):
            sample_df = pd.read_csv(os.path.join(file_path, disease, sample_file), sep='\t')
            cols = sample_df.columns

            if first:
                disease_df = sample_df[ ['Chromosome', 'Start', 'End', 'ID', cols[-1]] ].rename(columns={ cols[-1]: GSE_name_dict[cols[-1]] })
                first = False
            else:
                sub_df = sample_df[ ['ID', cols[-1]] ].rename(columns={ cols[-1]: GSE_name_dict[cols[-1]] })
                disease_df = disease_df.merge(sub_df, how='left', on='ID')

            print(f'[{idx}][{round(idx/len(file_list), 4) * 100}%] {sample_file}_sample_file done')
        
        display(disease_df)
        
        disease_df.to_csv(os.path.join(file_path, disease, disease + '.csv'), index=False)

        print(f'Saved the {disease} done')
        print()

# read_and_merge_gse(diseases_dir)

"""# COMMON FUNCTIONS"""

def read_files(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    return pheno_df, gse_file_header, bedtool_result_df

def create_control_case_file(pheno_df, gse_file_header):
    # create a control and case files list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'control' in control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' in control_case_dict[c_file] ]

    return control_files, case_files

def get_control_mean(bedtool_result_df, control_files):
    # get the mean of the control
    dmr_control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = dmr_control_df.groupby(dmr_control_df['DMR'], sort=False).mean().loc[:,dmr_control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    return dmr_control_df, mean_control_res

def get_control_mean_std(mean_control_res):
    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    std_mean_control_res = mean_control_res.std(axis=0)

    return mean_mean_control_res, std_mean_control_res

def get_case_maen(bedtool_result_df, case_files):
    # get the mean of the case
    dmr_case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = dmr_case_df.groupby(dmr_case_df['DMR'], sort=False).mean().loc[:,dmr_case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    return mean_case_res

def merge_GOM_LOM(mean_case_res, mean_mean_control_res, std_mean_control_res):
    # get the result of the GOM and LOM and combine both of the results
    GOM_res_df = (mean_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    LOM_res_df = (mean_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    GOM_LOM_res_df = GOM_res_df + LOM_res_df

    return GOM_LOM_res_df

def filter_significant_dmrs(bedtool_result_df, dmr_control_df, GOM_LOM_res_df):
    # filter the significant dmrs
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(dmr_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index
    GOM_LOM_res_df = GOM_LOM_res_df[ significant_dmr_list ]

    return GOM_LOM_res_df

def add_group_info_columns(ref_df, GOM_LOM_res_df):
    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    GOM_LOM_res_df['info'] = info_dict.values()

    return GOM_LOM_res_df

def add_mlid_column(GOM_LOM_res_df):
    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    mlid_res = dict()
    for sample in GOM_LOM_res_df.index:
        if (GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    GOM_LOM_res_df['MLID'] = mlid_res.values()
    
    return GOM_LOM_res_df

"""# RESULT OF THE 3STD ANALYSIS"""

def get_gse_result_3std(disease):
    if disease == 'GSE125367':
        get_gse_3std_1(disease)
    elif disease == 'GSE108423':
        get_gse_3std_2(disease)
    elif disease == 'GSE97362': #KMT2D / CHD7
        get_gse_3std_3(disease)
    elif disease == 'GSE74432':
        get_gse_3std_4(disease)
    elif disease == 'GSE133774' or disease == 'GSE55491':
        get_bws_srs_std(disease)

# GSE125362
def get_gse_3std_1(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'control' in control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' in control_case_dict[c_file] ]

    # get the mean of the control
    dmr_control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = dmr_control_df.groupby(dmr_control_df['DMR'], sort=False).mean().loc[:,dmr_control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    std_mean_control_res = mean_control_res.std(axis=0)

    # get the mean of the case
    dmr_case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = dmr_case_df.groupby(dmr_case_df['DMR'], sort=False).mean().loc[:,dmr_case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results
    GOM_res_df = (mean_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    LOM_res_df = (mean_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    GOM_LOM_res_df = GOM_res_df + LOM_res_df

    # filter the significant dmrs
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(dmr_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index
    GOM_LOM_res_df = GOM_LOM_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    mlid_res = dict()
    for sample in GOM_LOM_res_df.index:
        if (GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    GOM_LOM_res_df['MLID'] = mlid_res.values()

    # sort the row by index, which is sample id
    res = GOM_LOM_res_df
    res = res.reindex(index=natsorted(res.index))
    
    # print the result and save the file to the google drive and also to the local
    print(f'[ {disease} ]')
    display(res)

    from google.colab import files
    res.to_csv(f'{disease}/{disease}_std_res.csv') 
    # files.download(f'{disease}/{disease}_std_res.csv')

# GSE108423
def get_gse_3std_2(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]
    
    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files (p1,p2,p3,family) list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    info_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'info'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['info']
    control_files = [ c_file for c_file in gse_file_header if 'male_control' == control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' == control_case_dict[c_file] ]

    p1_case_files = [ c_file for c_file in gse_file_header if 'P1' in info_dict[c_file] ]
    p2_case_files = [ c_file for c_file in gse_file_header if 'P2' in info_dict[c_file] ]
    p3_case_files = [ c_file for c_file in gse_file_header if 'P3' in info_dict[c_file] ]

    family_control_files = [ c_file for c_file in gse_file_header if 'family_control' == control_case_dict[c_file] ]
    family_case_files = [ c_file for c_file in gse_file_header if 'family_case' == control_case_dict[c_file] ]

    # get the mean of the control
    control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = control_df.groupby(control_df['DMR'], sort=False).mean().loc[:,control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    family_control_df = bedtool_result_df[ ['DMR'] + family_control_files ]
    family_mean_control_res = family_control_df.groupby(family_control_df['DMR'], sort=False).mean().loc[:,family_control_df.columns[1]:].T
    family_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    std_mean_control_res = mean_control_res.std(axis=0)

    family_mean_mean_control_res = family_mean_control_res.mean(axis=0)
    family_std_mean_control_res = family_mean_control_res.std(axis=0)

    # get the mean of the case
    p1_case_df = pd.concat([ bedtool_result_df[ ['DMR', p1_case_files[0]] ], bedtool_result_df[ ['DMR', p1_case_files[0]] ] ])
    mean_p1_case_res = p1_case_df.groupby(p1_case_df['DMR'], sort=False).mean().loc[:,p1_case_df.columns[1]:].T
    mean_p1_case_res.rename_axis("samples", axis="rows", inplace=True)
    
    p2_case_df = pd.concat([ bedtool_result_df[ ['DMR', p2_case_files[0]] ], bedtool_result_df[ ['DMR', p2_case_files[0]] ] ])
    mean_p2_case_res = p2_case_df.groupby(p2_case_df['DMR'], sort=False).mean().loc[:,p2_case_df.columns[1]:].T
    mean_p2_case_res.rename_axis("samples", axis="rows", inplace=True)
    
    p3_case_df = pd.concat([ bedtool_result_df[ ['DMR', p3_case_files[0]] ], bedtool_result_df[ ['DMR', p3_case_files[0]] ] ])
    mean_p3_case_res = p3_case_df.groupby(p3_case_df['DMR'], sort=False).mean().loc[:,p3_case_df.columns[1]:].T
    mean_p3_case_res.rename_axis("samples", axis="rows", inplace=True)

    family_case_df = bedtool_result_df[ ['DMR'] + family_case_files ]
    family_mean_case_res = family_case_df.groupby(family_case_df['DMR'], sort=False).mean().loc[:,family_case_df.columns[1]:].T
    family_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results
    p1_GOM_res_df = (mean_p1_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    p1_LOM_res_df = (mean_p1_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    p1_GOM_LOM_res_df = p1_GOM_res_df + p1_LOM_res_df

    p2_GOM_res_df = (mean_p2_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    p2_LOM_res_df = (mean_p2_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    p2_GOM_LOM_res_df = p2_GOM_res_df + p2_LOM_res_df

    p3_GOM_res_df = (mean_p3_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    p3_LOM_res_df = (mean_p3_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    p3_GOM_LOM_res_df = p3_GOM_res_df + p3_LOM_res_df

    family_GOM_res_df = (family_mean_case_res - family_mean_mean_control_res > 3*family_std_mean_control_res).replace(to_replace={True: 2, False: 0})
    family_LOM_res_df = (family_mean_case_res - family_mean_mean_control_res < -3*family_std_mean_control_res).replace(to_replace={True: -2, False: 0})
    family_GOM_LOM_res_df = family_GOM_res_df + family_LOM_res_df

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    p1_GOM_LOM_res_df = p1_GOM_LOM_res_df[ significant_dmr_list ]
    p1_GOM_LOM_res_df.index = ['GSE108423_P1']
    p2_GOM_LOM_res_df = p2_GOM_LOM_res_df[ significant_dmr_list ]
    p2_GOM_LOM_res_df.index = ['GSE108423_P2']
    p3_GOM_LOM_res_df = p3_GOM_LOM_res_df[ significant_dmr_list ]
    p3_GOM_LOM_res_df.index = ['GSE108423_P3']
    family_GOM_LOM_res_df = family_GOM_LOM_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data (p1,p2,p3)
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ p1_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    p1_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ p1_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    p1_GOM_LOM_res_df['info'] = info_dict.values()

    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ p2_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    p2_GOM_LOM_res_df['group'] = group_dict.values()

    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ p2_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    p2_GOM_LOM_res_df['info'] = info_dict.values()

    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ p3_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    p3_GOM_LOM_res_df['group'] = group_dict.values()

    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ p3_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    p3_GOM_LOM_res_df['info'] = info_dict.values()

    ## add a column for group from reference data (family)
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ family_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    family_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ family_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    family_GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    mlid_res = dict()
    for sample in p1_GOM_LOM_res_df.index:
        if (p1_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + p1_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    p1_GOM_LOM_res_df['MLID'] = mlid_res.values()

    mlid_res = dict()
    for sample in p2_GOM_LOM_res_df.index:
        if (p2_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + p2_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    p2_GOM_LOM_res_df['MLID'] = mlid_res.values()

    mlid_res = dict()
    for sample in p3_GOM_LOM_res_df.index:
        if (p3_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + p3_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    p3_GOM_LOM_res_df['MLID'] = mlid_res.values()

    family_mlid_res = dict()
    for sample in family_GOM_LOM_res_df.index:
        if (family_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + family_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            family_mlid_res[sample] = 'possible'
        else:
            family_mlid_res[sample] = 'less possible'
    family_GOM_LOM_res_df['MLID'] = family_mlid_res.values()

    # sort the row by index, which is sample id (natsorted)
    p1_GOM_LOM_res_df = p1_GOM_LOM_res_df.reindex(index=natsorted(p1_GOM_LOM_res_df.index))
    p2_GOM_LOM_res_df = p2_GOM_LOM_res_df.reindex(index=natsorted(p2_GOM_LOM_res_df.index))
    p3_GOM_LOM_res_df = p3_GOM_LOM_res_df.reindex(index=natsorted(p3_GOM_LOM_res_df.index))
    family_GOM_LOM_res_df = family_GOM_LOM_res_df.reindex(index=natsorted(family_GOM_LOM_res_df.index))
    res = pd.concat([p1_GOM_LOM_res_df, p2_GOM_LOM_res_df, p3_GOM_LOM_res_df, family_GOM_LOM_res_df])

    from google.colab import files
    res.to_csv(f'{disease}/{disease}_std_res.csv') 
    # files.download(f'{disease}/{disease}_std_res.csv')

    print(f'[ {disease} ]')
    display(res)


# GSE97362
def get_gse_3std_3(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files (KMT2D, CHD7) list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    KMT2D_control_files = [ c_file for c_file in gse_file_header if 'control_KMT2D' in control_case_dict[c_file] ]
    KMT2D_case_files = [ c_file for c_file in gse_file_header if 'case_KMT2D' in control_case_dict[c_file] ]
    CHD7_control_files = [ c_file for c_file in gse_file_header if 'control_CHD7' in control_case_dict[c_file] ]
    CHD7_case_files = [ c_file for c_file in gse_file_header if 'case_CHD7' in control_case_dict[c_file] ]

    # get the mean of the control (KMT2D, CHD7)
    KMT2D_control_df = bedtool_result_df[ ['DMR'] + KMT2D_control_files ]
    KMT2D_mean_control_res = KMT2D_control_df.groupby(KMT2D_control_df['DMR'], sort=False).mean().loc[:,KMT2D_control_df.columns[1]:].T
    KMT2D_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    CHD7_control_df = bedtool_result_df[ ['DMR'] + CHD7_control_files ]
    CHD7_mean_control_res = CHD7_control_df.groupby(CHD7_control_df['DMR'], sort=False).mean().loc[:,CHD7_control_df.columns[1]:].T
    CHD7_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    KMT2D_mean_mean_control_res = KMT2D_mean_control_res.mean(axis=0)
    KMT2D_std_mean_control_res = KMT2D_mean_control_res.std(axis=0)

    CHD7_mean_mean_control_res = CHD7_mean_control_res.mean(axis=0)
    CHD7_std_mean_control_res = CHD7_mean_control_res.std(axis=0)

    # get the mean of the case (KMT2D, CHD7)
    KMT2D_case_df = bedtool_result_df[ ['DMR'] + KMT2D_case_files ]
    KMT2D_mean_case_res = KMT2D_case_df.groupby(KMT2D_case_df['DMR'], sort=False).mean().loc[:,KMT2D_case_df.columns[1]:].T
    KMT2D_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    CHD7_case_df = bedtool_result_df[ ['DMR'] + CHD7_case_files ]
    CHD7_mean_case_res = CHD7_case_df.groupby(CHD7_case_df['DMR'], sort=False).mean().loc[:,CHD7_case_df.columns[1]:].T
    CHD7_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results (KMT2D, CHD7)
    KMT2D_GOM_res_df = (KMT2D_mean_case_res - KMT2D_mean_mean_control_res > 3*KMT2D_std_mean_control_res).replace(to_replace={True: 2, False: 0})
    KMT2D_LOM_res_df = (KMT2D_mean_case_res - KMT2D_mean_mean_control_res < -3*KMT2D_std_mean_control_res).replace(to_replace={True: -2, False: 0})
    KMT2D_GOM_LOM_res_df = KMT2D_GOM_res_df + KMT2D_LOM_res_df

    CHD7_GOM_res_df = (CHD7_mean_case_res - CHD7_mean_mean_control_res > 3*CHD7_std_mean_control_res).replace(to_replace={True: 2, False: 0})
    CHD7_LOM_res_df = (CHD7_mean_case_res - CHD7_mean_mean_control_res < -3*CHD7_std_mean_control_res).replace(to_replace={True: -2, False: 0})
    CHD7_GOM_LOM_res_df = CHD7_GOM_res_df + CHD7_LOM_res_df
    
    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(KMT2D_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    KMT2D_GOM_LOM_res_df = KMT2D_GOM_LOM_res_df[ significant_dmr_list ]
    CHD7_GOM_LOM_res_df = CHD7_GOM_LOM_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ KMT2D_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    KMT2D_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ KMT2D_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    KMT2D_GOM_LOM_res_df['info'] = info_dict.values()

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ CHD7_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    CHD7_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ CHD7_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    CHD7_GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    KMT2D_mlid_res = dict()
    for sample in KMT2D_GOM_LOM_res_df.index:
        if (KMT2D_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + KMT2D_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            KMT2D_mlid_res[sample] = 'possible'
        else:
            KMT2D_mlid_res[sample] = 'less possible'
    KMT2D_GOM_LOM_res_df['MLID'] = KMT2D_mlid_res.values()

    CHD7_mlid_res = dict()
    for sample in CHD7_GOM_LOM_res_df.index:
        if (CHD7_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + CHD7_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            CHD7_mlid_res[sample] = 'possible'
        else:
            CHD7_mlid_res[sample] = 'less possible'
    CHD7_GOM_LOM_res_df['MLID'] = CHD7_mlid_res.values()

    # sort the row by index, which is sample id (natsorted)
    KMT2D_GOM_LOM_res_df = KMT2D_GOM_LOM_res_df.reindex(index=natsorted(KMT2D_GOM_LOM_res_df.index))
    CHD7_GOM_LOM_res_df = CHD7_GOM_LOM_res_df.reindex(index=natsorted(CHD7_GOM_LOM_res_df.index))
    res = pd.concat([CHD7_GOM_LOM_res_df, KMT2D_GOM_LOM_res_df])
    
    from google.colab import files
    res.to_csv(f'{disease}/{disease}_std_res.csv') 
    # files.download(f'{disease}/{disease}_std_res.csv')

    print(f'[ {disease} ]')
    display(res)


# GSE74432
def get_gse_3std_4(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files (normal, fibroblast) list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'Control' == control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' == control_case_dict[c_file] ]
    Fibroblast_control_files = [ c_file for c_file in gse_file_header if 'Control_Fibroblast' == control_case_dict[c_file] ]
    Fibroblast_case_files = [ c_file for c_file in gse_file_header if 'case_Fibroblast' == control_case_dict[c_file] ]

    # get the mean of the control (normal, fibroblast)
    control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = control_df.groupby(control_df['DMR'], sort=False).mean().loc[:,control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    Fibroblast_control_df = bedtool_result_df[ ['DMR'] + Fibroblast_control_files ]
    Fibroblast_mean_control_res = Fibroblast_control_df.groupby(Fibroblast_control_df['DMR'], sort=False).mean().loc[:,Fibroblast_control_df.columns[1]:].T
    Fibroblast_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    std_mean_control_res = mean_control_res.std(axis=0)

    Fibroblast_mean_mean_control_res = Fibroblast_mean_control_res.mean(axis=0)
    Fibroblast_std_mean_control_res = Fibroblast_mean_control_res.std(axis=0)

    # get the mean of the case (normal, fibroblast)
    case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = case_df.groupby(case_df['DMR'], sort=False).mean().loc[:,case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    Fibroblast_case_df = bedtool_result_df[ ['DMR'] + Fibroblast_case_files ]
    Fibroblast_mean_case_res = Fibroblast_case_df.groupby(Fibroblast_case_df['DMR'], sort=False).mean().loc[:,Fibroblast_case_df.columns[1]:].T
    Fibroblast_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results (normal, fibroblast)
    GOM_res_df = (mean_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    LOM_res_df = (mean_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    GOM_LOM_res_df = GOM_res_df + LOM_res_df

    Fibroblast_GOM_res_df = (Fibroblast_mean_case_res - Fibroblast_mean_mean_control_res > 3*Fibroblast_std_mean_control_res).replace(to_replace={True: 2, False: 0})
    Fibroblast_LOM_res_df = (Fibroblast_mean_case_res - Fibroblast_mean_mean_control_res < -3*Fibroblast_std_mean_control_res).replace(to_replace={True: -2, False: 0})
    Fibroblast_GOM_LOM_res_df = Fibroblast_GOM_res_df + Fibroblast_LOM_res_df

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    GOM_LOM_res_df = GOM_LOM_res_df[ significant_dmr_list ]
    Fibroblast_GOM_LOM_res_df = Fibroblast_GOM_LOM_res_df[ significant_dmr_list ]
    
    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data (normal, fibroblast)
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data (normal, fibroblast)
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    GOM_LOM_res_df['info'] = info_dict.values()

    ## add a column for group from reference data (normal, fibroblast)
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ Fibroblast_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    Fibroblast_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data (normal, fibroblast)
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ Fibroblast_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    Fibroblast_GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    mlid_res = dict()
    for sample in GOM_LOM_res_df.index:
        if (GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    GOM_LOM_res_df['MLID'] = mlid_res.values()

    Fibroblast_mlid_res = dict()
    for sample in Fibroblast_GOM_LOM_res_df.index:
        if (Fibroblast_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + Fibroblast_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            Fibroblast_mlid_res[sample] = 'possible'
        else:
            Fibroblast_mlid_res[sample] = 'less possible'
    Fibroblast_GOM_LOM_res_df['MLID'] = Fibroblast_mlid_res.values()

    # sort the row by index, which is sample id (natsorted)
    GOM_LOM_res_df = GOM_LOM_res_df.reindex(index=natsorted(GOM_LOM_res_df.index))
    Fibroblast_GOM_LOM_res_df = Fibroblast_GOM_LOM_res_df.reindex(index=natsorted(Fibroblast_GOM_LOM_res_df.index))
    res = pd.concat([GOM_LOM_res_df, Fibroblast_GOM_LOM_res_df])

    from google.colab import files
    res.to_csv(f'{disease}/{disease}_std_res.csv') 
    # files.download(f'{disease}/{disease}_std_res.csv')

    print(f'[ {disease} ]')
    display(res)

# BWS and SRS
def get_bws_srs_std(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join('BWS_SRS', disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join('BWS_SRS', disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join('BWS_SRS', disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files (normal, fibroblast) list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'control' == control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' in control_case_dict[c_file] ]

    # get the mean of the control
    dmr_control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = dmr_control_df.groupby(dmr_control_df['DMR'], sort=False).mean().loc[:,dmr_control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    std_mean_control_res = mean_control_res.std(axis=0)

    # get the mean of the case
    dmr_case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = dmr_case_df.groupby(dmr_case_df['DMR'], sort=False).mean().loc[:,dmr_case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results
    GOM_res_df = (mean_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    LOM_res_df = (mean_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    GOM_LOM_res_df = GOM_res_df + LOM_res_df

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(dmr_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    GOM_LOM_res_df = GOM_LOM_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join('BWS_SRS', disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    mlid_res = dict()
    for sample in GOM_LOM_res_df.index:
        if (GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    GOM_LOM_res_df['MLID'] = mlid_res.values()

    # sort the row by index, which is sample id (natsorted)
    res = GOM_LOM_res_df
    res = res.reindex(index=natsorted(res.index))
    
    from google.colab import files
    res.to_csv(f'BWS_SRS/{disease}/{disease}_std_res.csv') 
    # files.download(f'{disease}/{disease}_std_res.csv')

    print(f'[ {disease} ]')
    display(res)

"""# RESULT OF THE LOG ANALYSIS"""

def get_gse_result_log(disease):
    if disease == 'GSE125367':
        get_gse_log_1(disease)
    elif disease == 'GSE108423':
        get_gse_log_2(disease)
    elif disease == 'GSE97362':
        get_gse_log_3(disease)
    elif disease == 'GSE74432':
        get_gse_log_4(disease)
    elif disease == 'GSE133774' or disease == 'GSE55491':
        get_bws_srs_log(disease)

# GSE125362
def get_gse_log_1(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'control' in control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' in control_case_dict[c_file] ]

    # get the mean of the control
    dmr_control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = dmr_control_df.groupby(dmr_control_df['DMR'], sort=False).mean().loc[:,dmr_control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)

    # get the mean of the case
    dmr_case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = dmr_case_df.groupby(dmr_case_df['DMR'], sort=False).mean().loc[:,dmr_case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the log based 2 and combine both of the results
    res_df = np.log2(mean_case_res) - np.log2(mean_mean_control_res)
    info_df = pheno_df[ ['GSEnumber_in_GEO_analysis', 'info'] ].set_index('GSEnumber_in_GEO_analysis').loc[ res_df.index ]
    info_dict = info_df.to_dict()['info']
    res_df['info'] = info_dict.values()

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(dmr_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    res_df = res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ res_df.index ]
    group_dict = group_df.to_dict()['group']
    res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ res_df.index ]
    info_dict = info_df.to_dict()['info']
    res_df['info'] = info_dict.values()

    # sort the row by index, which is sample id (natsorted)
    res = res_df
    res = res.reindex(index=natsorted(res.index))

    from google.colab import files
    res.to_csv(f'{disease}/{disease}_log_res.csv') 
    # files.download(f'{disease}/{disease}_log_res.csv')

    print(f'[ {disease} ]')
    display(res)


# GSE108423
def get_gse_log_2(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    info_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'info'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['info']

    control_files = [ c_file for c_file in gse_file_header if 'male_control' == control_case_dict[c_file] ]
    p1_case_files = [ c_file for c_file in gse_file_header if 'P1' in info_dict[c_file] ]
    p2_case_files = [ c_file for c_file in gse_file_header if 'P2' in info_dict[c_file] ]
    p3_case_files = [ c_file for c_file in gse_file_header if 'P3' in info_dict[c_file] ]

    family_control_files = [ c_file for c_file in gse_file_header if 'family_control' == control_case_dict[c_file] ]
    family_case_files = [ c_file for c_file in gse_file_header if 'family_case' == control_case_dict[c_file] ]

    # get the mean of the control
    control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = control_df.groupby(control_df['DMR'], sort=False).mean().loc[:,control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    family_control_df = bedtool_result_df[ ['DMR'] + family_control_files ]
    family_mean_control_res = family_control_df.groupby(family_control_df['DMR'], sort=False).mean().loc[:,family_control_df.columns[1]:].T
    family_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    family_mean_mean_control_res = family_mean_control_res.mean(axis=0)

    # get the mean of the case
    p1_case_df = pd.concat([ bedtool_result_df[ ['DMR', p1_case_files[0]] ], bedtool_result_df[ ['DMR', p1_case_files[0]] ] ])
    mean_p1_case_res = p1_case_df.groupby(p1_case_df['DMR'], sort=False).mean().loc[:,p1_case_df.columns[1]:].T
    mean_p1_case_res.rename_axis("samples", axis="rows", inplace=True)
    
    p2_case_df = pd.concat([ bedtool_result_df[ ['DMR', p2_case_files[0]] ], bedtool_result_df[ ['DMR', p2_case_files[0]] ] ])
    mean_p2_case_res = p2_case_df.groupby(p2_case_df['DMR'], sort=False).mean().loc[:,p2_case_df.columns[1]:].T
    mean_p2_case_res.rename_axis("samples", axis="rows", inplace=True)
    
    p3_case_df = pd.concat([ bedtool_result_df[ ['DMR', p3_case_files[0]] ], bedtool_result_df[ ['DMR', p3_case_files[0]] ] ])
    mean_p3_case_res = p3_case_df.groupby(p3_case_df['DMR'], sort=False).mean().loc[:,p3_case_df.columns[1]:].T
    mean_p3_case_res.rename_axis("samples", axis="rows", inplace=True)

    family_case_df = bedtool_result_df[ ['DMR'] + family_case_files ]
    family_mean_case_res = family_case_df.groupby(family_case_df['DMR'], sort=False).mean().loc[:,family_case_df.columns[1]:].T
    family_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the log based 2 and combine both of the results
    p1_res_df = np.log2(mean_p1_case_res) - np.log2(mean_mean_control_res)
    p2_res_df = np.log2(mean_p2_case_res) - np.log2(mean_mean_control_res)
    p3_res_df = np.log2(mean_p3_case_res) - np.log2(mean_mean_control_res)
    family_res_df = np.log2(family_mean_case_res) - np.log2(family_mean_mean_control_res)

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    p1_res_df = p1_res_df[ significant_dmr_list ]
    p1_res_df.index = ['GSE108423_P1']
    p2_res_df = p2_res_df[ significant_dmr_list ]
    p2_res_df.index = ['GSE108423_P2']
    p3_res_df = p3_res_df[ significant_dmr_list ]
    p3_res_df.index = ['GSE108423_P3']
    family_res_df = family_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ p1_res_df.index ]
    group_dict = group_df.to_dict()['group']
    p1_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ p1_res_df.index ]
    info_dict = info_df.to_dict()['info']
    p1_res_df['info'] = info_dict.values()

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ p2_res_df.index ]
    group_dict = group_df.to_dict()['group']
    p2_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ p2_res_df.index ]
    info_dict = info_df.to_dict()['info']
    p2_res_df['info'] = info_dict.values()

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ p3_res_df.index ]
    group_dict = group_df.to_dict()['group']
    p3_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ p3_res_df.index ]
    info_dict = info_df.to_dict()['info']
    p3_res_df['info'] = info_dict.values()

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ family_res_df.index ]
    group_dict = group_df.to_dict()['group']
    family_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ family_res_df.index ]
    info_dict = info_df.to_dict()['info']
    family_res_df['info'] = info_dict.values()

    # sort the row by index, which is sample id (natsorted)
    p1_res_df = p1_res_df.reindex(index=natsorted(p1_res_df.index))
    p2_res_df = p2_res_df.reindex(index=natsorted(p2_res_df.index))
    p3_res_df = p3_res_df.reindex(index=natsorted(p3_res_df.index))
    family_res_df = family_res_df.reindex(index=natsorted(family_res_df.index))
    res = pd.concat([p1_res_df, p2_res_df, p3_res_df, family_res_df])
    
    from google.colab import files
    res.to_csv(f'{disease}/{disease}_log_res.csv') 
    files.download(f'{disease}/{disease}_log_res.csv')

    print(f'[ {disease} ]')
    display(res)


# GSE97362
def get_gse_log_3(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    KMT2D_control_files = [ c_file for c_file in gse_file_header if 'control_KMT2D' in control_case_dict[c_file] ]
    KMT2D_case_files = [ c_file for c_file in gse_file_header if 'case_KMT2D' in control_case_dict[c_file] ]
    CHD7_control_files = [ c_file for c_file in gse_file_header if 'control_CHD7' in control_case_dict[c_file] ]
    CHD7_case_files = [ c_file for c_file in gse_file_header if 'case_CHD7' in control_case_dict[c_file] ]

    # get the mean of the control
    KMT2D_control_df = bedtool_result_df[ ['DMR'] + KMT2D_control_files ]
    KMT2D_mean_control_res = KMT2D_control_df.groupby(KMT2D_control_df['DMR'], sort=False).mean().loc[:,KMT2D_control_df.columns[1]:].T
    KMT2D_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    CHD7_control_df = bedtool_result_df[ ['DMR'] + CHD7_control_files ]
    CHD7_mean_control_res = CHD7_control_df.groupby(CHD7_control_df['DMR'], sort=False).mean().loc[:,CHD7_control_df.columns[1]:].T
    CHD7_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    KMT2D_mean_mean_control_res = KMT2D_mean_control_res.mean(axis=0)
    CHD7_mean_mean_control_res = CHD7_mean_control_res.mean(axis=0)

    # get the mean of the case
    KMT2D_case_df = bedtool_result_df[ ['DMR'] + KMT2D_case_files ]
    KMT2D_mean_case_res = KMT2D_case_df.groupby(KMT2D_case_df['DMR'], sort=False).mean().loc[:,KMT2D_case_df.columns[1]:].T
    KMT2D_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    CHD7_case_df = bedtool_result_df[ ['DMR'] + CHD7_case_files ]
    CHD7_mean_case_res = CHD7_case_df.groupby(CHD7_case_df['DMR'], sort=False).mean().loc[:,CHD7_case_df.columns[1]:].T
    CHD7_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the log based 2 and combine both of the results
    KMT2D_res_df = np.log2(KMT2D_mean_case_res) - np.log2(KMT2D_mean_mean_control_res)
    CHD7_res_df = np.log2(CHD7_mean_case_res) - np.log2(CHD7_mean_mean_control_res)

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(KMT2D_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    KMT2D_res_df = KMT2D_res_df[ significant_dmr_list ]
    CHD7_res_df = CHD7_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ KMT2D_res_df.index ]
    group_dict = group_df.to_dict()['group']
    KMT2D_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ KMT2D_res_df.index ]
    info_dict = info_df.to_dict()['info']
    KMT2D_res_df['info'] = info_dict.values()

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ CHD7_res_df.index ]
    group_dict = group_df.to_dict()['group']
    CHD7_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ CHD7_res_df.index ]
    info_dict = info_df.to_dict()['info']
    CHD7_res_df['info'] = info_dict.values()

    # sort the row by index, which is sample id (natsorted)
    KMT2D_res_df = KMT2D_res_df.reindex(index=natsorted(KMT2D_res_df.index))
    CHD7_res_df = CHD7_res_df.reindex(index=natsorted(CHD7_res_df.index))
    res = pd.concat([CHD7_res_df, KMT2D_res_df])
    
    from google.colab import files
    res.to_csv(f'{disease}/{disease}_log_res.csv') 
    # files.download(f'{disease}/{disease}_log_res.csv')

    print(f'[ {disease} ]')
    display(res)


# GSE74432
def get_gse_log_4(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'Control' == control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' == control_case_dict[c_file] ]
    Fibroblast_control_files = [ c_file for c_file in gse_file_header if 'Control_Fibroblast' == control_case_dict[c_file] ]
    Fibroblast_case_files = [ c_file for c_file in gse_file_header if 'case_Fibroblast' == control_case_dict[c_file] ]

    # get the mean of the control
    control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = control_df.groupby(control_df['DMR'], sort=False).mean().loc[:,control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    Fibroblast_control_df = bedtool_result_df[ ['DMR'] + Fibroblast_control_files ]
    Fibroblast_mean_control_res = Fibroblast_control_df.groupby(Fibroblast_control_df['DMR'], sort=False).mean().loc[:,Fibroblast_control_df.columns[1]:].T
    Fibroblast_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    Fibroblast_mean_mean_control_res = Fibroblast_mean_control_res.mean(axis=0)

    # get the mean of the case
    case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = case_df.groupby(case_df['DMR'], sort=False).mean().loc[:,case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    Fibroblast_case_df = bedtool_result_df[ ['DMR'] + Fibroblast_case_files ]
    Fibroblast_mean_case_res = Fibroblast_case_df.groupby(Fibroblast_case_df['DMR'], sort=False).mean().loc[:,Fibroblast_case_df.columns[1]:].T
    Fibroblast_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the log based 2 and combine both of the results
    res_df = np.log2(mean_case_res) - np.log2(mean_mean_control_res)
    Fibroblast_res_df = np.log2(Fibroblast_mean_case_res) - np.log2(Fibroblast_mean_mean_control_res)

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    res_df = res_df[ significant_dmr_list ]
    Fibroblast_res_df = Fibroblast_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ res_df.index ]
    group_dict = group_df.to_dict()['group']
    res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ res_df.index ]
    info_dict = info_df.to_dict()['info']
    res_df['info'] = info_dict.values()

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ Fibroblast_res_df.index ]
    group_dict = group_df.to_dict()['group']
    Fibroblast_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ Fibroblast_res_df.index ]
    info_dict = info_df.to_dict()['info']
    Fibroblast_res_df['info'] = info_dict.values()

    # sort the row by index, which is sample id (natsorted)
    res_df = res_df.reindex(index=natsorted(res_df.index))
    Fibroblast_res_df = Fibroblast_res_df.reindex(index=natsorted(Fibroblast_res_df.index))
    res = pd.concat([res_df, Fibroblast_res_df])
    
    from google.colab import files
    res.to_csv(f'{disease}/{disease}_log_res.csv') 
    # files.download(f'{disease}/{disease}_log_res.csv')

    print(f'[ {disease} ]')
    display(res)


# BWS and SRS
def get_bws_srs_log(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join('BWS_SRS', disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join('BWS_SRS', disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join('BWS_SRS', disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'control' == control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' in control_case_dict[c_file] ]

    # get the mean of the control
    dmr_control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = dmr_control_df.groupby(dmr_control_df['DMR'], sort=False).mean().loc[:,dmr_control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)

    # get the mean of the case
    dmr_case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = dmr_case_df.groupby(dmr_case_df['DMR'], sort=False).mean().loc[:,dmr_case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the log based 2 and combine both of the results
    res_df = np.log2(mean_case_res) - np.log2(mean_mean_control_res)

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(dmr_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    res_df = res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join('BWS_SRS', disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ res_df.index ]
    group_dict = group_df.to_dict()['group']
    res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ res_df.index ]
    info_dict = info_df.to_dict()['info']
    res_df['info'] = info_dict.values()
    
    # sort the row by index, which is sample id (natsorted)
    res = res_df
    res = res.reindex(index=natsorted(res.index))
    
    from google.colab import files
    res.to_csv(f'BWS_SRS/{disease}/{disease}_log_res.csv') 
    # files.download(f'{disease}/{disease}_log_res.csv')

    print(f'[ {disease} ]')
    display(res)

"""# RESULT OF THE 3STD + LOG ANALYSIS"""

def get_gse_result_3std_log(disease):
    if disease == 'GSE125367':
        get_gse_3std_log_1(disease)
    elif disease == 'GSE108423':
        get_gse_3std_log_2(disease)
    elif disease == 'GSE97362':
        get_gse_3std_log_3(disease)
    elif disease == 'GSE74432':
        get_gse_3std_log_4(disease)
    elif disease == 'GSE133774' or disease == 'GSE55491':
        get_bws_srs_3std_log(disease)

# GSE125362
def get_gse_3std_log_1(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'control' in control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' in control_case_dict[c_file] ]

    # get the mean of the control
    dmr_control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = dmr_control_df.groupby(dmr_control_df['DMR'], sort=False).mean().loc[:,dmr_control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    std_mean_control_res = mean_control_res.std(axis=0)

    # get the mean of the case
    dmr_case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = dmr_case_df.groupby(dmr_case_df['DMR'], sort=False).mean().loc[:,dmr_case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results
    GOM_res_df = (mean_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    LOM_res_df = (mean_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    GOM_LOM_res_df = GOM_res_df + LOM_res_df

    # combine 3std and log result
    threshold = 0.4
    res_df = np.log2(mean_case_res) - np.log2(mean_mean_control_res)
    GOM_LOM_res_df = GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    GOM_LOM_res_df = GOM_LOM_res_df.fillna(0).astype('int16')

    # filter the significant dmrs
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(dmr_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index
    GOM_LOM_res_df = GOM_LOM_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    mlid_res = dict()
    for sample in GOM_LOM_res_df.index:
        if (GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    GOM_LOM_res_df['MLID'] = mlid_res.values()

    # sort the row by index, which is sample id
    res = GOM_LOM_res_df
    res = res.reindex(index=natsorted(res.index))

    # print the result and save the file to the google drive and also to the local
    print(f'[ {disease} ]')
    display(res)

    from google.colab import files
    res.to_csv(f'{disease}/{disease}_std_log_res.csv') 
    # files.download(f'{disease}_std_log_res.csv')


# GSE108423
def get_gse_3std_log_2(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]
    
    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files (p1,p2,p3,family) list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    info_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'info'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['info']
    control_files = [ c_file for c_file in gse_file_header if 'male_control' == control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' == control_case_dict[c_file] ]

    p1_case_files = [ c_file for c_file in gse_file_header if 'P1' in info_dict[c_file] ]
    p2_case_files = [ c_file for c_file in gse_file_header if 'P2' in info_dict[c_file] ]
    p3_case_files = [ c_file for c_file in gse_file_header if 'P3' in info_dict[c_file] ]

    family_control_files = [ c_file for c_file in gse_file_header if 'family_control' == control_case_dict[c_file] ]
    family_case_files = [ c_file for c_file in gse_file_header if 'family_case' == control_case_dict[c_file] ]

    # get the mean of the control
    control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = control_df.groupby(control_df['DMR'], sort=False).mean().loc[:,control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    family_control_df = bedtool_result_df[ ['DMR'] + family_control_files ]
    family_mean_control_res = family_control_df.groupby(family_control_df['DMR'], sort=False).mean().loc[:,family_control_df.columns[1]:].T
    family_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    std_mean_control_res = mean_control_res.std(axis=0)

    family_mean_mean_control_res = family_mean_control_res.mean(axis=0)
    family_std_mean_control_res = family_mean_control_res.std(axis=0)

    # get the mean of the case
    p1_case_df = pd.concat([ bedtool_result_df[ ['DMR', p1_case_files[0]] ], bedtool_result_df[ ['DMR', p1_case_files[0]] ] ])
    mean_p1_case_res = p1_case_df.groupby(p1_case_df['DMR'], sort=False).mean().loc[:,p1_case_df.columns[1]:].T
    mean_p1_case_res.rename_axis("samples", axis="rows", inplace=True)
    
    p2_case_df = pd.concat([ bedtool_result_df[ ['DMR', p2_case_files[0]] ], bedtool_result_df[ ['DMR', p2_case_files[0]] ] ])
    mean_p2_case_res = p2_case_df.groupby(p2_case_df['DMR'], sort=False).mean().loc[:,p2_case_df.columns[1]:].T
    mean_p2_case_res.rename_axis("samples", axis="rows", inplace=True)
    
    p3_case_df = pd.concat([ bedtool_result_df[ ['DMR', p3_case_files[0]] ], bedtool_result_df[ ['DMR', p3_case_files[0]] ] ])
    mean_p3_case_res = p3_case_df.groupby(p3_case_df['DMR'], sort=False).mean().loc[:,p3_case_df.columns[1]:].T
    mean_p3_case_res.rename_axis("samples", axis="rows", inplace=True)

    family_case_df = bedtool_result_df[ ['DMR'] + family_case_files ]
    family_mean_case_res = family_case_df.groupby(family_case_df['DMR'], sort=False).mean().loc[:,family_case_df.columns[1]:].T
    family_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results
    p1_GOM_res_df = (mean_p1_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    p1_LOM_res_df = (mean_p1_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    p1_GOM_LOM_res_df = p1_GOM_res_df + p1_LOM_res_df

    p2_GOM_res_df = (mean_p2_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    p2_LOM_res_df = (mean_p2_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    p2_GOM_LOM_res_df = p2_GOM_res_df + p2_LOM_res_df

    p3_GOM_res_df = (mean_p3_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    p3_LOM_res_df = (mean_p3_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    p3_GOM_LOM_res_df = p3_GOM_res_df + p3_LOM_res_df

    family_GOM_res_df = (family_mean_case_res - family_mean_mean_control_res > 3*family_std_mean_control_res).replace(to_replace={True: 2, False: 0})
    family_LOM_res_df = (family_mean_case_res - family_mean_mean_control_res < -3*family_std_mean_control_res).replace(to_replace={True: -2, False: 0})
    family_GOM_LOM_res_df = family_GOM_res_df + family_LOM_res_df

    # combine 3std and log result
    threshold = 0.4
    res_df = np.log2(mean_p1_case_res) - np.log2(mean_mean_control_res)
    p1_GOM_LOM_res_df = p1_GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    p1_GOM_LOM_res_df = p1_GOM_LOM_res_df.fillna(0).astype('int16')
    
    res_df = np.log2(mean_p2_case_res) - np.log2(mean_mean_control_res)
    p2_GOM_LOM_res_df = p2_GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    p2_GOM_LOM_res_df = p2_GOM_LOM_res_df.fillna(0).astype('int16')
    
    res_df = np.log2(mean_p2_case_res) - np.log2(mean_mean_control_res)
    p3_GOM_LOM_res_df = p3_GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    p3_GOM_LOM_res_df = p3_GOM_LOM_res_df.fillna(0).astype('int16')
    
    res_df = np.log2(family_mean_case_res) - np.log2(mean_mean_control_res)
    family_GOM_LOM_res_df = family_GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    family_GOM_LOM_res_df = family_GOM_LOM_res_df.fillna(0).astype('int16')
    

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    p1_GOM_LOM_res_df = p1_GOM_LOM_res_df[ significant_dmr_list ]
    p1_GOM_LOM_res_df.index = ['GSE108423_P1']
    p2_GOM_LOM_res_df = p2_GOM_LOM_res_df[ significant_dmr_list ]
    p2_GOM_LOM_res_df.index = ['GSE108423_P2']
    p3_GOM_LOM_res_df = p3_GOM_LOM_res_df[ significant_dmr_list ]
    p3_GOM_LOM_res_df.index = ['GSE108423_P3']
    family_GOM_LOM_res_df = family_GOM_LOM_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data (p1,p2,p3)
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ p1_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    p1_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ p1_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    p1_GOM_LOM_res_df['info'] = info_dict.values()

    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ p2_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    p2_GOM_LOM_res_df['group'] = group_dict.values()

    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ p2_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    p2_GOM_LOM_res_df['info'] = info_dict.values()

    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ p3_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    p3_GOM_LOM_res_df['group'] = group_dict.values()

    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ p3_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    p3_GOM_LOM_res_df['info'] = info_dict.values()

    ## add a column for group from reference data (family)
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ family_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    family_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ family_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    family_GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    mlid_res = dict()
    for sample in p1_GOM_LOM_res_df.index:
        if (p1_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + p1_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    p1_GOM_LOM_res_df['MLID'] = mlid_res.values()

    mlid_res = dict()
    for sample in p2_GOM_LOM_res_df.index:
        if (p2_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + p2_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    p2_GOM_LOM_res_df['MLID'] = mlid_res.values()

    mlid_res = dict()
    for sample in p3_GOM_LOM_res_df.index:
        if (p3_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + p3_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    p3_GOM_LOM_res_df['MLID'] = mlid_res.values()

    family_mlid_res = dict()
    for sample in family_GOM_LOM_res_df.index:
        if (family_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + family_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            family_mlid_res[sample] = 'possible'
        else:
            family_mlid_res[sample] = 'less possible'
    family_GOM_LOM_res_df['MLID'] = family_mlid_res.values()

    # sort the row by index, which is sample id (natsorted)
    p1_GOM_LOM_res_df = p1_GOM_LOM_res_df.reindex(index=natsorted(p1_GOM_LOM_res_df.index))
    p2_GOM_LOM_res_df = p2_GOM_LOM_res_df.reindex(index=natsorted(p2_GOM_LOM_res_df.index))
    p3_GOM_LOM_res_df = p3_GOM_LOM_res_df.reindex(index=natsorted(p3_GOM_LOM_res_df.index))
    family_GOM_LOM_res_df = family_GOM_LOM_res_df.reindex(index=natsorted(family_GOM_LOM_res_df.index))
    res = pd.concat([p1_GOM_LOM_res_df, p2_GOM_LOM_res_df, p3_GOM_LOM_res_df, family_GOM_LOM_res_df])

    from google.colab import files
    res.to_csv(f'{disease}/{disease}_std_log_res.csv') 
    # files.download(f'{disease}_std_res.csv')

    print(f'[ {disease} ]')
    display(res)


# GSE97362
def get_gse_3std_log_3(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files (KMT2D, CHD7) list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    KMT2D_control_files = [ c_file for c_file in gse_file_header if 'control_KMT2D' in control_case_dict[c_file] ]
    KMT2D_case_files = [ c_file for c_file in gse_file_header if 'case_KMT2D' in control_case_dict[c_file] ]
    CHD7_control_files = [ c_file for c_file in gse_file_header if 'control_CHD7' in control_case_dict[c_file] ]
    CHD7_case_files = [ c_file for c_file in gse_file_header if 'case_CHD7' in control_case_dict[c_file] ]

    # get the mean of the control (KMT2D, CHD7)
    KMT2D_control_df = bedtool_result_df[ ['DMR'] + KMT2D_control_files ]
    KMT2D_mean_control_res = KMT2D_control_df.groupby(KMT2D_control_df['DMR'], sort=False).mean().loc[:,KMT2D_control_df.columns[1]:].T
    KMT2D_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    CHD7_control_df = bedtool_result_df[ ['DMR'] + CHD7_control_files ]
    CHD7_mean_control_res = CHD7_control_df.groupby(CHD7_control_df['DMR'], sort=False).mean().loc[:,CHD7_control_df.columns[1]:].T
    CHD7_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    KMT2D_mean_mean_control_res = KMT2D_mean_control_res.mean(axis=0)
    KMT2D_std_mean_control_res = KMT2D_mean_control_res.std(axis=0)

    CHD7_mean_mean_control_res = CHD7_mean_control_res.mean(axis=0)
    CHD7_std_mean_control_res = CHD7_mean_control_res.std(axis=0)

    # get the mean of the case (KMT2D, CHD7)
    KMT2D_case_df = bedtool_result_df[ ['DMR'] + KMT2D_case_files ]
    KMT2D_mean_case_res = KMT2D_case_df.groupby(KMT2D_case_df['DMR'], sort=False).mean().loc[:,KMT2D_case_df.columns[1]:].T
    KMT2D_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    CHD7_case_df = bedtool_result_df[ ['DMR'] + CHD7_case_files ]
    CHD7_mean_case_res = CHD7_case_df.groupby(CHD7_case_df['DMR'], sort=False).mean().loc[:,CHD7_case_df.columns[1]:].T
    CHD7_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results (KMT2D, CHD7)
    KMT2D_GOM_res_df = (KMT2D_mean_case_res - KMT2D_mean_mean_control_res > 3*KMT2D_std_mean_control_res).replace(to_replace={True: 2, False: 0})
    KMT2D_LOM_res_df = (KMT2D_mean_case_res - KMT2D_mean_mean_control_res < -3*KMT2D_std_mean_control_res).replace(to_replace={True: -2, False: 0})
    KMT2D_GOM_LOM_res_df = KMT2D_GOM_res_df + KMT2D_LOM_res_df

    CHD7_GOM_res_df = (CHD7_mean_case_res - CHD7_mean_mean_control_res > 3*CHD7_std_mean_control_res).replace(to_replace={True: 2, False: 0})
    CHD7_LOM_res_df = (CHD7_mean_case_res - CHD7_mean_mean_control_res < -3*CHD7_std_mean_control_res).replace(to_replace={True: -2, False: 0})
    CHD7_GOM_LOM_res_df = CHD7_GOM_res_df + CHD7_LOM_res_df

    # combine 3std and log result
    threshold = 0.4
    res_df = np.log2(KMT2D_mean_case_res) - np.log2(KMT2D_mean_mean_control_res)
    KMT2D_GOM_LOM_res_df = KMT2D_GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    KMT2D_GOM_LOM_res_df = KMT2D_GOM_LOM_res_df.fillna(0).astype('int16')
    
    res_df = np.log2(CHD7_mean_case_res) - np.log2(CHD7_mean_mean_control_res)
    CHD7_GOM_LOM_res_df = CHD7_GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    CHD7_GOM_LOM_res_df = CHD7_GOM_LOM_res_df.fillna(0).astype('int16')
    
    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(KMT2D_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    KMT2D_GOM_LOM_res_df = KMT2D_GOM_LOM_res_df[ significant_dmr_list ]
    CHD7_GOM_LOM_res_df = CHD7_GOM_LOM_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ KMT2D_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    KMT2D_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ KMT2D_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    KMT2D_GOM_LOM_res_df['info'] = info_dict.values()

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ CHD7_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    CHD7_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ CHD7_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    CHD7_GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    KMT2D_mlid_res = dict()
    for sample in KMT2D_GOM_LOM_res_df.index:
        if (KMT2D_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + KMT2D_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            KMT2D_mlid_res[sample] = 'possible'
        else:
            KMT2D_mlid_res[sample] = 'less possible'
    KMT2D_GOM_LOM_res_df['MLID'] = KMT2D_mlid_res.values()

    CHD7_mlid_res = dict()
    for sample in CHD7_GOM_LOM_res_df.index:
        if (CHD7_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + CHD7_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            CHD7_mlid_res[sample] = 'possible'
        else:
            CHD7_mlid_res[sample] = 'less possible'
    CHD7_GOM_LOM_res_df['MLID'] = CHD7_mlid_res.values()

    # sort the row by index, which is sample id (natsorted)
    KMT2D_GOM_LOM_res_df = KMT2D_GOM_LOM_res_df.reindex(index=natsorted(KMT2D_GOM_LOM_res_df.index))
    CHD7_GOM_LOM_res_df = CHD7_GOM_LOM_res_df.reindex(index=natsorted(CHD7_GOM_LOM_res_df.index))
    res = pd.concat([CHD7_GOM_LOM_res_df, KMT2D_GOM_LOM_res_df])
    
    from google.colab import files
    res.to_csv(f'{disease}/{disease}_std_log_res.csv') 
    # files.download(f'{disease}_std_res.csv')

    print(f'[ {disease} ]')
    display(res)


# GSE74432
def get_gse_3std_log_4(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join(disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join(disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join(disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files (normal, fibroblast) list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'Control' == control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' == control_case_dict[c_file] ]
    Fibroblast_control_files = [ c_file for c_file in gse_file_header if 'Control_Fibroblast' == control_case_dict[c_file] ]
    Fibroblast_case_files = [ c_file for c_file in gse_file_header if 'case_Fibroblast' == control_case_dict[c_file] ]

    # get the mean of the control (normal, fibroblast)
    control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = control_df.groupby(control_df['DMR'], sort=False).mean().loc[:,control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    Fibroblast_control_df = bedtool_result_df[ ['DMR'] + Fibroblast_control_files ]
    Fibroblast_mean_control_res = Fibroblast_control_df.groupby(Fibroblast_control_df['DMR'], sort=False).mean().loc[:,Fibroblast_control_df.columns[1]:].T
    Fibroblast_mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    std_mean_control_res = mean_control_res.std(axis=0)

    Fibroblast_mean_mean_control_res = Fibroblast_mean_control_res.mean(axis=0)
    Fibroblast_std_mean_control_res = Fibroblast_mean_control_res.std(axis=0)

    # get the mean of the case (normal, fibroblast)
    case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = case_df.groupby(case_df['DMR'], sort=False).mean().loc[:,case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    Fibroblast_case_df = bedtool_result_df[ ['DMR'] + Fibroblast_case_files ]
    Fibroblast_mean_case_res = Fibroblast_case_df.groupby(Fibroblast_case_df['DMR'], sort=False).mean().loc[:,Fibroblast_case_df.columns[1]:].T
    Fibroblast_mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results (normal, fibroblast)
    GOM_res_df = (mean_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    LOM_res_df = (mean_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    GOM_LOM_res_df = GOM_res_df + LOM_res_df

    Fibroblast_GOM_res_df = (Fibroblast_mean_case_res - Fibroblast_mean_mean_control_res > 3*Fibroblast_std_mean_control_res).replace(to_replace={True: 2, False: 0})
    Fibroblast_LOM_res_df = (Fibroblast_mean_case_res - Fibroblast_mean_mean_control_res < -3*Fibroblast_std_mean_control_res).replace(to_replace={True: -2, False: 0})
    Fibroblast_GOM_LOM_res_df = Fibroblast_GOM_res_df + Fibroblast_LOM_res_df
    
    # combine 3std and log result
    threshold = 0.4
    res_df = np.log2(mean_case_res) - np.log2(mean_mean_control_res)
    GOM_LOM_res_df = GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    GOM_LOM_res_df = GOM_LOM_res_df.fillna(0).astype('int16')
    
    res_df = np.log2(Fibroblast_mean_case_res) - np.log2(Fibroblast_mean_mean_control_res)
    Fibroblast_GOM_LOM_res_df = Fibroblast_GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    Fibroblast_GOM_LOM_res_df = Fibroblast_GOM_LOM_res_df.fillna(0).astype('int16')

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    GOM_LOM_res_df = GOM_LOM_res_df[ significant_dmr_list ]
    Fibroblast_GOM_LOM_res_df = Fibroblast_GOM_LOM_res_df[ significant_dmr_list ]
    
    # start adding reference data
    ref_df = pd.read_csv(os.path.join(disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data (normal, fibroblast)
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data (normal, fibroblast)
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    GOM_LOM_res_df['info'] = info_dict.values()

    ## add a column for group from reference data (normal, fibroblast)
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ Fibroblast_GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    Fibroblast_GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data (normal, fibroblast)
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ Fibroblast_GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    Fibroblast_GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    mlid_res = dict()
    for sample in GOM_LOM_res_df.index:
        if (GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    GOM_LOM_res_df['MLID'] = mlid_res.values()

    Fibroblast_mlid_res = dict()
    for sample in Fibroblast_GOM_LOM_res_df.index:
        if (Fibroblast_GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + Fibroblast_GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            Fibroblast_mlid_res[sample] = 'possible'
        else:
            Fibroblast_mlid_res[sample] = 'less possible'
    Fibroblast_GOM_LOM_res_df['MLID'] = Fibroblast_mlid_res.values()

    # sort the row by index, which is sample id (natsorted)
    GOM_LOM_res_df = GOM_LOM_res_df.reindex(index=natsorted(GOM_LOM_res_df.index))
    Fibroblast_GOM_LOM_res_df = Fibroblast_GOM_LOM_res_df.reindex(index=natsorted(Fibroblast_GOM_LOM_res_df.index))
    res = pd.concat([GOM_LOM_res_df, Fibroblast_GOM_LOM_res_df])

    from google.colab import files
    res.to_csv(f'{disease}/{disease}_std_log_res.csv') 
    # files.download(f'{disease}_std_res.csv')

    print(f'[ {disease} ]')
    display(res)

# BWS and SRS
def get_bws_srs_3std_log(disease):
    # read files
    pheno_df = pd.read_csv(os.path.join('BWS_SRS', disease, pheno_format.format(disease)), sep='\t')
    gse_file_header = pd.read_csv(os.path.join('BWS_SRS', disease, disease + '.csv'), nrows=1).columns[4:]
    bedtool_result_df = pd.read_csv(os.path.join('BWS_SRS', disease, disease + '_bedtool_result.tsv'), sep='\t', header=None).loc[:,3:]

    # set the columns since the bedtool_result_df does not contain one
    bedtool_result_df.columns = ['DMR','Chromosome','Start','End', 'Probe_ID'] + list(gse_file_header)

    # create a control and case files (normal, fibroblast) list
    control_case_dict = pheno_df[ ['GSEnumber_in_GEO_analysis', 'group'] ].set_index('GSEnumber_in_GEO_analysis').to_dict()['group']
    control_files = [ c_file for c_file in gse_file_header if 'control' == control_case_dict[c_file] ]
    case_files = [ c_file for c_file in gse_file_header if 'case' in control_case_dict[c_file] ]

    # get the mean of the control
    dmr_control_df = bedtool_result_df[ ['DMR'] + control_files ]
    mean_control_res = dmr_control_df.groupby(dmr_control_df['DMR'], sort=False).mean().loc[:,dmr_control_df.columns[1]:].T
    mean_control_res.rename_axis("samples", axis="rows", inplace=True)

    # get the mean and std of the mean of the control
    mean_mean_control_res = mean_control_res.mean(axis=0)
    std_mean_control_res = mean_control_res.std(axis=0)

    # get the mean of the case
    dmr_case_df = bedtool_result_df[ ['DMR'] + case_files ]
    mean_case_res = dmr_case_df.groupby(dmr_case_df['DMR'], sort=False).mean().loc[:,dmr_case_df.columns[1]:].T
    mean_case_res.rename_axis("samples", axis="rows", inplace=True)

    # get the result of the GOM and LOM and combine both of the results
    GOM_res_df = (mean_case_res - mean_mean_control_res > 3*std_mean_control_res).replace(to_replace={True: 2, False: 0})
    LOM_res_df = (mean_case_res - mean_mean_control_res < -3*std_mean_control_res).replace(to_replace={True: -2, False: 0})
    GOM_LOM_res_df = GOM_res_df + LOM_res_df

    # combine 3std and log result
    threshold = 0.4
    res_df = np.log2(mean_case_res) - np.log2(mean_mean_control_res)
    GOM_LOM_res_df = GOM_LOM_res_df[ (np.abs(res_df) >= threshold) ]
    GOM_LOM_res_df = GOM_LOM_res_df.fillna(0).astype('int16')

    # filter the significant dmrs (more than 5 probes)
    dmr_grouped_df = bedtool_result_df[ ['DMR'] ].groupby(dmr_control_df['DMR'], sort=False)
    dmr_grouped_cnt_df = dmr_grouped_df.count().T.iloc[0]
    significant_dmr_list = dmr_grouped_cnt_df[ dmr_grouped_cnt_df >= 5 ].index

    GOM_LOM_res_df = GOM_LOM_res_df[ significant_dmr_list ]

    # start adding reference data
    ref_df = pd.read_csv(os.path.join('BWS_SRS', disease, f'{disease}_reference.csv'))

    ## add a column for group from reference data
    group_df = ref_df[ ['Sample', 'group'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    group_dict = group_df.to_dict()['group']
    GOM_LOM_res_df['group'] = group_dict.values()

    ## add a column for info from reference data
    info_df = ref_df[ ['Sample', 'info'] ].set_index('Sample').loc[ GOM_LOM_res_df.index ]
    info_dict = info_df.to_dict()['info']
    GOM_LOM_res_df['info'] = info_dict.values()

    # add a column for MLID result, which has more than 2 of GOMs and LOMs
    mlid_res = dict()
    for sample in GOM_LOM_res_df.index:
        if (GOM_LOM_res_df.loc[sample].value_counts().get(-2, 0) + GOM_LOM_res_df.loc[sample].value_counts().get(2, 0)) >= 2:
            mlid_res[sample] = 'possible'
        else:
            mlid_res[sample] = 'less possible'
    GOM_LOM_res_df['MLID'] = mlid_res.values()

    # sort the row by index, which is sample id (natsorted)
    res = GOM_LOM_res_df
    res = res.reindex(index=natsorted(res.index))

    # reorder the columns
    res_index = res.columns.to_list()
    res = res[ res_index[-3:] + res_index[:-3] ]
    
    from google.colab import files
    res.to_csv(f'BWS_SRS/{disease}/{disease}_std_log_res.csv') 
    # files.download(f'{disease}_std_res.csv')

    print(f'[ {disease} ]')
    display(res)

"""# RESULT SAMPLES

## 3STD LOG RESULT
"""
get_gse_result_3std_log('GSE125367')
get_gse_result_3std_log('GSE108423')
get_gse_result_3std_log('GSE97362')
get_gse_result_3std_log('GSE74432')
get_gse_result_3std_log('GSE55491')
get_gse_result_3std_log('GSE133774')

"""## LOG RESULT"""
get_gse_result_log('GSE125367')
get_gse_result_log('GSE108423')
get_gse_result_log('GSE97362')
get_gse_result_log('GSE74432')
get_gse_result_log('GSE55491')
get_gse_result_log('GSE133774')

"""## 3STD RESULT"""
get_gse_result_3std('GSE125367')
get_gse_result_3std('GSE108423')
get_gse_result_3std('GSE97362')
get_gse_result_3std('GSE74432')
get_gse_result_3std('GSE55491')
get_gse_result_3std('GSE133774')

"""# SAMPLES FOR DRAWING THE PLOTS USING PYTHON"""

import altair as alt
from vega_datasets import data

source = data.movies.url

alt.Chart(source).mark_rect().encode(
    alt.X('IMDB_Rating:Q', bin=alt.Bin(maxbins=60)),
    alt.Y('Rotten_Tomatoes_Rating:Q', bin=alt.Bin(maxbins=40)),
    alt.Color('count(IMDB_Rating):Q', scale=alt.Scale(scheme='greenblue'))
)

def draw_heatmap_log(disease):
    bws_srs = ''
    if disease == 'GSE133774' or disease == 'GSE55491':
        bws_srs = 'BWS_SRS/'
    log_res_df = pd.read_csv(f'{bws_srs}{disease}/{disease}_log_res.csv', index_col=[0])

    plt.rcParams['figure.figsize'] = (20.0, 5.0)

    sns_df = log_res_df.iloc[:,:-2]
    res_fig = sns.heatmap(sns_df, cmap='RdBu', linewidths=0.1, square=True)
    # sns.pairplot(sns_df)

    plt.title(f'The log result of the {disease}', fontdict={'fontsize':20, 'color': 'white'})
    plt.show()

    # save the plot figure
    res_fig = res_fig.get_figure()
    res_fig.savefig(f'{bws_srs}{disease}/{disease}_log_res_fig.png')

for disease in diseases_dir:
    draw_heatmap_log(disease)

# !pip install bioinfokit
# !pip install adjustText
from bioinfokit import analys, visuz
disease = 'GSE108423'
df = pd.read_csv(f'{disease}/{disease}_log_res.csv', index_col=[0]).iloc[:,:-2]
# df = pd.read_csv(f'{disease}/{disease}_log_res.csv', index_col=[0])
visuz.gene_exp.hmap(df=df, dim=(8, 2.5),zscore=0 , tickfont=(6, 4), show=True)

"""# RUN BEDTOOL"""

!apt-get install bedtools
# subprocess.run('bedtools', shell=True, check=True)

bedfile = os.path.join(file_path, 'Targets_hg19.bed')
diseases_dir = ['GSE108423', 'GSE125367', 'GSE74432', 'GSE97362']

for disease in diseases_dir:
    gse_file = os.path.join(file_path, disease, disease + '.csv')
    result_file = os.path.join(file_path, disease, disease + '_betool_result.tsv')
    command = f'bedtools intersect -wa -wb -a {bedfile} -b {gse_file} > {result_file}'
    stream = os.popen(command)
    # subprocess.run(command, shell=True, check=True, capture_output=True)

print('run bedtool')

# file_path = os.path.join('gdrive', 'My Drive', 'liv' ,'VIVA', 'viva_data')
bedfile = os.path.join(file_path, 'Targets_hg19.bed')

for disease in diseases_dir:
    gse_file = os.path.join(file_path, disease, disease + '.csv')
    gse_file_no_header = os.path.join(file_path, disease, disease + '_no_header.csv')
    result_file = os.path.join(file_path, disease, disease + '_bedtool_result.tsv')
    command = '''sed '1d' {} > {}'''.format(gse_file, gse_file_no_header)
    #stream = os.popen(command)
    subprocess.run(command, shell=True, check=True)
    command = f'bedtools intersect -wa -wb -a {bedfile} -b {gse_file_no_header} > {result_file}'
    #stream = os.popen(command)
    subprocess.run(command, shell=True, check=True)
    print(f'{disease} done')

print('bedtool done')

# pheno_df = pd.read_csv(os.path.join(file_path, disease, pheno_format.format(disease)), sep='\t')

# control_male_pheno_df = pheno_df[ (pheno_df['sex'] == 'male') & (pheno_df['group'] == 'control') ]
# control_female_pheno_df = pheno_df[ (pheno_df['sex'] == 'female') & (pheno_df['group'] == 'control') ]

# control_male_sample_ids = control_male_pheno_df['Sample_ID']
# control_female_sample_ids = control_female_pheno_df['Sample_ID']

# display(control_female_sample_ids)

##################
# read 450K file #
##################

file_path = os.path.join('drive', 'My Drive', 'liv', 'result')
methylation_result_file = os.path.join(file_path, 'methylation_result_std.csv')
std_result_df = pd.read_csv(methylation_result_file)

#gene = probedetail_df['UCSC_RefGene_Name'].squeeze().drop_duplicates().dropna()

std_result_df

col = std_result_df.columns

(std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ][col[3:]].count() / 21 > 0).value_counts()
( ( std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ][col[3:]].count() / 21 >= 0.7 ) & ( std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ][col[3:]].count() >= 10 ) ).value_counts()

std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ][col[3:]].count() / 21 >= 0.7
std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ][col[3:]].count() >= 10

std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ]['WDR60;WDR60'].count()

(std_result_df.iloc[21][3:] >= 5 ).value_counts()

#std_result_df.iloc[:21, 3:][ std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ].iloc[:21, 3:].count() == 0 ]
#std_result_df.iloc[:21, 3:]
std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ].iloc[:21, 3:].count() == 0 
#std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ]

std_result_df.iloc[21, 3:] >= 5

((std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ].iloc[:21, 3:].count() == 0) & (std_result_df.iloc[21, 3:] >= 5) ).value_counts()

std_result_df.iloc[:21, 3:] [ (std_result_df [ std_result_df[col[3:]].isin([-2, 2]) ].iloc[:21, 3:].count() == 0) & (std_result_df.iloc[21, 3:] >= 5) ]
