from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Attendance, Lecture
from .serializers import AttendanceSerializer
from utils.qr_utils import generate_qr_code, is_qr_valid
import random
import string
import csv
import os
import requests  # لإرسال رسائل لتليجرام
from django.conf import settings

CSV_FILE = "attendance_log.csv"

# ---------------------------
# دالة حفظ السجل في CSV
# ---------------------------
def save_attendance_csv(att):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "datetime", "user_id", "user_email", "status",
                "latitude", "longitude", "qr_code", "qr_expires_at"
            ])
        writer.writerow([
            att.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            att.user.id,
            att.user.email,
            att.status,
            att.latitude,
            att.longitude,
            att.qr_code,
            att.qr_expires_at.strftime("%Y-%m-%dT%H:%M:%S") if att.qr_expires_at else ""
        ])

# ---------------------------
# دالة إرسال رسالة على تليجرام
# ---------------------------
def send_telegram_message(chat_id, message):
    token = getattr(settings, "TELEGRAM_TOKEN", None)
    if not token or not chat_id:
        return  # ما في توكن أو ما سجلنا chat_id
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=payload, timeout=5)
    except requests.RequestException:
        pass  # نتجاهل أي خطأ بالشبكة

# ---------------------------
# تسجيل الحضور
# ---------------------------
class AttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        qr_code = serializer.validated_data.get("qr_code")
        # تحقق من صلاحية QR
        lecture_qr_valid = Lecture.objects.filter(
            qr_code=qr_code,
            qr_expires_at__gte=timezone.now()
        ).first()
        if not lecture_qr_valid or not is_qr_valid(qr_code, timezone.now()):
            return Response({"error": "QR غير صالح أو انتهت صلاحيته"}, status=400)

        qr_expires_at = timezone.now() + timedelta(minutes=10)
        attendance = serializer.save(
            user=request.user,
            lecture=lecture_qr_valid,
            timestamp=timezone.now(),
            qr_code=qr_code,
            qr_expires_at=qr_expires_at
        )

        save_attendance_csv(attendance)

        # إرسال إشعار عبر تليجرام لو كان مسجل chat_id
        if hasattr(request.user, "telegram_chat_id") and request.user.telegram_chat_id:
            send_telegram_message(
                request.user.telegram_chat_id,
                f"✅ تم تسجيل حضورك للمحاضرة: {lecture_qr_valid.title} ({attendance.timestamp.strftime('%H:%M:%S')})"
            )

        qr_image_base64 = generate_qr_code(qr_code)
        return Response({
            "message": "تم تسجيل الحضور بنجاح",
            "attendance": serializer.data,
            "qr_image_base64": qr_image_base64,
            "qr_expires_at": qr_expires_at
        }, status=201)

# ---------------------------
# استعراض سجل الحضور
# ---------------------------
class AttendanceHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attendances = Attendance.objects.filter(user=request.user).order_by('-timestamp')
        if not attendances.exists():
            return Response({"message": "لا يوجد حضور مسجل حتى الآن."})
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

# ---------------------------
# إحصائيات الحضور
# ---------------------------
class AttendanceStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        total = Attendance.objects.filter(user=user).count()
        today = Attendance.objects.filter(user=user, timestamp__date=timezone.now().date()).count()
        last_week = Attendance.objects.filter(user=user, timestamp__gte=timezone.now() - timedelta(days=7)).count()
        return Response({
            "total_attendance": total,
            "today_attendance": today,
            "last_7_days": last_week
        })

# ---------------------------
# توليد QR للمحاضرة
# ---------------------------
class LectureQRAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        qr_content = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        qr_expires_at = timezone.now() + timedelta(minutes=10)
        qr_image_base64 = generate_qr_code(qr_content)

        lecture = Lecture.objects.create(
            title="Lecture",
            lecturer=request.user,
            qr_code=qr_content,
            qr_expires_at=qr_expires_at
        )

        return Response({
            "message": "تم توليد QR للمحاضرة",
            "qr_code": qr_content,
            "qr_image_base64": qr_image_base64,
            "qr_expires_at": qr_expires_at,
            "lecture_id": lecture.id
        }, status=201)
