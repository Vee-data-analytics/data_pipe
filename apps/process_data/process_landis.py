import pandas as pd 



def landis_bom(input_file):
    df = pd.read_excel(input_file, header=5)

    # Select rows starting from index 4 (5th row)
    df = df.iloc[4:]

    # Define the columns to keep and rename
    columns_to_keep = ['Reference', 'Technical Description']
    renamed_columns = {'Reference': 'Location'}  # Corrected the typo here

    # Select specific columns and rename one of them
    filtered_df = df[columns_to_keep].rename(columns=renamed_columns)
    return filtered_df
    
def landis_txt(dirty_text_file):
    # Read the content of the uploaded text file
    content = dirty_text_file.read().decode('utf-8')

    # Split the content into lines
    lines = content.strip().split('\n')

    # Split each line into columns
    data = [line.split() for line in lines]

    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=['RefDes', 'Value', 'Column-X', 'Column-Y', 'Rotation', 'Column6','Column7','Column8','Column9','Column10'])
    columns_to_display = ['RefDes','Value' ,'Column-X', 'Column-Y', 'Rotation']
    df = df[columns_to_display]

    return df
 
     
     
def merge_land(df1, df2):
    mapping_dict = df1.set_index('Location').to_dict()

    # Map the values from df2 to df1 based on 'Designators'
    df2['X-Column'] = df2['Location'].map(mapping_dict['Column-X'])
    df2['Value'] = df2['Location'].map(mapping_dict['Value'])
    df2['Y-Column'] = df2['Location'].map(mapping_dict['Column-Y'])
    df2['Rotation'] = df2['Location'].map(mapping_dict['Rotation'])

    # Display the modified df1
    return df2
     
     
def process_landis(dirty_text_file, input_file, output_format = 'csv'):
    df_text_processed = landis_txt(dirty_text_file)
    df_excel_processed = landis_bom(input_file)
    
    
    # Merge data
    df_result = merge_land(df_text_processed, df_excel_processed)
    
    display_columns = ['Location','Value','Technical Description','X-Column', 'Y-Column', 'Rotation']
    df_result = df_result[display_columns]
    df_result = df_result[~df_result['Technical Description'].str.contains('PCBA')]
    df_result['Value'] = df_result['Value'].str.upper()
    export_path = None
    if output_format == 'csv':
        export_path = 'data_storage/exports/processed_landis.csv'
        df_result.to_csv(export_path, index=False)
    elif output_format == 'txt':
        export_path = 'data_storage/exports/processed_data.txt'
        df_result.to_csv(export_path, index=False, sep='\t')

    return df_result, export_path

