import pandas as pd
import spacy
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import csv  # Import the csv module
import io
import re
from . import  models
import os
import datetime
from django.core.files import File
import logging

logger =  logging.getLogger(__name__)


def process_and_save_txt_file(txt_file):
    nlp = spacy.load("en_core_web_sm")
    
    start_reading = False  # Initialize start_reading
    data = []  # Initialize data as an empty list
    

    for line in txt_file:
        # Check if the line contains "Designator" to start reading data
        if "Designator" in line.decode('latin1'):
            start_reading = True

        if start_reading:
            data.append(line.strip().decode('latin1'))
    # Recognize entities using spaCy NER
    recognized_entities = []
    for line in data:
        doc = nlp(line)
        entities = [ent.text for ent in doc.ents]
        recognized_entities.append(entities)
    
    # Organize the recognized entities into structured data
    structured_data = []
    for line, entities in zip(data, recognized_entities):
        parts = csv.reader([line], delimiter=' ', quotechar='"', skipinitialspace=True).__next__()  # Change this line
        # Pad entities with empty strings to match the length of parts
        entities += [''] * (len(parts) - len(entities))
        structured_data.append(parts + entities)
    
    # Ensure consistent column count
    max_columns = max(len(row) for row in structured_data)
    structured_data = [row + [''] * (max_columns - len(row)) for row in structured_data]
    
    # Create a DataFrame
    df = pd.DataFrame(structured_data, columns=[f"Col_{i}" for i in range(max_columns)])
    
    # Select relevant columns and rename them
    df = df[['Col_0', 'Col_2', 'Col_4', 'Col_5', 'Col_6']]
    df.columns = ['Designator', 'Layer', 'Center-X', 'Center-Y', 'Rotation']
    df = df.drop(df.index[0])
    # Clean the "Designator" column to handle the issue with single space
    df['Designator'] = df['Designator'].apply(lambda x: re.sub(r'\s(?=[A-Z])', '', x))
    
    # Filter out rows where the "Designator" column contains the string "Comment"
    df = df[~df['Designator'].str.contains('Comment')]
    return df




# Define a function to extract size and voltage information from the 'Description' column
def extract_size_and_voltage(description):
    # Use regular expressions to find size and voltage information
    size_match = re.search(r'\d+(\.\d+)?[^\d]+(\d+(\.\d+)?)?[^\d]+', description)
    voltage_match = re.search(r'\d+(\.\d+)?[^\d]*V', description)
    
    if size_match and voltage_match:
        size = size_match.group(0).strip()
        voltage = voltage_match.group(0).strip()
        return size, voltage
    else:
        return None, None

def extract_size_and_voltage_2(description):
    # Use regular expressions to find size and voltage information
    size_match = re.search(r'(\d{4})', description)  # Match 4-digit size (e.g., 0402)
    voltage_match = re.search(r'(\d+(\.\d+)?V)', description)  # Match voltage (e.g., 6.3V)
    
    if size_match and voltage_match:
        size = size_match.group(0)
        voltage = voltage_match.group(0)
        return size, voltage
    else:
        return None, None




def extract_resistor_component_size(description):
    size_match = re.search(r'\b\d{4}\b', description)  # Match 4-digit size (e.g., 0402 or 0201)
    if size_match:
        return size_match.group(0)
    else:
        return None, None

def extract_and_remove_voltage(value):
    value_without_voltage = re.sub(r'\d+(\.\d+)?[^\d]*V', '', value).strip()
    return value_without_voltage

def fb_in_value_with_blm(row):
    if 'FB' in row['Designator']:
        return row['1st Vendor Part No']
    else:
        return row['Value']

def replace_nh_with_vendor_part(row):
    if 'NH' in row['Value'] or 'UH' in row['Value']:
        return row['1st Vendor Part No']
    else:
        return row['Value']


import pandas as pd

