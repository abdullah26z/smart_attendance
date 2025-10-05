# attendance/urls.py
from django.urls import path
from .views import (
    create_lecture,
    mark_attendance,
    last_attendance,
    attendance_stats,
)

urlpatterns = [
    # إنشاء محاضرة جديدة (Doctor)
    path('lecture_qr/', create_lecture, name='create_lecture'),

    # تسجيل الحضور عن طريق QR (Student)
    path('mark/', mark_attendance, name='mark_attendance'),

    # آخر حضور للطالب
    path('last/', last_attendance, name='last_attendance'),

    # إحصائيات حضور لمحاضرة محددة (Doctor)
    path('stats/<int:lecture_id>/', attendance_stats, name='attendance_stats'),
]
