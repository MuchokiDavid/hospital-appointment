from django.db import models
from django.utils import timezone
from users.models import Doctor, Patient, UserDetails

class AvailabilitySchedule(models.Model):
    """Doctor's availability schedule"""
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability_schedules')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_recurring = models.BooleanField(default=True)
    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(blank=True, null=True)
    
    class Meta:
        unique_together = ('doctor', 'day_of_week', 'start_time', 'end_time')
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class TimeOff(models.Model):
    """Doctor's time off schedule"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='time_offs')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} off from {self.start_datetime} to {self.end_datetime}"


class Appointment(models.Model):
    """Appointment between patient and doctor"""
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    scheduled_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_time']
        unique_together = ('doctor', 'scheduled_time')  # Prevent double bookings
    
    def __str__(self):
        return f"Appointment: {self.patient.user.get_full_name()} with Dr. {self.doctor.user.get_full_name()} at {self.scheduled_time}"


class MedicalRecord(models.Model):
    """Medical records for patients (Bonus feature)"""
    RECORD_TYPE_CHOICES = (
        ('DIAGNOSIS', 'Diagnosis'),
        ('PRESCRIPTION', 'Prescription'),
        ('TEST_RESULT', 'Test Result'),
        ('TREATMENT', 'Treatment Plan'),
        ('NOTE', 'General Note'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_records')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_recorded = models.DateField(auto_now_add=True, null=True, blank=True)
    file = models.FileField(upload_to='medical_records/', blank=True, null=True)
    is_sensitive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_recorded']
    
    def __str__(self):
        return f"{self.get_record_type_display()} for {self.appointment.patient.user.get_full_name()}"


class Prescription(models.Model):
    """Prescriptions linked to medical records"""
    medical_record = models.OneToOneField(MedicalRecord, on_delete=models.CASCADE, related_name='prescription')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    refills_remaining = models.PositiveIntegerField(default=0)
    instructions = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.medication_name} for {self.medical_record.appointment.patient.user.get_full_name()}"


class Notification(models.Model):
    """System notifications for users"""
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_url = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# from django.contrib.auth.models import AbstractUser
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# class User(AbstractUser):
#     """Custom user model that extends Django's AbstractUser"""
#     USER_TYPE_CHOICES = (
#         ('PATIENT', 'Patient'),
#         ('DOCTOR', 'Doctor'),
#         ('ADMIN', 'Admin'),
#     )
    
#     user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
#     date_of_birth = models.DateField(blank=True, null=True)
#     profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
#     def __str__(self):
#         return f"{self.get_full_name()} ({self.user_type})"
    
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         if instance.user_type == 'PATIENT':
#             Patient.objects.create(user=instance)
#         elif instance.user_type == 'DOCTOR':
#             Doctor.objects.create(user=instance)


# class Patient(models.Model):
#     """Patient profile extending the User model"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='patient_profile')
#     GENDER_CHOICES = (
#         ('M', 'Male'),
#         ('F', 'Female'),
#         ('O', 'Other'),
#         ('U', 'Prefer not to say'),
#     )
    
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
#     emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
#     insurance_provider = models.CharField(max_length=100, blank=True, null=True)
#     insurance_policy_number = models.CharField(max_length=50, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"Patient: {self.user.get_full_name()}"


# class Specialization(models.Model):
#     """Medical specializations for doctors"""
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True, null=True)
    
#     def __str__(self):
#         return self.name


# class Doctor(models.Model):
#     """Doctor profile extending the User model"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='doctor_profile')
#     specializations = models.ManyToManyField(Specialization, related_name='doctors')
#     license_number = models.CharField(max_length=50, unique=True)
#     years_of_experience = models.PositiveIntegerField(blank=True, null=True)
#     hospital_affiliation = models.CharField(max_length=100, blank=True, null=True)
#     biography = models.TextField(blank=True, null=True)
#     consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"Dr. {self.user.get_full_name()}"
