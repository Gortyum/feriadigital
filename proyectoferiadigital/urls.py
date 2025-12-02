# proyectoferiadigital/urls.py (archivo principal de URLs del proyecto)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('appferiadigital.urls')),
]
