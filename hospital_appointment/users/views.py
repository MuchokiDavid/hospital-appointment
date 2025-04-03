from django.shortcuts import render
from .models import User, Doctor, Patient, Specialization
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
            
            if User.objects.filter(username=username).exists():
                return Response({'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=email).exists():
                return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(phone_number=phone_number).exists():
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
    
class GetSpecializationsView(APIView):    
    def get(self, request, format=None):
        try:
            specializations = Specialization.objects.all()
            serializer = SpecializationSerializer(specializations, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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

class RegisterPatient(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Create your views here.
class UserList(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
class Redirect(APIView):
    def get(self, request, format=None):
        return Response({'message': 'Hello World!'})