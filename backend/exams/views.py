# exams/views.py
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import Course, Exam, ExamEnrollment
from .serializers import (
    CourseSerializer, ExamSerializer, ExamCreateSerializer,
    ExamEnrollmentSerializer, ConflictCheckSerializer
)

class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.query_params.get('department', None)
        instructor = self.request.query_params.get('instructor', None)
        semester = self.request.query_params.get('semester', None)
        
        if department:
            queryset = queryset.filter(department=department)
        if instructor:
            queryset = queryset.filter(instructor=instructor)
        if semester:
            queryset = queryset.filter(semester=semester)
            
        return queryset.order_by('code')

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExamCreateSerializer
        return ExamSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on user role
        if user.is_student:
            # Students see exams from their department
            queryset = queryset.filter(course__department=user.department)
        elif user.is_instructor:
            # Instructors see their own exams and their department's exams
            queryset = queryset.filter(
                Q(course__instructor=user) | Q(course__department=user.department)
            )
        # Admins see all exams
        
        # Additional filters
        department = self.request.query_params.get('department', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        status_filter = self.request.query_params.get('status', None)
        
        if department:
            queryset = queryset.filter(course__department=department)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset.order_by('date', 'start_time')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_exams(request):
    user = request.user
    
    if user.is_instructor:
        # Get exams created by this instructor
        exams = Exam.objects.filter(course__instructor=user).order_by('date', 'start_time')
    elif user.is_student:
        # Get exams for student's enrolled courses
        enrolled_exams = ExamEnrollment.objects.filter(student=user)
        exams = [enrollment.exam for enrollment in enrolled_exams]
        exams.sort(key=lambda x: (x.date, x.start_time))
    else:
        # Admin gets all exams
        exams = Exam.objects.all().order_by('date', 'start_time')
    
    serializer = ExamSerializer(exams, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_conflicts(request):
    serializer = ConflictCheckSerializer(data=request.data)
    if serializer.is_valid():
        date = serializer.validated_data['date']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']
        room_id = serializer.validated_data['room_id']
        exclude_exam_id = serializer.validated_data.get('exclude_exam_id')
        
        conflicts = Exam.objects.filter(
            room_id=room_id,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=['scheduled', 'confirmed']
        )
        
        if exclude_exam_id:
            conflicts = conflicts.exclude(id=exclude_exam_id)
        
        conflict_serializer = ExamSerializer(conflicts, many=True)
        
        return Response({
            'has_conflicts': conflicts.exists(),
            'conflicts': conflict_serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def department_schedule(request, department_id):
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    exams = Exam.objects.filter(course__department_id=department_id)
    
    if date_from:
        exams = exams.filter(date__gte=date_from)
    if date_to:
        exams = exams.filter(date__lte=date_to)
        
    exams = exams.order_by('date', 'start_time')
    serializer = ExamSerializer(exams, many=True)
    
    return Response({
        'department_id': department_id,
        'exams': serializer.data
    })

class ExamEnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = ExamEnrollment.objects.all()
    serializer_class = ExamEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        exam = self.request.query_params.get('exam', None)
        student = self.request.query_params.get('student', None)
        
        if exam:
            queryset = queryset.filter(exam=exam)
        if student:
            queryset = queryset.filter(student=student)
            
        return queryset

class ExamEnrollmentDetailView(generics.RetrieveDestroyAPIView):
    queryset = ExamEnrollment.objects.all()
    serializer_class = ExamEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]