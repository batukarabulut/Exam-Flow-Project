# exams/models.py
from django.db import models
from django.core.exceptions import ValidationError
from authentication.models import CustomUser, Department
from rooms.models import Room
from datetime import datetime, timedelta

class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    instructor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'instructor'}
    )
    credits = models.PositiveIntegerField(default=3)
    semester = models.CharField(max_length=20)  # e.g., "Fall 2024"
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Exam(models.Model):
    EXAM_TYPES = [
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('makeup', 'Makeup'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    duration_minutes = models.PositiveIntegerField()
    max_students = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='created_exams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['course', 'exam_type', 'date']
    
    def __str__(self):
        return f"{self.course.code} {self.get_exam_type_display()} - {self.date}"
    
    def clean(self):
        # Validate that end_time is after start_time
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("End time must be after start time")
        
        # Validate that max_students doesn't exceed room capacity
        if self.room and self.max_students > self.room.capacity:
            raise ValidationError(
                f"Maximum students ({self.max_students}) exceeds room capacity ({self.room.capacity})"
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_past(self):
        from django.utils import timezone
        exam_datetime = timezone.make_aware(
            datetime.combine(self.date, self.start_time)
        )
        return exam_datetime < timezone.now()

class ExamEnrollment(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['exam', 'student']
    
    def __str__(self):
        return f"{self.student.username} - {self.exam}"