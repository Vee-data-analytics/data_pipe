import spacy
import re
from spacy.tokens import Doc
from spacy.training import Example
import pandas as pd
from spacy.util import minibatch, compounding

# Load the pre-existing spacy model
nlp = spacy.load("en_core_web_sm")

# Ensure spacy-lookups-data is available
try:
    from spacy.lookups import Lookups
    lookups = nlp.vocab.lookups
    if 'lexeme_norm' not in lookups:
        lookups.add_table('lexeme_norm')
        lookups.from_disk(nlp.vocab.lang + '_lexeme_norm')
except ImportError:
    raise ImportError("Please ensure you have the latest version of spaCy and that 'spacy-lookups-data' is installed. You can install it using 'pip install spacy-lookups-data'")


# Get the existing ner pipe
ner = nlp.get_pipe("ner")

# Add new labels to the ner
labels = ["SIZE", "VOLTAGE", "TYPE", "CAPACITANCE", "RESISTANCE", "PART_NUMBER", "BATTERY_CAPACITY",
          "KILO_RESISTANCE", "OHM_RESISTANCE", "MEG_RESISTANCE",
          "NANO_CAPACITANCE", "PICO_CAPACITANCE", "MICRO_CAPACITANCE",
          "NANO_INDUCTANCE", "MICRO_INDUCTANCE", "PICO_INDUCTANCE",
          "HERTZ_FREQUENCY", "KILO_FREQUENCY", "MEGA_FREQUENCY", "GIGA_FREQUENCY"]

for label in labels:
    ner.add_label(label)

# Function to categorize tokens
def identify_entity_type(token, position=0):
    # Resistance categories
    if re.match(r'\d+[kK]', token):
        return "KILO_RESISTANCE"
    elif re.match(r'\d+[mM]', token):
        return "MEG_RESISTANCE"
    elif re.match(r'\d+[rR]', token):
        return "OHM_RESISTANCE"

    # Capacitance categories
    elif re.match(r'\d+(\.\d+)?[nN][fF]', token):
        return "NANO_CAPACITANCE"
    elif re.match(r'\d+(\.\d+)?[pP][fF]', token):
        return "PICO_CAPACITANCE"
    elif re.match(r'\d+(\.\d+)?[uU][fF]', token):
        return "MICRO_CAPACITANCE"

    # Inductance categories
    elif re.match(r'\d+(\.\d+)?[nN][hH]', token):
        return "NANO_INDUCTANCE"
    elif re.match(r'\d+(\.\d+)?[pP][hH]', token):
        return "PICO_INDUCTANCE"
    elif re.match(r'\d+(\.\d+)?[uU][hH]', token):
        return "MICRO_INDUCTANCE"

    # Frequency categories
    elif re.match(r'\d+(\.\d+)?[hH][zZ]', token):
        return "HERTZ_FREQUENCY"
    elif re.match(r'\d+(\.\d+)?[kK][hH][zZ]', token):
        return "KILO_FREQUENCY"
    elif re.match(r'\d+(\.\d+)?[mM][hH][zZ]', token):
        return "MEGA_FREQUENCY"
    elif re.match(r'\d+(\.\d+)?[gG][hH][zZ]', token):
        return "GIGA_FREQUENCY"

    # Footprint size categories
    elif re.match(r'\d{4}', token):
        return "SIZE"
    elif re.match(r'\d\d\d\d', token):
        return "SIZE"
    elif re.match(r'\d{2}\d{2}', token):
        return "SIZE"

    # Other categories
    elif re.match(r'\d+(\.\d+)?[vV]', token):
        return "VOLTAGE"
    elif re.match(r'\d+(\.\d+)?[vV][dD][cC]', token):
        return "VOLTAGE"

    elif re.match(r'\d+[mM][aA][hH]', token):
        return "BATTERY_CAPACITY"
    elif position == 0 and token.isalnum():
        return "PART_NUMBER"
    else:
        return None

# Examples for training/testing
examples = [
    Example.from_dict(
        Doc(nlp.vocab, words=["10K", "0402"]),
        {"entities": [(0, 1, "KILO_RESISTANCE"), (1, 2, "SIZE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["100R", "0402"]),
        {"entities": [(0, 1, "OHM_RESISTANCE"), (1, 2, "SIZE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["1M", "0402"]),
        {"entities": [(0, 1, "MEG_RESISTANCE"), (1, 2, "SIZE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["4.7UF", "0402", "6.3V"]),
        {"entities": [(0, 1, "MICRO_CAPACITANCE"), (1, 2, "SIZE"), (2, 3, "VOLTAGE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["33PF", "0201", "50V"]),
        {"entities": [(0, 1, "PICO_CAPACITANCE"), (1, 2, "SIZE"), (2, 3, "VOLTAGE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["100NF", "0402", "50V"]),
        {"entities": [(0, 1, "NANO_CAPACITANCE"), (1, 2, "SIZE"), (2, 3, "VOLTAGE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["10nH", "0603"]),
        {"entities": [(0, 1, "NANO_INDUCTANCE"), (1, 2, "SIZE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["47uH", "0402"]),
        {"entities": [(0, 1, "MICRO_INDUCTANCE"), (1, 2, "SIZE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["100pH", "0805"]),
        {"entities": [(0, 1, "PICO_INDUCTANCE"), (1, 2, "SIZE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["16MHz", "0805"]),
        {"entities": [(0, 1, "MEGA_FREQUENCY"), (1, 2, "SIZE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["32.768kHz", "0603"]),
        {"entities": [(0, 1, "KILO_FREQUENCY"), (1, 2, "SIZE")]}
    ),
    Example.from_dict(
        Doc(nlp.vocab, words=["2.4GHz", "0402"]),
        {"entities": [(0, 1, "GIGA_FREQUENCY"), (1, 2, "SIZE")]}
    ),
]

# Read the data from 'BARRA_EDGE_4G_05_24B.csv'
cleaned_data = pd.read_csv('BARRA_EDGE_4G_05_24B.csv')

#cleaned_data = clean_data.drop_duplicates()
cleaned_data['Value'] = cleaned_data['Value'].astype(str).str.replace('-', ' ')

# Save the cleaned data to 'Training_data.csv'
cleaned_data.to_csv('Training_data.csv', index=False)

# Process the cleaned_data to identify entities and create examples
for cleaned_text in cleaned_data['Value']:  # Replace 'Value' with the actual column name if different
    tokens = cleaned_text.split()  # Split by spaces
    entities = []

    for i, token in enumerate(tokens):
        entity_type = identify_entity_type(token, i)
        if entity_type:
            start = sum(len(t) + 1 for t in tokens[:i]) - 1  # Adjust for spaces
            end = start + len(token)
            entities.append((start, end, entity_type))

    doc = Doc(nlp.vocab, words=tokens)
    example = Example.from_dict(doc, {"entities": entities})
    examples.append(example)

# Initialize and train the model
nlp.initialize(lambda: examples)
for i in range(100):
    losses = {}
    nlp.update(examples, losses=losses)
    print(losses)

# After training
nlp.to_disk("save_model")

