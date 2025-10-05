# File: attendance/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Lecture(models.Model):
    title = models.CharField(max_length=255)
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qr_code = models.CharField(max_length=100, blank=True, null=True)
    qr_expires_at = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")
    timestamp = models.DateTimeField(auto_now_add=True)
    qr_code = models.CharField(max_length=100, blank=True, null=True)
    qr_expires_at = models.DateTimeField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.lecture.title} - {self.status}"
