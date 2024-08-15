from django.db import models
from django.contrib.auth.models import User
from django.utils import timesince
import os 

class Customer(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name


class Job(models.Model):
    job_number = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='jobs')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='jobs')
    
    def __str__(self):
        return f'{self.job_number} - {self.customer.name} - {self.product.name}'

def upload_file_path(instance, filename, file_type):
    customer_name = instance.job.customer.name
    product_name = instance.job.product.name
    job_number = instance.job.job_number
    file_extension = os.path.splitext(filename)[1]
    return f'data_storage/dirty_data/uploads/{customer_name}/{product_name}/{job_number}/{file_type}/{filename}'

def gerber_upload_path(instance, filename):
    return upload_file_path(instance, filename, 'gerb')

def bom_upload_path(instance, filename):
    return upload_file_path(instance, filename, 'excel')

def pick_n_place_upload_path(instance, filename):
    return upload_file_path(instance, filename, 'txt')

class UploadedFiles(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='uploaded_files')
    gerber = models.FileField(upload_to=gerber_upload_path)
    bom = models.FileField(upload_to=bom_upload_path)
    pick_n_place = models.FileField(upload_to=pick_n_place_upload_path)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.job.job_number} - {self.job.customer.name} - {self.job.product.name}'
    

class ProcessedFile(models.Model):
    processed_file = models.FileField(upload_to='processed_files/')
    uploaded_file = models.ForeignKey(UploadedFiles, on_delete=models.CASCADE, related_name='processed_files')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='processed_files')
    revision = models.PositiveIntegerField(default=1)
    processed_date = models.DateTimeField(auto_now_add=True)
