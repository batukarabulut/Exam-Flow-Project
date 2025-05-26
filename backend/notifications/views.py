# notifications/views.py
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Notification, EmailLog
from .serializers import NotificationSerializer, NotificationCreateSerializer, EmailLogSerializer

class NotificationListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            # Admins can see all notifications
            queryset = Notification.objects.all()
        else:
            # Users see only their notifications
            queryset = Notification.objects.filter(recipient=user)
        
        # Filters
        is_read = self.request.query_params.get('is_read', None)
        notification_type = self.request.query_params.get('type', None)
        priority = self.request.query_params.get('priority', None)
        
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if priority:
            queryset = queryset.filter(priority=priority)
            
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Notification.objects.all()
        return Notification.objects.filter(recipient=user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_as_read(request):
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    )
    notifications.update(is_read=True)
    
    return Response({
        'message': f'{notifications.count()} notifications marked as read'
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return Response({'unread_count': count})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_summary(request):
    user = request.user
    notifications = Notification.objects.filter(recipient=user)
    
    summary = {
        'total': notifications.count(),
        'unread': notifications.filter(is_read=False).count(),
        'high_priority': notifications.filter(priority='high').count(),
        'urgent': notifications.filter(priority='urgent').count(),
    }
    
    # Recent notifications (last 5)
    recent = notifications.order_by('-created_at')[:5]
    recent_serializer = NotificationSerializer(recent, many=True)
    
    return Response({
        'summary': summary,
        'recent_notifications': recent_serializer.data
    })

class EmailLogListView(generics.ListAPIView):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset.order_by('-created_at')