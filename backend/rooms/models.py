# rooms/models.py
from django.db import models

class Building(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Room(models.Model):
    ROOM_TYPES = [
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('amphitheater', 'Amphitheater'),
        ('conference', 'Conference Room'),
    ]
    
    name = models.CharField(max_length=50)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='classroom')
    has_projector = models.BooleanField(default=False)
    has_computer = models.BooleanField(default=False)
    has_whiteboard = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'building']
    
    def __str__(self):
        return f"{self.building.code}-{self.name} (Cap: {self.capacity})"
    
    @property
    def full_name(self):
        return f"{self.building.code}-{self.name}"