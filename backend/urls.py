# File: backend/urls.py

from django.contrib import admin
from django.urls import path, include
from accounts.views import LoginAPIView
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Smart AI Attendance Backend is running"})

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/attendance/', include('attendance.urls')),
]
