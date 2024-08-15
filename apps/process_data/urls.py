from django.urls import path
from . import views
# from . import data_table
 
app_name = 'processing_data'

urlpatterns = [
    
    #production directories
    path('process-data/lg/', views.process_data, name='process_data'),
    path('process-data/dme/', views.process_data_dme, name = 'process_dme'),
    path('process-data/dme-bom/', views.upload_bom_file, name = 'process_dme_bom'),
    path('process-data/kaon/',views.process_data_kaon, name='process_kaon'),
    path('process-data/landis/',views.process_data_landis, name='process_landis'),
    path('process-data/dme/dir', views.process_data_page_dme,name='process_dme_dir'),
    path('process-data-page/', views.process_data_page, name='process_data_page'),
    path('objects/', views.list_objects, name='list_objects'),
    path('objects/dme/', views.list_objects_dme, name='list_objects_dme'),
  
  
    #Raw data 
    path('view_object_dme/<int:id>/', views.list_objects_dme, name='raw_view_object_dme'),
    path('download_object/<int:id>/', views.raw_download_object, name='raw_download_object'),
    path('delete_object/<int:id>/', views.raw_delete_object, name='raw_delete_object'),
    path('edit_object/<int:id>/', views.raw_edit_object, name='raw_edit_object'),
    path('raw_path_rout/',views.raw_upload_data, name='raw_data_rout'),

    #processed data 
    path('data-processing/objects/list', views.processed_data_route, name='processed_data_route'),
    path('download/<int:object_id>/', views.download_object, name='download_object'),
    path('edit/<int:object_id>/', views.edit_object, name='edit_object'),
    path('delete/<int:object_id>/', views.delete_object, name='delete_object'),
    path('objects/<int:object_id>/', views.view_object, name='view_object'),
    path('objects-dme/<int:object_id>',views.view_object_dme, name='view_object_dme'),
]

