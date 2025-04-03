from django.urls import path, include
from . import views
urlpatterns = [
    path('noexist/callback/', views.Redirect.as_view()),
    path('register', views.RegisterUser.as_view(), name='register'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('post-specialization/', views.PostSpecializationView.as_view(), name='post specialisation'),
    path('get-specialization/', views.GetSpecializationsView.as_view(), name='get specialisation'),
    
    path('doctor-profile/', views.DoctorProfileView.as_view(), name='doctor profile'),
    
    path('user/', views.UserList.as_view()),
]