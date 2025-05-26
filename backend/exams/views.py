from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from authentication.models import CustomUser
from .models import Course, Exam, ExamEnrollment
from .serializers import (
    CourseSerializer, ExamSerializer, ExamCreateSerializer,
    ExamEnrollmentSerializer, ConflictCheckSerializer
)

# 🔔 Yardımcı fonksiyon: öğrencilere e-posta gönder
def notify_students_of_exam_change(exam):
    print(f"[*] Notifying students for Exam ID: {exam.id}")
    
    department = exam.course.department
    students = CustomUser.objects.filter(role='student', department=department)
    print(f"[*] Found {students.count()} students in department: {department.name}")

    for student in students:
        if student.email:
            print(f"[*] Sending to {student.email}")
            try:
                send_mail(
                    subject="Sınav Takviminiz Güncellendi",
                    message="Merhaba, bağlı olduğunuz bölümdeki sınav programında bir değişiklik yapıldı. Lütfen sistemden kontrol ediniz.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[student.email],
                    fail_silently=False
                )
            except Exception as e:
                print(f"[!] Email failed to {student.email}: {e}")

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
        
        if user.is_student:
            queryset = queryset.filter(course__department=user.department)
        elif user.is_instructor:
            queryset = queryset.filter(
                Q(course__instructor=user) | Q(course__department=user.department)
            )

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
        exam = serializer.save(created_by=self.request.user)
        notify_students_of_exam_change(exam)  # ✔️ Yeni sınavda bildirim gönder

class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def perform_update(self, serializer):
        exam = serializer.save()
        notify_students_of_exam_change(exam)  # ✔️ Sınav güncellendiğinde bildir

    def perform_destroy(self, instance):
        notify_students_of_exam_change(instance)  # ✔️ Sınav silinmeden önce bildir
        instance.delete()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_exams(request):
    user = request.user
    
    if user.is_instructor:
        exams = Exam.objects.filter(course__instructor=user).order_by('date', 'start_time')
    elif user.is_student:
        enrolled_exams = ExamEnrollment.objects.filter(student=user)
        exams = [enrollment.exam for enrollment in enrolled_exams]
        exams.sort(key=lambda x: (x.date, x.start_time))
    else:
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
