from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML
from .models import Employee, KitInspection, Customer, Product, SolderPasteInspection, FirstOffBoardInspection, LastBoardProducedInspection, Wastage, Job_number
from django.contrib.auth.models import User
from .models import Employee
from django.contrib.auth.models import Group


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Employee Details',
                Field('user', css_class='form-control'),
                Field('name', css_class='form-control'),
                Field('role', css_class='form-control'),
                Field('photo', css_class='form-control'),
            ),
            HTML('<br>'),
            Div(
                HTML('<button type="submit" class="btn btn-primary">Submit</button>'),
                css_class='d-grid gap-2',
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        if user and Employee.objects.filter(user=user).exists():
            raise forms.ValidationError('An employee for this user already exists.')
        return cleaned_data

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Customer Details',
                Field('name', css_class='form-control'),
                Field('details', css_class='form-control'),
            ),
            HTML('<br>'),
            Div(
                HTML('<button type="submit" class="btn btn-primary">Submit</button>'),
                css_class='d-grid gap-2',
            ),
        )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Product Details',
                Field('customer', css_class='form-control'),
                Field('job_no', css_class='form-control'),
                Field('product_ID', css_class='form-control'),
                Field('rev_number', css_class='form-control'),
            ),
            HTML('<br>'),
            Div(
                HTML('<button type="submit" class="btn btn-primary">Submit</button>'),
                css_class='d-grid gap-2',
            ),
        )


class KitInspectionForm(forms.ModelForm):
    inspector = forms.ModelChoiceField(queryset=Employee.objects.none(), required=True)

    class Meta:
        model = KitInspection
        fields = '__all__'
        exclude = ['kit_inspector']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Kit Inspection Details',
                Field('customer', css_class='form-control'),
                Field('product', css_class='form-control'),
                Field('quantity', css_class='form-control'),
                Field('kit_inspector', css_class='form-control'),
                Field('barcode_scanning_enabled', css_class='form-check-input'),
                Field('photo', css_class='form-control'),
                Field('job_no', css_class='form-control'),
            ),
            HTML('<br>'),
            Div(
                HTML('<button type="submit" class="btn btn-primary">Submit</button>'),
                css_class='d-grid gap-2',
            ),
        )
        # Set the initial value of the inspector field
        if self.user:
            employee = Employee.objects.get(user=self.user)
            self.fields['inspector'].initial = employee

        # Set the queryset for the inspector field
        if self.user:
            employee = Employee.objects.get(user=self.user)
            self.fields['inspector'].queryset = Employee.objects.filter(pk=employee.pk)
        else:
            self.fields['inspector'].queryset = Employee.objects.none()

        # Make the inspector field read-only for non-admin users
        if self.user is not None:
            if not (self.user.is_superuser or self.user.groups.filter(name='admin').exists()):
                self.fields['inspector'].disabled = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.kit_inspector = self.cleaned_data.get('inspector')
        if commit:
            instance.save()
        return instance

    
    @classmethod
    def get_initial_inspector_data(cls, user):
        try:
            employee = Employee.objects.get(user=user)
            return {'kit_inspector':employee}
        except Employee.DoesNotExist:
            return{}
            
        
        
        
class SolderPasteInspectionForm(forms.ModelForm):
    inspector = forms.ModelChoiceField(queryset=Employee.objects.none(), required=True)

    class Meta:
        model = SolderPasteInspection
        fields = '__all__'
        exclude = ['paste_inspector']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Solder Paste Inspection Details',
                Field('customer', css_class='form-control'),
                Field('product', css_class='form-control'),
                Field('paste_type', css_class='form-control'),
                Field('paste_inspector', css_class='form-control'),
                Field('barcode_scanning_enabled', css_class='form-check-input'),
                Field('photo', css_class='form-control'),
                Field('job_no', css_class='form-control'),
            ),
            HTML('<br>'),
            Div(
                HTML('<button type="submit" class="btn btn-primary">Submit</button>'),
                css_class='d-grid gap-2',
            ),
        )
        

        # Set the initial value of the inspector field
        if self.user:
            employee = Employee.objects.get(user=self.user)
            self.fields['inspector'].initial = employee

        # Set the queryset for the inspector field
        if self.user:
            employee = Employee.objects.get(user=self.user)
            self.fields['inspector'].queryset = Employee.objects.filter(pk=employee.pk)
        else:
            self.fields['inspector'].queryset = Employee.objects.none()

        # Make the inspector field read-only for non-admin users
        if self.user is not None:
            if not (self.user.is_superuser or self.user.groups.filter(name='admin').exists()):
                self.fields['inspector'].disabled = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.paste_inspector = self.cleaned_data.get('inspector')
        if commit:
            instance.save()
        return instance
        
    @classmethod
    def get_initial_inspector_data(cls, user):
        try:
            employee = Employee.objects.get(user=user)
            return {'paste_inspector':employee}
        except Employee.DoesNotExist:
            return{}

        
        
