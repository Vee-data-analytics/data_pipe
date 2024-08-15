from django.urls import path
from . import views
from apps.process_data.views import raw_upload_data

app_name = "customer"

urlpatterns = [
    path("dme_raw", views.uploadlist_dme, name="dme_list"),
    path('view/<int:object_id>/', views.view_uploaded_object, name= 'view_uploaded_object'),
    path('download_object/<int:id>/', views.download_object, name='download_object'),
    path("raw_kaon", views.uploadlist_kaon, name= 'kaon_list'),
    path('raw_path_rout/', raw_upload_data, name='raw_data_rout'),

    #path("<int:pk>/", views.customer_detail, name="detail"),
    #path("create/", views.customer_create, name="create"),
]