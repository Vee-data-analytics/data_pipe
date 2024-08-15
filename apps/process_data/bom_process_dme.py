import pandas as pd
import numpy as  np
import re



def process_xlsx_file_bom(input_file):
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
        # Handle the case where the header row is not found
        print("Header row not found.")
        return
    
    sorted_df = df.sort_values(by='Designator')
    
    # Split them into rows by ","
    #sorted_df['Designator'] = sorted_df['Designator'].str.split(",")
    #sorted_df = sorted_df.explode('Designator')
    
    # Select the columns you want to keep in the df
    columns_to_keep = ['Quantity','Designator','DNF','Value','1st Vendor','1st Vendor Part No','DEAR SKU','Component Class' ,'Description', 'Footprint']
    sorted_df = sorted_df[columns_to_keep]
    
    sorted_df['Value'] = sorted_df['Value'].str.upper()
    # Filter the df by dropping duplicates
    filtered_df = sorted_df.drop_duplicates('Designator')
    
    filtered_df['Value'] = filtered_df['Value'].str.upper()
    
    # Fill NaN values in the 'Value' column with an empty string
    filtered_df['Value'].fillna('', inplace=True)
    
    filtered_df['Value'] = filtered_df['Value'].str.split(',').str[0]
    filtered_df['Value'] = filtered_df['Value'].astype(str)
    filtered_df['Footprint'] = filtered_df['Footprint'].astype(str)

    # Convert the 'Component Class' column into a string
    filtered_df['Component Class'] = filtered_df['Component Class'].astype(str)
    # Delete the rows if they contain the string 'Mechanical' or 'Electro-mechanical'
    filtered_df = filtered_df[~filtered_df['Component Class'].str.contains('Mechanical')]
    filtered_df = filtered_df[~filtered_df['Component Class'].str.contains('Electro-mechanical')]
    filtered_df = filtered_df[filtered_df['Description'].apply(lambda x: isinstance(x, str))]
    
    def fb_in_value_with_blm(row):
        if 'FB' in row['Designator']:
            return row['1st Vendor Part No']
        else:['Value']   
    
    def replace_nh_with_vendor_part(row):
        # Convert row['Value'] to a string
        value_str = str(row['Value'])
        
        if 'NH' in value_str or 'UH' in value_str:
            return row['1st Vendor Part No']
        else:
            return row['Value']
    
        
    def extract_capacitor_details(row):
        # Use regular expressions to find capacitance and voltage information
        cap_match = re.search(r'(\d+(\.\d+)?[pnu]?F)', row['Value'], re.IGNORECASE)
        voltage_match = re.search(r'(\d+(\.\d+)?V)', row['Value'])
        size_match = re.search(r'(\d{4})', row['Footprint'])  # Match 4-digit size (e.g., 0402)
    
        if cap_match and size_match:
            cap = cap_match.group(0)
            size = size_match.group(0)
            voltage = voltage_match.group(0) if voltage_match else ''
            return f"{cap}-{size}-{voltage}".strip('-')
        else:
            return None
    
    def extract_resistor_details(row):
        # Use regular expressions to find resistance and voltage information
        res_match = re.search(r'(\d+(\.\d+)?[kKmMrR])', row['Value'], re.IGNORECASE)
        voltage_match = re.search(r'(\d+(\.\d+)?V)', row['Value'])
        size_match = re.search(r'(\d{4})', row['Footprint'])  # Match 4-digit size (e.g., 0402)
    
        if res_match and size_match:
            res = res_match.group(0)
            size = size_match.group(0)
            voltage = voltage_match.group(0) if voltage_match else ''
            return f"{res}-{size}-{voltage}".strip('-')
        else:
            return None
    
    filtered_df['Cap_Details'] = filtered_df.apply(extract_capacitor_details, axis=1)
    filtered_df['Res_Details'] = filtered_df.apply(extract_resistor_details, axis=1)
    # Combine 'Cap_Details' and 'Res_Details' into a new column 'New_Value'
    filtered_df['New_Value'] = np.where(filtered_df['Cap_Details'].notnull(), filtered_df['Cap_Details'],
                                        np.where(filtered_df['Res_Details'].notnull(), filtered_df['Res_Details'], 
                                                 filtered_df['Value']))
    
    # Replace the 'Value' column with 'New_Value'
    filtered_df['Value'] = filtered_df['New_Value']
    
    # Manipulation of the value column 
    filtered_df.drop(columns=['New_Value', 'Cap_Details', 'Res_Details'], inplace=True)
    filtered_df['Value'] = filtered_df.apply(replace_nh_with_vendor_part, axis=1)
    filtered_df['Value'] = filtered_df['Value'].str.split('-').str[0]
    filtered_df['Value'] = filtered_df['Value'].str.split(',').str[0]
    filtered_df['Value'] = filtered_df['Value'].str.split('+').str[0]
    filtered_df['Value'] = filtered_df['Value'].str.split('=').str[0]
    filtered_df['Value'] = filtered_df['Value'].str.replace('220UF', '220UF-6.3V')
    filtered_df['Value'] = filtered_df['Value'].str.replace('/', '-')
    filtered_df['Value'] = filtered_df['Value'].apply(lambda x: re.sub(r'\(.*?\)', '', x))
    filtered_df['Value'] = filtered_df.apply(lambda row: row['1st Vendor Part No'] if pd.isna(row['Value']) or row['Value'] == '' else row['Value'], axis=1)
    filtered_df['Value'] = filtered_df['Value'].astype(str).str.split(',').str[0]


     # Manipulation of the Vender Part no column
    filtered_df['1st Vendor Part No'] = filtered_df['1st Vendor Part No'].astype(str)
    filtered_df['1st Vendor Part No'] = filtered_df['1st Vendor Part No'].str.replace('_', '-')
    filtered_df['1st Vendor Part No'] = filtered_df['1st Vendor Part No'].str.split('=').str[0]
    filtered_df['1st Vendor Part No'] = filtered_df['1st Vendor Part No'].str.split(',').str[0]
    filtered_df['1st Vendor Part No'] = filtered_df['1st Vendor Part No'].apply(lambda x: re.sub(r'\(.*?\)', '', x))
    filtered_df['1st Vendor Part No'] = filtered_df['1st Vendor Part No'].str.replace('/','-')


    # Convert the columns to string type
    filtered_df['Value'] = filtered_df['Value'].astype(str)
    filtered_df['DNF'] = filtered_df['DNF'].astype(str)
    filtered_df['Designator'] = filtered_df['Designator'].astype(str)
    
    # Remove rows containing 'DNF' or 'dnf' in 'Value', 'DNF', or 'Designator' columns
    filtered_df = filtered_df[~filtered_df['Value'].str.contains('DNF|dnf', case=False)]
    filtered_df = filtered_df[~filtered_df['DNF'].str.contains('DNF|dnf', case=False)]
    filtered_df = filtered_df[~filtered_df['Designator'].str.contains('DNF|dnf', case=False)]
    columns_to_keep = ['Quantity','Designator', 'Value','1st Vendor', '1st Vendor Part No' ,'Component Class','DEAR SKU', 'Description', 'Footprint']
    filtered_df = filtered_df[columns_to_keep]


    return filtered_df