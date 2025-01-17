import dash
from dash import html, dcc, dash_table, callback
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
import base64
import io
from enum import Enum
import numpy as np
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any,Tuple
import re
from decimal import Decimal



# Data Processing Classes
class ProcessingRuleType(Enum):
    COLUMN_MAP = "column_map"
    VALUE_FILTER = "value_filter"
    VALUE_TRANSFORM = "value_transform"
    SPLIT_EXPAND = "split_expand"
    MERGE_COLUMNS = "merge_columns"
    CUSTOM_FUNCTION = "custom_function"


class ComponentType(Enum):
    RESISTOR = "resistor"
    CAPACITOR = "capacitor"
    INDUCTOR = "inductor"
    IC = "ic"
    CONNECTOR = "connector"
    CRYSTAL = "crystal"
    DIODE = "diode"
    TRANSISTOR = "transistor"
    OTHER = "other"
@dataclass
class ValueFormat:
    unit: str
    multipliers: Dict[str, Decimal]
    standard_format: str
    validate_pattern: str



@dataclass
class ComponentRule:
    component_type: ComponentType
    designator_prefixes: List[str]
    value_format: ValueFormat
    description_patterns: List[str] = field(default_factory=list)
    custom_processor: Optional[Callable[[str, Dict[str, Any]], str]] = None
    additional_attributes: Dict[str, Any] = field(default_factory=dict)

class ValueProcessor:
    """Handles standardization of component values"""
    
    def __init__(self):
        self.value_formats = {
            ComponentType.RESISTOR: ValueFormat(
                unit="Ω",
                multipliers={"M": Decimal("1000000"), "K": Decimal("1000"), "R": Decimal("1")},
                standard_format="{value}{multiplier}",
                validate_pattern=r"^\d*\.?\d+[RKM]?$"
            ),
            ComponentType.CAPACITOR: ValueFormat(
                unit="F",
                multipliers={"U": Decimal("0.000001"), "N": Decimal("0.000000001"), "P": Decimal("0.000000000001")},
                standard_format="{value}{multiplier}F-{voltage}V",
                validate_pattern=r"^\d*\.?\d+[UNP]F-\d+\.?\d*V$"
            ),
            ComponentType.INDUCTOR: ValueFormat(
                unit="H",
                multipliers={"U": Decimal("0.000001"), "N": Decimal("0.000000001"), "M": Decimal("0.001")},
                standard_format="{value}{multiplier}H",
                validate_pattern=r"^\d*\.?\d+[UNM]H$"
            )
        }

    def standardize_value(self, value: str, component_type: ComponentType, attributes: Dict[str, Any]) -> str:
        """Standardize component value based on type and attributes"""
        

        try:
            # Extract numerical value and unit
            match = re.match(r"^([\d.]+)([A-Z])?.*$", value)
            if not match:
                return value

            num_value, unit = match.groups()
            num_value = Decimal(num_value)

            # Apply standardization based on component type
            if component_type == ComponentType.RESISTOR:
                return self._standardize_resistor(num_value, unit or 'R', format_spec)
            elif component_type == ComponentType.CAPACITOR:
                voltage = attributes.get('voltage', '')
                return self._standardize_capacitor(num_value, unit or 'U', voltage, format_spec)
            elif component_type == ComponentType.INDUCTOR:
                return self._standardize_inductor(num_value, unit or 'U', format_spec)
            
            elif not value:
            
                value = value.upper().strip()
                format_spec = self.value_formats.get(component_type)
            
            if not format_spec:

                return value
            

        except (ValueError, Decimal.InvalidOperation):
            return value

    def _standardize_resistor(self, value: Decimal, unit: str, format_spec: ValueFormat) -> str:
        """Standardize resistor value"""
        if unit not in format_spec.multipliers:
            unit = 'R'
        return format_spec.standard_format.format(value=value, multiplier=unit)

    def _standardize_capacitor(self, value: Decimal, unit: str, voltage: str, format_spec: ValueFormat) -> str:
        """Standardize capacitor value"""
        if unit not in format_spec.multipliers:
            unit = 'U'
        voltage = voltage.replace('V', '').strip() if voltage else ''
        return format_spec.standard_format.format(value=value, multiplier=unit, voltage=voltage)

    def _standardize_inductor(self, value: Decimal, unit: str, format_spec: ValueFormat) -> str:
        """Standardize inductor value"""
        if unit not in format_spec.multipliers:
            unit = 'U'
        return format_spec.standard_format.format(value=value, multiplier=unit)

@dataclass
class PatternMatch:
    value: str
    confidence: float
    source_field: str
    match_type: str

@dataclass
class ComponentPattern:
    pattern_type: str
    patterns: List[str]
    priority: int
    validation_func: Optional[callable] = None
    transform_func: Optional[callable] = None

