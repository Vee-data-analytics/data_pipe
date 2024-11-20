from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from .data_processing import process_uploaded_files
from .forms import  UploadDataForm,UploadBomDataForm
from .forms import UploadDataForm2
from dash.exceptions import PreventUpdate
from .process_dme import process_data_and_merge
from .process_kaon import process_data_merge
from .process_landis import process_landis
from .bom_process_dme import process_xlsx_file_bom
import pandas as pd
from django.core.files import File
from . import models
import datetime
from django.http import FileResponse
import dash
from celery import shared_task
import base64
import io
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from dash import dash_table
import pandas as pd
from django_plotly_dash import DjangoDash
from django.http import JsonResponse
import pandas as pd
from django.views.decorators.csrf import csrf_protect
import os
import dash as dcc
#import dash_html_components as html
from dash import dash_table
from dash.dependencies import Input, Output,State
import pandas as pd
from dash.exceptions import PreventUpdate
import logging
from django.conf import settings
from django.contrib import messages



logger = logging.getLogger(__name__)



def process_data_page(request):
    return render(request, 'process_data_page.html')

def raw_upload_data(request):
    return render(request, 'raw_data_dir.html')

def process_data_page_dme(request):
    return render(request, 'dme/dme_dir.html')


def processed_data_route(request):
    return render(request, 'processed_list.html')

def list_objects(request):
    objects = models.ProcessedDataLG.objects.all()
    return render(request, 'transactions.html', {'objects': objects})


def list_uploaded_files(request):
    files = models.UploadedFileDME.objects.all()
    return render(request, 'uploaded_files.html', {'files': files})


@shared_task
def cleanup_nonexistent_files():
    all_objects = models.ProcessedDataDME.objects.all()
    for obj in all_objects:
        file_path = os.path.join(settings.MEDIA_ROOT, str(obj.processed_file))
        if not os.path.exists(file_path):
            obj.delete()

def list_objects_dme(request):
    all_objects = models.ProcessedDataDME.objects.all()
    existing_objects = []

    for obj in all_objects:
        file_path = os.path.join(settings.MEDIA_ROOT, str(obj.processed_file))
        if os.path.exists(file_path):
            existing_objects.append(obj)
        else:
            # Optionally, you can delete the database entry if the file doesn't exist
            obj.delete()

    return render(request, 'dme/transactions.html', {'objects': existing_objects})

def raw_download_object(request, object_id):
    if request.method == 'GET':
        object = get_object_or_404(models.UploadedFileDME, id=object_id)
        
        file_obj = object.processed_file.open()
        response = HttpResponse(file_obj.read(), content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename={object.processed_file.name}'
        return response
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def raw_edit_object(request, object_id):
    object = get_object_or_404(models.UploadedFileDME, id=object_id)
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        if not new_name:
            return JsonResponse({'success': False, 'error': 'No new name provided'})

        old_file_path = object.processed_file.name
        new_file_path = os.path.join(os.path.dirname(old_file_path), new_name)

        # Check if file with the new name already exists
        if default_storage.exists(new_file_path):
            return JsonResponse({'success': False, 'error': 'File with this name already exists'})

        # Save the file with the new name
        file_content = object.processed_file.file.read()
        default_storage.delete(old_file_path)
        default_storage.save(new_file_path, file_content)
        
        # Update the database record
        object.processed_file.name = new_file_path
        object.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



def raw_delete_object(request, object_id):
    object = get_object_or_404(models.UploadedFileDME, id=object_id)
    
    if request.method == 'POST':
        default_storage.delete(object.processed_file.name)
        object.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})







