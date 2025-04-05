from rest_framework import serializers
from .models import *
from users.serializers import *

class AvailabilityScheduleSerializer(serializers.ModelSerializer):
    doctor= DoctorSerializer(read_only=True)
    class Meta:
        model = AvailabilitySchedule
        fields= ['id', 'doctor', 'day_of_week', 'start_time', 'end_time', 'is_recurring', 'valid_from', 'valid_until']
        
class TimeOffSerializer(serializers.ModelSerializer):
    doctor= DoctorSerializer
    class Meta:
        model= TimeOff
        fields= ['id', 'doctor', 'start_datetime', 'end_datetime', 'reason', 'is_approved', 'created_at', 'updated_at']
        read_only_fields= ['created_at', 'updated_at']
        
    # def validate(self, data):
    #     if data['start_datetime'] >= data['end_datetime']:
    #         raise serializers.ValidationError("End datetime must be after start datetime")
    #     if data['start_datetime'] < timezone.now():
    #         raise serializers.ValidationError("Cannot create time off in the past")
    #     return data
    
class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor',
                 'scheduled_time', 'end_time', 'status', 'reason', 'notes',
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    # def validate(self, data):
    #     if data['scheduled_time'] >= data['end_time']:
    #         raise serializers.ValidationError("End time must be after scheduled time")
        
    #     # Check for overlapping appointments
    #     if Appointment.objects.filter(
    #         doctor=data['doctor'],
    #         scheduled_time__lt=data['end_time'],
    #         end_time__gt=data['scheduled_time']
    #     ).exists():
    #         raise serializers.ValidationError("This appointment overlaps with an existing one")
            
    #     return data


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    appointment= AppointmentSerializer(read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = ['id', 'patient', 'doctor',
                 'appointment', 'record_type', 'title',
                 'description', 'date_recorded', 'file', 'is_sensitive',
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        if 'file' in data and data['file'] and data['file'].size > 10*1024*1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB")
        return data
    
class PrescriptionSerializer(serializers.ModelSerializer):
    medical_record= MedicalRecordSerializer(read_only=True)
    
    class Meta:
        model = Prescription
        fields = ['id', 'medical_record', 'medication_name',
                 'dosage', 'frequency', 'start_date', 'end_date',
                 'refills_remaining', 'instructions']
    
    def validate(self, data):
        if 'end_date' in data and data['end_date'] and data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data

    
class NotificationSerializer(serializers.ModelSerializer):
    user= UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read',
                 'created_at', 'related_url']
        read_only_fields = ['created_at']