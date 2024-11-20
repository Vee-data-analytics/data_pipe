from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Component, Manufacturer, Category, PhysicalClass

class ComponentResource(resources.ModelResource):
    manufacturer = fields.Field(
        column_name='manufacturer',
        attribute='manufacturer',
        widget=ForeignKeyWidget(Manufacturer, 'name')
    )
    category = fields.Field(
        column_name='Functional Class',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    physical_class = fields.Field(
        column_name='Physical Class',
        attribute='physical_class',
        widget=ForeignKeyWidget(PhysicalClass, 'name')
    )
    mpn = fields.Field(column_name='Part Name', attribute='mpn')
    part_library_name = fields.Field(column_name='Part Library Name', attribute='part_library_name')
    ref = fields.Field(column_name='REF', attribute='ref')
    description = fields.Field(column_name='Description', attribute='description')
    shape_code = fields.Field(column_name='Shape Code', attribute='shape_code')
    length = fields.Field(column_name='L', attribute='length')
    width = fields.Field(column_name='W', attribute='width')
    height = fields.Field(column_name='T', attribute='height')
    supply_type = fields.Field(column_name='Supply Type', attribute='supply_type')
    supply_kind = fields.Field(column_name='Supply Kind', attribute='supply_kind')
    tape_kind = fields.Field(column_name='Tape Kind', attribute='tape_kind')
    tape_width = fields.Field(column_name='Tape Width', attribute='tape_width')
    tape_pitch = fields.Field(column_name='Tape Pitch', attribute='tape_pitch')
    reel_size = fields.Field(column_name='Reel Size', attribute='reel_size')
    part_count = fields.Field(column_name='Part Count', attribute='part_count')
    supply_direction = fields.Field(column_name='Supply Direction', attribute='supply_direction')

    class Meta:
        model = Component
        import_id_fields = ['mpn']
        fields = (
            'manufacturer', 'category', 'physical_class', 'mpn', 'part_library_name',
            'ref', 'description', 'shape_code', 'length', 'width', 'height',
            'supply_type', 'supply_kind', 'tape_kind', 'tape_width', 'tape_pitch',
            'reel_size', 'part_count', 'supply_direction'
        )

    def before_import_row(self, row, **kwargs):
        # If manufacturer is not in the imported data, you might want to set a default
        if 'manufacturer' not in row:
            row['manufacturer'] = 'Unknown Manufacturer'  # Or handle this as appropriate for your use case

    def get_instance(self, instance_loader, row):
        return instance_loader.get_instance(row, ['mpn'])