def download_object(request, object_id):
    if request.method == 'GET':
        object = get_object_or_404(models.ProcessedDataDME, id=object_id)
        
        file_obj = object.processed_file.open()
        response = HttpResponse(file_obj.read(), content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename={object.processed_file.name}'
        return response
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def edit_object(request, object_id):
    object = get_object_or_404(models.ProcessedDataDME, id=object_id)
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        if not new_name:
            return JsonResponse({'success': False, 'error': 'No new name provided'})

        old_file_path = object.processed_file.name
        new_file_path = os.path.join(os.path.dirname(old_file_path), new_name)

        # Check if file with the new name already exists
        if default_storage.exists(new_file_path):
            return JsonResponse({'success': False, 'error': 'File with this name already exists'})

        # Save the file with the new name
        file_content = object.processed_file.file.read()
        default_storage.delete(old_file_path)
        default_storage.save(new_file_path, file_content)
        
        # Update the database record
        object.processed_file.name = new_file_path
        object.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_object(request, object_id):
    object = get_object_or_404(models.ProcessedDataDME, id=object_id)
    
    if request.method == 'POST':
        default_storage.delete(object.processed_file.name)
        object.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

app = DjangoDash("DataTableApp")

def view_object(request, object_id):
    object = models.ProcessedDataLG.objects.get(id=object_id)
    df = pd.read_csv(object.processed_data.path)
    
    data_table_columns = [{'name': i, 'id': i} for i in df.columns]

    app.layout = html.Div([
        dash_table.DataTable(
        id='data-table',
        columns=data_table_columns,
        data=df.to_dict('records'),
        editable=True,
        row_deletable=True,
        sort_action="native",
        sort_mode="single",
        filter_action="native",
        page_action='none',
        style_table={'height': '1000px', 'overflowY': 'auto'},
        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '300px', 'maxWidth': '300px'},
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


    return render(request, 'data_table.html', {'object_id': object_id})







def view_object_dme(request, object_id):
    object = models.ProcessedDataDME.objects.get(id=object_id)
    original_df = pd.read_csv(object.processed_file.path)
    data_table_columns = [{'name': i, 'id': i} for i in original_df.columns]

    app.layout = html.Div([
        dash_table.DataTable(
            id='data-table',
            columns=data_table_columns,
            data=original_df.to_dict('records'),
            editable=True,
            row_deletable=True,
            sort_action="native",
            sort_mode="single",
            filter_action="native",
            page_action='none',
            style_table={'height': '600px', 'overflowY': 'auto', 'border': '1px solid #ddd', 'padding': '10px'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'font-size': '14px'},
            style_header={'backgroundColor': '#f0f0f0', 'fontWeight': 'bold', 'color': '#333', 'border-bottom': '1px solid #ddd'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f8f8'},
                {'if': {'column_id': 'Designator'}, 'minWidth': '100px', 'width': '150px', 'maxWidth': '150px'},
                {'if': {'column_id': 'Value'}, 'minWidth': '200px', 'width': '250px', 'maxWidth': '250px'},
                # Add more conditional styles for other columns as needed
            ]
        ),
        html.Div([
            html.Button("Save Changes", id="save-changes")
        ], style={'display': 'inline-block'})
    ])

    @app.callback(
        Output('data-table', 'data'),
        Input('save-changes', 'n_clicks'),
        State('data-table', 'data'),
        prevent_initial_call=True,
    )
    def save_changes(n_clicks, updated_data):
        if n_clicks is None:
            raise PreventUpdate
        updated_df = pd.DataFrame(updated_data)
        updated_df.to_csv(object.processed_file.path, index=False)
        return updated_data

    return render(request, 'data_table.html', {'object_id': object_id})


def view_object_dme(request, object_id):
    object = models.ProcessedDataDME.objects.get(id=object_id)
    original_df = pd.read_csv(object.processed_file.path)
    data_table_columns = [{'name': i, 'id': i} for i in original_df.columns]

    app.layout = html.Div([
        dash_table.DataTable(
            id='data-table',
            columns=data_table_columns,
            data=original_df.to_dict('records'),
            editable=True,
            row_deletable=True,
            sort_action="native",
            sort_mode="single",
            filter_action="native",
            page_action='none',
            style_table={'height': '600px', 'overflowY': 'auto', 'border': '1px solid #ddd', 'padding': '10px'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'font-size': '14px'},
            style_header={'backgroundColor': '#f0f0f0', 'fontWeight': 'bold', 'color': '#333', 'border-bottom': '1px solid #ddd'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f8f8'},
                {'if': {'column_id': 'Designator'}, 'minWidth': '100px', 'width': '150px', 'maxWidth': '150px'},
                {'if': {'column_id': 'Value'}, 'minWidth': '200px', 'width': '250px', 'maxWidth': '250px'},
                # Add more conditional styles for other columns as needed
            ]
        ),
        html.Div([
            html.Button("Save Changes", id="save-changes")
        ], style={'display': 'inline-block'})
    ])

    @app.callback(
        Output('data-table', 'data'),
        Input('save-changes', 'n_clicks'),
        State('data-table', 'data'),
        prevent_initial_call=True,
    )
    def save_changes(n_clicks, updated_data):
        if n_clicks is None:
            raise PreventUpdate
        updated_df = pd.DataFrame(updated_data)
        updated_df.to_csv(object.processed_file.path, index=False)
        return updated_data

    return render(request, 'data_table.html', {'object_id': object_id})

def upload_bom_file(request):
    form = UploadBomDataForm()
    if request.method == 'POST':
        form = UploadBomDataForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['dirty_excel_file']
            if uploaded_file.name.endswith('.xlsx'):
                data = form.cleaned_data['dirty_excel_file']
                result = process_xlsx_file_bom(data)
                response = HttpResponse(content_type='application/vnd.ms-excel')

                # Extract the base name of the uploaded_file without extension
                base_name = os.path.splitext(os.path.basename(uploaded_file.name))[0]

                # Use the base name for the filename in the Content-Disposition header
                response['Content-Disposition'] = f'attachment; filename={base_name}.xlsx'
                result.to_excel(response)
                return response
    return render(request, 'dme/bom_pro.html', {'form': form})


@csrf_protect
def process_data(request):
    df_result = None
    export_path = None

    if request.method == 'POST':
        upload_form = UploadDataForm(request.POST, request.FILES)
        if upload_form.is_valid():
            text_file = upload_form.cleaned_data['dirty_txt_file']
            excel_file = upload_form.cleaned_data['dirty_excel_file']
    
            uploaded_file = models.UploadedFileLG.objects.create(
                bom=File(excel_file),
                pick_n_place=File(text_file)
            )
    
            df_result = process_uploaded_files(uploaded_file)
            return render(request, 'result.html', {'df_result': df_result, 'export_path': export_path})

    else:
        upload_form = UploadDataForm()

    return render(request, 'process_data.html', {'upload_form': upload_form})




def process_data_dme(request):
    if request.method == 'POST':
        form = UploadDataForm(request.POST, request.FILES)
        if form.is_valid():
            dirty_text_file = request.FILES['dirty_txt_file']
            dirty_excel_file = request.FILES['dirty_excel_file']

            uploaded_file = models.UploadedFileDME.objects.create(
                bom=File(dirty_excel_file),
                pick_n_place=File(dirty_text_file)
            )
    
            try:
                df_result = process_data_and_merge(uploaded_file)
                messages.success(request, 'Data processed successfully.')
                
                # Convert DataFrame to a list of dictionaries for easy rendering
                result_data = df_result.to_dict('records')

                # Get the export path from the ProcessedDataDME instance
                processed_data = models.ProcessedDataDME.objects.filter(uploaded_file=uploaded_file).last()
                export_path = processed_data.processed_file.path if processed_data else None

                return render(request, 'dme/result.html', {
                    'result_data': result_data, 'export_path': export_path
                })
            except Exception as e:
                messages.error(request, f'Data processing failed: {e}')
                return render(request, 'dme/process_data.html', {'form': form})
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = UploadDataForm()

    return render(request, 'dme/process_data.html', {'form': form})


def process_data_kaon(request):
    df_result = None
    export_path = None

    if request.method == 'POST':
        form = UploadDataForm2(request.POST, request.FILES)
        if form.is_valid():
            dirty_html = request.FILES['dirty_html']
            dirty_excel_file = request.FILES['dirty_excel_file']
            try:
                uploaded_file = models.UploadedFileKaon.objects.create(
                    bom=dirty_excel_file,
                    pick_n_place=dirty_html
                )

                df_result = process_data_merge(uploaded_file)
                messages.success(request, 'Data processed successfully.')

                bom_file_name = os.path.splitext(os.path.basename(uploaded_file.bom.name))[0]
                now = datetime.datetime.now()
                timestamp = now.strftime('%Y%m%d%H%M%S')
                export_path = f'data_storage/exports/kaon/{bom_file_name}_processed_{timestamp}.csv'

                return render(request, 'kaon/result.html', {
                    'df_result': df_result.to_dict('records'),  # Pass DataFrame as a list of dictionaries
                    'export_path': export_path
                })
            except Exception as e:
                logger.error(f"Data processing failed: {e}", exc_info=True)
                messages.error(request, f'Data processing failed: {e}')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = UploadDataForm2()

    return render(request, 'kaon/process_data.html', {'form': form})



def process_data_landis(request):
    df_result = None
    export_path = None

    if request.method == 'POST':
        upload_form = UploadDataForm(request.POST, request.FILES)
        if upload_form.is_valid():
            dirty_text_file = request.FILES['dirty_txt_file']
            dirty_excel_file = request.FILES['dirty_excel_file']

            # Process and merge the data
            df_result, export_path = process_landis(dirty_text_file, dirty_excel_file)

            return render(request, 'landis/result.html', {'df_result': df_result, 'export_path': export_path})

    else:
        upload_form = UploadDataForm()

    return render(request, 'landis/process_data.html', {'upload_form': upload_form})






