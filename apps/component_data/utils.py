from import_export import resources
from tablib import Dataset
from .resource import ComponentResource

def import_data(file_path, file_format='csv'):
    component_resource = ComponentResource()
    dataset = Dataset()
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:  # Try different encodings if needed
        data = file.read()
        
    try:
        imported_data = dataset.load(data, format=file_format)
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return
    
    result = component_resource.import_data(dataset, dry_run=True)
    
    if not result.has_errors():
        component_resource.import_data(dataset, dry_run=False)
        print("Import successful")
    else:
        print("Errors encountered during import:")
        for error in result.row_errors():
            print(f"Row {error[0]}: {error[1][0].error}")
        
        print("\nFull error report:")
        print(result.invalid_rows)