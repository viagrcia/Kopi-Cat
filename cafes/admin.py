from django.contrib import admin
from .models import Cafe

@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ('name', 'barangay', 'price_range', 'created_at')
    search_fields = ('name', 'barangay', 'vibe_tags')
    prepopulated_fields = {'slug': ('name',)}