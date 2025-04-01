from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Patient, Doctor, Specialization, 
    AvailabilitySchedule, TimeOff, Appointment,
    MedicalRecord, Prescription, Notification
)


class CustomUserAdmin(UserAdmin):
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


class AvailabilityScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time', 'is_recurring')
    list_filter = ('doctor', 'day_of_week', 'is_recurring')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name')
    date_hierarchy = 'valid_from'


class TimeOffAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'start_datetime', 'end_datetime', 'is_approved')
    list_filter = ('doctor', 'is_approved', 'start_datetime')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 'reason')
    date_hierarchy = 'start_datetime'


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'scheduled_time', 'end_time', 'status')
    list_filter = ('doctor', 'status', 'scheduled_time')
    search_fields = (
        'patient__user__first_name', 'patient__user__last_name',
        'doctor__user__first_name', 'doctor__user__last_name', 'reason'
    )
    raw_id_fields = ('patient', 'doctor')
    date_hierarchy = 'scheduled_time'
    ordering = ('-scheduled_time',)


class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'record_type', 'title', 'date_recorded', 'is_sensitive')
    list_filter = ('record_type', 'is_sensitive', 'date_recorded', 'doctor')
    search_fields = (
        'patient__user__first_name', 'patient__user__last_name',
        'doctor__user__first_name', 'doctor__user__last_name', 'title', 'description'
    )
    raw_id_fields = ('patient', 'doctor', 'appointment')
    date_hierarchy = 'date_recorded'


class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medical_record', 'medication_name', 'dosage', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = (
        'medical_record__patient__user__first_name',
        'medical_record__patient__user__last_name',
        'medication_name'
    )
    raw_id_fields = ('medical_record',)
    date_hierarchy = 'start_date'


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_short', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'message')
    date_hierarchy = 'created_at'
    
    def message_short(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = 'Message'


admin.site.register(User, CustomUserAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Specialization, SpecializationAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(AvailabilitySchedule, AvailabilityScheduleAdmin)
admin.site.register(TimeOff, TimeOffAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(MedicalRecord, MedicalRecordAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(Notification, NotificationAdmin)