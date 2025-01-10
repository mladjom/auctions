# auctions/admin/auction_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ..models.auction_document_model import AuctionDocument

class AuctionDocumentInline(admin.TabularInline):
    model = AuctionDocument.auctions.through
    extra = 1
    verbose_name = _("Document")
    verbose_name_plural = _("Documents")
    
    # Show these fields in the inline
    readonly_fields = ('get_title',  'get_file')
    fields = ('get_title', 'get_file')

    def get_title(self, obj):
        return obj.auctiondocument.title if obj.auctiondocument else ""
    get_title.short_description = _("Title")

    def get_file(self, obj):
        if obj.auctiondocument and obj.auctiondocument.file:
            return obj.auctiondocument.file.url
        return ""
    get_file.short_description = _("File")

class AuctionAdmin(admin.ModelAdmin):
    list_display = ('code', 'title','status', 'starting_price', 'estimated_value', 
                   'publication_date', 'start_time', 'end_time', 'category', 'executor')
    list_filter = ('status', 'category', 'executor', 'publication_date', 'start_time', 'end_time')
    search_fields = ('code', 'title', 'description')
    readonly_fields = ('code', 'slug', 'url')
    filter_horizontal = ('tags',)
    date_hierarchy = 'publication_date'
    inlines = [AuctionDocumentInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'title', 'slug', 'status', 'url', 'description')
        }),
        (_('Pricing'), {
            'fields': ('starting_price', 'estimated_value', 'bidding_step')
        }),
        (_('Dates'), {
            'fields': ('publication_date', 'start_time', 'end_time')
        }),

        (_('Relations'), {
            'fields': ('category', 'executor', 'location', 'tags')
        }),
        (_('Additional Information'), {
            'fields': ('sale_number',)
        }),
    )
    
    # def related_documents(self, obj):
    #     """Display related AuctionDocuments."""
    #     return ", ".join([doc.title for doc in obj.documents.all()])
    
    # related_documents.short_description = "Related Documents"