from django.db import models
from django.utils import timezone
from accounts.models import User

class Lecture(models.Model):
    title = models.CharField(max_length=200, default="Lecture")
    lecturer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'lecturer'}
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    qr_code = models.CharField(max_length=100, blank=True, null=True)
    qr_expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} by {self.lecturer.email}"


class Attendance(models.Model):
    STATUS_CHOICES = [('present', 'Present'), ('absent', 'Absent')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    qr_code = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'lecture')

    def __str__(self):
        return f"{self.user.email} - {self.lecture.title} - {self.status}"