class SmartPatternMatcher:
    def __init__(self):
        self.value_ranges = {
            'voltage': {
                'valid_range': (1.0, 100.0),
                'common_values': [1.8, 2.5, 3.3, 5.0, 6.3, 10, 16, 25, 35, 50, 63, 100],
                'units': ['V', 'VDC', 'WV'],
                'prefixes': ['rated', 'working', 'max']
            },
            'current': {
                'valid_range': (0.001, 10.0),  # 1mA to 10A
                'common_values': [0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5],
                'units': ['A', 'MA', 'mA'],
                'prefixes': ['rated', 'max']
            },
            'tolerance': {
                'valid_range': (0.1, 20.0),
                'common_values': [0.1, 0.5, 1, 2, 5, 10, 20],
                'units': ['%', 'PCT', 'PERCENT'],
                'prefixes': ['±', '+-', 'tol']
            }
        }
        
        self.footprint_patterns = {
            'metric': ['0201', '0402', '0603', '0805', '1206', '1210', '2010', '2512'],
            'imperial': ['0603M', '1005M', '1608M', '2012M', '3216M', '3225M'],
            'special': ['SOT23', 'SOD123', 'SOIC8', 'QFN']
        }

    def find_attribute_in_row(self, row: Dict[str, str], attribute: str) -> List[PatternMatch]:
        """Search for an attribute across all fields in a row"""
        matches = []
        
        # Get validation parameters for the attribute
        range_info = self.value_ranges.get(attribute, {})
        valid_range = range_info.get('valid_range')
        common_values = range_info.get('common_values', [])
        units = range_info.get('units', [])
        prefixes = range_info.get('prefixes', [])
        
        for field_name, field_value in row.items():
            if not isinstance(field_value, str):
                continue
                
            field_value = field_value.upper()
            words = field_value.replace(',', ' ').split()
            
            for i, word in enumerate(words):
                # Look for numbers followed by units
                numeric_match = re.search(r'([\d.]+)', word)
                if numeric_match:
                    try:
                        value = float(numeric_match.group(1))
                        
                        # Check if the value is within valid range
                        if valid_range and valid_range[0] <= value <= valid_range[1]:
                            # Check if unit follows the number
                            has_unit = any(unit in word[numeric_match.end():].upper() for unit in units)
                            
                            # Check if there's a prefix before the number
                            has_prefix = i > 0 and any(prefix in words[i-1].lower() for prefix in prefixes)
                            
                            confidence = 0.5
                            if has_unit:
                                confidence += 0.3
                            if has_prefix:
                                confidence += 0.2
                            if value in common_values:
                                confidence += 0.2
                                
                            matches.append(PatternMatch(
                                value=str(value),
                                confidence=min(confidence, 1.0),
                                source_field=field_name,
                                match_type=attribute
                            ))
                    except ValueError:
                        continue
                        
        return sorted(matches, key=lambda x: x.confidence, reverse=True)

    def find_footprint_in_row(self, row: Dict[str, str]) -> Optional[PatternMatch]:
        """Search for footprint information across all fields"""
        matches = []
        
        for field_name, field_value in row.items():
            if not isinstance(field_value, str):
                continue
                
            field_value = field_value.upper()
            
            # Check for exact matches in known footprint patterns
            for category, patterns in self.footprint_patterns.items():
                for pattern in patterns:
                    if pattern in field_value:
                        confidence = 0.8  # High confidence for exact matches
                        if field_name.upper() in ['FOOTPRINT', 'PACKAGE', 'SIZE']:
                            confidence = 1.0  # Highest confidence if found in relevant fields
                        matches.append(PatternMatch(
                            value=pattern,
                            confidence=confidence,
                            source_field=field_name,
                            match_type='footprint'
                        ))
        
        return matches[0] if matches else None

class EnhancedComponentValueProcessor:
    def __init__(self):
        self.pattern_matcher = SmartPatternMatcher()
        self.parser = SmartComponentParser()
        
    def process_component_value(self, row: Dict[str, str], designator: str) -> str:
        """Process component value with enhanced pattern matching"""
        component_type = self.detect_component_type(designator)
        base_value = str(row.get('value', ''))
        
        # Find attributes based on component type
        if component_type == ComponentType.CAPACITOR:
            voltage_matches = self.pattern_matcher.find_attribute_in_row(row, 'voltage')
            voltage = voltage_matches[0].value if voltage_matches else ''
            
            footprint_match = self.pattern_matcher.find_footprint_in_row(row)
            footprint = footprint_match.value if footprint_match else ''
            
            if voltage and footprint:
                return f"{base_value}-{voltage}V-{footprint}"
            elif voltage:
                return f"{base_value}-{voltage}V"
            elif footprint:
                return f"{base_value}-{footprint}"
                
        elif component_type == ComponentType.INDUCTOR:
            current_matches = self.pattern_matcher.find_attribute_in_row(row, 'current')
            current = current_matches[0].value if current_matches else ''
            
            footprint_match = self.pattern_matcher.find_footprint_in_row(row)
            footprint = footprint_match.value if footprint_match else ''
            
            if current and footprint:
                return f"{base_value}-{current}A-{footprint}"
            elif current:
                return f"{base_value}-{current}A"
            elif footprint:
                return f"{base_value}-{footprint}"
        
        return base_value

    def detect_component_type(self, designator: str) -> ComponentType:
        """Detect component type from designator"""
        if not designator:
            return ComponentType.OTHER
            
        prefix = designator[0].upper()
        type_map = {
            'R': ComponentType.RESISTOR,
            'C': ComponentType.CAPACITOR,
            'L': ComponentType.INDUCTOR
        }
        return type_map.get(prefix, ComponentType.OTHER)

