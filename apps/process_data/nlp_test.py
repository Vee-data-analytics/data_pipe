import pandas as pd
import spacy


# Load your trained model

nlp = spacy.load("save_model")

# Read the Excel file
df = pd.read_excel('Bill-of-Materials-Ensurity-Mini.xlsx')

# Function to process resistors
def process_resistor(row):
    value = row.get('Value', '')
    size = row.get('Size', '')
    return f"{value}-{size}"

# Function to process capacitors
def process_capacitor(row):
    value = row.get('Value', '')
    volts = row.get('Voltz', '')
    size = row.get('Size', '')
    return f"{value}-{volts}-{size}"

# Function to process inductors
def process_inductor(row):
    return row.get('Value', '')

# Function to process a row based on its type
def process_row(row):
    component_type = row.get('Type', '').lower()
    if 'resistor' in component_type:
        return process_resistor(row)
    elif 'capacitor' in component_type:
        return process_capacitor(row)
    elif 'inductor' in component_type:
        return process_inductor(row)
    else:
        return ''

# Process each row and store the results
processed_data = []
for _, row in df.iterrows():
    processed_text = process_row(row)
    processed_data.append(processed_text)

# Test the model on processed data
results = []
for text in processed_data:
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    results.append((text, entities))

# Print results
for original, entities in results:
    print(f"Original: {original}")
    print("Entities found:")
    for entity, label in entities:
        print(f"  - {entity}: {label}")
    print()

# Optional: Save results to a new Excel file
result_df = pd.DataFrame(results, columns=['Original', 'Entities'])
result_df.to_excel('NER_Results.xlsx', index=False)