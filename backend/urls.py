# File: backend/urls.py
from django.contrib import admin
from django.urls import path, include
from accounts.views import LoginAPIView
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def home(request):
    return JsonResponse({"message": "Smart AI Attendance Backend is running"})

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),

    # Auth APIs
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', include('accounts.urls')),  # تسجيل مستخدم جديد / حسابي

    # Attendance APIs
    path('api/attendance/', include('attendance.urls')),  # حضور، محاضرات، QR، إحصائيات
]
