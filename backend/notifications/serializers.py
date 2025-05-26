# notifications/serializers.py
from rest_framework import serializers
from .models import Notification, EmailLog
from authentication.serializers import UserSerializer
from exams.serializers import ExamSerializer

class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    related_exam = ExamSerializer(read_only=True)
    recipient_id = serializers.IntegerField(write_only=True)
    sender_id = serializers.IntegerField(write_only=True, required=False)
    related_exam_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_id', 'sender', 'sender_id',
            'notification_type', 'title', 'message', 'priority',
            'related_exam', 'related_exam_id', 'is_read',
            'is_email_sent', 'email_sent_at', 'created_at'
        ]

class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'recipient', 'notification_type', 'title', 'message',
            'priority', 'related_exam'
        ]

class EmailLogSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'notification', 'recipient_email', 'subject',
            'status', 'error_message', 'sent_at', 'created_at'
        ]