class FirstOffBoardInspectionForm(forms.ModelForm):
    inspector = forms.ModelChoiceField(queryset=Employee.objects.none(), required=True)

    class Meta:
        model = FirstOffBoardInspection
        fields = '__all__'
        exclude = ['roaming_qc_name']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'First Off Board Inspection Details',
                Field('customer', css_class='form-control'),
                Field('product', css_class='form-control'),
                Field('roaming_qc_name', css_class='form-control'),
                Field('barcode_scanning_enabled', css_class='form-check-input'),
                Field('photo', css_class='form-control'),
                Field('job_no', css_class='form-control'),
            ),
            HTML('<br>'),
            Div(
                HTML('<button type="submit" class="btn btn-primary">Submit</button>'),
                css_class='d-grid gap-2',
            ),
        )
        # Set the initial value of the inspector field
        if self.user:
            employee = Employee.objects.get(user=self.user)
            self.fields['inspector'].initial = employee

        # Set the queryset for the inspector field
        if self.user:
            employee = Employee.objects.get(user=self.user)
            self.fields['inspector'].queryset = Employee.objects.filter(pk=employee.pk)
        else:
            self.fields['inspector'].queryset = Employee.objects.none()

        # Make the inspector field read-only for non-admin users
        if self.user is not None:
            if not (self.user.is_superuser or self.user.groups.filter(name='admin').exists()):
                self.fields['inspector'].disabled = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.roaming_qc_name = self.cleaned_data.get('inspector')
        if commit:
            instance.save()
        return instance

    @classmethod
    def get_initial_inspector_data(cls, user):
        try:
            employee = Employee.objects.get(user=user)
            return {'roaming_qc_name':employee}
        except Employee.DoesNotExist:
            return{}

class LastBoardProducedInspectionForm(forms.ModelForm):
    inspector = forms.ModelChoiceField(queryset=Employee.objects.none(), required=True)

    class Meta:
        model = LastBoardProducedInspection
        fields = '__all__'
        exclude = ['setup_operator']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Last Board Produced Inspection Details',
                Field('customer', css_class='form-control'),
                Field('product', css_class='form-control'),
                Field('quantity_produced', css_class='form-control'),
                Field('setup_operator_name', css_class='form-control'),
                Field('barcode_scanning_enabled', css_class='form-check-input'),
                Field('photo', css_class='form-control'),
                Field('job_no', css_class='form-control'),
            ),
            HTML('<br>'),
            Div(
                HTML('<button type="submit" class="btn btn-primary">Submit</button>'),
                css_class='d-grid gap-2',
            ),
        )

       # Set the initial value of the inspector field
        if self.user:
            employee = Employee.objects.get(user=self.user)
            self.fields['inspector'].initial = employee

        # Set the queryset for the inspector field
        if self.user:
            employee = Employee.objects.get(user=self.user)
            self.fields['inspector'].queryset = Employee.objects.filter(pk=employee.pk)
        else:
            self.fields['inspector'].queryset = Employee.objects.none()

        # Make the inspector field read-only for non-admin users
        if self.user is not None:
            if not (self.user.is_superuser or self.user.groups.filter(name='admin').exists()):
                self.fields['inspector'].disabled = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.setup_operator = self.cleaned_data.get('inspector')
        if commit:
            instance.save()
        return instance
        
    @classmethod
    def get_initial_inspector_data(cls, user):
        try:
            employee = Employee.objects.get(user=user)
            return {'setup_operator':employee}
        except Employee.DoesNotExist:
            return{}

                
class WastageForm(forms.ModelForm):
    class Meta:
        model = Wastage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Wastage Details',
                Field('name', css_class='form-control'),
                Field('kit_inspection', css_class='form-control'),
                Field('last_board_produced_inspection', css_class='form-control'),
                Field('calculated_wastage', css_class='form-control'),
                Field('photo', css_class='form-control'),
                Field('job_no', css_class='form-control'),
            ),
            HTML('<br>'),
            Div(
                HTML('<button type="submit" class="btn btn-primary">Submit</button>'),
                css_class='d-grid gap-2',
            ),
        )
    @classmethod
    def get_initial_inspector_data(cls, user):
        try:
            employee = Employee.objects.get(user=user)
            return {'kit_inspector':employee}
        except Employee.DoesNotExist:
            return{}

class JobNumberForm(forms.ModelForm):
    class Meta:
        model = Job_number
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Job Number Details',
                Field('job_number', css_class='form-control'),
            ),
            HTML('<br>'),
            Div(
                HTML('<button type="submit" class="btn btn-primary">Submit</button>'),
                css_class='d-grid gap-2',
            ),
        )