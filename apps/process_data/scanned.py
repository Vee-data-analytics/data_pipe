import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from collections import defaultdict
import pandas as pd
import keyboard
import threading

# Initialize the app
app = dash.Dash(__name__)

# Initialize data storage
scan_data = defaultdict(int)
scan_data['scanned'] = 0
scan_data['target'] = 100  # Default target value

# Global variable to stop the scanner thread
stop_thread = False

def listen_for_scans():
    global stop_thread
    while not stop_thread:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN and event.name == 'enter':  # Assuming 'enter' key indicates end of scan
            scan_data['scanned'] += 1
# Start the scanner thread
scanner_thread = threading.Thread(target=listen_for_scans)
scanner_thread.start()

# Layout of the dashboard
app.layout = html.Div([
    html.Div([
        dcc.Input(id='product-input', type='text', placeholder="Enter CustomerName - ProductName - Model", style={'width': '100%'}),
        html.Button('Set Product', id='set-product', n_clicks=0),
        html.H2(id='output-product', children='Enter Product Details Above'),
        dcc.Input(id='target-input', type='number', value=100, min=1, step=1, placeholder="Enter daily target"),
        html.Button('Set Target', id='set-target', n_clicks=0),
        html.Button('Reset Target', id='reset-target', n_clicks=0),
        html.Div(id='output-target', children='Daily Target: 100'),
    ], style={'width': '70%', 'padding': '10px'}),
    dcc.Graph(id='pie-chart', style={'width': '800%'}),
], style={'display': 'flex', 'flex-direction': 'row'})

# Callback to update the product name
@app.callback(
    Output('output-product', 'children'),
    Input('set-product', 'n_clicks'),
    State('product-input', 'value')
)
def update_product_name(n_clicks, value):
    if n_clicks > 0 and value:
        return value
    return 'Enter Product Details Above'

# Callback to update or reset the target
@app.callback(
    [Output('output-target', 'children'), Output('target-input', 'value')],
    [Input('set-target', 'n_clicks'), Input('reset-target', 'n_clicks')],
    [State('target-input', 'value')]
)
def update_or_reset_target(set_n_clicks, reset_n_clicks, value):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'set-target' and value is not None:
        scan_data['target'] = value
        return f'Daily Target: {value}', value
    elif button_id == 'reset-target':
        scan_data['scanned'] = 0
        scan_data['target'] = 100  # Reset to default target value
        return f'Daily Target: {scan_data["target"]}', scan_data['target']

# Callback to update the pie chart
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('set-target', 'n_clicks'), Input('reset-target', 'n_clicks')]
)
def update_chart(set_n_clicks, reset_n_clicks):
    target = scan_data.get('target', 100)
    scanned = scan_data['scanned']
    outstanding = max(target - scanned, 0)

    # Create a dataframe for the pie chart
    df = pd.DataFrame({
        'Category': ['Scanned', 'Outstanding'],
        'Count': [scanned, outstanding]
    })

    # Create the pie chart
    fig = {
        'data': [{
            'labels': df['Category'],
            'values': df['Count'],
            'type': 'pie',
            'marker': {'colors': ['green', 'red']}
        }],
        'layout': {
            'title': f' Target: {target} /Total Scanned: {scanned}',
            'width': 1000,
            'height': 800
        }
    }
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
