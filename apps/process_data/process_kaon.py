import pandas as pd
import numpy as np
import os
import spacy
import string
import csv
from django.http import FileResponse
from django.conf import settings
from django.core.files import File
from .import models
from io import BytesIO
import datetime
import logging

logger = logging.getLogger(__name__)

def html_manip(dirty_html):
    dfs = pd.read_html(dirty_html)

    # The first DataFrame in the list is typically the main table
    df = dfs[0]

    # Ensure the directory exists
    output_dir = 'data_storage/tmp/kaon'
    os.makedirs(output_dir, exist_ok=True)

    # Display the DataFrame
    output_path = os.path.join(output_dir, 'placecom_ETV_TMP_FILE.csv')
    df.to_csv(output_path, index=False)
    
    df_csv = pd.read_csv(output_path, header=1)
    
    df_csv['SYM_MIRROR'] = df_csv['SYM_MIRROR'].str.lower()
    
    df_csv['SYM_MIRROR'] = np.where(df_csv['SYM_MIRROR'] == 'yes', 'B', 
                                    np.where(df_csv['SYM_MIRROR'] == 'no', 'T', df_csv['SYM_MIRROR']))
    df_csv['Location'] = df_csv['REFDES']
    
    column_to_keep = ['Location', 'COMP_DEVICE_TYPE', 'SYM_X', 'SYM_Y', 'SYM_ROTATE', 'SYM_MIRROR']
    df_csv = df_csv[column_to_keep]
    df_csv.sort_values(by="Location", inplace=True)
    return df_csv


def text_manip(dirty_text_file):
    content = dirty_text_file.read().decode('ascii')
    lines = content.strip().split('\n')
    data = [line.split() for line in lines]

    df = pd.DataFrame(data, columns=['Location', 'Column2', 'Column-X', 'Column-Y', 'Rotation', 'Column6'])
    columns_to_display = ['Location', 'Column-X', 'Column-Y', 'Rotation']
    df = df[columns_to_display]

    df.to_excel('kaon_output_data1.xlsx', index=False)
    return df

def bom_manip(input_excel_file):
    df = pd.read_excel(input_excel_file, header=None)
    header_row = None
    for index, row in df.iterrows():
        if "Location" in row.values:
            header_row = index
            break
    
    if header_row is not None:
        df = pd.read_excel(input_excel_file, header=header_row)
    
    column_to_keep = ['Location', 'Item category', 'Component', 'Sort String', 'Mat. Provision', 'Alt. Group', 'Usage']
    
    df['Location'] = df['Location'].apply(lambda x: 'R'+str(x) if isinstance(x, int) else x)
    df = df[column_to_keep]
    
    df['Location'] = df['Location'].astype(str)
    df['Location'] = df['Location'].str.split(',')
    df = df.explode('Location')
    df['Sort String'] = df['Sort String'].astype(str)
    
    # Perform filtering on the original DataFrame
    df = df[~df['Sort String'].str.contains('ASSY', case=False)]
    df = df[~df['Sort String'].str.contains('NaN', case=False)]
    df = df[~df['Location'].str.contains('NaN', case=False)]
    df = df[~df['Sort String'].str.contains('PBA')]
    
    # Filter for duplicates where 'Usage' is 100
    duplicates_with_usage_100 = df[df.duplicated(subset=['Location'], keep=False) & (df['Usage'] == 100)]
    
    # Filter for non-duplicates
    non_duplicates = df[~df.duplicated(subset=['Location'], keep=False)]
    
    # Concatenate the two DataFrames
    final_df = pd.concat([duplicates_with_usage_100, non_duplicates], ignore_index=True)
    
    # Now select the desired columns from final_df
    column_to_keep = ['Location', 'Component']
    filtered_df = final_df[column_to_keep]
    filtered_df = filtered_df.sort_values(by='Location')
    return filtered_df

def merge_kaon(df_csv, filtered_df):
    mapping_dict = df_csv.set_index('Location').to_dict()
    filtered_df['Location'] = filtered_df['Location'].str.strip()
    df_csv['Location'] = df_csv['Location'].str.strip()
    
    filtered_df['COMP_DEVICE_TYPE'] = filtered_df['Location'].map(mapping_dict['COMP_DEVICE_TYPE'])
    filtered_df['SYM_MIRROR'] = filtered_df['Location'].map(mapping_dict['SYM_MIRROR'])
    filtered_df['SYM_X'] = filtered_df['Location'].map(mapping_dict['SYM_X'])
    filtered_df['SYM_Y'] = filtered_df['Location'].map(mapping_dict['SYM_Y'])
    filtered_df['SYM_ROTATE'] = filtered_df['Location'].map(mapping_dict['SYM_ROTATE'])
    
    df_pnp = filtered_df
    return df_pnp




def process_data_merge(uploaded_file_instance, output_format='csv'):
    base_name = os.path.splitext(uploaded_file_instance.pick_n_place.name)[0]

    try:
        df_pnp_processed = html_manip(uploaded_file_instance.pick_n_place)
        df_excel_processed = bom_manip(uploaded_file_instance.bom)

        df_result = merge_kaon(df_pnp_processed, df_excel_processed)

        bom_file_name = os.path.splitext(os.path.basename(uploaded_file_instance.bom.name))[0]
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y%m%d%H%M%S')
        export_dir = 'data_storage/exports/kaon'
        os.makedirs(export_dir, exist_ok=True)
        processed_data_csv_path = f'{export_dir}/{bom_file_name}_processed_{timestamp}.csv'
        df_result.to_csv(processed_data_csv_path, index=False)

        # Open the file without closing it immediately
        processed_data_file = open(processed_data_csv_path, 'rb')
        django_file = File(processed_data_file, name=f'{bom_file_name}_processed.csv')

        processed_data_instance = models.ProcessedDataKaon.objects.create(
            uploaded_file=uploaded_file_instance,
            processed_file=django_file
        )

        # Close the file after creating the instance
        processed_data_file.close()
        return df_result
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        raise e




