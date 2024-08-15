from django.db import models
from django.core.files import File
import os


class DME_Bom_prooceeding(models.Model):
    bom = models.FileField(upload_to='data_storage/dirty_data/uploads/DME/excel/')

class UploadedFileLandis(models.Model):
    bom = models.FileField(upload_to='data_storage/dirty_data/uploads/landis/')
    pick_n_place = models.FileField(upload_to='data_storage/text_data/uploads/landis/txt/')
    uploaded_data = models.DateTimeField(auto_now_add=True)


class UploadedFileDME(models.Model):
    bom = models.FileField(upload_to='data_storage/dirty_data/uploads/DME/excel/')
    pick_n_place = models.FileField(upload_to='data_storage/dirty_text/uploads/DME/txt/')
    uploaded_date = models.DateTimeField(auto_now_add=True)

class ProcessedDataDME(models.Model):
    uploaded_file = models.ForeignKey(UploadedFileDME, on_delete=models.CASCADE)
    processed_file = models.FileField(upload_to='data_storage/exports/dme/processed_DME/')
    processed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return os.path.splitext(os.path.basename(self.uploaded_file.bom.name))[0]

class UploadedFileCartrack(models.Model):
    bom = models.FileField(upload_to='data_storage/dirty_data/uploads/cartrack/excel/')
    pick_n_place = models.FileField(upload_to='data_storage/dirty_text/uploads/cartrack/txt/')
    uploaded_data = models.DateTimeField(auto_now_add=True)

class ProcessedDataCartrack(models.Model):
    uploaded_file = models.ForeignKey(UploadedFileCartrack, on_delete=models.CASCADE)
    processed_file = models.FileField(upload_to='data_storage/exports/landis/processed_landis/')
    processed_date = models.DateTimeField(auto_now_add=True)

class UploadedFileKaon(models.Model):
    bom = models.FileField(upload_to='data_storage/dirty_data/uploads/Kaon/excel/')
    pick_n_place = models.FileField(upload_to='data_storage/uploads/dirty_text/kaon/html/')
    uploaded_date = models.DateTimeField(auto_now_add=True)

class ProcessedDataKaon(models.Model):
    uploaded_file = models.ForeignKey(UploadedFileKaon, on_delete=models.CASCADE)
    processed_file = models.FileField(upload_to='data_storage/exports/kaon/processed_KAON/')
    processed_date = models.DateTimeField(auto_now_add=True)


class UploadedFileLG(models.Model):
    bom = models.FileField(upload_to='data_storage/dirty_data/uploads/lg/')
    pick_n_place = models.FileField(upload_to='data_storage/text_data/uploads/lg/txt/')
    uploaded_date = models.DateTimeField(auto_now_add=True)

class ProcessedDataLG(models.Model):
    uploaded_file = models.ForeignKey(UploadedFileLG, on_delete=models.CASCADE)
    processed_data = models.FileField(upload_to='data_storage/exports/lg')

    def __str__(self):
        return os.path.splitext(os.path.basename(self.uploaded_file.bom.name))[0]