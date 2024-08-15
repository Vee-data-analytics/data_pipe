import pandas as pd
import io
import base64
import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import datetime
import logging
from itertools import zip_longest

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app.layout = html.Div([
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
        multiple=True
    ),
    html.Div([
        html.P("Select Header Row"),
        dcc.Dropdown(id='header-row-dropdown', options=[{'label': str(i), 'value': i} for i in range(1, 11)]),
        html.Button(id="apply-header-row", children="Apply Header Row")
    ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),
    html.Div([
        html.Button(id="filter-button", children="Apply Filter")
    ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),
    html.Div(id='output-datatable'),
    dcc.Store(id='stored-data', data=None),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        logging.error(f"Error processing file {filename}: {e}")
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        html.P("Insert X axis data"),
        dcc.Dropdown(id='xaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),
        html.P("Insert Y axis data"),
        dcc.Dropdown(id='yaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),
        html.Hr(),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=15
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr(),
    ])

@app.callback(
    Output('stored-data', 'data'),
    [Input('upload-data', 'contents'),
     Input('apply-header-row', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('header-row-dropdown', 'value')]
)
def store_uploaded_data(contents, n_clicks, filename, header_row):
    if contents is None or filename is None:
        return None

    data = []
    for content, name in zip(contents, filename):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in name:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in name:
                df = pd.read_excel(io.BytesIO(decoded))
            data.append(df)
        except Exception as e:
            logging.error(f"Error processing file {name}: {e}")
            return None

    try:
        combined_data = pd.concat(data, ignore_index=True)
        if header_row is not None and header_row > 0:
            combined_data.columns = combined_data.iloc[header_row - 1]
            combined_data = combined_data.iloc[header_row:, :]
        return combined_data.to_dict('records')
    except Exception as e:
        logging.error(f"Error combining data: {e}")
        return None

def generate_options(column):
    try:
        if isinstance(column, pd.Series):
            unique_values = column.dropna().unique()
        elif isinstance(column, pd.DataFrame):
            unique_values = column.dropna().iloc[:, 0].unique()
        else:
            logging.error(f"Unsupported data type for column: {type(column)}")
            return []

        return [{'label': str(value), 'value': value} for value in unique_values]
    except Exception as e:
        logging.error(f"Error generating options for column: {e}")
        return []

def transform_location(df):
    try:
        df["Location"] = df["Location"].str.replace(' ', ',')
        df["Location"] = df["Location"].str.split(",")
        df["Location"] = df["Location"].explode()
    except Exception as e:
        logging.error(f"Error transforming location: {e}")
    return df

def generate_data_table(data):
    header = [html.Tr([html.Th(col) for col in data.columns])]
    dropdown_row = html.Tr([
        html.Th(dcc.Dropdown(
            id={'type': 'dynamic-dropdown', 'index': idx},
            options=[
                {'label': 'Component ID', 'value': 'component_id'},
                {'label': 'Sorting', 'value': 'sorting'},
                {'label': 'Location', 'value': 'location'},
                {'label': 'Unused', 'value': 'unused'}
            ],
            value='',
            placeholder='Select an option'
        ))
        for idx, col in enumerate(data.columns)
    ])
    header.append(dropdown_row)
    body = [html.Tr([html.Td(data.iloc[i][col]) for col in data.columns]) for i in range(len(data))]
    data_table = dbc.Table(
        [html.Thead(header), html.Tbody(body)],
        bordered=True,
        striped=True,
        hover=True
    )
    return data_table

@app.callback(
    Output('output-datatable', 'children'),
    [Input('stored-data', 'data'),
     Input('filter-button', 'n_clicks')],
    [State({'type': 'dynamic-dropdown', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'filter-dropdown', 'index': dash.dependencies.ALL}, 'value')],
    prevent_initial_call=True
)
def update_output(stored_data, n_clicks, dynamic_values, filter_values):
    if stored_data is None:
        return "Drag and Drop or Upload a file"

    try:
        data = pd.DataFrame(stored_data)
    except Exception as e:
        logging.error(f"Error creating DataFrame from stored data: {e}")
        return "Error processing data"

    # Apply transformations based on dynamic dropdown selections
    for idx, dropdown_value in enumerate(dynamic_values):
        if dropdown_value == 'location':
            try:
                data = transform_location(data)
            except Exception as e:
                logging.error(f"Error applying transformation for location: {e}")

    # Apply filters based on filter dropdown selections
    filtered_data = data.copy()
    for idx, filter_value in enumerate(filter_values):
        if filter_value:
            filtered_data = filtered_data[filtered_data.iloc[:, idx].isin(filter_value)]

    # Generate the header with filter dropdowns
    header = [html.Tr([html.Th(html.Div([col, dcc.Dropdown(
        id={'type': 'filter-dropdown', 'index': idx},
        options=generate_options(filtered_data[col]),
        multi=True,
        value=filter_values[idx] if filter_values else None,
        placeholder=f'Filter by {col}'
    )], style={'position': 'relative'})) for idx, col in enumerate(filtered_data.columns)])]

    body = [html.Tr([html.Td(filtered_data.iloc[i][col]) for col in filtered_data.columns]) for i in range(len(filtered_data))]
    data_table = dbc.Table(
        [html.Thead(header), html.Tbody(body)],
        bordered=True,
        striped=True,
        hover=True
    )
    return data_table

if __name__ == '__main__':
    app.run_server(debug=True)


"""
import pandas as pd
import io
import base64
import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import datetime
import logging

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app.layout = html.Div([
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
        multiple=True
    ),
    html.Div([
        html.P("Select Header Row"),
        dcc.Dropdown(id='header-row-dropdown', options=[{'label': str(i), 'value': i} for i in range(1, 11)]),
        html.Button(id="apply-header-row", children="Apply Header Row")
    ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),
    html.Div([
        html.Button(id="filter-button", children="Apply Filter")
    ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),
    html.Div(id='output-datatable'),
    dcc.Store(id='stored-data', data=None),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        logging.error(f"Error processing file {filename}: {e}")
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        html.P("Insert X axis data"),
        dcc.Dropdown(id='xaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),
        html.P("Insert Y axis data"),
        dcc.Dropdown(id='yaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),
        html.Hr(),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=15
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr(),
    ])

def generate_options(column):
    try:
        if isinstance(column, pd.Series):
            unique_values = column.dropna().unique()
        elif isinstance(column, pd.DataFrame):
            unique_values = column.dropna().iloc[:, 0].unique()
        else:
            logging.error(f"Unsupported data type for column: {type(column)}")
            return []

        return [{'label': str(value), 'value': value} for value in unique_values]
    except Exception as e:
        logging.error(f"Error generating options for column: {e}")
        return []

@app.callback(
    Output('stored-data', 'data'),
    [Input('upload-data', 'contents'),
     Input('apply-header-row', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('header-row-dropdown', 'value')]
)
def store_uploaded_data(contents, n_clicks, filename, header_row):
    if contents is None or filename is None:
        return None

    data = []
    for content, name in zip(contents, filename):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in name:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in name:
                df = pd.read_excel(io.BytesIO(decoded))
            data.append(df)
        except Exception as e:
            logging.error(f"Error processing file {name}: {e}")
            return None

    try:
        combined_data = pd.concat(data, ignore_index=True)
        if header_row is not None and header_row > 0:
            combined_data.columns = combined_data.iloc[header_row - 1]
            combined_data = combined_data.iloc[header_row:, :]
        return combined_data.to_dict('records')
    except Exception as e:
        logging.error(f"Error combining data: {e}")
        return None

@app.callback(
    Output('output-datatable', 'children'),
    [Input('stored-data', 'data'),
     Input({'type': 'filter-dropdown', 'index': dash.dependencies.ALL}, 'value'),
     Input('filter-button', 'n_clicks')],
    prevent_initial_call=True
)
def update_output(stored_data, filter_values, n_clicks):
    if stored_data is None:
        return "Drag and Drop or Upload a file"

    try:
        data = pd.DataFrame(stored_data)
    except Exception as e:
        logging.error(f"Error creating DataFrame from stored data: {e}")
        return "Error processing data"

    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    filtered_data = data.copy()
    if triggered_id == 'filter-button':
        for idx, filter_value in enumerate(filter_values):
            if filter_value:
                try:
                    filtered_data = filtered_data[filtered_data.iloc[:, idx].isin(filter_value)]
                except Exception as e:
                    logging.error(f"Error applying filter: {e}")
                    return "Error applying filter"

    header = [html.Tr([html.Th(html.Div([col, dcc.Dropdown(
        id={'type': 'filter-dropdown', 'index': idx},
        options=generate_options(filtered_data[col]),
        multi=True,
        value=filter_values[idx] if filter_values else None,
        placeholder=f'Filter by {col}'
    )], style={'position': 'relative'})) for idx, col in enumerate(filtered_data.columns)])]
    body = [html.Tr([html.Td(filtered_data.iloc[i][col]) for col in filtered_data.columns]) for i in range(len(filtered_data))]
    data_table = dbc.Table(
        [html.Thead(header), html.Tbody(body)],
        bordered=True,
        striped=True,
        hover=True
    )
    return data_table

if __name__ == '__main__':
    app.run_server(debug=True)
    """