from django.db import models
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class PhysicalClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Component(models.Model):
    mpn = models.CharField(max_length=100, unique=True, verbose_name="Manufacturer Part Number")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    physical_class = models.ForeignKey(PhysicalClass, on_delete=models.CASCADE)
    
    # Common fields
    description = models.TextField(blank=True)
    length = models.FloatField(help_text="Length in mm")
    width = models.FloatField(help_text="Width in mm")
    height = models.FloatField(help_text="Height in mm")
    
    # Machine A specific fields
    part_name = models.CharField(max_length=100, blank=True)
    part_library_name = models.CharField(max_length=100, blank=True)
    ref = models.CharField(max_length=100, blank=True)
    shape_code = models.CharField(max_length=100, blank=True)
    supply_type = models.CharField(max_length=50, blank=True)
    supply_kind = models.CharField(max_length=50, blank=True)
    tape_kind = models.CharField(max_length=50, blank=True)
    tape_width = models.FloatField(null=True, blank=True)
    tape_pitch = models.FloatField(null=True, blank=True)
    reel_size = models.CharField(max_length=50, blank=True)
    part_count = models.IntegerField(null=True, blank=True)
    supply_direction = models.CharField(max_length=50, blank=True)
    
    # Machine B specific fields
    alias = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    groups = models.CharField(max_length=100, blank=True)
    action = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.mpn} - {self.manufacturer.name}"

