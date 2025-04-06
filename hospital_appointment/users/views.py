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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

client_id= decouple.config('CLIENT_ID')
client_secret= decouple.config('CLIENT_SECRET')
    
class RegisterUser(APIView):
    @swagger_auto_schema(
        operation_summary="Create user account",
        operation_description="Create user account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password', 'email', 'phone_number', 'user_type'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'phone_number': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Phone number in the format +254XXXXXXXXX'
                    ),
                'user_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User type, either DOCTOR or ADMIN',
                    enum=['DOCTOR', 'ADMIN']
                    ),
                'specializations': openapi.Schema(
                    type=openapi.TYPE_ARRAY, 
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='List of specialization IDs, Fetched from specialisation endpoint'
                    )
            },
        ),
        responses={
            201: openapi.Response('User created successfully',
                                  schema=UserSerializer
                                ),
            400: openapi.Response('Bad request'),
            500: openapi.Response('Internal server error')
        },
        tags=["User Accounts"]
    )
    
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
    @swagger_auto_schema(
        operation_summary="Login user",
        operation_description="Login user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response('User logged in successfully',
                                    schema=(openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    required=['username', 'password'],
                                    properties={
                                        'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                                        'expires_in': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'token_type': openapi.Schema(type=openapi.TYPE_STRING),
                                        'scope': openapi.Schema(type=openapi.TYPE_STRING),
                                        'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
                                        'user': openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                                                'user_type': openapi.Schema(type=openapi.TYPE_STRING),
                                            }
                                        )
                                    }
                                  )
                                  ) 
                                ),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        tags=["User Accounts"]
    )
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
    
    @swagger_auto_schema(
        operation_summary="Logout user",
        operation_description="Logout user",
        responses={
            200: openapi.Response('User logged out successfully'),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["User Accounts"]
    )

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
    
    @swagger_auto_schema(
        operation_summary="Get user list",
        operation_description="Get user list",
        responses={
            200: openapi.Response('User list',
                                    schema=openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                                                'user_type': openapi.Schema(type=openapi.TYPE_STRING),
                                            }
                                        )
                                    )
                                ),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["User Accounts"]
    )

    def get(self, request, format=None):
        users = UserDetails.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

# Hospital staff manage user profile------------------------------------------
class StaffViewUserById(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get user by id",
        operation_description="Get user by id",
        responses={
            200: openapi.Response('User',
                                    schema=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                                            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                                            'user_type': openapi.Schema(type=openapi.TYPE_STRING),
                                        }
                                    )
                                ),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["User Accounts"]
    )

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
        
    @swagger_auto_schema(
        operation_summary="Update user by id",
        operation_description="Update user by id",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'user_type': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response('User updated successfully',
                                    schema=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                                            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                                            'user_type': openapi.Schema(type=openapi.TYPE_STRING),
                                        }
                                    )
                                ),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["User Accounts"]
   )
        
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

