from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from pages.models import PageModel


@admin.register(PageModel)
class PageModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'view_count', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at', 'updated_at')
    search_fields = ('title_sr', 'title_lat', 'content_sr', 'content_lat', 'meta_title_sr', 'meta_title_lat')
    prepopulated_fields = {'slug': ('title_lat',)}  # Prepopulate slug from title (Cyrillic)
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    save_on_top = True
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('title_sr', 'title_lat'),
                'slug',
                ('content_sr', 'content_lat'),
            )
        }),
        (_('SEO Settings'), {
            'fields': (
                ('meta_title_sr', 'meta_title_lat'),
                ('meta_description_sr', 'meta_description_lat'),
            ),
            'classes': ('collapse',),
        }),
        (_('Publication Settings'), {
            'fields': (
                'is_published',
                ('created_at', 'updated_at'),
                'view_count',
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_at',)
        return self.readonly_fields

    def view_count_display(self, obj):
        return format_html('<b>{}</b>', obj.view_count)
    view_count_display.short_description = _('Views')
    view_count_display.admin_order_field = 'view_count'

    def save_model(self, request, obj, form, change):
        """Override save_model to handle automatic Latin script conversion if needed"""
        if not obj.title_lat and obj.title_sr:
            from serbian_text_converter import SerbianTextConverter
            obj.title_lat = SerbianTextConverter.to_latin(obj.title_sr)
        super().save_model(request, obj, form, change)