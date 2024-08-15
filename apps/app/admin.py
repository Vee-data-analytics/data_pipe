from django.contrib import admin
from .models import ProcessedFile, UploadedFiles, Job, Customer, Customer, Product, Product

admin.site.register(ProcessedFile)
admin.site.register(UploadedFiles)
admin.site.register(Job)
admin.site.register(Customer)
admin.site.register(Product)

