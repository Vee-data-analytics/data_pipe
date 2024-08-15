# Generated by Django 4.2.9 on 2024-02-14 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process_data', '0005_alter_processeddatalg_processed_data_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='processeddatacartrack',
            old_name='processed_at',
            new_name='processed',
        ),
        migrations.RenameField(
            model_name='processeddatadme',
            old_name='processed_at',
            new_name='processed_data',
        ),
        migrations.RenameField(
            model_name='processeddatakaon',
            old_name='processed_at',
            new_name='processed_data',
        ),
        migrations.RenameField(
            model_name='uploadedfilecartrack',
            old_name='uploaded_at',
            new_name='uploaded_data',
        ),
        migrations.RenameField(
            model_name='uploadedfiledme',
            old_name='uploaded_at',
            new_name='uploaded_data',
        ),
        migrations.RenameField(
            model_name='uploadedfilekaon',
            old_name='uploaded_at',
            new_name='uploaded_data',
        ),
        migrations.RenameField(
            model_name='uploadedfilelandis',
            old_name='uploaded_at',
            new_name='uploaded_data',
        ),
        migrations.RenameField(
            model_name='uploadedfilelg',
            old_name='uploaded_at',
            new_name='uploaded_data',
        ),
        migrations.AlterField(
            model_name='processeddatadme',
            name='processed_file',
            field=models.FileField(upload_to='data_storage/exports/landis/processed_DME/'),
        ),
    ]
