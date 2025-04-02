from .models import *
from rest_framework import serializers
# from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'date_of_birth', 'profile_picture', 'password']
        extra_kwargs = {'password': {'write_only': True},
                        'email': {"required": True},
                        'user_type': {"required": True},
                        'phone_number': {"required": True},
                        'username': {"required": True},
                    }
        
    # Function to harsh password
    def create(self, validated_data):
        password=validated_data.pop('password', None)
        instance= self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Patient
        fields = ['id', 'user', 'gender', 'address', 'emergency_contact_name', 'emergency_contact_phone', 'insurance_provider', 'insurance_policy_number', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        
class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description']
        read_only_fields = ['created_at', 'updated_at']
        
class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = SpecializationSerializer(many=True, read_only=True)
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specializations', 'license_number', 'years_of_experience', 'hospital_affiliation', 'biography', 'consultation_fee', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']