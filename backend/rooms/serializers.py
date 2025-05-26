# rooms/serializers.py
from rest_framework import serializers
from .models import Building, Room

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'name', 'code', 'address']

class RoomSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    building_id = serializers.IntegerField(write_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'building', 'building_id', 'full_name',
            'capacity', 'room_type', 'has_projector', 'has_computer',
            'has_whiteboard', 'is_available', 'notes', 'created_at'
        ]

class RoomAvailabilitySerializer(serializers.Serializer):
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    exclude_exam_id = serializers.IntegerField(required=False)