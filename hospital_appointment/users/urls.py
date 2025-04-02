from django.urls import path, include
from . import views
urlpatterns = [
    path('noexist/callback/', views.Redirect.as_view()),
    path('register', views.RegisterUser.as_view(), name='register'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    
    path('user/', views.UserList.as_view()),
]