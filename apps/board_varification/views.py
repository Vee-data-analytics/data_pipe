from django.shortcuts import render,redirect, get_object_or_404
from .forms import EmployeeForm,ProductForm, CustomerForm, KitInspectionForm, SolderPasteInspectionForm, FirstOffBoardInspectionForm, LastBoardProducedInspectionForm, WastageForm, JobNumberForm
from .models import Employee, Customer, KitInspection, SolderPasteInspection, FirstOffBoardInspection, LastBoardProducedInspection, Wastage, Job_number
from django.shortcuts import render
from .models import Product
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
import pyzbar.pyzbar as pyzbar
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from .models import Employee
from django.views.decorators.http import require_POST
from .models import Employee
from django.contrib.auth.models import User
import json
from django.http import HttpResponse
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
import cv2
from io import BytesIO
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)





def logout_view(request):
    logout(request)
    return redirect('qrcode_scan')


@csrf_exempt
def qrscanner(request):
    if request.method == 'POST':
        logger.debug(f"Received POST request with body: {request.body}")
        try:
            data = json.loads(request.body)
            qr_data = data.get('qrData')
            if not qr_data:
                return JsonResponse({'error': 'No QR data provided'}, status=400)
            
            user_id = int(qr_data)
            user = User.objects.get(pk=user_id)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            redirect_url = reverse('board_varification:form_overview')
            logger.info(f"User {user.username} logged in successfully. Redirecting to {redirect_url}")
            return JsonResponse({'redirect_url': redirect_url})
        
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from request body")
            return JsonResponse({'error': 'Invalid JSON in request'}, status=400)
        except ValueError:
            logger.error(f"Failed to convert QR data to integer: {qr_data}")
            return JsonResponse({'error': 'Invalid QR code format'}, status=400)
        except User.DoesNotExist:
            logger.error(f"No user found with ID: {user_id}")
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            logger.exception("Unexpected error in qrscanner view")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
    else:
        return render(request, 'QR_scanner.html')

        
@login_required
def forms_overview(request):
    employee = request.user.employee
    context = {
        'role': employee.role,
        'is_programmer': employee.role == 'programmer',
        'is_kitter': employee.role == 'kitter',
        'is_setup_operator': employee.role == 'setup_operator',
        'is_qc': employee.role == 'qc',
        'is_paste_inspector': employee.role == 'paste_inspector',
    }
    return render(request, 'form_overview.html', context)




def download_pdf(request, job_number):
    job = Job_number.objects.get(job_number=job_number)
    
    # Render the HTML template with job details
    html_string = render_to_string('job_detail_pdf.html', {'job': job})
    html = HTML(string=html_string)
    
    # Create a BytesIO buffer to receive PDF data
    buffer = BytesIO()
    html.write_pdf(target=buffer)
    
    # FileResponse sets the Content-Disposition header for you
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="job_{job.job_number}.pdf"'
    
    # Close the buffer
    buffer.close()
    
    return response


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('board_varification:product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('board_varification:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'app_name/product_form.html', {'form': form})


# Employee Views
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})

def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('board_varification:employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employee_form.html', {'form': form})

def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee_form.html', {'form': form})

