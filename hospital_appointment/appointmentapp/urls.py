from django.urls import path
from . import views

urlpatterns = [
    # ---<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Doctor availability schedule>>>>>>>>>>>>>>>>>>>>>>--------------------
    path('doctor-availability-schedule/', views.AvailabilityScheduleView.as_view(), name='availability-schedule'), #GET, POST Authenticate: Doctor user
    path('availability-schedule-by-id/<int:id>/', views.AvailabilityScheduleByIdView.as_view(), name='update-availability-schedule'), #PUT, DELETE Authenticate: Doctor user
    path('all-availability-schedule/', views.GetAllAvailabilityScheduleView.as_view(), name='all-availability-schedule'), #GET, POST Authenticate user
    
    # ---<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Doctor time off schedule>>>>>>>>>>>>>>>>>>>>>>--------------------
    path('time-off/', views.TimeOffView.as_view(), name='time-off'), #GET, POST Authenticate: Doctor user
    path('time-off-by-id/<int:id>/', views.TimeOffByIdView.as_view(), name='update-time-off'), #PUT, DELETE Authenticate: Doctor user
    path('all-time-off/', views.GetAllTimeOffView.as_view(), name='all-time-off'), #GET, POST Authenticate user
    
    # ---<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Appointment>>>>>>>>>>>>>>>>>>>>>>--------------------
    path('appointment/', views.AppointmentView.as_view(), name='appointment'), #GET, POST Authenticate: Doctor user
    path('appointment-by-id/<int:id>/', views.AppointmentByIdView.as_view(), name='update-appointment'), #PUT, DELETE Authenticate: Doctor user
    path('all-appointment/', views.GetAllAppointmentView.as_view(), name='all-appointment'), #GET, POST Authenticate user
    
    # ----<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Medical Record>>>>>>>>>>>>>>>>>>>>>>--------------------
    path('medical-record/', views.MedicalRecordView.as_view(), name='medical-record'), #GET, POST Authenticate: Doctor user
    path('medical-record-by-id/<int:id>/', views.MedicalRecordByIdView.as_view(), name='update-medical-record'), #PUT, DELETE Authenticate: Doctor user
    path('all-medical-record/', views.GetAllMedicalRecordView.as_view(), name='all-medical-record'), #GET, POST Authenticate user
    
    # ----<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Prescription>>>>>>>>>>>>>>>>>>>>>>--------------------
    # path('prescription/', views.PrescriptionView.as_view(), name='prescription'), #GET, POST Authenticate: Doctor user
    # path('update-prescription/<int:id>/', views.PrescriptionUpdateView.as_view(), name='update-prescription'), #PUT, DELETE Authenticate: Doctor user
    # path('all-prescription/', views.GetAllPrescriptionView.as_view(), name='all-prescription'), #GET, POST Authenticate user
    
    # ------<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Notification>>>>>>>>>>>>>>>>>>>>>>--------------------
    path('notification/', views.GetNotifications.as_view(), name='notification'), #GET Authenticate: Doctor user
    path('notification-by-id/<int:id>/', views.NotificationById.as_view(), name='update-notification'), #PUT, DELETE Authenticate: Doctor user
]
