from django.shortcuts import render
from apps.process_data import models
import pandas as pd
from django_plotly_dash import DjangoDash
import dash as dcc
#import dash_html_components as html
from dash import dash_table
from dash.dependencies import Input, Output,State
from django.shortcuts import render, get_object_or_404
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import pandas as pd
from apps.process_data import models
import zipfile
import io
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404



"""
This part is where the uploaded BOM and pick and place data will be listed in the app. 
Eventually the dirty data will be and the processed data will be in the same section of app just sepaated by a button with in the app
"""

def uploadlist_dme(request):
    
    uploaded_files = models.UploadedFileDME.objects.all().order_by('-uploaded_date')
    processed_files = models.ProcessedDataDME.objects.all().order_by('-processed_date')
    context =  {'uploaded_files': uploaded_files,
                 'objects': processed_files}
    return render(request, "dme/dme_uploaded_files.html", context)



def uploadlist_landis(request):
    bom_data = models.UploadedFileLandis.bom.objects.all()
    pick_n_place = models.UploadedFileLandis.pick_n_place.objects.all()
    objects = {
        bom_data:'bom_data',
        pick_n_place:'pick_n_place'
    }

    return render(request,"landis/dme_upload.html",{objects:"objects"})




def uploadlist_kaon(request,render):
    
    uploaded_files = models.UploadedFileKaon.objects.all().order_by('-uploaded_date')
    processed_files = models.UploadedFileKaon.objects.all().order_by('-processed_date')
    context =  {'uploaded_files': uploaded_files,
                 'objects': processed_files}
    return render(request, "kaon/uploaded_files.html", context)



def uploadlist_cartrack(request,render):
    bom_data = models.UploadedFileCartrack.bom.objects.all()
    pick_n_place = models.UploadedFileCartrack.pick_n_place.objects.all()
    objects = {
        bom_data:'bom_data',
        pick_n_place:'pick_n_place'
    }

    return render(request,"kaon/kaon_upload.html",{objects:"objects"})



"""
this section below if for all the BOM file and PnP objects in a better context
displaying dataframes in a dash data table
"""


def view_uploaded_object(request, object_id):
    object = get_object_or_404(models.UploadedFileDME, id=object_id)
    
    # Read BOM file
    df_bom = pd.read_excel(object.bom.path)
    
    
    # Read Pick and Place file
    # Read Pick and Place file
    df_pnp = pd.read_csv(object.pick_n_place.path, delimiter='\t', encoding='ISO-8859-1')  # Adjust encoding if needed

    
    # Create Dash app for BOM
    app_bom = DjangoDash(f'DataTableBOM_{object_id}')
    create_dash_table_layout(app_bom, df_bom, 'BOM Data')

    # Create Dash app for Pick and Place
    app_pnp = DjangoDash(f'DataTablePnP_{object_id}')
    create_dash_table_layout(app_pnp, df_pnp, 'Pick and Place Data')

    context = {
        'object': object,
        'bom_app_name': f'DataTableBOM_{object_id}',
        'pnp_app_name': f'DataTablePnP_{object_id}',
    }
    
    return render(request, 'dme/view_object.html', context)

def create_dash_table_layout(app, df, title):
    app.layout = html.Div([
        html.H3(title),
        dash_table.DataTable(
            id='data-table',
            columns=[{'name': i, 'id': i} for i in df.columns],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True,
            sort_action="native",
            sort_mode="single",
            filter_action="native",
            page_action='native',
            page_size=20,
            style_table={'height': '500px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '150px', 'maxWidth': '300px'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        ),
    ])

def download_object(request, object_id):
    if request.method == 'GET':
        obj = get_object_or_404(models.UploadedFileDME, id=object_id)
        
        # Create an in-memory zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # Add BOM file to zip
            with obj.bom.open('rb') as bom_file:
                zip_file.writestr(f'{obj.bom.name}', bom_file.read())
            
            # Add Pick and Place file to zip
            with obj.pick_n_place.open('rb') as pnp_file:
                zip_file.writestr(f'{obj.pick_n_place.name}', pnp_file.read())
        
        zip_buffer.seek(0)

        # Create response
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=downloaded_files.zip'

        return response
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
