# attendance/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Lecture, Attendance
from accounts.models import User
import random, string

# ---------------------------
# توليد QR Code عشوائي
# ---------------------------
def generate_qr_code(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# ---------------------------
# إنشاء محاضرة جديدة (Doctor)
# ---------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_lecture(request):
    user = request.user
    if user.role not in ['lecturer', 'admin']:
        return Response({"detail": "Only lecturers can create lectures."}, status=status.HTTP_403_FORBIDDEN)

    title = request.data.get('title')
    if not title:
        return Response({"detail": "Title is required."}, status=status.HTTP_400_BAD_REQUEST)

    qr_code = generate_qr_code()
    qr_expires_at = timezone.now() + timedelta(minutes=10)

    lecture = Lecture.objects.create(
        title=title,
        lecturer=user,
        qr_code=qr_code,
        qr_expires_at=qr_expires_at
    )

    return Response({
        "lecture": {
            "id": lecture.id,
            "title": lecture.title,
            "qr_code": lecture.qr_code,
            "qr_expires_at": lecture.qr_expires_at
        }
    }, status=status.HTTP_201_CREATED)

# ---------------------------
# تسجيل الحضور عن طريق QR (Student)
# ---------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    user = request.user
    qr_code = request.data.get('qr_code')

    if not qr_code:
        return Response({"detail": "QR code is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        lecture = Lecture.objects.get(qr_code=qr_code)
    except Lecture.DoesNotExist:
        return Response({"detail": "Invalid QR code."}, status=status.HTTP_404_NOT_FOUND)

    # تحقق من صلاحية QR
    if lecture.qr_expires_at < timezone.now():
        return Response({"detail": "QR code expired."}, status=status.HTTP_400_BAD_REQUEST)

    attendance, created = Attendance.objects.get_or_create(
        user=user,
        lecture=lecture,
        defaults={
            "status": "present",
            "qr_code": qr_code,
            "latitude": request.data.get("latitude"),
            "longitude": request.data.get("longitude"),
            "qr_expires_at": lecture.qr_expires_at
        }
    )

    if not created:
        return Response({"detail": "Attendance already marked."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "attendance": {
            "lecture": lecture.title,
            "status": attendance.status,
            "timestamp": attendance.timestamp
        }
    }, status=status.HTTP_201_CREATED)

# ---------------------------
# آخر حضور (Student)
# ---------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def last_attendance(request):
    user = request.user
    att = Attendance.objects.filter(user=user).order_by('-timestamp').first()
    if not att:
        return Response({"detail": "No attendance found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "lecture": att.lecture.title,
        "status": att.status,
        "timestamp": att.timestamp,
        "qr_code": att.qr_code,
        "qr_expires_at": att.qr_expires_at
    })

# ---------------------------
# إحصائيات حضور (Doctor)
# ---------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_stats(request, lecture_id):
    user = request.user
    if user.role not in ['lecturer', 'admin']:
        return Response({"detail": "Only lecturers can view stats."}, status=status.HTTP_403_FORBIDDEN)

    try:
        lecture = Lecture.objects.get(id=lecture_id, lecturer=user)
    except Lecture.DoesNotExist:
        return Response({"detail": "Lecture not found."}, status=status.HTTP_404_NOT_FOUND)

    total = Attendance.objects.filter(lecture=lecture).count()
    present = Attendance.objects.filter(lecture=lecture, status='present').count()
    return Response({
        "lecture": lecture.title,
        "total_attendance": total,
        "present": present
    })
