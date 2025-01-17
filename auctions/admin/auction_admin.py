from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ..models.auction_document_model import AuctionDocument
from .base_admin import BaseModelAdmin

class AuctionDocumentInline(admin.TabularInline):
    model = AuctionDocument.auctions.through
    extra = 1
    verbose_name = _("Document")
    verbose_name_plural = _("Documents")
    
    readonly_fields = ('get_title', 'get_file')
    fields = ('get_title', 'get_file')

    def get_title(self, obj):
        return obj.auctiondocument.title if obj.auctiondocument else ""
    get_title.short_description = _("Title")

    def get_file(self, obj):
        if obj.auctiondocument and obj.auctiondocument.file:
            return obj.auctiondocument.file.url
        return ""
    get_file.short_description = _("File")

class AuctionAdmin(BaseModelAdmin):
    list_display = ('code', 'title_sr', 'title_lat', 'status', 'starting_price', 
                   'estimated_value', 'publication_date', 'start_time', 'end_time', 
                   'category', 'executor')
    
    list_filter = ('status', 'category', 'executor', 'publication_date', 
                  'start_time', 'end_time')
    
    search_fields = BaseModelAdmin.search_fields + ('code',)
    
    readonly_fields = BaseModelAdmin.readonly_fields + ('code', 'url')
    filter_horizontal = ('tags',)
    date_hierarchy = 'publication_date'
    inlines = [AuctionDocumentInline]

    def get_fieldsets(self, request, obj=None):
        # Get the base fieldsets from BaseModelAdmin
        fieldsets = super().get_fieldsets(request, obj)
        
        # Add additional fieldsets specific to AuctionAdmin as a tuple
        additional_fieldsets = (
            (_('Basic Information'), {
                'fields': ('code', 'status', 'url', 'is_active')
            }),
            (_('Pricing'), {
                'fields': ('starting_price', 'estimated_value', 'bidding_step')
            }),
            (_('Dates'), {
                'fields': (
                    'publication_date', 
                    'start_time', 
                    'end_time',
                    'created_at',
                    'updated_at'
                )
            }),
            (_('Relations'), {
                'fields': ('category', 'executor', 'location', 'tags')
            }),
            (_('Additional Information'), {
                'fields': ('sale_number',)
            }),
        )
        
        return fieldsets + additional_fieldsets