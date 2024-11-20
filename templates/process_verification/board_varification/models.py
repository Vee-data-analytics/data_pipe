from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import os
from django.conf import settings
from django.utils.deconstruct import deconstructible



class Customer(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Job_number(models.Model):
    job_number = models.IntegerField(null=False, default = 0 , unique=True, primary_key=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_number} ({self.date})"


@deconstructible
class UploadToPathAndRename(object):
    def __init__(self, path):
        self.sub_path = path
        
    def __call__(self, instance, filename):
        extention = filename.split('.')[-1]
        filename = '{}.{}'.format(instance.job_no.job_number, extention)
        return '{}/{}/{}'.format(self.sub_path,instance.job_no.job_number, filename)

class Product(models.Model):
    customer = models.ForeignKey(Customer, related_name='products', on_delete=models.CASCADE)
    job_no = models.ForeignKey(Job_number, null=True, on_delete=models.CASCADE)
    product_ID = models.CharField(max_length=255, default='default_value')
    rev_number = models.CharField(max_length=15, default='default_value')

    def __str__(self):
        return f"{self.product_ID} {self.rev_number} ({self.customer.name})"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('kitter', 'Kitter'),
        ('setup_operator', 'Setup Operator'),
        ('programmer', 'Programmer'),
        ('paste_inspector', 'Paste Inspector'),
        ('qc', 'Quality Control'),
    ]
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='employee_qr_codes/', blank=True, null=True)
    def __str__(self):
        return self.name



    def generate_qr_code(self):
        filename = f'{self.user.username}_qr.png'
        filepath = os.path.join(settings.BASE_DIR, 'employee_qr_codes', filename)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(str(self.user.id))
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        with open(filepath, 'wb') as f:
            img.save(f, format='PNG')

        # Save the file path to the qr_code field
        self.qr_code.name = os.path.join('employee_qr_codes', filename)
        


class KitInspection(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='kit_inspections')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='kit_inspections')
    quantity = models.IntegerField()
    kit_inspector = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='kit_inspections')
    barcode_scanning_enabled = models.BooleanField(default=True)
    photo = models.ImageField(upload_to=UploadToPathAndRename('kit_inspection_photos'), blank=True, null=True)    
    job_no = models.ForeignKey(Job_number, null=True, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.kit_inspector.name} ({self.kit_inspector.role}) - Job No. {self.job_no.job_number}"


class SolderPasteInspection(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='solder_paste_inspections')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='solder_paste_inspections')
    paste_type = models.CharField(max_length=100)
    paste_inspector = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='solder_paste_inspections')
    barcode_scanning_enabled = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='solder_paste_inspection_photos/', blank=True, null=True)
    job_no = models.ForeignKey(Job_number, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.paste_inspector.name} ({self.paste_inspector.role}) - Job No. {self.job_no.job_number}"


class FirstOffBoardInspection(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='first_off_board_inspections')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='first_off_board_inspections')
    roaming_qc_name = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='first_off_board_inspections')
    barcode_scanning_enabled = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='first_off_board_inspection_photos/', blank=True, null=True)
    job_no = models.ForeignKey(Job_number, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.roaming_qc_name.name} ({self.roaming_qc_name.role}) - Job No. {self.job_no.job_number}"



class LastBoardProducedInspection(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='last_board_produced_inspections')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='last_board_produced_inspections')
    quantity_produced = models.IntegerField()
    setup_operator_name = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='last_board_produced_inspections')
    barcode_scanning_enabled = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='last_board_produced_inspection_photos/', blank=True, null=True)
    job_no = models.ForeignKey(Job_number, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.setup_operator_name.name} ({self.setup_operator_name.role}) - Job No. {self.job_no.job_number}"


class Wastage(models.Model):
    name = models.CharField(max_length=12, null = True)
    kit_inspection = models.ForeignKey(KitInspection, on_delete=models.CASCADE)
    last_board_produced_inspection = models.ForeignKey(LastBoardProducedInspection, on_delete=models.CASCADE)
    calculated_wastage = models.IntegerField()
    photo = models.ImageField(upload_to='wastage_photos/', blank=True, null=True)
    job_no = models.ForeignKey(Job_number,null=True ,on_delete=models.CASCADE)  # Assuming you want to track wastage by Job_number as well
    
    def __str__(self):
        return f"{self.kit_inspection.kit_inspector.name} ({self.kit_inspection.kit_inspector.role}) - Job No. {self.job_no.job_number}"
