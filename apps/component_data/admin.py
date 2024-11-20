from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Component, Manufacturer, Category, PhysicalClass
from .resource import ComponentResource

@admin.register(Component)
class ComponentAdmin(ImportExportModelAdmin):
    resource_class = ComponentResource

# Register other models if needed
admin.site.register(Manufacturer)
admin.site.register(Category)
admin.site.register(PhysicalClass)