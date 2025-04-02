from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# class CustomUserManager(UserManager):
#     def _create_user(self, email, password, **extra_fields):
#         if not email:
#             raise ValueError("Invalid email provided")
        
#         email= self.normalize_email(email)
#         user= self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)

#         return user
    
#     def create_user(self, email=None, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', False)
#         extra_fields.setdefault('is_superuser', False)    
#         return self._create_user(email, password, **extra_fields)
    
#     def create_superuser(self, email=None, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser',True)
#         return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Custom user model that extends Django's AbstractUser"""
    USER_TYPE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # objects= CustomUserManager()
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'PATIENT':
            Patient.objects.create(user=instance)
        elif instance.user_type == 'DOCTOR':
            Doctor.objects.create(user=instance)


class Patient(models.Model):
    """Patient profile extending the User model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='patient_profile')
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Prefer not to say'),
    )
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"


class Specialization(models.Model):
    """Medical specializations for doctors"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Doctor(models.Model):
    """Doctor profile extending the User model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='doctor_profile')
    specializations = models.ManyToManyField(Specialization, related_name='doctors')
    license_number = models.CharField(max_length=50, unique=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    hospital_affiliation = models.CharField(max_length=100, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"