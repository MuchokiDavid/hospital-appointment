from django.contrib import admin
from .models import Patient, Doctor, Specialization, UserDetails
from django.contrib.auth.admin import UserAdmin

# Register your models here.

# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
#     list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
#     search_fields = ('username', 'email', 'first_name', 'last_name')
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'user_type', 'phone_number', 'date_of_birth', 'profile_picture')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'user_type', 'phone_number', 'date_of_birth', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'insurance_provider', 'created_at')
    list_filter = ('gender', 'insurance_provider', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'insurance_provider', 'insurance_policy_number')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'


class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'consultation_fee', 'years_of_experience')
    list_filter = ('specializations', 'years_of_experience')
    search_fields = ('user__first_name', 'user__last_name', 'license_number', 'hospital_affiliation')
    filter_horizontal = ('specializations',)
    raw_id_fields = ('user',)



admin.site.register(UserDetails, CustomUserAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Specialization, SpecializationAdmin)
admin.site.register(Doctor, DoctorAdmin)
