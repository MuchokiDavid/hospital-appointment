# Generated by Django 4.2.18 on 2025-04-05 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("appointmentapp", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="medicalrecord",
            name="patient",
        ),
    ]