@dataclass
class ParsedValue:
    base_value: str = ""
    unit: str = ""
    voltage: str = ""
    footprint: str = ""
    dielectric: str = ""
    tolerance: str = ""

class SmartComponentParser:
    def __init__(self):
        self.value_units = {
            'resistor': ['R', 'K', 'M'],
            'capacitor': ['F', 'UF', 'NF', 'PF'],
            'inductor': ['H', 'UH', 'NH', 'MH']
        }
        
        self.dielectric_types = ['X5R', 'X7R', 'X6S', 'NPO', 'COG']
        self.common_voltages = ['6.3', '10', '16', '25', '35', '50', '63', '100']
        self.common_footprints = ['0201', '0402', '0603', '0805', '1206', '1210']
        self.common_currents = ['100', '200', '300', '500', '1000', '2000']  # mA
        
    def standardize_component_value(self, row: Dict[str, str], component_type: str) -> str:
        """
        Standardize component value based on type and available information
        """
        # Get all relevant information from the row
        value = str(row.get('value', '')).upper()
        description = str(row.get('description', '')).upper()
        footprint = str(row.get('footprint', '')).upper()
        
        # Tokenize the value string
        tokens = self.tokenize_value(value)
        
        # Parse components
        base_value, unit = self.find_value_and_unit(tokens, component_type)
        if not base_value:
            return value  # Return original if parsing fails
            
        footprint_size = self.find_footprint(tokens, footprint)
        
        if component_type == 'resistor':
            # Format: {VALUE}{UNIT}-{FOOTPRINT}
            return f"{base_value}{unit}-{footprint_size}" if footprint_size else f"{base_value}{unit}"
            
        elif component_type == 'capacitor':
            # Format: {VALUE}{UNIT}-{VOLTAGE}V-{FOOTPRINT}
            voltage = self.find_voltage(tokens, description)
            unit = 'F' if unit == '' else unit
            
            if voltage and footprint_size:
                return f"{base_value}{unit}-{voltage}V-{footprint_size}"
            elif voltage:
                return f"{base_value}{unit}-{voltage}V"
            elif footprint_size:
                return f"{base_value}{unit}-{footprint_size}"
            else:
                return f"{base_value}{unit}"
                
        elif component_type == 'inductor':
            # Format: {VALUE}{UNIT}-{CURRENT}A-{FOOTPRINT}
            current = self.find_current(tokens, description)
            unit = 'H' if unit == '' else unit
            
            if current and footprint_size:
                return f"{base_value}{unit}-{current}A-{footprint_size}"
            elif current:
                return f"{base_value}{unit}-{current}A"
            elif footprint_size:
                return f"{base_value}{unit}-{footprint_size}"
            else:
                return f"{base_value}{unit}"
        
        return value
    
    def find_current(self, tokens: List[str], description: str = '') -> str:
        """Find current rating from tokens or description"""
        for token in tokens:
            # Remove 'A' or 'MA' suffix if present
            token = token.upper().replace('A', '').replace('MA', '').strip()
            if token in self.common_currents:
                return token
        
        if description:
            desc_tokens = self.tokenize_value(description)
            for token in desc_tokens:
                token = token.upper().replace('A', '').replace('MA', '').strip()
                if token in self.common_currents:
                    return token
        
        return ''
        
    def tokenize_value(self, value_str: str) -> List[str]:
        """Split value string into tokens without using regex"""
        # Replace common separators with spaces
        for sep in [',', '/', '_', '-', '±']:
            value_str = value_str.replace(sep, ' ')
        
        # Split and clean tokens
        tokens = [token.strip().upper() for token in value_str.split()]
        return [t for t in tokens if t]

    def find_value_and_unit(self, tokens: List[str], component_type: str) -> Tuple[str, str]:
        """Find the base value and unit from tokens"""
        valid_units = self.value_units[component_type]
        
        for token in tokens:
            # Try to find a number followed by a valid unit
            numeric_part = ''
            unit_part = ''
            
            # Split numeric and alpha parts
            for char in token:
                if char.isdigit() or char == '.':
                    numeric_part += char
                else:
                    unit_part += char
            
            unit_part = unit_part.upper()
            if numeric_part and (unit_part in valid_units or not unit_part):
                return numeric_part, unit_part if unit_part else valid_units[0]
                
        return '', ''

    def find_voltage(self, tokens: List[str], description: str = '') -> str:
        """Find voltage value from tokens or description"""
        # First check tokens
        for token in tokens:
            # Remove 'V' suffix if present
            token = token.upper().replace('V', '').strip()
            if token in self.common_voltages:
                return token
        
        # Check description if no voltage found in tokens
        if description:
            desc_tokens = self.tokenize_value(description)
            for token in desc_tokens:
                token = token.upper().replace('V', '').strip()
                if token in self.common_voltages:
                    return token
        
        return ''

    def find_footprint(self, tokens: List[str], footprint_col: str = '') -> str:
        """Find footprint from tokens or dedicated column"""
        # First check dedicated footprint column
        if footprint_col:
            for size in self.common_footprints:
                if size in footprint_col.upper():
                    return size
        
        # Check tokens
        for token in tokens:
            if token in self.common_footprints:
                return token
                
        return ''

    def standardize_component_value(self, row: Dict[str, str], component_type: str) -> str:
        """
        Standardize component value based on type and available information
        """
        # Get all relevant information from the row
        value = str(row.get('value', '')).upper()
        description = str(row.get('description', '')).upper()
        footprint = str(row.get('footprint', '')).upper()
        
        # Tokenize the value string
        tokens = self.tokenize_value(value)
        
        # Parse components
        base_value, unit = self.find_value_and_unit(tokens, component_type)
        if not base_value:
            return value  # Return original if parsing fails
            
        footprint_size = self.find_footprint(tokens, footprint)
        
        # Standardize based on component type
        if component_type == 'resistor':
            # Format: {VALUE}{UNIT}-{FOOTPRINT}
            return f"{base_value}{unit}-{footprint_size}" if footprint_size else f"{base_value}{unit}"
            
        elif component_type == 'capacitor':
            # Format: {VALUE}{UNIT}-{VOLTAGE}V-{FOOTPRINT}
            voltage = self.find_voltage(tokens, description)
            unit = 'F' if unit == '' else unit
            
            if voltage and footprint_size:
                return f"{base_value}{unit}-{voltage}V-{footprint_size}"
            elif voltage:
                return f"{base_value}{unit}-{voltage}V"
            elif footprint_size:
                return f"{base_value}{unit}-{footprint_size}"
            else:
                return f"{base_value}{unit}"
                
        return value


