import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import io

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
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
    html.Div(id='header-selection-div'),
    html.Div(id='column-selection-div'),
    html.Div(id='output-data-upload'),
    dcc.Store(id='stored-data'),
    dcc.Store(id='processed-data')
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, html.Div(['Unsupported file type.'])
    except Exception as e:
        print(e)
        return None, html.Div(['There was an error processing this file.'])
    return df, None

@app.callback(
    Output('header-selection-div', 'children'),
    Output('stored-data', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_header_selection(contents, filename):
    if contents is not None:
        df, error_message = parse_contents(contents, filename)
        if df is not None:
            options = [{'label': f'Row {i}', 'value': i} for i in range(min(10, len(df)))]
            return (html.Div([
                html.H5('Select Header Row'),
                dcc.Dropdown(id='header-row-dropdown', options=options, value=0),
                html.Button('Apply Header', id='apply-header-button', n_clicks=0)
            ]), df.to_json(date_format='iso', orient='split'))
    return html.Div(), None

@app.callback(
    Output('column-selection-div', 'children'),
    Output('processed-data', 'data'),
    Input('apply-header-button', 'n_clicks'),
    State('stored-data', 'data'),
    State('header-row-dropdown', 'value')
)
def update_column_selection(n_clicks, stored_data, header_row):
    if n_clicks > 0 and stored_data is not None:
        df = pd.read_json(stored_data, orient='split')
        df.columns = df.iloc[header_row]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
        
        # Filter out null values and create column options
        column_options = [{'label': str(col), 'value': str(col)} for col in df.columns if col is not None]
        
        column_selectors = html.Div([
            html.H5('Select and Rename Columns'),
            html.Div([
                html.Label('Designator'),
                dcc.Dropdown(id='designator-column', options=column_options, placeholder='Select column'),
                dcc.Input(id='designator-rename', type='text', placeholder='Rename column (optional)')
            ]),
            html.Div([
                html.Label('Value'),
                dcc.Dropdown(id='value-column', options=column_options, placeholder='Select column'),
                dcc.Input(id='value-rename', type='text', placeholder='Rename column (optional)')
            ]),
            html.Div([
                html.Label('1st Vendor Number/Manufacture Part No'),
                dcc.Dropdown(id='vendor-column', options=column_options, placeholder='Select column'),
                dcc.Input(id='vendor-rename', type='text', placeholder='Rename column (optional)')
            ]),
            html.Div([
                html.Label('Class/Component Class'),
                dcc.Dropdown(id='class-column', options=column_options, placeholder='Select column'),
                dcc.Input(id='class-rename', type='text', placeholder='Rename column (optional)')
            ]),
            html.Button('Apply Column Selection', id='apply-column-button', n_clicks=0)
        ])
        
        return column_selectors, df.to_json(date_format='iso', orient='split')
    return html.Div(), None

@app.callback(
    Output('output-data-upload', 'children'),
    Input('apply-column-button', 'n_clicks'),
    State('processed-data', 'data'),
    State('designator-column', 'value'),
    State('value-column', 'value'),
    State('vendor-column', 'value'),
    State('class-column', 'value'),
    State('designator-rename', 'value'),
    State('value-rename', 'value'),
    State('vendor-rename', 'value'),
    State('class-rename', 'value')
)
def update_output(n_clicks, processed_data, designator_col, value_col, vendor_col, class_col,
                  designator_rename, value_rename, vendor_rename, class_rename):
    if n_clicks > 0 and processed_data is not None:
        df = pd.read_json(processed_data, orient='split')
        
        # Select only the chosen columns
        df = df[[designator_col, value_col, vendor_col, class_col]]
        
        # Rename columns if new names are provided
        new_names = {
            designator_col: designator_rename or 'Designator',
            value_col: value_rename or 'Value',
            vendor_col: vendor_rename or 'Vendor Number',
            class_col: class_rename or 'Component Class'
        }
        df = df.rename(columns=new_names)
        
        # Process the Designator column
        designator_column = new_names[designator_col]
        df[designator_column] = df[designator_column].str.split(',')
        df = df.explode(designator_column)
        
        return html.Div([
            html.H5('Processed Data'),
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                page_size=10,
            ),
            html.Hr(),
        ])
    return html.Div()

if __name__ == '__main__':
    app.run_server(debug=True)