#accounts/urls.py
from django.urls import path
from .views import RegisterAPIView, LogoutAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api-register'),
    path('logout/', LogoutAPIView.as_view(), name='api-logout'),
]