class ComponentValueProcessor:
    def __init__(self):
        self.parser = SmartComponentParser()
        
    def process_value(self, value: str, designator: str, description: str = '', footprint: str = '') -> str:
        """Process component value using smart parser"""
        # Determine component type from designator
        
        # Determine component type from designator
        if designator.startswith('R'):
            component_type = 'resistor'
        elif designator.startswith('C'):
            component_type = 'capacitor'
        else:
            component_type = 'other'
        
        if component_type in ['resistor', 'capacitor']:
            row = {
                'value': value,
                'description': description,
                'footprint': footprint
            }
            return self.parser.standardize_component_value(row, component_type)
            
        return value    
    def __init__(self):
        self.value_processor = ValueProcessor()
        self.component_rules = self._initialize_rules()
        
    def _initialize_rules(self) -> Dict[ComponentType, ComponentRule]:
        """Initialize component rules"""
        return {
            ComponentType.RESISTOR: ComponentRule(
                component_type=ComponentType.RESISTOR,
                designator_prefixes=['R'],
                value_format=self.value_processor.value_formats[ComponentType.RESISTOR],
                description_patterns=['Chip Resistor', 'Array Resistor']
            ),
            ComponentType.CAPACITOR: ComponentRule(
                component_type=ComponentType.CAPACITOR,
                designator_prefixes=['C'],
                value_format=self.value_processor.value_formats[ComponentType.CAPACITOR],
                description_patterns=['Capacitor', 'MLCC']
            ),
            ComponentType.INDUCTOR: ComponentRule(
                component_type=ComponentType.INDUCTOR,
                designator_prefixes=['L'],
                value_format=self.value_processor.value_formats[ComponentType.INDUCTOR],
                description_patterns=['Inductor', 'Choke', 'Ferrite']
            )
        }

    def detect_component_type(self, designator: str, description: str = '') -> ComponentType:
        """Detect component type from designator and description"""
        if not designator:
            return ComponentType.OTHER
            
        prefix = ''.join(filter(str.isalpha, designator[:2])).upper()
        
        # Check designator prefix first
        for comp_type, rule in self.component_rules.items():
            if prefix in rule.designator_prefixes:
                # Verify with description if available
                if description and rule.description_patterns:
                    if any(pattern.lower() in description.lower() for pattern in rule.description_patterns):
                        return comp_type
                else:
                    return comp_type
                    
        return ComponentType.OTHER

@dataclass
class ProcessingRule:
    rule_type: ProcessingRuleType
    parameters: Dict[str, Any]
    priority: int = 0

