# rooms/views.py
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Building, Room
from .serializers import BuildingSerializer, RoomSerializer, RoomAvailabilitySerializer
from exams.models import Exam

class BuildingListCreateView(generics.ListCreateAPIView):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

class BuildingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]

class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        building = self.request.query_params.get('building', None)
        is_available = self.request.query_params.get('is_available', None)
        min_capacity = self.request.query_params.get('min_capacity', None)
        
        if building:
            queryset = queryset.filter(building=building)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        if min_capacity:
            queryset = queryset.filter(capacity__gte=min_capacity)
            
        return queryset.order_by('building__code', 'name')

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_room_availability(request):
    serializer = RoomAvailabilitySerializer(data=request.data)
    if serializer.is_valid():
        date = serializer.validated_data['date']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']
        exclude_exam_id = serializer.validated_data.get('exclude_exam_id')
        
        # Get all rooms
        rooms = Room.objects.filter(is_available=True)
        available_rooms = []
        
        for room in rooms:
            # Check for conflicts
            conflicting_exams = Exam.objects.filter(
                room=room,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
                status__in=['scheduled', 'confirmed']
            )
            
            if exclude_exam_id:
                conflicting_exams = conflicting_exams.exclude(id=exclude_exam_id)
            
            if not conflicting_exams.exists():
                available_rooms.append(room)
        
        serializer = RoomSerializer(available_rooms, many=True)
        return Response({
            'available_rooms': serializer.data,
            'total_count': len(available_rooms)
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def room_schedule(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        exams = Exam.objects.filter(room=room)
        
        if date_from:
            exams = exams.filter(date__gte=date_from)
        if date_to:
            exams = exams.filter(date__lte=date_to)
            
        from exams.serializers import ExamSerializer
        serializer = ExamSerializer(exams, many=True)
        
        return Response({
            'room': RoomSerializer(room).data,
            'exams': serializer.data
        })
        
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)