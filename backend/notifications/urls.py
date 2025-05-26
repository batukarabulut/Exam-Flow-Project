# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification endpoints
    path('', views.NotificationListCreateView.as_view(), name='notification_list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('<int:notification_id>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('summary/', views.notification_summary, name='notification_summary'),
    
    # Email log endpoints
    path('email-logs/', views.EmailLogListView.as_view(), name='email_log_list'),
]