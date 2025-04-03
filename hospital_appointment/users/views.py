from django.shortcuts import render
from .models import UserDetails, Doctor, Patient, Specialization
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope,OAuth2Authentication
from django.contrib.auth import login, logout, authenticate
from oauth2_provider.models import AccessToken,  RefreshToken, Application
from oauth2_provider.views.mixins import OAuthLibMixin
from django.contrib import messages
import json
from datetime import datetime, timedelta
import decouple
from .utility import *

client_id= decouple.config('CLIENT_ID')
client_secret= decouple.config('CLIENT_SECRET')
    
class RegisterUser(APIView):
    def post(self, request, format=None):
        try:
            data= request.data
            username= data.get('username')
            password= data.get('password')
            email= data.get('email')
            phone_number= data.get('phone_number')
            user_type= data.get('user_type')
            specialisations= data.get('specializations')
            
            if not username or not password or not email or not phone_number or not user_type:
                return Response({'message': 'Please provide all the required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
            if UserDetails.objects.filter(username=username).exists():
                return Response({'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if UserDetails.objects.filter(email=email).exists():
                return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if UserDetails.objects.filter(phone_number=phone_number).exists():
                return Response({'message': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                saved_user= serializer.save()
                if saved_user:
                    if user_type == 'DOCTOR':
                        if not specialisations:
                            return Response({'message': 'Please provide specializations'}, status=status.HTTP_400_BAD_REQUEST)
                        
                        for spec in specialisations:
                            specialization= Specialization.objects.get(id=spec)
                            if not specialization:
                                return Response({'message': 'Invalid specialization'}, status=status.HTTP_400_BAD_REQUEST)
                            
                            doctor= Doctor.objects.filter(user=saved_user).first()
                            if not doctor:
                                doctor= Doctor.objects.create(user=saved_user, specialization=specialization)
                            doctor.specializations.add(specialization)
                            doctor.save()
                        
                    # elif user_type == 'patient':
                    #     patient= Patient.objects.get(user=saved_user)
                    #     patient.save()
                    
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class Login(APIView):
    def post(self, request, format=None):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response({'message': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(username=username, password=password)
            if not user:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                application = Application.objects.get(client_id=client_id)
            except Application.DoesNotExist:
                return Response({'message': 'Invalid client credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Revoke any existing tokens
            AccessToken.objects.filter(user=user, application=application).delete()
            
            expires = datetime.now() + timedelta(days=1)
            scope = 'read write'
            # Create new access token
            access_token = AccessToken.objects.create(
                user=user,
                application=application,
                token=generate_unique_id(),
                expires=expires,
                scope=scope
            )
            
            # Create refresh token
            refresh_token = RefreshToken.objects.create(
                user=user,
                application=application,
                token=generate_unique_id(),
                access_token=access_token
            )

            login(request, user)
            return Response({
                'access_token': access_token.token,
                'expires_in': 3600,
                'token_type': 'Bearer',
                'scope': access_token.scope,
                'refresh_token': refresh_token.token,
                'user': UserSerializer(user).data
            })
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

class Logout(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]

    def post(self, request, format=None):
        tokens=  AccessToken.objects.filter(user=request.user)
        for token in tokens:
            token.delete()
        
        refresh_tokens=  RefreshToken.objects.filter(user=request.user)
        for token in refresh_tokens:
            token.delete()
                    
        logout(request)
        return Response({'message': 'Logged out successfully'})
    

# Get user list while authenticated-----------------------------------------------
class UserList(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]

    def get(self, request, format=None):
        users = UserDetails.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

# Hospital staff manage user profile------------------------------------------
class StaffViewUserById(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]

    def get(self, request, id, format=None):
        try:
            user= request.user
            if not user:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if user.user_type != 'DOCTOR' and user.user_type != 'ADMIN':
                return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)                            
            
            current_user = UserDetails.objects.get(id=id)
            serializer = UserSerializer(current_user)
            return Response(serializer.data)
        except UserDetails.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, id, format=None):
        try:
            user= request.user
            if not user:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if user.user_type != 'DOCTOR' and user.user_type != 'ADMIN':
                return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

            current_user = UserDetails.objects.get(id=id)
            serializer = UserSerializer(current_user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserDetails.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
class Redirect(APIView):
    def get(self, request, format=None):
        return Response({'message': 'Hospital Appointment System!'})

# Get specializations--------------------------------------------------------------
class GetSpecializationsView(APIView):    
    def get(self, request, format=None):
        try:
            specializations = Specialization.objects.all()
            serializer = SpecializationSerializer(specializations, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#Add specialization -----------------------------------------------------------------
class PostSpecializationView(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]            
    def post(self, request, format=None):
        try:
            data= request.data
            name= data.get('name')
            description= data.get('description')
            if not name or not description:
                return Response({'message': 'Please provide name and description'}, status=status.HTTP_400_BAD_REQUEST)
            specialization= Specialization.objects.create(name=name, description=description)
            specialization.save()
            return Response({'message': 'Specialization created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# Doctor profile view-----------------------------------------------------------------
class DoctorProfileView(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]

    def get(self, request, format=None):
        try:
            current_user= request.user
            doctor= Doctor.objects.filter(user=current_user).first()
            if not doctor:
                return Response({'message': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = DoctorSerializer(doctor)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        try:
            user= request.user
            doctor= Doctor.objects.filter(user=user).first()
            if not doctor:
                return Response({'message': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = DoctorSerializer(doctor, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetDoctorsListView(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]

    def get(self, request, format=None):
        try:
            doctors = Doctor.objects.all()
            serializer = DoctorSerializer(doctors, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Add patient while authenticated as Admin or Doctor-------------------------------
class RegisterPatient(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]
    
    def post(self, request, format=None):
        user= request.user
        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.user_type != 'DOCTOR' and user.user_type != 'ADMIN':
            return Response({'message': 'User is not a doctor or an admin'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.user_type == 'PATIENT':
            return Response({'message': 'User is already a patient'}, status=status.HTTP_400_BAD_REQUEST)
        
        data= request.data
        user_type= 'PATIENT'
        phone_number= data.get('phone_number')
        dob= data.get('date_of_birth')
        email= data.get('email')
        first_name= data.get('first_name')
        last_name= data.get('last_name')
        gender= data.get('gender')
        address= data.get('address')
        insuarance_provider= data.get('insuarance_provider')
        insuarance_policy= data.get('insuarance_policy')
        address= data.get('address')
        emergency_contact_name= data.get('emergency_contact_name')
        emergency_contact_phone= data.get('emergency_contact_phone')
        
        if not phone_number or not email:
            return Response({'message': 'Please provide phone number and email'}, status=status.HTTP_400_BAD_REQUEST)
        
        new_user= UserDetails.objects.create(username=phone_number, 
                                      email=email, 
                                      phone_number=phone_number, 
                                      user_type=user_type,
                                      first_name=first_name,
                                      last_name=last_name,
                                      date_of_birth= dob,
                                      )
        
        patient= None
        if new_user:
            patient= Patient.objects.filter(user=new_user).first()
            patient.gender= gender
            patient.address= address
            patient.emergency_contact_name= emergency_contact_name
            patient.emergency_contact_phone=  emergency_contact_phone
            patient.insurance_policy_number= insuarance_policy
            patient.insurance_provider= insuarance_provider
            patient.save()
            
        res= {'message': 'Patient registered successfully', 'patient': PatientSerializer(patient).data}
        return Response(res, status=status.HTTP_201_CREATED)

#Get all patients ---------------------------------------------------------------------
class PatientListView(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]

    def get(self, request, format=None):
        try:
            patients= Patient.objects.all()
            serializer = PatientSerializer(patients, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Staff manage patient profile--------------------------------------------------------------
class PatientProfileView(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]

    def get(self, request, id, format=None):
        try:
            user= request.user
            if not user:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if user.user_type != 'DOCTOR' and user.user_type != 'ADMIN':
                return Response({'message': 'User is not a doctor or an admin'}, status=status.HTTP_400_BAD_REQUEST)            
            
            patient= Patient.objects.filter(id=id).first()
            if not patient:
                return Response({'message': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = PatientSerializer(patient)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        try:
            user= request.user
            if not user:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if user.user_type != 'DOCTOR' and user.user_type != 'ADMIN':
                return Response({'message': 'User is not a doctor or an admin'}, status=status.HTTP_400_BAD_REQUEST)

            patient= Patient.objects.filter(id=id).first()
            if not patient:
                return Response({'message': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = PatientSerializer(patient, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
