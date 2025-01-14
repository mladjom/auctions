# auctions/admin/base_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

class BaseModelAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Content (Serbian Cyrillic)'), {
            'fields': (
                'title_sr',
                'description_sr',
                'meta_title_sr',
                'meta_description_sr',
            )
        }),
        (_('Content (Serbian Latin)'), {
            'fields': (
                'title_lat',
                'description_lat',
                'meta_title_lat',
                'meta_description_lat',
            )
        }),
        (_('URL and Dates'), {
            'fields': ('slug',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title_lat',)}    
    list_display = ('title_sr', 'title_lat', 'updated_at', 'slug')
    search_fields = ('title_sr', 'title_lat', 'description_sr', 'description_lat')
