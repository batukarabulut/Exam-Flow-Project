# rooms/admin.py
from django.contrib import admin
from .models import Building, Room

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'address']
    search_fields = ['name', 'code']
    ordering = ['code']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'building', 'capacity', 'room_type', 'is_available']
    list_filter = ['building', 'room_type', 'is_available', 'has_projector', 'has_computer']
    search_fields = ['name', 'building__name', 'building__code']
    ordering = ['building__code', 'name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'building', 'capacity', 'room_type')
        }),
        ('Equipment', {
            'fields': ('has_projector', 'has_computer', 'has_whiteboard')
        }),
        ('Status', {
            'fields': ('is_available', 'notes')
        }),
    )