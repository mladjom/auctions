# auctions/admin/document_admin.py
from django.contrib import admin

class AuctionDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')