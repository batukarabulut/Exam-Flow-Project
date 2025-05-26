# rooms/urls.py
from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    # Building endpoints
    path('buildings/', views.BuildingListCreateView.as_view(), name='building_list'),
    path('buildings/<int:pk>/', views.BuildingDetailView.as_view(), name='building_detail'),
    
    # Room endpoints
    path('', views.RoomListCreateView.as_view(), name='room_list'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('<int:room_id>/schedule/', views.room_schedule, name='room_schedule'),
    
    # Room availability endpoints
    path('check-availability/', views.check_room_availability, name='check_availability'),
]