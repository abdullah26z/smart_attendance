# File: attendance/serializers.py
from rest_framework import serializers
from .models import Attendance, Lecture

class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'
        read_only_fields = (
            'qr_code',
            'qr_expires_at',
            'start_time',
            'end_time',
            'lecturer',
        )


class AttendanceSerializer(serializers.ModelSerializer):
    lecture_title = serializers.CharField(source='lecture.title', read_only=True)
    lecture_course = serializers.CharField(source='lecture.course', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ('user', 'timestamp', 'lecture_title', 'lecture_course')
