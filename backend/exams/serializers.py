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
    course = CourseSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    room_id = serializers.IntegerField(write_only=True)
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Exam
        fields = [
            'id', 'course', 'course_id', 'exam_type', 'date',
            'start_time', 'end_time', 'room', 'room_id',
            'duration_minutes', 'max_students', 'status',
            'notes', 'created_by', 'created_at', 'updated_at', 'is_past'
        ]
    
    def validate(self, attrs):
        # Validate that end_time is after start_time
        if 'start_time' in attrs and 'end_time' in attrs:
            if attrs['end_time'] <= attrs['start_time']:
                raise serializers.ValidationError("End time must be after start time")
        
        # Validate that exam is not in the past (for new exams)
        if 'date' in attrs and not self.instance:
            if attrs['date'] < timezone.now().date():
                raise serializers.ValidationError("Cannot schedule exam in the past")
        
        return attrs

class ExamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            'course', 'exam_type', 'date', 'start_time', 'end_time',
            'room', 'duration_minutes', 'max_students', 'notes'
        ]
    
    def validate(self, attrs):
        # Check room availability
        from .models import Exam
        room = attrs.get('room')
        date = attrs.get('date')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if room and date and start_time and end_time:
            # Check for conflicts
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