class ComponentValueProcessor:
    def __init__(self):
        self.resistor_multipliers = {'M': 1000000, 'K': 1000, 'R': 1}
        self.capacitor_multipliers = {'U': 0.000001, 'N': 0.000000001, 'P': 0.000000000001}
        self.inductor_multipliers = {'M': 0.001, 'U': 0.000001, 'N': 0.000000001}
        
    def clean_manufacturer_info(self, value: str) -> str:
        """Remove manufacturer information and trailing specs"""
        if not value:
            return value
            
        value = value.upper().strip()
        
        # Remove manufacturer tags
        value = re.sub(r'<[^>]+>', '', value)
        
        # Remove everything after common delimiters
        delimiters = [',', '--', ' ', '+', '=', '<']
        for delimiter in delimiters:
            if delimiter in value:
                value = value.split(delimiter)[0]
                
        # Clean up common substitutions
        value = value.replace('_', '-')
        value = value.replace('/', '-')
        
        return value.strip()
    
    def _is_manufacturer_part(self, value: str) -> bool:
        """Check if the value appears to be a manufacturer part number"""
        # Look for patterns like GRM32ER71K475KE14, GJM1555C1H6R8CB01D
        return bool(re.match(r'^[A-Z]{2,3}\d{2,4}[A-Z0-9]{10,}.*$', value))
    
    def process_capacitor(self, value: str, description: str = '', footprint: str = '') -> str:
        """Process capacitor values and add voltage information"""
        value = self.clean_manufacturer_info(value)
        
        # If it's a manufacturer part number, just clean it and add footprint
        if self._is_manufacturer_part(value):
            if footprint:
                return f"{value}-{self._extract_footprint_size(footprint)}"
            return value
        
        # Extract voltage from description if available
        voltage = self._extract_voltage(description)
        
        # Add voltage to value if not already present and we have voltage info
        if voltage and 'V' not in value.upper():
            value = f"{value}-{voltage}"
        
        # Add footprint if available
        if footprint:
            footprint_size = self._extract_footprint_size(footprint)
            if footprint_size:
                value = f"{value}-{footprint_size}"
                
        return value
    
    def _extract_voltage(self, description: str) -> str:
        """Extract voltage information from description"""
        if not description:
            return ''
            
        # Look for voltage patterns like "50V", "3.3V", etc.
        voltage_match = re.search(r'(\d+(\.\d+)?V)', description)
        if voltage_match:
            return voltage_match.group(1)
        return ''
    
    def _extract_footprint_size(self, footprint: str) -> str:
        """Extract size from footprint"""
        # Look for common footprint sizes (0402, 0603, 0805, 1210, etc.)
        size_match = re.search(r'(\d{4})(?:_CAP)?', footprint)
        if size_match:
            return size_match.group(1)
        return ''
    
    def process_resistor(self, value: str, footprint: str = '') -> str:
        """Process resistor values maintaining original format"""
        value = self.clean_manufacturer_info(value)
        
        # Add footprint if available
        if footprint:
            footprint_size = self._extract_footprint_size(footprint)
            if footprint_size:
                value = f"{value}-{footprint_size}"
                
        return value
    
    def process_value(self, value: str, designator: str, description: str = '', footprint: str = '') -> str:
        """Process component value based on designator"""
        if not value or not designator:
            return value
            
        designator = designator.upper()
        
        try:
            if designator.startswith('R'):
                return self.process_resistor(value, footprint)
            elif designator.startswith('C'):
                return self.process_capacitor(value, description, footprint)
            else:
                return self.clean_manufacturer_info(value)
        except Exception as e:
            print(f"Error processing value {value}: {str(e)}")
            return value

