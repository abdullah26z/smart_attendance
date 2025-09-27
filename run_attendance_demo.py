# File: run_attendance_demo.py
import csv
import os
import django
import random
import string
from datetime import timedelta
from django.utils import timezone

# ---------------------------
# إعداد Django للعمل خارج manage.py
# ---------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from accounts.models import User
from attendance.models import Lecture, Attendance
from utils.qr_utils import generate_qr_code

CSV_FILE = "attendance_log.csv"

def save_attendance_to_csv(student_email, lecture, status):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["student_email", "lecture_title", "status", "timestamp"])
        writer.writerow([student_email, lecture.title, status, lecture.start_time])
        
def save_attendance_csv(att):
    """حفظ سجل الحضور في CSV"""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["datetime", "user_email", "status", "latitude", "longitude", "qr_code", "qr_expires_at"])
        writer.writerow([
            att.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            att.user.email,
            att.status,
            att.latitude,
            att.longitude,
            att.qr_code,
            att.qr_expires_at.strftime("%Y-%m-%dT%H:%M:%S") if att.qr_expires_at else ""
        ])

# ---------------------------
# إنشاء الدكتور والطلاب
# ---------------------------
def create_demo_users():
    doctor, created = User.objects.get_or_create(
        email="3booody.om@gmail.com",
        defaults={
            "full_name": "Dr. Abdullah",
            "role": "lecturer",
            "is_staff": True
        }
    )
    if created:
        doctor.set_password("3B00dy_26")
        doctor.save()
        print("✅ Doctor created:", doctor.email)
    else:
        print("⚠️ Doctor already exists:", doctor.email)

    students_data = [
        {"email": "student1@test.com", "full_name": "Student One"},
        {"email": "student2@test.com", "full_name": "Student Two"},
        {"email": "student3@test.com", "full_name": "Student Three"},
    ]

    students = []
    for s in students_data:
        student, created = User.objects.get_or_create(
            email=s["email"],
            defaults={
                "full_name": s["full_name"],
                "role": "student"
            }
        )
        if created:
            student.set_password("Student123!")
            student.save()
            print("✅ Student created:", student.email)
        else:
            print("⚠️ Student already exists:", student.email)
        students.append(student)
    return doctor, students

# ---------------------------
# توليد QR للمحاضرة
# ---------------------------
def generate_lecture_qr(doctor):
    qr_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    qr_expires_at = timezone.now() + timedelta(minutes=10)
    lecture = Lecture.objects.create(
        title="Demo Lecture",
        lecturer=doctor,
        qr_code=qr_code,
        qr_expires_at=qr_expires_at
    )
    qr_image_base64 = generate_qr_code(qr_code)
    print(f"🎓 Lecture QR generated: {qr_code} (expires at {qr_expires_at})")
    return lecture, qr_image_base64

# ---------------------------
# تسجيل حضور الطلاب
# ---------------------------
def mark_attendance(students, lecture):
    from attendance.models import Attendance
    for student in students:
        att = Attendance.objects.create(
            user=student,
            lecture=lecture,
            status="present",
            qr_code=lecture.qr_code,  # نخزن نفس QR كود المحاضرة
            latitude=24.774265,
            longitude=46.738586,
        )
        print(f"✅ Attendance marked for: {student.email}")
        save_attendance_to_csv(student.email, lecture, "present")


# ---------- 4) حفظ CSV ----------
def save_to_csv(records):
    csv_path = os.path.join(os.path.dirname(__file__), "attendance_records.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Lecture", "Status", "Timestamp"])
        writer.writerows(records)
    print(f"📂 CSV saved at: {csv_path}")


# ---------------------------
# التشغيل
# ---------------------------
if __name__ == "__main__":
    doctor, students = create_demo_users()
    lecture, qr_image = generate_lecture_qr(doctor)
    mark_attendance(students, lecture)
    print("✅ Demo complete! Check database and CSV for records.")
