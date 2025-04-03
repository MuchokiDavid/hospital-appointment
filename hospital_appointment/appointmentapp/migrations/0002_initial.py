# Generated by Django 4.2.18 on 2025-04-03 14:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("appointmentapp", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="timeoff",
            name="doctor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="time_offs",
                to="users.doctor",
            ),
        ),
        migrations.AddField(
            model_name="prescription",
            name="medical_record",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="prescription",
                to="appointmentapp.medicalrecord",
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notifications",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="medicalrecord",
            name="appointment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="records",
                to="appointmentapp.appointment",
            ),
        ),
        migrations.AddField(
            model_name="medicalrecord",
            name="doctor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_records",
                to="users.doctor",
            ),
        ),
        migrations.AddField(
            model_name="medicalrecord",
            name="patient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="medical_records",
                to="users.patient",
            ),
        ),
        migrations.AddField(
            model_name="availabilityschedule",
            name="doctor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="availability_schedules",
                to="users.doctor",
            ),
        ),
        migrations.AddField(
            model_name="appointment",
            name="doctor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments",
                to="users.doctor",
            ),
        ),
        migrations.AddField(
            model_name="appointment",
            name="patient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments",
                to="users.patient",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="availabilityschedule",
            unique_together={("doctor", "day_of_week", "start_time", "end_time")},
        ),
        migrations.AlterUniqueTogether(
            name="appointment",
            unique_together={("doctor", "scheduled_time")},
        ),
    ]
