# Generated by Django 5.1.3 on 2024-12-12 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('measurements', '0003_measurement_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurement',
            name='measurement_file',
            field=models.FileField(blank=True, null=True, upload_to='measurements/'),
        ),
    ]
