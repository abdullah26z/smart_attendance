from django.urls import path
from .views import AttendanceAPIView, AttendanceHistoryAPIView, AttendanceStatsAPIView, LectureQRAPIView

urlpatterns = [
    path('mark/', AttendanceAPIView.as_view(), name='attendance-mark'),
    path('history/', AttendanceHistoryAPIView.as_view(), name='attendance-history'),
    path('stats/', AttendanceStatsAPIView.as_view(), name='attendance-stats'),
    path('lecture_qr/', LectureQRAPIView.as_view(), name='lecture-qr'),
]
