from django.contrib import admin
from django import forms
from .models import (
    Employee,
    KitInspection,
    SolderPasteInspection,
    FirstOffBoardInspection,
    LastBoardProducedInspection,
    Wastage,
    Customer,
    Product,
    Job_number
)

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Job_number)



# Employee Admin
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')
    search_fields = ('name', 'role')

admin.site.register(Employee, EmployeeAdmin)


class KitInspectionAdminForm(forms.ModelForm):
    class Meta:
        model = KitInspection
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(KitInspectionAdminForm, self).__init__(*args, **kwargs)
        # Custom initialization here, if needed

@admin.register(KitInspection)
class KitInspectionAdmin(admin.ModelAdmin):
    form = KitInspectionAdminForm
    list_display = ['customer', 'product', 'quantity', 'kit_inspector', 'barcode_scanning_enabled', 'photo']


# Solder Paste Inspection Admin
class SolderPasteInspectionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'paste_type', 'paste_inspector', 'barcode_scanning_enabled')
    list_filter = ('customer', 'product', 'paste_type', 'paste_inspector')
    search_fields = ('customer', 'product', 'paste_type')
    list_editable = ('barcode_scanning_enabled',)

admin.site.register(SolderPasteInspection, SolderPasteInspectionAdmin)

# First Off Board Inspection Admin
class FirstOffBoardInspectionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'roaming_qc_name', 'barcode_scanning_enabled')
    list_filter = ('customer', 'product', 'roaming_qc_name')
    search_fields = ('customer', 'product')
    list_editable = ('barcode_scanning_enabled',)

admin.site.register(FirstOffBoardInspection, FirstOffBoardInspectionAdmin)

# Last Board Produced Inspection Admin
class LastBoardProducedInspectionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity_produced', 'setup_operator_name', 'barcode_scanning_enabled')
    list_filter = ('customer', 'product', 'setup_operator_name')
    search_fields = ('customer', 'product')
    list_editable = ('barcode_scanning_enabled',)

admin.site.register(LastBoardProducedInspection, LastBoardProducedInspectionAdmin)

# Wastage Admin
class WastageAdmin(admin.ModelAdmin):
    list_display = ('kit_inspection', 'last_board_produced_inspection', 'calculated_wastage')
    list_filter = ('kit_inspection', 'last_board_produced_inspection')
    search_fields = ('kit_inspection__customer', 'last_board_produced_inspection__customer')

admin.site.register(Wastage, WastageAdmin)
