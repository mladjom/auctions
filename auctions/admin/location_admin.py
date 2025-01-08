# auctions/admin/location_admin.py
from django.contrib import admin

class LocationAdmin(admin.ModelAdmin):
    list_display = ('municipality', 'city', 'cadastral_municipality', 'slug')
    search_fields = ('municipality', 'city', 'cadastral_municipality')
    list_filter = ('municipality', 'city')
    readonly_fields = ('slug',)