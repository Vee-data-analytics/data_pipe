import dash
from dash import html, dcc, dash_table, callback
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
import base64
import io
from typing import Tuple, Optional, Dict

# Initialize Dash app
app = dash.Dash(__name__)

# Define required column mappings
REQUIRED_COLUMNS = {
    'Row': 'row',
    'Designator': 'designator',
    'Value': 'value',
    'Vendor Number': 'vendor',
    'Component Class': 'class',
    'SMT': 'smt',
    'DNF': 'dnf'
}

class DataProcessor:
    @staticmethod
    def parse_uploaded_file(contents: str, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Parse uploaded file contents into a DataFrame."""
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            if 'csv' in filename.lower():
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename.lower():
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return None, 'Unsupported file type. Please upload CSV or Excel files.'
            
            df['Row'] = df.index
            return df, None
            
        except Exception as e:
            return None, f'Error processing file: {str(e)}'
    
    @staticmethod
    def apply_header_row(df: pd.DataFrame, header_row: int) -> pd.DataFrame:
        """Apply a new header row from the specified row index."""
        if header_row > 0:
            new_headers = df.iloc[header_row]
            df = df.iloc[header_row + 1:].reset_index(drop=True)
            df.columns = [str(val) for val in new_headers]
        return df
    
    @staticmethod
    def process_data(df: pd.DataFrame, column_state: Dict) -> pd.DataFrame:
        """Process the DataFrame according to column mappings and filters."""
        # Apply filters
        for col, state in column_state.items():
            if state.get('filters'):
                df = df[~df[col].astype(str).isin(state['filters'])]
        
        # Apply column mappings
        mapped_columns = {col: state['map'] for col, state in column_state.items() 
                        if state.get('map')}
        if mapped_columns:
            df = df.rename(columns=mapped_columns)
            
            # Process designator column if present
            if 'designator' in df.columns:
                df['designator'] = df['designator'].str.split(',')
                df = df.explode('designator').reset_index(drop=True)
        
        return df



def create_column_control(col: str, unique_values: list, 
                         current_map: Optional[str] = None, 
                         current_filters: Optional[list] = None) -> html.Div:
    """Create column mapping and filtering controls."""
    # Convert all values to strings for consistent handling
    formatted_values = []
    for val in unique_values:
        if pd.isna(val):
            continue
        if isinstance(val, (int, float)):
            # Format numbers without trailing zeros
            formatted_val = f"{val:g}"
        else:
            formatted_val = str(val)
        formatted_values.append(formatted_val)
    
    # Sort strings naturally (so "2" comes before "10")
    formatted_values.sort()
    
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


# App layout
app.layout = html.Div([
    # File Upload
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    
    # Controls
    html.Div([
        html.Label('Select Header Row:'),
        dcc.Input(
            id='header-row-input',
            type='number',
            min=0,
            value=0,
            style={'marginRight': '10px', 'width': '100px'}
        ),
        html.Button(
            'Apply Header',
            id='apply-header-button',
            n_clicks=0,
            style={'marginRight': '10px'}
        ),
        html.Button(
            'Process Data',
            id='process-button',
            n_clicks=0,
            style={
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'padding': '5px 10px'
            }
        ),
    ], style={'marginBottom': '20px'}),
    
    # Column Controls and Data Display
    html.Div(id='column-controls', style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'}),
    html.Div(id='preview-table', style={'marginTop': '20px'}),
    html.Div(id='output-data-upload', style={'marginTop': '20px'}),
    
    # Store components for state management
    dcc.Store(id='raw-data'),
    dcc.Store(id='column-state')
])

# Callbacks
@callback(
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

    # Handle file upload or header application
    if trigger_id in ['upload-data', 'apply-header-button']:
        if trigger_id == 'upload-data' and contents:
            df, error = DataProcessor.parse_uploaded_file(contents, filename)
            if error:
                return [], html.Div(error), None, None
        elif trigger_id == 'apply-header-button' and stored_data:
            df = pd.read_json(stored_data, orient='split')
            df = DataProcessor.apply_header_row(df, header_row)
        else:
            return [], None, None, None

        # Get unique values for each column
        unique_values = {}
        for col in df.columns:
            # Convert column to series and get unique values
            series = pd.Series(df[col])
            unique_vals = series.drop_duplicates().dropna().tolist()
            unique_values[col] = unique_vals
        
        # Create column controls
        column_controls = [
            create_column_control(
                col,
                unique_values[col],
                current_map=column_state.get(col, {}).get('map'),
                current_filters=column_state.get(col, {}).get('filters')
            ) for col in df.columns
        ]

        # Create preview table
        preview_table = html.Div([
            html.H5('Data Preview'),
            dash_table.DataTable(
                data=df.head(10).to_dict('records'),
                columns=[{'name': str(i), 'id': str(i)} for i in df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'}
            )
        ])

        return column_controls, preview_table, df.to_json(date_format='iso', orient='split'), column_state

    # Handle column mappings and filters
    elif '{' in trigger_id:  # Check if the trigger is from a pattern-matching callback
        try:
            for map_id, map_val, filter_id, filter_val in zip(map_ids, map_values, filter_ids, filter_values):
                col = map_id['index']
                column_state[col] = {
                    'map': map_val,
                    'filters': filter_val or []
                }
        except Exception as e:
            print(f"Error updating column state: {e}")
        return dash.no_update, dash.no_update, dash.no_update, column_state

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@callback(
    Output('output-data-upload', 'children'),
    [Input('process-button', 'n_clicks')],
    [State('raw-data', 'data'),
     State('column-state', 'data')]
)
def process_data_callback(n_clicks, raw_data, column_state):
    """Process the data according to user-specified mappings and filters."""
    if n_clicks == 0 or raw_data is None or not column_state:
        return html.Div()

    df = pd.read_json(raw_data, orient='split')
    processed_df = DataProcessor.process_data(df, column_state)

    return html.Div([
        html.H5('Processed Data'),
        html.Div(f'Total rows: {len(processed_df)}', style={'marginBottom': '10px'}),
        dash_table.DataTable(
            data=processed_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in processed_df.columns],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'}
        )
    ])

if __name__ == '__main__':
    app.run_server(debug=True)