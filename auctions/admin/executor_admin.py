# auctions/admin/executor_admin.py
from django.contrib import admin

class ExecutorAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title',)
    readonly_fields = ('slug',)