# Customer Views
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('board_varification::customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form})

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('board_varification:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_form.html', {'form': form})

# KitInspection Views
def kit_inspection_list(request):
    kit_inspections = KitInspection.objects.all()
    return render(request, 'kit_inspection_list.html', {'kit_inspections': kit_inspections})

def kit_inspection_update(request, pk):
    kit_inspection = get_object_or_404(KitInspection, pk=pk)
    if request.method == 'POST':
        form = KitInspectionForm(request.POST, request.FILES, instance=kit_inspection)
        if form.is_valid():
            form.save()
            return redirect('board_varification:kit_inspection_list')
    else:
        form = KitInspectionForm(instance=kit_inspection)
    return render(request, 'kit_inspection_form.html', {'form': form})



@login_required
def kit_inspection_create(request):
    if request.method == 'POST':
        form = KitInspectionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('board_varification:kit_inspection_list')
    else:
        user = request.user
        try:
            employee = Employee.objects.get(user=user)
            form = KitInspectionForm(initial={'inspector': employee}, user=request.user)
        except Employee.DoesNotExist:
            form = KitInspectionForm(user=request.user)
    return render(request, 'kit_inspection_form.html', {'form': form})

# SolderPasteInspection Views
def solder_paste_inspection_list(request):
    solder_paste_inspections = SolderPasteInspection.objects.all()
    return render(request, 'solder_paste_inspection_list.html', {'solder_paste_inspections': solder_paste_inspections})


@login_required
def solder_paste_inspection_create(request):
    if request.method == 'POST':
        form = SolderPasteInspectionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('board_varification:solder_paste_inspection_list')
    else:
        # Get the currently logged-in user
        user = request.user
        try:
            employee = Employee.objects.get(user=user)
            form = SolderPasteInspectionForm(initial={'paste_inspector': employee}, user=request.user)
        except Employee.DoesNotExist:
            form = SolderPasteInspectionForm(user=request.user)

    return render(request, 'solder_paste_inspection_form.html', {'form': form})

def solder_paste_inspection_update(request, pk):
    solder_paste_inspection = get_object_or_404(SolderPasteInspection, pk=pk)
    if request.method == 'POST':
        form = SolderPasteInspectionForm(request.POST, request.FILES, instance=solder_paste_inspection)
        if form.is_valid():
            form.save()
            return redirect('board_varification:solder_paste_inspection_list')
    else:
        form = SolderPasteInspectionForm(instance=solder_paste_inspection)
    return render(request, 'solder_paste_inspection_form.html', {'form': form})

# FirstOffBoardInspection Views
def first_off_board_inspection_list(request):
    first_off_board_inspections = FirstOffBoardInspection.objects.all()
    return render(request, 'first_off_board_inspection_list.html', {'first_off_board_inspections': first_off_board_inspections})

@login_required
def first_off_board_inspection_create(request):
    if request.method == 'POST':
        form = FirstOffBoardInspectionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('board_varification:first_off_board_inspection_list')
    else:
        user = request.user
        try:
            employee = Employee.objects.get(user=user)
            form = FirstOffBoardInspectionForm(initial={'inspector': employee}, user=request.user)
        except Employee.DoesNotExist:
            form = FirstOffBoardInspectionForm(user=request.user)
    return render(request, 'first_off_board_inspection_form.html', {'form': form})
    
    
def first_off_board_inspection_update(request, pk):
    first_off_board_inspection = get_object_or_404(FirstOffBoardInspection, pk=pk)
    if request.method == 'POST':
        form = FirstOffBoardInspectionForm(request.POST, request.FILES, instance=first_off_board_inspection)
        if form.is_valid():
            form.save()
            return redirect('board_varification:first_off_board_inspection_list')
    else:
        form = FirstOffBoardInspectionForm(instance=first_off_board_inspection)
    return render(request, 'first_off_board_inspection_form.html', {'form': form})

# LastBoardProducedInspection Views
def last_board_produced_inspection_list(request):
    last_board_produced_inspections = LastBoardProducedInspection.objects.all()
    return render(request, 'last_board_produced_inspection_list.html', {'last_board_produced_inspections': last_board_produced_inspections})

@login_required
def last_board_produced_inspection_create(request):
    if request.method == 'POST':
        form = LastBoardProducedInspectionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('board_varification:last_board_produced_inspection_list')
    else:
        user = request.user
        try:
            employee = Employee.objects.get(user=user)
            form = LastBoardProducedInspectionForm(initial={'inspector': employee}, user=request.user)
        except Employee.DoesNotExist:
            form = LastBoardProducedInspectionForm(user=request.user)
    return render(request, 'last_board_produced_inspection_form.html', {'form': form})
    
def last_board_produced_inspection_update(request, pk):
    last_board_produced_inspection = get_object_or_404(LastBoardProducedInspection, pk=pk)
    if request.method == 'POST':
        form = LastBoardProducedInspectionForm(request.POST, request.FILES, instance=last_board_produced_inspection)
        if form.is_valid():
            form.save()
            return redirect('board_varification:last_board_produced_inspection_list')
    else:
        form = LastBoardProducedInspectionForm(instance=last_board_produced_inspection)
    return render(request, 'last_board_produced_inspection_form.html', {'form': form})

# Wastage Views
def wastage_list(request):
    wastages = Wastage.objects.all()
    return render(request, 'wastage_list.html', {'wastages': wastages})

@login_required
def wastage_create(request):
    if request.method == 'POST':
        form = WastageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('board_varification:wastage_list')
    else:
        user = request.user
        try:
            employee = Employee.objects.get(user=user)
            form = WastageForm(initial={'inspector': employee}, user=request.user)
        except Employee.DoesNotExist:
            form = WastageForm(user=request.user)
    return render(request, 'wastage_form.html', {'form': form})
    
    
def wastage_update(request, pk):
    wastage = get_object_or_404(Wastage, pk=pk)
    if request.method == 'POST':
        form = WastageForm(request.POST, request.FILES, instance=wastage)
        if form.is_valid():
            form.save()
            return redirect('board_varification:wastage_list')
    else:
        form = WastageForm(instance=wastage)
    return render(request, 'wastage_form.html', {'form': form})


from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

@login_required
def job_details(request, job_number):
    job = get_object_or_404(Job_number, job_number=job_number)
    context = {'job': job}

    # Handle the case where the photo field is None for different inspections
    for inspection in job.kitinspection_set.all():
        if inspection.photo:
            inspection.photo_url = inspection.photo.url
        else:
            inspection.photo_url = None

    for inspection in job.solderpasteinspection_set.all():
        if inspection.photo:
            inspection.photo_url = inspection.photo.url
        else:
            inspection.photo_url = None

    for inspection in job.firstoffboardinspection_set.all():
        if inspection.photo:
            inspection.photo_url = inspection.photo.url
        else:
            inspection.photo_url = None

    for inspection in job.lastboardproducedinspection_set.all():
        if inspection.photo:
            inspection.photo_url = inspection.photo.url
        else:
            inspection.photo_url = None

    for wastage in job.wastage_set.all():
        if wastage.photo:
            wastage.photo_url = wastage.photo.url
        else:
            wastage.photo_url = None

    # KitInspection
    kit_inspection = KitInspection.objects.filter(job_no=job, kit_inspector__user=request.user).first()
    kit_inspection_form = handle_inspection_form(request, KitInspectionForm, kit_inspection, job)
    context['kit_inspection_form'] = kit_inspection_form

    # SolderPasteInspection
    solder_paste_inspection = SolderPasteInspection.objects.filter(job_no=job, paste_inspector__user=request.user).first()
    solder_paste_form = handle_inspection_form(request, SolderPasteInspectionForm, solder_paste_inspection, job)
    context['solder_paste_form'] = solder_paste_form

    # FirstOffBoardInspection
    first_off_board_inspection = FirstOffBoardInspection.objects.filter(job_no=job, roaming_qc_name__user=request.user).first()
    first_off_board_form = handle_inspection_form(request, FirstOffBoardInspectionForm, first_off_board_inspection, job)
    context['first_off_board_form'] = first_off_board_form

    # LastBoardProducedInspection
    last_board_produced_inspection = LastBoardProducedInspection.objects.filter(job_no=job, setup_operator_name__user=request.user).first()
    last_board_produced_form = handle_inspection_form(request, LastBoardProducedInspectionForm, last_board_produced_inspection, job)
    context['last_board_produced_form'] = last_board_produced_form

    # Wastage
    wastage = Wastage.objects.filter(job_no=job, kit_inspection__kit_inspector__user=request.user).first()
    wastage_form = handle_inspection_form(request, WastageForm, wastage, job)
    context['wastage_form'] = wastage_form

    return render(request, 'job_detail_pdf.html', context)

def handle_inspection_form(request, form_class, inspection, job):
    if request.method == 'POST':
        if inspection:
            # Update the existing instance if the current user created it
            if inspection.inspector_check(request.user):
                form = form_class(request.POST, request.FILES, instance=inspection)
                if form.is_valid():
                    form.save()
            else:
                # Return an error message if the user trying to update is not the creator
                pass
        else:
            # Create a new instance
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                inspection = form.save(commit=False)
                inspection.job_no = job
                inspection.set_inspector(request.user)
                inspection.save()
    else:
        if inspection:
            form = form_class(instance=inspection)
        else:
            initial_data = {'job_no': job}
            initial_data.update(form_class.get_initial_inspector_data(request.user))
            form = form_class(initial=initial_data)

    return form


def job_number_list(request):
    job_numbers = Job_number.objects.all()
    return render(request, 'job_number_list.html', {'job_numbers': job_numbers})

def job_number_create(request):
    if request.method == 'POST':
        form = JobNumberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('board_varification:job_number_list')
    else:
        form = JobNumberForm()
    return render(request, 'job_number_form.html', {'form': form})

def job_number_update(request, pk):
    job_number = get_object_or_404(Job_number, pk=pk)
    if request.method == 'POST':
        form = JobNumberForm(request.POST, instance=job_number)
        if form.is_valid():
            form.save()
            return redirect('board_varification:job_number_list')
    else:
        form = JobNumberForm(instance=job_number)
    return render(request, 'job_number_form.html', {'form': form})