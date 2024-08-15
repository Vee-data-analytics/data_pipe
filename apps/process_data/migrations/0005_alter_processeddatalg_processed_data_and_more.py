# Generated by Django 4.2.9 on 2024-01-24 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process_data', '0004_processeddatalg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processeddatalg',
            name='processed_data',
            field=models.FileField(upload_to='data_storage/exports/lg'),
        ),
        migrations.AlterField(
            model_name='uploadedfilelg',
            name='bom',
            field=models.FileField(upload_to='data_storage/dirty_data/uploads/lg/'),
        ),
        migrations.AlterField(
            model_name='uploadedfilelg',
            name='pick_n_place',
            field=models.FileField(upload_to='data_storage/text_data/uploads/lg/txt/'),
        ),
    ]