class DataProcessor:
    def __init__(self):
        self.value_processor = EnhancedComponentValueProcessor()
        
    def process_data(self, df: pd.DataFrame, custom_rules: List[ProcessingRule]) -> pd.DataFrame:
        """Process data using provided rules"""
        try:
            df = df.copy()
            
            # Sort rules by priority
            sorted_rules = sorted(custom_rules, key=lambda x: x.priority)
            
            # Apply rules in order
            for rule in sorted_rules:
                if rule.rule_type == ProcessingRuleType.COLUMN_MAP:
                    # Apply column mapping
                    valid_mappings = {
                        old_col: new_col 
                        for old_col, new_col in rule.parameters['mapping'].items()
                        if old_col in df.columns
                    }
                    df = df.rename(columns=valid_mappings)
                
                elif rule.rule_type == ProcessingRuleType.VALUE_FILTER:
                    # Apply value filtering
                    col = rule.parameters['column']
                    values = rule.parameters['values']
                    filter_type = rule.parameters.get('filter_type', 'exclude')
                    
                    if col in df.columns and values:
                        # Convert both series and filter values to string for comparison
                        df[col] = df[col].astype(str)
                        values = [str(v) for v in values]
                        
                        # Create mask for filtering
                        mask = df[col].isin(values)
                        if filter_type == 'exclude':
                            df = df[~mask]  # Keep rows where value is NOT in the filter list
                        else:
                            df = df[mask]   # Keep rows where value IS in the filter list
                
                elif rule.rule_type == ProcessingRuleType.SPLIT_EXPAND:
                    # Handle designator splitting
                    col = rule.parameters['column']
                    if col in df.columns:
                        df[col] = df[col].astype(str)
                        df = df[df[col].str.strip() != '']
                        df = df.assign(designator=df[col].str.split(',')).explode('designator')
                        df['designator'] = df['designator'].str.strip()
            
            # Update the value processing to use the new system
            if all(col in df.columns for col in ['value', 'designator']):
                df['value'] = df.apply(lambda row: self.value_processor.process_component_value(
                    row.to_dict(),  # Pass the entire row as a dictionary
                    str(row['designator'])
                ), axis=1)
            
            return df
            
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            raise
            
    
    def _apply_rule(self, df: pd.DataFrame, rule: ProcessingRule) -> pd.DataFrame:
        """Apply a single processing rule to the DataFrame"""
        try:
            if rule.rule_type == ProcessingRuleType.COLUMN_MAP:
                valid_mappings = {
                    old_col: new_col 
                    for old_col, new_col in rule.parameters['mapping'].items()
                    if old_col in df.columns
                }
                return df.rename(columns=valid_mappings)
                
            elif rule.rule_type == ProcessingRuleType.VALUE_FILTER:
                col = rule.parameters['column']
                values = rule.parameters['values']
                filter_type = rule.parameters.get('filter_type', 'exclude')
                
                if col in df.columns and values:
                    mask = df[col].isin(values)
                    if filter_type == 'exclude':
                        return df[~mask]
                    return df[mask]
                return df
                
            elif rule.rule_type == ProcessingRuleType.VALUE_TRANSFORM:
                col = rule.parameters['column']
                transform_func = rule.parameters['transform']
                if col in df.columns:
                    df[col] = df[col].apply(transform_func)
                return df
                
            elif rule.rule_type == ProcessingRuleType.SPLIT_EXPAND:
                col = rule.parameters['column']
                separator = rule.parameters.get('separator', ',')
                if col in df.columns:
                    # Ensure the column is string type before splitting
                    df[col] = df[col].astype(str)
                    df[col] = df[col].str.split(separator)
                    return df.explode(col).reset_index(drop=True)
                return df
                
            elif rule.rule_type == ProcessingRuleType.MERGE_COLUMNS:
                cols = rule.parameters['columns']
                new_col = rule.parameters['new_column']
                separator = rule.parameters.get('separator', '')
                
                if all(col in df.columns for col in cols):
                    # Convert all columns to string type before joining
                    df[new_col] = df[cols].astype(str).apply(
                        lambda x: separator.join(val for val in x if pd.notna(val)), axis=1
                    )
                return df
                
            elif rule.rule_type == ProcessingRuleType.CUSTOM_FUNCTION:
                func = rule.parameters['function']
                return func(df)
                
            return df
        
        except Exception as e:
            print(f"Error applying rule {rule.rule_type}: {str(e)}")
            return df

    def add_component_rule(self, rule: ComponentRule):
        """Add or update a component rule"""
        self.component_rules[rule.component_type] = rule

    

class DashDataProcessor:
    def __init__(self):
        self.processor = DataProcessor()
        
    def create_rules_from_column_state(self, column_state: Dict) -> List[ProcessingRule]:
        """Convert Dash app column state to processing rules"""
        rules = []
        
        # Create mapping rule first (Priority 0)
        mapping = {
            col: state['map'] 
            for col, state in column_state.items() 
            if state.get('map')
        }
        if mapping:
            rules.append(ProcessingRule(
                rule_type=ProcessingRuleType.COLUMN_MAP,
                parameters={'mapping': mapping},
                priority=0
            ))
        
        # Add value filtering rules (Priority 1)
        for col, state in column_state.items():
            if state.get('filters'):
                # Get the mapped column name if it exists, otherwise use original
                mapped_col = state.get('map', col)
                rules.append(ProcessingRule(
                    rule_type=ProcessingRuleType.VALUE_FILTER,
                    parameters={
                        'column': mapped_col,  # Use mapped column name
                        'values': state['filters'],
                        'filter_type': 'exclude'
                    },
                    priority=1
                ))
        
        # Add designator splitting rule if needed (Priority 2)
        if any(state.get('map') == 'designator' for state in column_state.values()):
            rules.append(ProcessingRule(
                rule_type=ProcessingRuleType.SPLIT_EXPAND,
                parameters={'column': 'designator'},
                priority=2
            ))
        
        # Sort rules by priority
        rules.sort(key=lambda x: x.priority)
        return rules
        
    def process_dash_data(self, df: pd.DataFrame, column_state: Dict) -> pd.DataFrame:
        """Process data using rules created from Dash app column state"""
        try:
            rules = self.create_rules_from_column_state(column_state)
            return self.processor.process_data(df, custom_rules=rules)
        except Exception as e:
            print(f"Error in process_dash_data: {str(e)}")
            raise
        
    def process_dash_data(self, df: pd.DataFrame, column_state: Dict) -> pd.DataFrame:
        """Process data using rules created from Dash app column state"""
        rules = self.create_rules_from_column_state(column_state)
        return self.processor.process_data(df, custom_rules=rules)

# Initialize Dash app and processor
app = dash.Dash(__name__)
dash_processor = DashDataProcessor()

# Define required column mappings
REQUIRED_COLUMNS = {
    'Designator': 'designator',
    'Value': 'value',
    'Part name': 'part name',
    'Footprint': 'Footprint',
    'Description': 'description',
    'Rotation': 'rotation',
    'Component Class': 'class',
    'DNF': 'dnf'
}

