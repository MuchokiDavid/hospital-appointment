"""
URL configuration for hospital_appointment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from appointmentapp import views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Healthcare Appointment Scheduling System API",
        default_version='v1',
        description="""A secure backend service for managing patient appointments and doctor schedules.
        Includes patient management, doctor scheduling, and medical records.""",
        # terms_of_service="https://yourhealthcareapp.com/terms/",
        contact=openapi.Contact(email="support@yourhealthcareapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [    
    path('', views.main),
    path("admin/", admin.site.urls),
    path('api/v1/', include('appointmentapp.urls')),
    path('api/v1/auth/', include('users.urls')),
    
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('documentation/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

admin.site.site_header = 'Hospital Appointment System'
admin.site.site_title = 'HAS'