# auctions/admin/tag_admin.py
from django.contrib import admin

class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('titles',)
    readonly_fields = ('slug',)