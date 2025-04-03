from django.urls import path, include
from . import views
urlpatterns = [
    # -----------<<<<<<<<<<<<<<<<<<<<Authentication>>>>>>>>>>>>>>>>>>>>>>--------------------
    path('noexist/callback/', views.Redirect.as_view()),
    path('register', views.RegisterUser.as_view(), name='register'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('user/', views.UserList.as_view()),
    path('user/<int:id>/', views.StaffViewUserById.as_view()),
    
    # -----------<<<<<<<<<<<<<<<<<<<<Doctor>>>>>>>>>>>>>>>>>>>>>>-----------------------------
    path('doctor-profile/', views.DoctorProfileView.as_view(), name='doctor profile'),
    
    
    # ----------------<<<<<<<<<<<<<<<<Doctor specialisation>>>>>>>>>>>>>>>>>-----------------
    path('post-specialization/', views.PostSpecializationView.as_view(), name='post specialisation'),
    path('get-specialization/', views.GetSpecializationsView.as_view(), name='get specialisation'),
    
    
    # -----------<<<<<<<<<<<<<<<<<<<<Patient>>>>>>>>>>>>>>>>>>>>>>---------------------------
    path('register-patient/', views.RegisterPatient.as_view(), name='register patient'),
    path('patient-list/', views.PatientListView.as_view(), name='patient list'),
    path('patient-profile/<int:id>/', views.PatientProfileView.as_view(), name='patient profile'), #Pass patient id
    
]