# Get specializations--------------------------------------------------------------
class GetSpecializationsView(APIView):    
    
    @swagger_auto_schema(
        operation_summary="Get specializations",
        operation_description="Get specializations",
        responses={
            200: openapi.Response('Specializations',
                                    schema=openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                'description': openapi.Schema(type=openapi.TYPE_STRING),
                                            }
                                        )
                                    )
                                ),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        tags=["Specializations"]
    )
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
    
    @swagger_auto_schema(
        operation_summary="Add specialization",
        operation_description="Add specialization",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            201: openapi.Response('Specialization created successfully',SpecializationSerializer),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Specializations"]
    )       
    def post(self, request, format=None):
        try:
            data= request.data
            name= data.get('name')
            description= data.get('description')
            if not name or not description:
                return Response({'message': 'Please provide name and description'}, status=status.HTTP_400_BAD_REQUEST)
            specialization= Specialization.objects.create(name=name, description=description)
            specialization.save()
            return Response({'message': 'Specialization created successfully', 'specialization': SpecializationSerializer(specialization).data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# Doctor profile view-----------------------------------------------------------------
class DoctorProfileView(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get doctor profile",
        operation_description="Get doctor profile",
        responses={
            200: openapi.Response('Doctor profile',DoctorSerializer ),
            400: openapi.Response('Bad request'),
            404: openapi.Response('Doctor not found'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Staff"]
    )

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
        
    @swagger_auto_schema(
        operation_summary="Update doctor profile",
        operation_description="Update doctor profile",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'years_of_experience': openapi.Schema(type=openapi.TYPE_INTEGER),
                'is_available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            }
        ),
        responses={
            200: openapi.Response('Doctor profile updated successfully', DoctorSerializer),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Staff"]
   
    )

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

# Doctors list
class GetDoctorsListView(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get doctors list",
        operation_description="Get doctors list",
        responses={
            200: openapi.Response('Doctors list', DoctorSerializer(many=True)),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Staff"]
    )

    def get(self, request, format=None):
        try:
            doctors = Doctor.objects.all()
            serializer = DoctorSerializer(doctors, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#Doctor by id---------------------------------------------------------------------
class GetDoctorByIdView(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get doctor by id",
        operation_description="Get doctor by id",
        responses={
            200: openapi.Response('Doctor', DoctorSerializer),
            400: openapi.Response('Bad request'),
            404: openapi.Response('Doctor not found'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Staff"]
   )

    def get(self, request, id, format=None):
        try:
            doctor = Doctor.objects.get(id=id)
            serializer = DoctorSerializer(doctor)
            return Response(serializer.data)
        except Doctor.DoesNotExist:
            return Response({'message': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

# Add patient while authenticated as Admin or Doctor-------------------------------
class RegisterPatient(APIView):
    authentication_classes= [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope,  IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Register patient",
        operation_description="Register patient",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'gender': openapi.Schema(type=openapi.TYPE_STRING),
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                'insuarance_provider': openapi.Schema(type=openapi.TYPE_STRING),
                'insuarance_policy': openapi.Schema(type=openapi.TYPE_STRING),
                'emergency_contact_name': openapi.Schema(type=openapi.TYPE_STRING),
                'emergency_contact_phone': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            201: openapi.Response('Patient registered successfully', PatientSerializer),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Patients"]
    
    )
    
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
    
    @swagger_auto_schema(
        operation_summary="Get patients list",
        operation_description="Get patients list",
        responses={
            200: openapi.Response('Patients list', PatientSerializer(many=True)),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Patients"]
    )

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
    
    @swagger_auto_schema(
        operation_summary="Get patient profile",
        operation_description="Get patient profile",
        responses={
            200: openapi.Response('Patient profile', PatientSerializer),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Patients"])

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
        
    @swagger_auto_schema(
        operation_summary="Update patient profile",
        operation_description="Update patient profile",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'gender': openapi.Schema(type=openapi.TYPE_STRING),
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                'insuarance_provider': openapi.Schema(type=openapi.TYPE_STRING),
                'insuarance_policy': openapi.Schema(type=openapi.TYPE_STRING),
                'emergency_contact_name': openapi.Schema(type=openapi.TYPE_STRING),
                'emergency_contact_phone': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response('Patient profile updated successfully', PatientSerializer),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Patients"])

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
        
#  Patient search view  ----------------------------------------------------------------------------------
class PatientSearchView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Search patients",
        operation_description="Search patients",
        responses={
            200: openapi.Response('Patients list', PatientSerializer(many=True)),
            400: openapi.Response('Bad request'),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error')
        },
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                description="Bearer token for authentication"
            )
        ],
        tags=["Patients"]
    )

    def get(self, request):
        try:
            search_term = request.query_params.get('q', '')
            
            patients = Patient.objects.filter(
                models.Q(user__first_name__icontains=search_term) |
                models.Q(user__last_name__icontains=search_term) |
                models.Q(user__email__icontains=search_term) |
                models.Q(user__phone_number__icontains=search_term)
            )[:15]
            
            serializer = PatientSerializer(patients, many=True)
            return Response(serializer.data) 
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
