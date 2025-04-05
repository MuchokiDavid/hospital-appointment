from django.shortcuts import render
from .serializers import *
from .models import *
from .utility import parse_datetime
from users.models import UserDetails,Doctor,Patient,Specialization
from users.serializers import UserSerializer,DoctorSerializer,PatientSerializer,SpecializationSerializer
from rest_framework.views import APIView
from decouple import config
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework.permissions import TokenHasReadWriteScope, OAuth2Authentication
from django.shortcuts import get_object_or_404, get_list_or_404
from time import gmtime, strftime
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

# Create your views here.

# Get and POST availability schedule view by an authenticated doctor---------------------------------------------------------------
class AvailabilityScheduleView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    authentication_classes = [OAuth2Authentication]

    def get(self, request):
        user= request.user
        if not user:
            return Response({'message': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)
        
        if user.user_type not in ['DOCTOR', 'ADMIN']:
            return Response({'message': 'Only doctors or admins can perform this action'}, 
                          status=http_status.HTTP_403_FORBIDDEN)
        
        current_doctor = Doctor.objects.filter(user=user).first()
        if not current_doctor:
            return Response({'message': 'Doctor not found'}, status=http_status.HTTP_404_NOT_FOUND)
        
        availability = AvailabilitySchedule.objects.filter(doctor_id=current_doctor.id).all()
        serializer = AvailabilityScheduleSerializer(availability, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            user= request.user
            if not user:
                return Response({'message': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)
            if user.user_type not in ['DOCTOR', 'ADMIN']:
                return Response({'message': 'Only doctors or admins can perform this action'}, 
                          status=http_status.HTTP_403_FORBIDDEN)
            
            # Get the doctor instance
            doctor= Doctor.objects.filter(user=user).first()
            if not doctor:
                return Response({'message': 'Doctor not found'}, status=http_status.HTTP_404_NOT_FOUND)
            
            # Request data
            day_of_week = request.data.get('day_of_week') # e.g 0:Monday,1:Tuesday etc.
            start_time = request.data.get('start_time')
            end_time = request.data.get('end_time')
            is_recurring = request.data.get('is_recurring', True)
            valid_from = request.data.get('valid_from')
            valid_until = request.data.get('valid_until')
            
            if self.check_availability( doctor, day_of_week, start_time, end_time ):
                return Response({'message': 'Doctor is already scheduled for this time'}, status=http_status.HTTP_400_BAD_REQUEST)
            
            # Creteate the availability schedule
            availability_schedule = AvailabilitySchedule(
                doctor=doctor,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                is_recurring=is_recurring,
                valid_from=valid_from,
                valid_until=valid_until
            )
            availability_schedule.save()
            
            serializer = AvailabilityScheduleSerializer(availability_schedule)
            return Response(serializer.data, status=http_status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'message': str(e)}, status=http_status.HTTP_400_BAD_REQUEST)
        
    def check_availability(self, doctor, day_of_week, start_time, end_time):
        # Check if the doctor is already scheduled for the given time
        return AvailabilitySchedule.objects.filter(
            doctor_id=doctor.id,
            day_of_week=day_of_week,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        
# Doctor put/delete availability schedule view----------------------------------------------------------------------------------
class AvailabilityScheduleUpdateView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    authentication_classes = [OAuth2Authentication]

    def put(self, request, id):
        availability_schedule = get_object_or_404(AvailabilitySchedule, id=id)
        serializer = AvailabilityScheduleSerializer(availability_schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        availability_schedule = get_object_or_404(AvailabilitySchedule, id=id)
        availability_schedule.delete()
        return Response(status=http_status.HTTP_204_NO_CONTENT)
        
#Get all availability schedule view--------------------------------------------------------------- 
class GetAllAvailabilityScheduleView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    authentication_classes = [OAuth2Authentication]

    def get(self, request):
        availability = AvailabilitySchedule.objects.all()
        serializer = AvailabilityScheduleSerializer(availability, many=True)
        return Response(serializer.data)
    
# Doctor manage time off view----------------------------------------------------------------------------------
class TimeOffView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    authentication_classes = [OAuth2Authentication]

    def get(self, request):
        try:
            user= request.user
            if not user:
                return Response({'message': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)

            if user.user_type not in ['DOCTOR', 'ADMIN']:
                return Response({'message': 'Only doctors or admins can perform this action'}, 
                            status=http_status.HTTP_403_FORBIDDEN)

            current_doctor = Doctor.objects.filter(user=user).first()
            if not current_doctor:
                return Response({'message': 'Doctor not found'}, status=http_status.HTTP_404_NOT_FOUND)

            time_off = TimeOff.objects.filter(doctor=current_doctor).order_by('-start_datetime')
            serializer = TimeOffSerializer(time_off, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=http_status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            user= request.user
            if not user:
                return Response({'message': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)
            if user.user_type not in ['DOCTOR', 'ADMIN']:
                return Response({'message': 'Only doctors or admins can perform this action'}, 
                            status=http_status.HTTP_403_FORBIDDEN)

            # Get the doctor instance
            doctor= Doctor.objects.filter(user=user).first()
            if not doctor:
                return Response({'message': 'Doctor not found'}, status=http_status.HTTP_404_NOT_FOUND)

            # Request data
            start_datetime = request.data.get('start_datetime')
            end_datetime = request.data.get('end_datetime')
            reason = request.data.get('reason')
            is_approved = request.data.get('is_approved', False)
            
            if not start_datetime or not end_datetime:
                return Response({'message': 'Start and end datetime are required'},
                            status=http_status.HTTP_400_BAD_REQUEST)
                
            if not reason:
                return Response({'message': 'Reason is required'},
                            status=http_status.HTTP_400_BAD_REQUEST)
            
            # Parse datetime strings
            try:
                start_datetime = parse_datetime(start_datetime)
                end_datetime = parse_datetime(end_datetime)
            except ValueError as e:
                return Response({'message': str(e)}, 
                            status=http_status.HTTP_400_BAD_REQUEST)

            # Validate time off period
            validation_error = self.validate_time_off(start_datetime, end_datetime)
            if validation_error:
                return Response({'message': validation_error}, 
                            status=http_status.HTTP_400_BAD_REQUEST)
            
            # Check for overlapping time off periods
            if self.has_time_off_conflict(doctor, start_datetime, end_datetime):
                return Response({'message': 'Time off conflicts with existing time off'}, status=http_status.HTTP_400_BAD_REQUEST)
            
            time_off = TimeOff.objects.create(
                doctor=doctor,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                reason=reason,
                is_approved=is_approved
            )
            
            if time_off:
                # Send notification to doctor
                self.send_notifications(doctor, start_datetime, end_datetime)        
            
            serializer = TimeOffSerializer(time_off)
            return Response(serializer.data, status=http_status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'message': str(e)}, status=http_status.HTTP_400_BAD_REQUEST)  
    
    def validate_time_off(self, start, end):
        """Validate time off period"""
        now = timezone.now()        
        if start >= end:
            return "End datetime must be after start datetime"
        if start < now:
            return "Cannot schedule time off in the past"
        if (end - start).total_seconds() < 3600:
            return "Minimum time off duration is 1 hour"
        return None
    
    def send_notifications(self, doctor, start, end):
        """Send notifications about new time off"""
        timezone.activate(pytz.timezone('Africa/Nairobi'))        
        message = f"Time off scheduled from {start.strftime('%b %d, %Y %I:%M %p')} to {end.strftime('%b %d, %Y %I:%M %p')}"
        
        # To doctor
        Notification.objects.create(
            user=doctor.user,
            message=message
        )
        
    def has_time_off_conflict(self, doctor, start, end):
        """Check for overlapping time off periods"""
        return TimeOff.objects.filter(
            doctor=doctor,
            start_datetime__lt=end,
            end_datetime__gt=start
        ).exists()

        
# Doctor put/delete time off view----------------------------------------------------------------------------------
class TimeOffUpdateView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    authentication_classes = [OAuth2Authentication]

    def put(self, request, id):
        try:
            user= request.user
            if not user:
                return Response({'message': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)
            if user.user_type not in ['DOCTOR', 'ADMIN']:
                return Response({'message': 'Only doctors or admins can perform this action'}, 
                            status=http_status.HTTP_403_FORBIDDEN)
            current_doctor = Doctor.objects.filter(user=user).first()
            if not current_doctor:
                return Response({'message': 'Doctor not found'}, status=http_status.HTTP_404_NOT_FOUND)
            
            # Get data
            start_datetime = request.data.get('start_datetime')
            end_datetime = request.data.get('end_datetime')
            
            # Parse datetime strings
            if start_datetime and end_datetime:
                try:
                    start_datetime = parse_datetime(start_datetime)
                    end_datetime = parse_datetime(end_datetime)
                except ValueError as e:
                    return Response({'message': str(e)}, 
                                status=http_status.HTTP_400_BAD_REQUEST)
                
                # Validate time off period
                validation_error = self.validate_time_off(start_datetime, end_datetime)
                if validation_error:
                    return Response({'message': validation_error}, 
                                status=http_status.HTTP_400_BAD_REQUEST)
            
            time_off = get_object_or_404(TimeOff,doctor=current_doctor, id=id)
            serializer = TimeOffSerializer(time_off, data=request.data, partial=True)
            if serializer.is_valid():
                update_time= serializer.save()
                if update_time.is_approved:
                    Notification.objects.create(user=update_time.doctor.user, message=f"Time off approved from {update_time.start_datetime} to {update_time.end_datetime}")
                return Response(serializer.data)
            return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'message': str(e)}, status=http_status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        time_off = get_object_or_404(TimeOff, id=id)
        time_off.delete()
        return Response(status=http_status.HTTP_204_NO_CONTENT)
    
    def validate_time_off(self, start, end):
        """Validate time off period"""
        now = timezone.now()        
        if start >= end:
            return "End datetime must be after start datetime"
        if start < now:
            return "Cannot schedule time off in the past"
        if (end - start).total_seconds() < 3600:
            return "Minimum time off duration is 1 hour"
        return None
        
        
# Get all time off view----------------------------------------------------------------------------------
class GetAllTimeOffView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    authentication_classes = [OAuth2Authentication]

    def get(self, request):
        time_off = TimeOff.objects.all()
        serializer = TimeOffSerializer(time_off, many=True)
        return Response(serializer.data)

# Appintments view----------------------------------------------------------------------------------
class AppointmentView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    authentication_classes = [OAuth2Authentication]
    
    def get(self, request):
        user= request.user
        if not user:
            return Response({'message': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)
        if user.user_type not in ['DOCTOR', 'ADMIN']:
            return Response({'message': 'Only doctors or admins can perform this action'}, 
                          status=http_status.HTTP_403_FORBIDDEN)
        
        current_doctor = self.get_doctor(user)
        if not current_doctor:
            return Response({'message': 'Doctor not found'}, status=http_status.HTTP_404_NOT_FOUND)
        
        # Get all appointments for the current doctor
        appointments = Appointment.objects.filter(doctor_id=current_doctor.id).all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        user= request.user
        if not user:
            return Response({'message': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)
        
        if user.user_type not in ['DOCTOR', 'ADMIN']:
            return Response({'message': 'Only doctors or admins can perform this action'}, 
                          status=http_status.HTTP_403_FORBIDDEN)
        
        doctor = self.get_doctor(user)
        if not doctor:
            return Response({'message': 'Doctor not found'}, status=http_status.HTTP_404_NOT_FOUND)
        
        data= request.data
        scheduled_time = data.get('scheduled_time')
        end_time = data.get('end_time')
        status = data.get('status', 'SCHEDULED')
        reason = data.get('reason')
        notes = data.get('notes')
        patient_id = data.get('patient_id')
        
        if not scheduled_time or not end_time:
            return Response({'message': 'Scheduled time and end time are required'},
                        status=http_status.HTTP_400_BAD_REQUEST)
            
        if not reason:
            return Response({'message': 'Reason is required'},
                        status=http_status.HTTP_400_BAD_REQUEST)
        if not notes:
            return Response({'message': 'Notes are required'},
                        status=http_status.HTTP_400_BAD_REQUEST)
            
        if not patient_id:
            return Response({'message': 'Patient ID is required'},
                        status=http_status.HTTP_400_BAD_REQUEST)
            
        # Parse datetime strings
        try:
            scheduled_time = parse_datetime(scheduled_time)
            end_time = parse_datetime(end_time)
        except ValueError as e:
            return Response({'message': str(e)}, 
                        status=http_status.HTTP_400_BAD_REQUEST)
        
        # Validate time period
        validation_error = self.validate_time(scheduled_time, end_time)
        if validation_error:
            return Response({'message': validation_error},
                        status=http_status.HTTP_400_BAD_REQUEST)
        
        # Check patient
        patient = self.get_patient(patient_id)
        if not patient:
            return Response({'message': 'Patient not found'}, status=http_status.HTTP_404_NOT_FOUND)
        if patient.user.user_type != 'PATIENT':
            return Response({'message': 'User is not a patient'}, status=http_status.HTTP_400_BAD_REQUEST)
        
        availability= self.check_doctor_availability(doctor, scheduled_time, end_time)
        if availability:
            return Response({'message': 'Doctor not available at this time'}, 
                       status=http_status.HTTP_400_BAD_REQUEST)  
            
        
        timeoff_availability= self.check_doctor_time_off(doctor, scheduled_time, end_time)
        if timeoff_availability:
            return Response({'message': 'Doctor is on leave during this time'}, 
                       status=http_status.HTTP_400_BAD_REQUEST)
        
        # Check for overlapping appointments
        appointment_overlap= self.check_appointment_overlap(doctor, scheduled_time, end_time)
        if appointment_overlap:
            return Response({'message': 'This appointment overlaps with an existing one'}, status=http_status.HTTP_400_BAD_REQUEST)    
        
        # Create appointment
        new_appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            scheduled_time=scheduled_time,
            end_time=end_time,
            status=status,
            reason=reason,
            notes=notes
        )
        
        # Send notification to doctor
        if new_appointment:
           self.send_notifications(doctor, scheduled_time, end_time)
        
        serializer = AppointmentSerializer(new_appointment)
        return Response(serializer.data, status=http_status.HTTP_201_CREATED)
    
    def get_doctor(self, user):
        try:
            doctor = Doctor.objects.filter(user=user).first()
            return doctor
        except Doctor.DoesNotExist:
            return None
        
    def get_patient(self, id):
        try:
            patient = Patient.objects.filter(id=id).first()
            return patient
        except Patient.DoesNotExist:
            return None
        
    def check_doctor_availability(self, doctor, scheduled_time, end_time):
        """Check if doctor is available during the requested time period"""
        scheduled_day = scheduled_time.weekday()  # 0=Monday, 6=Sunday
        scheduled_date = scheduled_time.date()
        
        # Convert time portions for comparison
        start_time = scheduled_time.time()
        end_time = end_time.time()
        
        # Check regular availability
        available = AvailabilitySchedule.objects.filter(
            doctor=doctor,
            day_of_week=scheduled_day,
            start_time__gte=start_time,
            end_time__lte=end_time,
            valid_from__lte=scheduled_date,
            valid_until__gte=scheduled_date
        ).exists()
        
        return available
    
    def check_doctor_time_off(self, doctor, scheduled_time, end_time):
        """Check if doctor has time off during the requested period"""
        time_off_exists = TimeOff.objects.filter(
            doctor=doctor,
            is_approved=True,
            start_datetime__lt=end_time,
            end_datetime__gt=scheduled_time
        ).exists()
        
        return time_off_exists
    
    def check_appointment_overlap(self, doctor, scheduled_time, end_time):
        """Check for overlapping appointments"""
        overlap = Appointment.objects.filter(
            doctor=doctor,
            scheduled_time__lt=end_time,
            end_time__gt=scheduled_time,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).exists()
        
        return overlap   
    
    def validate_time(self, start, end):
        """Validate time off period"""
        now = timezone.now()        
        if start >= end:
            return "End datetime must be after start datetime"
        if start < now:
            return "Cannot schedule time off in the past"
        if (end - start).total_seconds() < 3600:
            return "Minimum time off duration is 1 hour"
        return None
    
    def send_notifications(self, doctor, start, end):
        """Send notifications about new time off"""
        timezone.activate(pytz.timezone('Africa/Nairobi'))        
        message = f"Time off scheduled from {start.strftime('%b %d, %Y %I:%M %p')} to {end.strftime('%b %d, %Y %I:%M %p')}"
        
        # To doctor
        Notification.objects.create(
            user=doctor.user,
            message=message
        )
    
class AppointmentUpdateView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    authentication_classes = [OAuth2Authentication]

    def put(self, request, id):
        user= request.user
        if not user:
            return Response({'message': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)
        if user.user_type not in ['DOCTOR', 'ADMIN']:
            return Response({'message': 'Only doctors or admins can perform this action'}, 
                          status=http_status.HTTP_403_FORBIDDEN)

        current_doctor = Doctor.objects.filter(user=user).first()
        if not current_doctor:
            return Response({'message': 'Doctor not found'}, status=http_status.HTTP_404_NOT_FOUND)

        appointment = get_object_or_404(Appointment, doctor=current_doctor, id=id)
        data= request.data
        scheduled_time = data.get('scheduled_time')
        end_time = data.get('end_time')
        status = data.get('status')
        reason = data.get('reason')
        notes = data.get('notes')
        patient_id = data.get('patient_id')
        
        if scheduled_time and end_time:
            try:
                scheduled_time= parse_datetime(scheduled_time)
                end_time= parse_datetime(end_time)
            except ValueError as e:
                return Response({'message': str(e)}, 
                            status=http_status.HTTP_400_BAD_REQUEST)
            
            # Validate time period
            validation_error = self.validate_time(scheduled_time, end_time)
            if validation_error:
                return Response({'message': validation_error},
                            status=http_status.HTTP_400_BAD_REQUEST)
        
            availability= self.check_doctor_availability(current_doctor, scheduled_time, end_time)
            if availability:
                return Response({'message': 'Doctor not available at this time'},
                        status=http_status.HTTP_400_BAD_REQUEST)
                
            timeoff_availability= self.check_doctor_time_off(current_doctor, scheduled_time, end_time)
            if timeoff_availability:
                return Response({'message': 'Doctor is on leave during this time'}, 
                        status=http_status.HTTP_400_BAD_REQUEST)
            
            # Check for overlapping appointments
            appointment_overlap= self.check_appointment_overlap(current_doctor, scheduled_time, end_time)
            if appointment_overlap:
                return Response({'message': 'This appointment overlaps with an existing one'}, status=http_status.HTTP_400_BAD_REQUEST)
            
        if scheduled_time:
            appointment.scheduled_time= scheduled_time
        if end_time:
            appointment.end_time= end_time            
        if status:
            appointment.status= status
        if reason:
            appointment.reason= reason
        if notes:
            appointment.notes= notes
        if patient_id:
            return  Response({'message': 'Patient cannot be updated'}, status=http_status.HTTP_400_BAD_REQUEST)
        
        appointment.save()  
        serializer = AppointmentSerializer(appointment)        
        if status== 'CONFIRMED':
            Notification.objects.create(user=appointment.patient.user, message=f"Appointment confirmed with {appointment.doctor.user.get_full_name()} on {appointment.scheduled_time}")
        elif status== 'CANCELLED':
            Notification.objects.create(user=appointment.patient.user, message=f"Appointment cancelled with {appointment.doctor.user.get_full_name()} on {appointment.scheduled_time}")
        elif status== 'COMPLETED':
            Notification.objects.create(user=appointment.patient.user, message=f"Appointment completed with {appointment.doctor.user.get_full_name()} on {appointment.scheduled_time}")
        elif status== 'NO_SHOW':
            Notification.objects.create(user=appointment.patient.user, message=f"Patient no show for appointment with {appointment.doctor.user.get_full_name()} on {appointment.scheduled_time}")
        elif status== 'IN_PROGRESS':
            Notification.objects.create(user=appointment.patient.user, message=f"Appointment in progress with {appointment.doctor.user.get_full_name()} on {appointment.scheduled_time}")
        elif status== 'SCHEDULED':
            Notification.objects.create(user=appointment.patient.user, message=f"Appointment scheduled with {appointment.doctor.user.get_full_name()} on {appointment.scheduled_time}")
        elif status== 'RESCHEDULED':
            Notification.objects.create(user=appointment.patient.user, message=f"Appointment rescheduled with {appointment.doctor.user.get_full_name()} on {appointment.scheduled_time}")
        return Response(serializer.data)

    def delete(self, request, id):
        appointment = get_object_or_404(Appointment, id=id)
        appointment.delete()
        return Response(status=http_status.HTTP_204_NO_CONTENT)
    
    def validate_time(self, start, end):
        """Validate time off period"""
        now = timezone.now()        
        if start >= end:
            return "End datetime must be after start datetime"
        if start < now:
            return "Cannot schedule time off in the past"
        if (end - start).total_seconds() < 3600:
            return "Minimum time off duration is 1 hour"
        return None
    
    def check_doctor_availability(self, doctor, scheduled_time, end_time):
        """Check if doctor is available during the requested time period"""
        scheduled_day = scheduled_time.weekday()  # 0=Monday, 6=Sunday
        scheduled_date = scheduled_time.date()
        
        # Convert time portions for comparison
        start_time = scheduled_time.time()
        end_time = end_time.time()
        
        # Check regular availability
        available = AvailabilitySchedule.objects.filter(
            doctor=doctor,
            day_of_week=scheduled_day,
            start_time__gte=start_time,
            end_time__lte=end_time,
            valid_from__lte=scheduled_date,
            valid_until__gte=scheduled_date
        ).exists()
        
        return available
    
    def check_doctor_time_off(self, doctor, scheduled_time, end_time):
        """Check if doctor has time off during the requested period"""
        time_off_exists = TimeOff.objects.filter(
            doctor=doctor,
            is_approved=True,
            start_datetime__lt=end_time,
            end_datetime__gt=scheduled_time
        ).exists()
        
        return time_off_exists

    def check_appointment_overlap(self, doctor, scheduled_time, end_time):
        """Check for overlapping appointments"""
        overlap = Appointment.objects.filter(
            doctor=doctor,
            scheduled_time__lt=end_time,
            end_time__gt=scheduled_time,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).exists()
        
        return overlap
    

class GetNotifications(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    authentication_classes = [OAuth2Authentication]

    def get(self, request):
        user= request.user
        if not user:
            return Response({'message': 'User not found'}, status=http_status.HTTP_404_NOT_FOUND)
        
        notifications = Notification.objects.filter(user=user).all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)