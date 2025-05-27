# exams/serializers.py
from rest_framework import serializers
from .models import Course, Exam, ExamEnrollment
from authentication.serializers import UserSerializer, DepartmentSerializer
from rooms.serializers import RoomSerializer
from django.utils import timezone
from datetime import datetime

class CourseSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    instructor = UserSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    instructor_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'code', 'department', 'department_id',
            'instructor', 'instructor_id', 'credits', 'semester'
        ]

class ExamSerializer(serializers.ModelSerializer):
    course = serializers.CharField(write_only=True)
    room = serializers.CharField(write_only=True)
    course_detail = CourseSerializer(source='course', read_only=True)
    room_detail = RoomSerializer(source='room', read_only=True)
    created_by = UserSerializer(read_only=True)
    is_past = serializers.BooleanField(read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'course', 'course_detail', 'exam_type', 'date',
            'start_time', 'end_time', 'room', 'room_detail',
            'duration_minutes', 'max_students', 'status',
            'notes', 'created_by', 'created_at', 'updated_at', 'is_past'
        ]

    def validate(self, attrs):
        from .models import Course
        from rooms.models import Room

        course_code = attrs.get('course')
        room_name = attrs.get('room')

        try:
            course_obj = Course.objects.get(code=course_code)
            attrs['course'] = course_obj
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course with code '{course_code}' not found.")

        try:
            room_obj = Room.objects.get(name=room_name)
            attrs['room'] = room_obj
        except Room.DoesNotExist:
            raise serializers.ValidationError(f"Room with name '{room_name}' not found.")

        if 'start_time' in attrs and 'end_time' in attrs:
            if attrs['end_time'] <= attrs['start_time']:
                raise serializers.ValidationError("End time must be after start time")

        return attrs

    def update(self, instance, validated_data):
        print("[*] update validated_data:", validated_data)
        return super().update(instance, validated_data)


class ExamCreateSerializer(serializers.ModelSerializer):
    course = serializers.CharField()
    room = serializers.CharField()

    class Meta:
        model = Exam
        fields = [
            'course', 'exam_type', 'date', 'start_time', 'end_time',
            'room', 'duration_minutes', 'max_students', 'notes'
        ]

    def validate(self, attrs):
        from .models import Exam, Course
        from rooms.models import Room

        course_code = attrs.get('course')
        room_name = attrs.get('room')

        try:
            course_obj = Course.objects.get(code=course_code)
            attrs['course'] = course_obj
        except Course.DoesNotExist:
            raise serializers.ValidationError(f"Course '{course_code}' not found")

        try:
            room_obj = Room.objects.get(name=room_name)
            attrs['room'] = room_obj
        except Room.DoesNotExist:
            raise serializers.ValidationError(f"Room '{room_name}' not found")

        # Room conflict check
        room = attrs['room']
        date = attrs.get('date')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if room and date and start_time and end_time:
            conflicting_exams = Exam.objects.filter(
                room=room,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(status='cancelled')

            if self.instance:
                conflicting_exams = conflicting_exams.exclude(id=self.instance.id)

            if conflicting_exams.exists():
                raise serializers.ValidationError(
                    f"Room {room.full_name} is not available at this time"
                )

        return super().validate(attrs)

class ExamEnrollmentSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    student = UserSerializer(read_only=True)
    exam_id = serializers.IntegerField(write_only=True)
    student_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ExamEnrollment
        fields = ['id', 'exam', 'exam_id', 'student', 'student_id', 'enrolled_at']

class ConflictCheckSerializer(serializers.Serializer):
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    room_id = serializers.IntegerField()
    exclude_exam_id = serializers.IntegerField(required=False)