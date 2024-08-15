# forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit


class UploadDataForm(forms.Form):
    dirty_txt_file = forms.FileField(
        label='Upload Text File (.txt)',
        help_text='Select a Text file to upload (.txt format)',
        widget=forms.ClearableFileInput(attrs={'accept': '.txt'}),
    )

    dirty_excel_file = forms.FileField(
        label='Upload Excel File (.xlsx)',
        help_text='Select an Excel file to upload (.xlsx format)',
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'}),
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.add_input(Submit('submit', 'Process Data'))





class UploadDataForm2(forms.Form):
    dirty_html = forms.FileField(
        label='Upload Htm File (.htm/.html)',
        help_text='Select an Htm file to upload (.htm/.html format)',
        widget=forms.ClearableFileInput(attrs={'accept': '.htm,.html'})
    )
    dirty_excel_file = forms.FileField(
        label='Upload Excel File (.xlsx)',
        help_text='Select an Excel file to upload (.xlsx format)',
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'})
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('dirty_html'),
        Field('dirty_excel_file'),
        Submit('submit', 'Process Data')
    )


class UploadBomDataForm(forms.Form):
    dirty_excel_file = forms.FileField(
        label='Upload Excel File (.xlsx)',
        help_text='Select an Excel file to upload (.xlsx format)',
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'}),
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.add_input(Submit('submit', 'Process Data'))