def create_column_control(col: str, df: pd.DataFrame, 
                         current_map: Optional[str] = None, 
                         current_filters: Optional[list] = None) -> html.Div:
    """
    Create column mapping and filtering controls.
    
    Args:
        col (str): Column name
        df (pd.DataFrame): DataFrame containing the data
        current_map (str, optional): Current column mapping
        current_filters (list, optional): Current filter values
    """
    try:
        # Safely get unique values from the column
        if col in df.columns:
            # Convert to series and get unique values
            series = df[col]
            if isinstance(series, pd.Series):
                unique_vals = series.dropna().unique()
                # Convert all values to strings and sort
                formatted_values = sorted([str(val) for val in unique_vals if pd.notna(val)])
            else:
                formatted_values = []
        else:
            formatted_values = []
            
        return html.Div([
            html.Div(col, style={'fontWeight': 'bold', 'textAlign': 'center', 'marginBottom': '5px'}),
            html.Label('Map to:'),
            dcc.Dropdown(
                id={'type': 'column-map', 'index': col},
                options=[{'label': k, 'value': v} for k, v in REQUIRED_COLUMNS.items()],
                value=current_map,
                placeholder='Select mapping',
                style={'marginBottom': '10px', 'width': '200px'}
            ),
            html.Label('Exclude values:'),
            dcc.Dropdown(
                id={'type': 'column-filter', 'index': col},
                options=[{'label': val, 'value': val} for val in formatted_values],
                value=current_filters,
                multi=True,
                placeholder='Select values to exclude',
                style={'width': '200px'}
            )
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'margin': '5px', 'minWidth': '250px'})
    except Exception as e:
        print(f"Error creating column control for {col}: {str(e)}")
        # Return empty div if there's an error
        return html.Div(f"Error loading controls for column: {col}")


# App layout
app = dash.Dash(__name__)
dash_processor = DashDataProcessor()

