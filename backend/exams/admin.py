# exams/admin.py
from django.contrib import admin
from .models import Course, Exam, ExamEnrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'instructor', 'credits', 'semester']
    list_filter = ['department', 'credits', 'semester']
    search_fields = ['code', 'name', 'instructor__username']
    ordering = ['code']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['course', 'exam_type', 'date', 'start_time', 'room', 'status', 'max_students']
    list_filter = ['exam_type', 'status', 'date', 'course__department']
    search_fields = ['course__code', 'course__name', 'room__name']
    ordering = ['date', 'start_time']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Exam Details', {
            'fields': ('course', 'exam_type', 'status')
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'duration_minutes')
        }),
        ('Location & Capacity', {
            'fields': ('room', 'max_students')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_by')
        }),
    )

@admin.register(ExamEnrollment)
class ExamEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['exam', 'student', 'enrolled_at']
    list_filter = ['exam__date', 'exam__course__department']
    search_fields = ['exam__course__code', 'student__username', 'student__first_name', 'student__last_name']
    ordering = ['exam__date']