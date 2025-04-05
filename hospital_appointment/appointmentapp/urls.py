from django.urls import path
from . import views

urlpatterns = [
    path('doctor-availability-schedule/', views.AvailabilityScheduleView.as_view(), name='availability-schedule'), #GET, POST Authenticate: Doctor user
    path('all-availability-schedule/', views.GetAllAvailabilityScheduleView.as_view(), name='all-availability-schedule'), #GET, POST Authenticate user
    path('update-availability-schedule/<int:id>/', views.AvailabilityScheduleUpdateView.as_view(), name='update-availability-schedule'), #PUT, DELETE Authenticate: Doctor user
    
    path('doctor-time-off/', views.TimeOffView.as_view(), name='time-off'), #GET, POST Authenticate: Doctor user
    path('all-time-off/', views.GetAllTimeOffView.as_view(), name='all-time-off'), #GET, POST Authenticate user
    path('update-time-off/<int:id>/', views.TimeOffUpdateView.as_view(), name='update-time-off'), #PUT, DELETE Authenticate: Doctor user
    
    path('appointment/', views.AppointmentView.as_view(), name='appointment'), #GET, POST Authenticate: Doctor user
    path('update-appointment/<int:id>/', views.AppointmentUpdateView.as_view(), name='update-appointment'), #PUT, DELETE Authenticate: Doctor user
    # path('all-appointment/', views.GetAllAppointmentView.as_view(), name='all-appointment'), #GET, POST Authenticate user
    
    path('notification/', views.GetNotifications.as_view(), name='notification'), #GET Authenticate: Doctor user
]