# Modified app layout to include download components
app.layout = html.Div([
    # Header
    html.H1("Production Data Processor", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
    
    # File Upload Section
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files', style={'color': '#3498db'})
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'backgroundColor': '#f8f9fa'
            },
            multiple=False
        ),
        
        # Controls Section
        html.Div([
            html.Label('Select Header Row:', 
                      style={'marginRight': '10px', 'fontWeight': 'bold'}),
            dcc.Input(
                id='header-row-input',
                type='number',
                min=0,
                value=0,
                style={'marginRight': '20px', 'width': '100px', 'padding': '5px'}
            ),
            html.Button(
                'Apply Header',
                id='apply-header-button',
                n_clicks=0,
                style={
                    'marginRight': '20px',
                    'backgroundColor': '#2ecc71',
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'borderRadius': '5px'
                }
            ),
            html.Button(
                'Process Data',
                id='process-button',
                n_clicks=0,
                style={
                    'backgroundColor': '#3498db',
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'borderRadius': '5px'
                }
            ),
        ], style={'marginBottom': '20px', 'marginTop': '20px'}),
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Column Controls and Data Display
    html.Div([
        html.Div(id='column-controls', 
                 style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px', 'marginTop': '20px'}),
        html.Div(id='preview-table', style={'marginTop': '20px'}),
        html.Div(id='output-data-upload', style={'marginTop': '20px'})
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginTop': '20px', 
              'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Add download button and component to main layout
    html.Button(
        'Download CSV',
        id='btn-download',
        style={
            'backgroundColor': '#27ae60',
            'color': 'white',
            'border': 'none',
            'padding': '10px 20px',
            'borderRadius': '5px',
            'marginTop': '10px',
            'marginBottom': '10px',
            'display': 'none'  # Hidden by default
        }
    ),
    dcc.Download(id='download-dataframe-csv'),
    
    # Store components for state management
    dcc.Store(id='raw-data'),
    dcc.Store(id='column-state')
])


# Callbacks
@app.callback(
    [Output('column-controls', 'children'),
     Output('preview-table', 'children'),
     Output('raw-data', 'data'),
     Output('column-state', 'data')],
    [Input('upload-data', 'contents'),
     Input('apply-header-button', 'n_clicks'),
     Input({'type': 'column-map', 'index': ALL}, 'value'),
     Input({'type': 'column-filter', 'index': ALL}, 'value')],
    [State('upload-data', 'filename'),
     State('header-row-input', 'value'),
     State('raw-data', 'data'),
     State('column-state', 'data'),
     State({'type': 'column-map', 'index': ALL}, 'id'),
     State({'type': 'column-filter', 'index': ALL}, 'id')]
)
def update_interface(contents, n_clicks, map_values, filter_values,
                    filename, header_row, stored_data, column_state,
                    map_ids, filter_ids):
    """Update the interface based on user interactions."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return [], None, None, None

    trigger = ctx.triggered[0]
    trigger_id = trigger['prop_id'].split('.')[0]
    column_state = column_state or {}

    try:
        # Handle file upload or header application
        if trigger_id in ['upload-data', 'apply-header-button']:
            if trigger_id == 'upload-data' and contents:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                
                if 'csv' in filename.lower():
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                elif 'xls' in filename.lower():
                    df = pd.read_excel(io.BytesIO(decoded))
                else:
                    return [], html.Div('Unsupported file type. Please upload CSV or Excel files.'), None, None
                    
            elif trigger_id == 'apply-header-button' and stored_data:
                df = pd.read_json(stored_data, orient='split')
                if header_row > 0:
                    new_headers = df.iloc[header_row]
                    df = df.iloc[header_row + 1:].reset_index(drop=True)
                    df.columns = [str(val) for val in new_headers]
            else:
                return [], None, None, None

            # Serialize the data for preview
            df = serialize_df(df)

            # Create column controls
            column_controls = [
                create_column_control(
                    str(col),
                    df,
                    current_map=column_state.get(str(col), {}).get('map'),
                    current_filters=column_state.get(str(col), {}).get('filters')
                ) for col in df.columns
            ]

            # Create preview table
            preview_table = html.Div([
                html.H5('Data Preview'),
                dash_table.DataTable(
                    data=df.head(10).to_dict('records'),
                    columns=[{'name': str(i), 'id': str(i)} for i in df.columns],
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    }
                )
            ])
            
            return column_controls, preview_table, df.to_json(date_format='iso', orient='split'), column_state

        # Handle column mappings and filters
        elif '{' in trigger_id:
            for map_id, map_val, filter_id, filter_val in zip(map_ids, map_values, filter_ids, filter_values):
                col = map_id['index']
                column_state[col] = {
                    'map': map_val,
                    'filters': filter_val or []
                }
            return dash.no_update, dash.no_update, dash.no_update, column_state

    except Exception as e:
        print(f"Error in update_interface: {str(e)}")  # Add debug logging
        return [], html.Div(f'Error processing file: {str(e)}'), None, None

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

def serialize_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Serialize DataFrame to ensure all values are compatible with Dash DataTable.
    Converts all values to strings, numbers, or booleans.
    """
    df = df.copy()
    
    for column in df.columns:
        # Handle lists/arrays
        if df[column].apply(lambda x: isinstance(x, (list, np.ndarray))).any():
            df[column] = df[column].apply(lambda x: str(x) if isinstance(x, (list, np.ndarray)) else x)
        
        # Convert objects and other non-compatible types to strings
        if df[column].dtype == 'object' or df[column].dtype.name not in ['bool', 'int64', 'float64']:
            df[column] = df[column].apply(lambda x: str(x) if pd.notna(x) else '')
            
        # Replace NaN/None with empty string
        df[column] = df[column].fillna('')
    
    return df


@app.callback(
    [Output('output-data-upload', 'children'),
     Output('btn-download', 'style')],
    [Input('process-button', 'n_clicks')],
    [State('raw-data', 'data'),
     State('column-state', 'data')]
)
def process_data_callback(n_clicks, raw_data, column_state):
    """Process the data according to user-specified mappings and filters."""
    if n_clicks == 0 or raw_data is None or not column_state:
        return html.Div(), {'display': 'none'}

    try:
        df = pd.read_json(raw_data, orient='split')
        processed_df = dash_processor.process_dash_data(df, column_state)
        
        # Serialize the DataFrame for DataTable
        serialized_df = serialize_df(processed_df)

        # Show download button style
        download_style = {
            'backgroundColor': '#27ae60',
            'color': 'white',
            'border': 'none',
            'padding': '10px 20px',
            'borderRadius': '5px',
            'marginTop': '10px',
            'marginBottom': '10px',
            'display': 'block'
        }

        return html.Div([
            html.H5('Processed Data'),
            html.Div([
                html.Strong('Total rows: '),
                html.Span(f"{len(serialized_df)}"),
            ], style={'marginBottom': '20px'}),
            dash_table.DataTable(
                data=serialized_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in serialized_df.columns],
                page_size=10,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                style_table={
                    'overflowX': 'auto',
                    'maxHeight': '500px',
                    'overflowY': 'auto'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'minWidth': '100px',
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'borderBottom': '2px solid #dee2e6'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9'
                    }
                ],
                export_format="csv"
            )
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'}), download_style

    except Exception as e:
        print(f"Error in process_data_callback: {str(e)}")  # Add debug logging
        return html.Div([
            html.H5('Error Processing Data', style={'color': 'red'}),
            html.Div(str(e)),
        ], style={'backgroundColor': '#ffe6e6', 'padding': '20px', 'borderRadius': '10px'}), {'display': 'none'}

# Also update the preview table in the update_interface callback

@app.callback(
    Output('download-dataframe-csv', 'data'),
    Input('btn-download', 'n_clicks'),
    [State('raw-data', 'data'),
     State('column-state', 'data')],
    prevent_initial_call=True
)
def download_csv(n_clicks, raw_data, column_state):
    if n_clicks is None or raw_data is None or column_state is None:
        return None

if __name__ == '__main__':
    app.run_server(debug=True)