from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


app_name = "board_varification"

urlpatterns = [
    #verify forms and user_authentication
    path('forms/', views.forms_overview, name='form_overview'),
    path('logout/', views.logout_view, name='logout'),
    #path('authenticate-employee/', views.authenticate_employee, name='authenticate_employee'),
    #path('verify-employee-and-redirect/', views.verify_employee_and_redirect, name='verify_employee_and_redirect'),
    #path('verify-qr-code/',views.verify_qr_code, name='verify_qr_code'),
    
    # Employee URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/update/<int:pk>/', views.employee_update, name='employee_update'),

    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/update/<int:pk>/', views.customer_update, name='customer_update'),
    
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    
    # Kit Inspection URLs
    path('kit-inspections/', views.kit_inspection_list, name='kit_inspection_list'),
    path('kit-inspections/create/', views.kit_inspection_create, name='kit_inspection_create'),
    path('kit-inspections/update/<int:pk>/', views.kit_inspection_update, name='kit_inspection_update'),

    # Solder Paste Inspection URLs
    path('solder-paste-inspections/', views.solder_paste_inspection_list, name='solder_paste_inspection_list'),
    path('solder-paste-inspections/create/', views.solder_paste_inspection_create, name='solder_paste_inspection_create'),
    path('solder-paste-inspections/update/<int:pk>/', views.solder_paste_inspection_update, name='solder_paste_inspection_update'),

    # First Off Board Inspection URLs
    path('first-off-board-inspections/', views.first_off_board_inspection_list, name='first_off_board_inspection_list'),
    path('first-off-board-inspections/create/', views.first_off_board_inspection_create, name='first_off_board_inspection_create'),
    path('first-off-board-inspections/update/<int:pk>/', views.first_off_board_inspection_update, name='first_off_board_inspection_update'),

    # Last Board Produced Inspection URLs
    path('last-board-produced-inspections/', views.last_board_produced_inspection_list, name='last_board_produced_inspection_list'),
    path('last-board-produced-inspections/create/', views.last_board_produced_inspection_create, name='last_board_produced_inspection_create'),
    path('last-board-produced-inspections/update/<int:pk>/', views.last_board_produced_inspection_update, name='last_board_produced_inspection_update'),

    # Wastage URLs
    path('wastages/', views.wastage_list, name='wastage_list'),
    path('wastages/create/', views.wastage_create, name='wastage_create'),
    path('wastages/update/<int:pk>/', views.wastage_update, name='wastage_update'),

    # Job Number URLs
    path('job-numbers/', views.job_number_list, name='job_number_list'),
    path('job-numbers/<int:job_number>/download_pdf',views.download_pdf, name='download_pdf'),
    path('job-numbers/<int:job_number>/', views.job_details, name='job_details'),    
    path('job-numbers/create/', views.job_number_create, name='job_number_create'),
    path('job-numbers/update/<int:pk>/', views.job_number_update, name='job_number_update'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 






































'''from .views import (EmployeeRetrieveView, KitInspectionListCreate, SolderPasteInspectionListCreate, 
                    FirstOffBoardInspectionListCreate, LastBoardProducedInspectionListCreate, WastageListCreate)
from .views import EmployeeDetailView



urlpatterns = [
    #path('employees/', EmployeeListCreate.as_view(), name='employee-list-create'),
    path('api/employee/<int:user_id>/', EmployeeRetrieveView.as_view(), name='employee-retrieve'),
    path('api/board_varification/employees/<int:user_id>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('kit-inspections/', KitInspectionListCreate.as_view(), name='kit-inspection-list-create'),
    path('solder-paste-inspections/', SolderPasteInspectionListCreate.as_view(), name='solder-paste-inspection-list-create'),
    path('first-off-board-inspections/', FirstOffBoardInspectionListCreate.as_view(), name='first-off-board-inspection-list-create'),
    path('last-board-produced-inspections/', LastBoardProducedInspectionListCreate.as_view(), name='last-board-produced-inspection-list-create'),
    path('wastages/', WastageListCreate.as_view(), name='wastage-list-create'),
]
'''