def process_xlsx_file(input_file):
    # Read the XLSX file
    df = pd.read_excel(input_file, header=None)
    df = df.dropna(how='all')

    header_row = None
    for index, row in df.iterrows():
        if 'Designator' in row.values:
            header_row = index
            break

    if header_row is not None:
        df = pd.read_excel(input_file, header=header_row)
    else:
        print("Header row not found.")
        return

    # Sort the values
    df = df.sort_values(by='Designator')

    # Split them into rows by ","
    df['Designator'] = df['Designator'].str.split(",")
    df = df.explode('Designator')

    # Select the columns you want to keep in the df
    columns_to_keep = ['Designator', 'Value', 'DNF' , '1st Vendor Part No', 'Component Class', 'Description', 'Footprint']
    df = df[columns_to_keep]

    # Capitalize the values in the 'Value' column
    df['Value'] = df['Value'].str.upper()

    # Fill NaN values in the 'Value' column with an empty string
    df['Value'].fillna('', inplace=True)

    # Convert the 'Component Class' column into a string
    df['Component Class'] = df['Component Class'].astype(str)

    # Delete the rows if they contain the string 'Mechanical' or 'Electro-mechanical'
    df = df[~df['Component Class'].str.contains('Mechanical')]
    df = df[~df['Component Class'].str.contains('Electro-mechanical')]

    df = df[df['Description'].apply(lambda x: isinstance(x, str))]

    # Filter data for Resistors and return them, then add a hyphen to the 'Size_R' column
    resistor_indices = df[df['Description'].str.contains('Chip Resistor', case=False)].index

    df.loc[resistor_indices, 'Size_R'] = df.loc[resistor_indices, 'Description'].apply(extract_resistor_component_size)
    df.loc[resistor_indices, 'Size_R'] = '-' + df.loc[resistor_indices, 'Size_R']

    # Apply the extraction function to the 'Description' column
    df['Size_C'], df['Voltage_M'] = zip(*df['Description'].apply(extract_size_and_voltage_2))

    # Add a hyphen to the 'Size_C' column
    df['Size_C'] = '-' + df['Size_C'] + '-'
    df['Size_C'] = df['Size_C'] + df['Voltage_M']

    # Apply the extraction function to the 'Description' column
    df['Size'], df['Voltage'] = zip(*df['Description'].apply(extract_size_and_voltage))

    # Clean up the 'Size' column
    df['Size'] = df['Size'].str.replace(', ', '-')
    df['Size'] = df['Size'].str.replace('V C', 'V')
    df['Size'] = df['Size'].str.replace('V X', 'V')
    df['Size_combined'] = df['Size_R'].fillna('') + df['Size_C'].fillna('')

    df = df[~df['Designator'].str.contains('Tape', case=False)]
    df = df[~df['Designator'].str.contains('Warn', case=False)]
    df = df[~df['Designator'].str.contains('Overpack Label', case=False)]
    df = df[~df['Designator'].str.contains('Ribbon', case=False)]
    df = df[~df['Designator'].str.contains('Box', case=False)]
    df = df[~df['Designator'].str.contains('Serial', case=False)] 
    df = df[~df['Value'].str.contains('DNF')]
    df = df[~df['DNF'].fillna('').astype(str).str.contains('DNF')]

    # Filter the data through in the value column and strip voltage from the value
    df['Value'] = df['Value'].apply(extract_and_remove_voltage)

    # Merge 'Size_combined' and 'Value' columns and fill NaN values with empty strings
    df['Value'] = df['Value'].fillna('') + df['Size_combined'].fillna('')
    df['Value'] = df.apply(replace_nh_with_vendor_part, axis=1)

    df['Value'] = df.apply(lambda row: row['1st Vendor Part No'] if pd.isna(row['Value']) or (row['Value'] == '' and 'ANT' in row['Designator'].upper()) else row['Value'], axis=1)
    df['Value'] = df.apply(fb_in_value_with_blm, axis=1)
    df['Value'] = df.apply(lambda row: row['1st Vendor Part No'] if pd.isna(row['Value']) or row['Value'] == '' else row['Value'], axis=1)

    df['Value'] = df['Value'].str.replace('_', '-')
    df['Value'] = df['Value'].str.replace('/', '-')
    df['Value'] = df['Value'].str.replace('220UF', '220UF-6.3V')
    df['Value'] = df['Value'].str.split(',').str[0]
    df['Value'] = df['Value'].str.split('--').str[0]
    df['Value'] = df['Value'].str.split('  ').str[0]
    df['Value'] = df['Value'].str.replace(' ', '-')
    df['Value'] = df['Value'].str.split('+').str[0]
    df['Value'] = df['Value'].str.split('=').str[0]
    df['Value'] = df.apply(lambda row: row['1st Vendor Part No'] if pd.isna(row['Value']) or row['Value'] == '' else row['Value'], axis=1)
    df.drop(columns=['Size_combined'], inplace=True)
    
    
    columns_to_keep = ['Designator', 'Value', '1st Vendor Part No']
    df['Value'] = df['Value'].str.split('--').str[0]
    df = df[columns_to_keep]

    print(df)
    return df
    
    


def map_data(df1, df2):
    # Strip whitespace from the 'Designator' column in both DataFrames
    mapping_dict = df1.set_index('Designator').to_dict()

    
    df1['Designator'] = df1['Designator'].str.strip()
    df2['Designator'] = df2['Designator'].str.strip()

    # Map the 'Center-X(mm)', 'Center-Y(mm)', and 'Rotation' columns using the provided mapping dictionary
    df2['Layer'] = df2['Designator'].map(mapping_dict['Layer'])
    df2['Center-X'] = df2['Designator'].map(mapping_dict['Center-X'])
    df2['Center-Y'] = df2['Designator'].map(mapping_dict['Center-Y'])
    df2['Rotation'] = df2['Designator'].map(mapping_dict['Rotation'])
    print(df2)
    return df2
    


def process_data_and_merge(uploaded_file_instance, output_format='csv'):
    base_name =  os.path.splitext(uploaded_file_instance.pick_n_place.name)[0]

    try:
        df_text_processed = process_and_save_txt_file(uploaded_file_instance.pick_n_place)
        df_excel_processed = process_xlsx_file(uploaded_file_instance.bom)
    
        df_result = map_data(df_text_processed, df_excel_processed)
        display_columns = ['Designator', 'Value', '1st Vendor Part No', 'Layer','Center-X', 'Center-Y', 'Rotation']
        df_result = df_result[display_columns]
    
        bom_file_name = os.path.splitext(os.path.basename(uploaded_file_instance.bom.name))[0]
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y%m%d%H%M%S')
        export_dir = 'data_storage/exports/dme'
        os.makedirs(export_dir, exist_ok=True)
        processed_data_csv_path = f'{export_dir}/{bom_file_name}_{timestamp}.csv'
        df_result.to_csv(processed_data_csv_path, index=False)
        
        with open(processed_data_csv_path, 'rb') as processed_data_file:
            django_file = File(processed_data_file)
            processed_data_instance = models.ProcessedDataDME.objects.create(
                uploaded_file=uploaded_file_instance,
                processed_file=django_file
            )

        return df_result
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        raise e



