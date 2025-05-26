# exams/urls.py
from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    # Course endpoints
    path('courses/', views.CourseListCreateView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # Exam endpoints
    path('', views.ExamListCreateView.as_view(), name='exam_list'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
    path('my-exams/', views.my_exams, name='my_exams'),
    path('check-conflicts/', views.check_conflicts, name='check_conflicts'),
    path('department/<int:department_id>/schedule/', views.department_schedule, name='department_schedule'),
    
    # Exam enrollment endpoints
    path('enrollments/', views.ExamEnrollmentListCreateView.as_view(), name='enrollment_list'),
    path('enrollments/<int:pk>/', views.ExamEnrollmentDetailView.as_view(), name='enrollment_detail'),
]