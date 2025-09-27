# File: create_users.py

import os
import django

# إعداد Django للعمل خارج manage.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from accounts.models import User

# إنشاء دكتور
doctor, created = User.objects.get_or_create(
    email="doctor1@example.com",
    defaults={
        "full_name": "Dr. Abdullah",
        "password": "Doctor123!",
        "role": "lecturer",
        "is_staff": True
    }
)
if created:
    doctor.set_password("Doctor123!")
    doctor.save()
    print("✅ Doctor created:", doctor.email)
else:
    print("⚠️ Doctor already exists:", doctor.email)

# إنشاء طلاب
students_data = [
    {"email": "student1@example.com", "full_name": "Student One"},
    {"email": "student2@example.com", "full_name": "Student Two"},
    {"email": "student3@example.com", "full_name": "Student Three"},
]

for s in students_data:
    student, created = User.objects.get_or_create(
        email=s["email"],
        defaults={
            "full_name": s["full_name"],
            "password": "Student123!",
            "role": "student"
        }
    )
    if created:
        student.set_password("Student123!")
        student.save()
        print("✅ Student created:", student.email)
    else:
        print("⚠️ Student already exists:", student.email)
