# auctions/admin/auction_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

class AuctionAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'status', 'starting_price', 'estimated_value', 
                   'publication_date', 'start_time', 'end_time', 'category', 'executor')
    list_filter = ('status', 'category', 'executor', 'publication_date', 'start_time', 'end_time')
    search_fields = ('code', 'title', 'description')
    readonly_fields = ('code', 'slug', 'url')
    filter_horizontal = ('tags',)
    date_hierarchy = 'publication_date'
    
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